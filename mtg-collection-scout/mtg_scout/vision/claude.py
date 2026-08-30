"""Fotoauswertung mit Claude (offizielles Anthropic-SDK).

Das Kernprogramm bleibt abhaengigkeitsfrei; fuer die Bildanalyse wird das SDK
nur bei Bedarf geladen:

    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Ohne Schluessel und ohne SDK laeuft alles Uebrige unveraendert weiter; als
netzfreie Alternative gibt es die OCR-Auswertung in ocr.py.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .facts import PhotoCard, PhotoFacts, normalize_sealed

log = logging.getLogger("mtg_scout.vision.claude")

DEFAULT_MODEL = "claude-opus-5"
MAX_TOKENS = 4000

SYSTEM_PROMPT = (
    "Du bist ein erfahrener Magic-the-Gathering-Sammler und begutachtest Fotos aus "
    "Verkaufsanzeigen. Beschreibe ausschliesslich, was auf den Bildern tatsaechlich zu "
    "sehen ist. Erfinde keine Karten. Nenne einen Kartennamen nur, wenn du ihn lesen "
    "oder das Artwork sicher zuordnen kannst, und gib deine Sicherheit ehrlich an. "
    "Schaetze die Kartenmenge konservativ (sichtbare Stapel, Ordnerseiten, Kisten). "
    "Weise auf Auffaelligkeiten hin: Proxys oder Faelschungen, Beschaedigungen, "
    "fremde Sammelkartenspiele im Stapel, oder wenn es sich offensichtlich um ein "
    "Symbolbild statt der echten Ware handelt."
)

RESULT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "erkannte_karten": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "englischer Kartenname"},
                    "anzahl": {"type": "integer"},
                    "sicherheit": {"type": "number", "description": "0.0 bis 1.0"},
                },
                "required": ["name", "anzahl", "sicherheit"],
                "additionalProperties": False,
            },
        },
        "versiegelte_produkte": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "produkt": {"type": "string"},
                    "anzahl": {"type": "integer"},
                },
                "required": ["produkt", "anzahl"],
                "additionalProperties": False,
            },
        },
        "geschaetzte_kartenzahl": {"type": ["integer", "null"]},
        "zustand": {
            "type": "string",
            "enum": ["mint", "near_mint", "excellent", "good", "played", "poor", "unbekannt"],
        },
        "auffaelligkeiten": {"type": "array", "items": {"type": "string"}},
        "beschreibung": {"type": "string"},
    },
    "required": [
        "erkannte_karten", "versiegelte_produkte", "geschaetzte_kartenzahl",
        "zustand", "auffaelligkeiten", "beschreibung",
    ],
    "additionalProperties": False,
}


class VisionError(RuntimeError):
    """Bildanalyse nicht moeglich (fehlendes SDK, kein Schluessel, API-Fehler)."""


class ClaudeVision:
    """Wertet Anzeigenfotos mit Claude aus und liefert strukturierte Fakten."""

    def __init__(self, model: str = DEFAULT_MODEL, api_key: Optional[str] = None,
                 client: Any = None, max_images: int = 4) -> None:
        self.model = model or DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.max_images = max_images
        self._client = client          # fuer Tests injizierbar

    # ------------------------------------------------------------ Verfuegbarkeit
    def available(self) -> Tuple[bool, str]:
        if self._client is not None:
            return True, ""
        try:
            import anthropic  # noqa: F401
        except ImportError:
            return False, ("Fuer die Fotoauswertung fehlt das Anthropic-SDK: "
                           "pip install anthropic")
        if not self.api_key and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            return False, ("Kein API-Schluessel gefunden: ANTHROPIC_API_KEY setzen "
                           "(oder 'ant auth login' verwenden)")
        return True, ""

    def _ensure_client(self) -> Any:
        if self._client is None:
            ok, reason = self.available()
            if not ok:
                raise VisionError(reason)
            import anthropic

            self._client = (
                anthropic.Anthropic(api_key=self.api_key) if self.api_key
                else anthropic.Anthropic()
            )
        return self._client

    # -------------------------------------------------------------------- Analyse
    def analyze(self, images: Sequence[Tuple[str, str]], context: str = "") -> PhotoFacts:
        """images: Liste von (media_type, base64). context: Anzeigentitel als Hilfe."""
        if not images:
            return PhotoFacts()
        client = self._ensure_client()
        selected = list(images)[: self.max_images]

        content: List[Dict[str, Any]] = [
            {"type": "image", "source": {"type": "base64", "media_type": mime, "data": data}}
            for mime, data in selected
        ]
        content.append({"type": "text", "text": self._prompt(context)})

        response = self._create(client, content)
        if getattr(response, "stop_reason", "") == "refusal":
            details = getattr(response, "stop_details", None)
            raise VisionError(
                "Die Bildanalyse wurde abgelehnt"
                + (f" ({getattr(details, 'category', '')})" if details else "")
            )
        payload = self._first_json(response)
        facts = self.parse_payload(payload)
        facts.images_analyzed = len(selected)
        return facts

    def _prompt(self, context: str) -> str:
        lead = "Werte die Fotos dieser Verkaufsanzeige aus."
        if context:
            lead += f' Titel der Anzeige: "{context.strip()}"'
        return (
            f"{lead}\n\n"
            "Liste alle sicher erkennbaren Karten mit Anzahl und Sicherheit auf, "
            "erkenne versiegelte Produkte, schaetze die Gesamtzahl der Karten und "
            "den Zustand, und nenne Auffaelligkeiten. Antworte ausschliesslich im "
            "vorgegebenen JSON-Format."
        )

    def _create(self, client: Any, content: List[Dict[str, Any]]) -> Any:
        """Anfrage mit serverseitigem Refusal-Fallback, sonst ohne."""
        request: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": content}],
            "output_config": {"format": {"type": "json_schema", "schema": RESULT_SCHEMA}},
            "thinking": {"type": "adaptive"},
        }
        try:
            return client.beta.messages.create(
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                **request,
            )
        except Exception as exc:      # aeltere SDK-Version oder Beta nicht verfuegbar
            log.info("Fallback-Variante nicht nutzbar (%s) - Standardaufruf", exc)
            try:
                return client.messages.create(**request)
            except Exception as inner:
                raise VisionError(f"Anfrage an Claude fehlgeschlagen: {inner}") from inner

    @staticmethod
    def _first_json(response: Any) -> Dict[str, Any]:
        for block in getattr(response, "content", []) or []:
            if getattr(block, "type", "") == "text":
                try:
                    return json.loads(block.text)
                except json.JSONDecodeError as exc:
                    raise VisionError(f"Antwort war kein gueltiges JSON: {exc}") from exc
        raise VisionError("Antwort enthielt keinen Textblock")

    # --------------------------------------------------------------- Auswertung
    @staticmethod
    def parse_payload(payload: Dict[str, Any]) -> PhotoFacts:
        """Antwort-JSON in PhotoFacts uebersetzen (auch ohne Netz testbar)."""
        facts = PhotoFacts(source="claude")
        for entry in payload.get("erkannte_karten") or []:
            name = str(entry.get("name") or "").strip()
            if not name:
                continue
            facts.cards.append(
                PhotoCard(
                    name=name,
                    count=max(1, min(100, int(entry.get("anzahl") or 1))),
                    confidence=max(0.0, min(1.0, float(entry.get("sicherheit") or 0.5))),
                )
            )
        for entry in payload.get("versiegelte_produkte") or []:
            key = normalize_sealed(str(entry.get("produkt") or ""))
            if not key:
                continue
            quantity = max(1, min(50, int(entry.get("anzahl") or 1)))
            facts.sealed[key] = facts.sealed.get(key, 0) + quantity

        count = payload.get("geschaetzte_kartenzahl")
        if isinstance(count, (int, float)) and 1 <= count <= 500000:
            facts.card_count = int(count)

        condition = str(payload.get("zustand") or "").strip()
        facts.condition = "" if condition in ("", "unbekannt") else condition
        facts.flags = [str(f) for f in (payload.get("auffaelligkeiten") or []) if str(f).strip()]
        facts.summary = str(payload.get("beschreibung") or "").strip()
        return facts

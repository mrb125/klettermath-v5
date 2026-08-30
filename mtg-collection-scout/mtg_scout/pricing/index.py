"""Erkennung von Kartennamen in Freitext (Anzeigentitel/-beschreibung)."""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Tuple

from ..models import CardHit
from ..util import normalize

# Einzelwort-Namen, die als deutsches/englisches Alltagswort zu oft falsch anschlagen.
SINGLE_WORD_BLOCKLIST = {
    "island", "mountain", "forest", "swamp", "plains", "wish", "fury", "grief",
    "brainstorm", "counterspell", "healing", "shock", "giant", "wall", "opt",
    "duress", "lightning", "dark", "fog", "rest", "balance", "armageddon",
    "control", "power", "storm", "hope", "future", "past", "legends", "revised",
}

_TOKEN_RE = re.compile(r"[a-z0-9'’,\-]+")
_COUNT_RE = re.compile(r"(\d{1,2})\s*[x×]\s*$", re.IGNORECASE)


class CardIndex:
    """Nachschlagewerk Name -> Preis, plus n-Gramm-Scan ueber Anzeigentexte."""

    def __init__(self, entries: Iterable[Tuple[str, float, bool]], max_tokens: int = 5,
                 source: str = "scryfall") -> None:
        self.by_norm: Dict[str, Tuple[str, float, bool]] = {}
        self.max_tokens = 1
        self.source = source
        for name, price, reserved in entries:
            norm = normalize(name)
            if not norm:
                continue
            token_count = len(norm.split())
            if token_count > max_tokens:
                continue
            previous = self.by_norm.get(norm)
            if previous is None or price > previous[1]:
                self.by_norm[norm] = (name, float(price or 0.0), bool(reserved))
            self.max_tokens = max(self.max_tokens, token_count)

    def __len__(self) -> int:
        return len(self.by_norm)

    @classmethod
    def from_fallback(cls) -> "CardIndex":
        from .catalog import FALLBACK_CARDS
        return cls(
            ((name, price, reserved) for name, (price, reserved) in FALLBACK_CARDS.items()),
            source="katalog",
        )

    def lookup(self, name: str) -> Optional[Tuple[str, float, bool]]:
        return self.by_norm.get(normalize(name))

    def find(self, text: str, min_eur: float = 3.0, max_hits: int = 25) -> List[CardHit]:
        """Kartennamen im Text finden - laengste Treffer gewinnen, Ueberlappungen fallen weg."""
        if not text:
            return []
        norm_text = normalize(text)
        tokens = _TOKEN_RE.findall(norm_text)
        if not tokens:
            return []
        # Positionen der Token im Originaltext fuer Gross-/Kleinschreibungs-Check
        raw_tokens = _TOKEN_RE.findall(text.lower())
        used: set[int] = set()
        hits: Dict[str, CardHit] = {}

        for size in range(min(self.max_tokens, len(tokens)), 0, -1):
            for i in range(len(tokens) - size + 1):
                if used & set(range(i, i + size)):
                    continue
                phrase = " ".join(tokens[i : i + size]).strip(",")
                entry = self.by_norm.get(phrase)
                if entry is None:
                    continue
                name, price, reserved = entry
                if price < min_eur:
                    continue
                if size == 1 and not self._single_word_ok(phrase, text):
                    continue
                confidence = {1: 0.45, 2: 0.8}.get(size, 0.9)
                if reserved or price >= 200:
                    confidence = min(1.0, confidence + 0.1)
                count = self._preceding_count(text, name)
                used.update(range(i, i + size))
                existing = hits.get(name)
                if existing is None or count > existing.count:
                    hits[name] = CardHit(
                        name=name, price_eur=price, confidence=confidence,
                        count=count, reserved=reserved, source=self.source,
                    )
        ranked = sorted(hits.values(), key=lambda h: h.weighted_eur, reverse=True)
        return ranked[:max_hits]

    @staticmethod
    def _single_word_ok(word: str, original: str) -> bool:
        if word in SINGLE_WORD_BLOCKLIST or len(word) < 5:
            return False
        # Einzelwort-Namen nur akzeptieren, wenn sie im Original gross geschrieben sind
        return re.search(rf"\b{re.escape(word[0].upper() + word[1:])}", original) is not None

    @staticmethod
    def _preceding_count(text: str, name: str) -> int:
        """'4x Force of Will' -> 4 (auf Playset-Groesse gedeckelt)."""
        idx = normalize(text).find(normalize(name))
        if idx <= 0:
            return 1
        match = _COUNT_RE.search(text[:idx])
        if not match:
            return 1
        return max(1, min(4, int(match.group(1))))

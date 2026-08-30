"""Scryfall-Anbindung: Preis-Spiegel lokal aufbauen und Einzelabfragen."""

from __future__ import annotations

import json
import logging
from typing import Iterator, List, Optional, Tuple

from ..net import FetchError, HttpClient
from ..store import Store
from .index import CardIndex

log = logging.getLogger("mtg_scout.scryfall")

BULK_ENDPOINT = "https://api.scryfall.com/bulk-data"
NAMED_ENDPOINT = "https://api.scryfall.com/cards/named?fuzzy="


class ScryfallPrices:
    """Haelt einen lokalen Preisspiegel (SQLite) und baut daraus den Namensindex."""

    def __init__(self, store: Store, client: Optional[HttpClient] = None) -> None:
        self.store = store
        self.client = client

    # ------------------------------------------------------------ Aktualisieren
    def refresh(self, bulk_type: str = "oracle_cards") -> int:
        """Bulk-Datei von Scryfall laden und Preise in die Datenbank schreiben."""
        if self.client is None:
            raise FetchError("Kein HTTP-Client verfuegbar (Offline-Modus?)")
        catalog = self.client.fetch_json(BULK_ENDPOINT, use_cache=False)
        entry = next(
            (e for e in catalog.get("data", []) if e.get("type") == bulk_type), None
        )
        if entry is None:
            raise FetchError(f"Bulk-Typ {bulk_type} nicht im Scryfall-Katalog gefunden")
        log.info("Lade %s (%s MB) ...", entry.get("name"),
                 round((entry.get("size") or 0) / 1e6, 1))
        payload = self.client.fetch(entry["download_uri"], use_cache=False)
        cards = json.loads(payload)
        count = self.store.replace_cards(self._rows(cards))
        log.info("%s Karten gespeichert", count)
        return count

    @staticmethod
    def _rows(cards: List[dict]) -> Iterator[Tuple[str, Optional[float], Optional[float], str, bool, str]]:
        for card in cards:
            name = card.get("name")
            if not name:
                continue
            prices = card.get("prices") or {}
            eur = _as_float(prices.get("eur")) or _as_float(prices.get("eur_foil"))
            usd = _as_float(prices.get("usd")) or _as_float(prices.get("usd_foil"))
            if eur is None and usd is not None:
                eur = round(usd * 0.92, 2)
            yield (
                name, eur, usd, card.get("rarity") or "",
                bool(card.get("reserved")), card.get("set") or "",
            )

    # ------------------------------------------------------------------ Abfrage
    def index(self, min_eur: float = 4.0) -> CardIndex:
        """Namensindex bauen: aus der DB, sonst aus dem eingebauten Katalog."""
        rows = self.store.expensive_card_names(min_eur=min_eur)
        if not rows:
            log.info("Kein Scryfall-Spiegel vorhanden - nutze eingebauten Katalog "
                     "(mtg-scout preise --aktualisieren fuer echte Marktpreise)")
            return CardIndex.from_fallback()
        return CardIndex(
            ((row["name"], row["eur"] or (row["usd"] or 0) * 0.92, bool(row["reserved"]))
             for row in rows),
            source="scryfall",
        )

    def price_of(self, name: str) -> Optional[float]:
        row = self.store.lookup_card(name)
        if row is not None:
            return row["eur"] or ((row["usd"] or 0) * 0.92) or None
        from .catalog import FALLBACK_CARDS
        entry = FALLBACK_CARDS.get(name)
        if entry:
            return entry[0]
        if self.client is None:
            return None
        try:
            data = self.client.fetch_json(NAMED_ENDPOINT + name.replace(" ", "+"))
        except FetchError:
            return None
        prices = data.get("prices") or {}
        return _as_float(prices.get("eur")) or (
            (_as_float(prices.get("usd")) or 0) * 0.92 or None
        )


def _as_float(value: object) -> Optional[float]:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None

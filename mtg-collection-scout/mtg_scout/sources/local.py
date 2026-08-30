"""Lokale Quellen: eigene JSON/CSV-Dateien und ein Demo-Datensatz ohne Netz."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from ..models import Listing
from ..util import parse_price
from .base import SearchQuery, Source

log = logging.getLogger("mtg_scout.sources.local")

DEMO_FILE = Path(__file__).resolve().parent.parent / "data" / "demo_listings.json"


def load_listings_file(path: Path) -> List[Listing]:
    """JSON (Liste von Objekten) oder CSV mit Spaltenkopf einlesen."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        rows: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                rows.append({k: (v or "").strip() for k, v in row.items() if k})
    else:
        data = json.loads(path.read_text("utf-8"))
        rows = data["listings"] if isinstance(data, dict) else data

    listings: List[Listing] = []
    for row in rows:
        row = dict(row)
        row.setdefault("source", "datei")
        price = row.get("price")
        if isinstance(price, str):
            parsed, currency = parse_price(price, row.get("currency") or "EUR")
            row["price"] = parsed
            row["currency"] = currency
        elif price is not None:
            row["price"] = float(price)
        if not row.get("title"):
            continue
        row.setdefault("url", "")
        listings.append(Listing.from_dict(row))
    return listings


class FileSource(Source):
    """Angebote aus einer eigenen Datei bewerten (z.B. manuell kopierte Anzeigen)."""

    name = "datei"
    label = "Lokale Datei"

    def __init__(self, config: Dict[str, Any], client, path: Path | str = "") -> None:
        super().__init__(config, client)
        self.path = Path(path) if path else None

    def available(self) -> tuple[bool, str]:
        if not self.path:
            return False, "Kein Dateipfad gesetzt (--datei angeben)"
        if not self.path.exists():
            return False, f"Datei {self.path} nicht gefunden"
        return True, ""

    def search(self, query: SearchQuery) -> List[Listing]:
        ok, reason = self.available()
        if not ok:
            log.warning("Datei-Quelle uebersprungen: %s", reason)
            return []
        return load_listings_file(self.path)[: query.limit]


class DemoSource(Source):
    """Beispielangebote, damit das Tool auch ohne Netz und Zugangsdaten laeuft."""

    name = "demo"
    label = "Demo-Datensatz (offline)"

    def search(self, query: SearchQuery) -> List[Listing]:
        if not DEMO_FILE.exists():
            return []
        return load_listings_file(DEMO_FILE)[: query.limit]

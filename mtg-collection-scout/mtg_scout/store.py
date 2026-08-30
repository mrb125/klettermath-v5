"""SQLite-Speicher: Kartenpreise (Scryfall-Spiegel) und bereits gesehene Angebote."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .util import normalize

SCHEMA = """
CREATE TABLE IF NOT EXISTS card_prices (
    name_norm TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    eur       REAL,
    usd       REAL,
    rarity    TEXT,
    reserved  INTEGER DEFAULT 0,
    set_code  TEXT,
    updated   REAL
);
CREATE TABLE IF NOT EXISTS seen_listings (
    listing_id TEXT PRIMARY KEY,
    source     TEXT,
    title      TEXT,
    url        TEXT,
    price_eur  REAL,
    score      REAL,
    first_seen REAL,
    last_seen  REAL
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE INDEX IF NOT EXISTS idx_seen_last ON seen_listings(last_seen);
"""


class Store:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ------------------------------------------------------------ Kartenpreise
    def replace_cards(self, rows: Iterable[Tuple[str, Optional[float], Optional[float], str, bool, str]]) -> int:
        """rows: (name, eur, usd, rarity, reserved, set_code). Ersetzt den Bestand."""
        now = time.time()
        payload = [
            (normalize(name), name, eur, usd, rarity, int(bool(reserved)), set_code, now)
            for name, eur, usd, rarity, reserved, set_code in rows
        ]
        cur = self.conn.cursor()
        cur.execute("DELETE FROM card_prices")
        cur.executemany(
            "INSERT OR REPLACE INTO card_prices"
            " (name_norm, name, eur, usd, rarity, reserved, set_code, updated)"
            " VALUES (?,?,?,?,?,?,?,?)",
            payload,
        )
        self.conn.commit()
        self.set_meta("cards_updated", str(now))
        return len(payload)

    def card_count(self) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM card_prices").fetchone()[0])

    def lookup_card(self, name: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM card_prices WHERE name_norm = ?", (normalize(name),)
        ).fetchone()

    def expensive_card_names(self, min_eur: float = 4.0, limit: int = 60000) -> List[sqlite3.Row]:
        """Namensindex fuer die Texterkennung - nur Karten oberhalb einer Wertschwelle."""
        return list(
            self.conn.execute(
                "SELECT name, name_norm, eur, usd, reserved, rarity FROM card_prices"
                " WHERE COALESCE(eur, usd * 0.92, 0) >= ? ORDER BY eur DESC LIMIT ?",
                (min_eur, limit),
            )
        )

    # ----------------------------------------------------------- Angebotsspur
    def is_new(self, listing_id: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM seen_listings WHERE listing_id = ?", (listing_id,)
        ).fetchone() is None

    def mark_seen(self, listing_id: str, source: str, title: str, url: str,
                  price_eur: Optional[float], score: float) -> None:
        now = time.time()
        self.conn.execute(
            "INSERT INTO seen_listings (listing_id, source, title, url, price_eur, score,"
            " first_seen, last_seen) VALUES (?,?,?,?,?,?,?,?)"
            " ON CONFLICT(listing_id) DO UPDATE SET last_seen=excluded.last_seen,"
            " price_eur=excluded.price_eur, score=excluded.score",
            (listing_id, source, title, url, price_eur, score, now, now),
        )
        self.conn.commit()

    def mark_seen_many(self, entries: Sequence[Tuple[str, str, str, str, Optional[float], float]]) -> None:
        for entry in entries:
            self.mark_seen(*entry)

    # -------------------------------------------------------------------- meta
    def set_meta(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES (?,?)", (key, value)
        )
        self.conn.commit()

    def get_meta(self, key: str) -> Optional[str]:
        row = self.conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None

    def stats(self) -> Dict[str, object]:
        return {
            "karten": self.card_count(),
            "gesehene_angebote": int(
                self.conn.execute("SELECT COUNT(*) FROM seen_listings").fetchone()[0]
            ),
            "preise_aktualisiert": self.get_meta("cards_updated"),
        }

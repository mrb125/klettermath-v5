"""Waehrungsumrechnung nach EUR - live (EZB via frankfurter.dev) mit statischem Fallback."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional

from .net import FetchError, HttpClient

log = logging.getLogger("mtg_scout.currency")

# Grobe Fallback-Kurse (1 Einheit -> EUR). Nur Notnagel, wenn kein Live-Kurs verfuegbar ist.
FALLBACK_RATES: Dict[str, float] = {
    "EUR": 1.0,
    "USD": 0.92,
    "GBP": 1.17,
    "CHF": 1.05,
    "PLN": 0.23,
    "CZK": 0.040,
    "SEK": 0.088,
    "DKK": 0.134,
    "NOK": 0.086,
    "CAD": 0.68,
    "AUD": 0.61,
    "JPY": 0.0060,
}

_API = "https://api.frankfurter.dev/v1/latest?base=EUR"


class CurrencyConverter:
    # Klassenweite Vorgaben, damit Unterklassen ohne eigenes __init__ funktionieren
    _fresh = False
    _tried_refresh = False

    def __init__(self, client: Optional[HttpClient] = None, cache_file: Optional[Path] = None,
                 ttl: float = 86400.0) -> None:
        self.client = client
        self.cache_file = Path(cache_file) if cache_file else None
        self.ttl = ttl
        self.rates: Dict[str, float] = dict(FALLBACK_RATES)
        self.live = False
        self._fresh = False
        self._tried_refresh = False
        self._load_cache()

    def _load_cache(self) -> None:
        if not (self.cache_file and self.cache_file.exists()):
            return
        try:
            data = json.loads(self.cache_file.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        self.rates.update(data.get("rates", {}))
        self.live = True
        self._fresh = (time.time() - self.cache_file.stat().st_mtime) < self.ttl

    def refresh(self) -> bool:
        """Kurse aktualisieren. Gibt False zurueck, wenn nur Fallback-Kurse gelten."""
        self._tried_refresh = True
        if self.client is None:
            return self.live
        try:
            payload = self.client.fetch_json(_API)
            # API liefert EUR -> X; wir brauchen X -> EUR
            rates = {"EUR": 1.0}
            for code, value in (payload.get("rates") or {}).items():
                if value:
                    rates[code.upper()] = 1.0 / float(value)
            if len(rates) > 1:
                self.rates.update(rates)
                self.live = True
                self._fresh = True
                if self.cache_file:
                    self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                    self.cache_file.write_text(json.dumps({"rates": rates}), "utf-8")
                return True
        except (FetchError, ValueError, TypeError, OSError) as exc:
            log.debug("Live-Wechselkurse nicht verfuegbar (%s) - nutze Fallback", exc)
        return self.live

    def to_eur(self, amount: Optional[float], currency: str) -> Optional[float]:
        """Betrag in EUR umrechnen. Live-Kurse werden erst bei Bedarf geholt."""
        if amount is None:
            return None
        code = (currency or "EUR").upper()
        if code != "EUR" and not self._fresh and not self._tried_refresh:
            self.refresh()
        rate = self.rates.get(code)
        if rate is None:
            log.warning("Unbekannte Waehrung %s - behandle 1:1 zu EUR", currency)
            rate = 1.0
        return round(amount * rate, 2)

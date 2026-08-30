"""Gemeinsame Schnittstelle aller Marktplatz-Quellen."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models import Listing
from ..net import HttpClient

log = logging.getLogger("mtg_scout.sources")

DEFAULT_TERMS = [
    "magic the gathering sammlung",
    "magic the gathering konvolut",
    "mtg collection lot",
]


@dataclass
class SearchQuery:
    """Was gesucht werden soll - quellenunabhaengig formuliert."""

    terms: List[str] = field(default_factory=lambda: list(DEFAULT_TERMS))
    limit: int = 50
    min_price_eur: Optional[float] = None
    max_price_eur: Optional[float] = None
    markets: List[str] = field(default_factory=list)      # z.B. EBAY_DE, EBAY_US
    postal_code: str = ""                                  # fuer regionale Portale
    radius_km: Optional[int] = None
    max_pages: int = 2


class Source(ABC):
    """Eine Angebotsquelle (Marktplatz)."""

    name: str = "quelle"
    label: str = "Quelle"
    countries: List[str] = []

    def __init__(self, config: Dict[str, Any], client: HttpClient) -> None:
        self.config = config
        self.client = client

    def available(self) -> tuple[bool, str]:
        """(nutzbar?, Begruendung) - z.B. fehlende API-Zugangsdaten."""
        return True, ""

    @abstractmethod
    def search(self, query: SearchQuery) -> List[Listing]:
        """Angebote suchen. Fehler einzelner Seiten werden geloggt, nicht geworfen."""

    # Hilfsfunktion fuer Unterklassen
    @staticmethod
    def _dedupe(listings: List[Listing]) -> List[Listing]:
        seen: set[str] = set()
        unique: List[Listing] = []
        for listing in listings:
            if listing.listing_id in seen:
                continue
            seen.add(listing.listing_id)
            unique.append(listing)
        return unique

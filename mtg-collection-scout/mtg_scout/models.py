"""Datenmodelle fuer Angebote, Preistreffer und Bewertungen."""

from __future__ import annotations

import dataclasses
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def _slug(*parts: str) -> str:
    raw = "|".join(p or "" for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


@dataclass
class Listing:
    """Ein Angebot von einem Marktplatz (roh, noch unbewertet)."""

    source: str
    title: str
    url: str
    price: Optional[float] = None
    currency: str = "EUR"
    description: str = ""
    country: str = ""
    location: str = ""
    seller: str = ""
    seller_rating: Optional[float] = None      # z.B. eBay-Bewertungsquote in Prozent
    seller_feedback: Optional[int] = None      # Anzahl Bewertungen
    condition: str = ""
    image_url: str = ""
    posted_at: str = ""
    shipping: Optional[float] = None
    listing_id: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.listing_id:
            self.listing_id = f"{self.source}:{_slug(self.url or self.title, self.title)}"
        self.currency = (self.currency or "EUR").upper()

    @property
    def text(self) -> str:
        """Titel + Beschreibung, gemeinsam durchsuchbar."""
        return f"{self.title}\n{self.description}".strip()

    def to_dict(self) -> Dict[str, Any]:
        d = dataclasses.asdict(self)
        d.pop("raw", None)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Listing":
        allowed = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in allowed})


@dataclass
class CardHit:
    """Ein im Text erkannter Kartenname mit Marktpreis."""

    name: str
    price_eur: float
    confidence: float = 0.6
    count: int = 1
    reserved: bool = False
    source: str = "scryfall"

    @property
    def weighted_eur(self) -> float:
        """Preis gewichtet mit Trefferwahrscheinlichkeit und erkannter Stueckzahl."""
        return self.price_eur * self.confidence * max(1, self.count)


@dataclass
class ValueEstimate:
    """Geschaetzter Sammlungswert mit Spannweite und nachvollziehbarer Herleitung."""

    low: float = 0.0
    mid: float = 0.0
    high: float = 0.0
    breakdown: List[str] = field(default_factory=list)
    confidence: float = 0.3   # 0..1, wie belastbar die Schaetzung ist


@dataclass
class Evaluation:
    """Bewertetes Angebot."""

    listing: Listing
    price_eur: Optional[float]
    estimate: ValueEstimate
    card_hits: List[CardHit] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    card_count: Optional[int] = None
    score: float = 0.0          # 0..100 Deal-Score
    grade: str = "?"            # A+ .. F
    verdict: str = ""

    @property
    def ratio(self) -> Optional[float]:
        """Verhaeltnis geschaetzter Wert / Preis (>1 = potenziell guenstig)."""
        if not self.price_eur or self.price_eur <= 0:
            return None
        return self.estimate.mid / self.price_eur

    @property
    def price_per_card(self) -> Optional[float]:
        if not self.price_eur or not self.card_count:
            return None
        return self.price_eur / self.card_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "listing": self.listing.to_dict(),
            "price_eur": self.price_eur,
            "estimate": dataclasses.asdict(self.estimate),
            "card_hits": [dataclasses.asdict(c) for c in self.card_hits],
            "signals": self.signals,
            "risks": self.risks,
            "card_count": self.card_count,
            "score": round(self.score, 1),
            "grade": self.grade,
            "verdict": self.verdict,
            "ratio": round(self.ratio, 2) if self.ratio else None,
            "price_per_card": round(self.price_per_card, 3) if self.price_per_card else None,
        }

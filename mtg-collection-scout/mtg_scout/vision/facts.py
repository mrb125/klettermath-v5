"""Ergebnis einer Fotoauswertung."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PhotoCard:
    """Eine auf einem Foto erkannte Karte."""

    name: str
    count: int = 1
    confidence: float = 0.5


@dataclass
class PhotoFacts:
    """Was auf den Anzeigenfotos zu sehen ist."""

    cards: List[PhotoCard] = field(default_factory=list)
    sealed: Dict[str, int] = field(default_factory=dict)
    card_count: Optional[int] = None
    condition: str = ""
    flags: List[str] = field(default_factory=list)
    summary: str = ""
    images_analyzed: int = 0
    source: str = "vision"

    def __bool__(self) -> bool:
        return bool(
            self.cards or self.sealed or self.card_count or self.flags or self.summary
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "karten": [{"name": c.name, "anzahl": c.count, "sicherheit": c.confidence}
                       for c in self.cards],
            "versiegelt": self.sealed,
            "kartenzahl": self.card_count,
            "zustand": self.condition,
            "auffaelligkeiten": self.flags,
            "beschreibung": self.summary,
            "bilder": self.images_analyzed,
            "quelle": self.source,
        }


# Freitext der Bildanalyse -> interne Schluessel der versiegelten Produkte
# Reihenfolge zaehlt: spezifische Begriffe zuerst pruefen
SEALED_KEYWORDS = {
    "collector booster": "collector_booster_box",
    "booster box": "display",
    "display": "display",
    "fat pack": "bundle",
    "bundle": "bundle",
    "commander deck": "precon_deck",
    "precon": "precon_deck",
    "tournament pack": "starter_deck",
    "starter": "starter_deck",
    "booster": "booster",
}


def normalize_sealed(label: str) -> str:
    """Produktbezeichnung der Bildanalyse auf einen bekannten Schluessel abbilden."""
    text = (label or "").lower()
    for keyword, key in SEALED_KEYWORDS.items():
        if keyword in text:
            return key
    return ""

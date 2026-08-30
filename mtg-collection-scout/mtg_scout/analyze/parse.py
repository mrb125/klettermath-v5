"""Aus Anzeigentext harte Fakten ziehen: Kartenzahl, Aera, Zustand, Risiken."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..util import normalize_de as normalize

# --------------------------------------------------------------------- Aeren
# Schluesselwort -> (Aera-Schluessel, Gewicht 0..1 fuer die Trefferstaerke)
ERA_KEYWORDS: Dict[str, tuple[str, float]] = {}


def _register(era: str, weight: float, *keywords: str) -> None:
    for keyword in keywords:
        ERA_KEYWORDS[normalize(keyword)] = (era, weight)


# 1993-1995: die teure Zeit
_register("vintage", 1.0, "alpha", "limited edition alpha", "beta", "limited edition beta",
          "unlimited", "collectors edition", "international edition", "summer magic",
          "arabian nights", "antiquities", "the dark", "legends", "revised", "revised edition",
          "3rd edition", "3. edition", "fbb", "foreign black border", "sammleredition")
_register("oldschool", 0.6, "90er", "90s", "1990er", "neunziger", "aus den 90ern")
_register("oldschool", 0.7, "fallen empires", "homelands", "ice age", "alliances", "chronicles",
          "mirage", "visions", "weatherlight", "4th edition", "4. edition", "renaissance",
          "5th edition", "portal", "starter 1999")
_register("retro", 0.45, "tempest", "stronghold", "exodus", "urza", "urza's saga",
          "urzas saga", "masques", "mercadian", "invasion", "odyssey", "onslaught",
          "mirrodin", "kamigawa", "ravnica", "time spiral", "lorwyn", "zendikar",
          "innistrad", "6th edition", "7th edition", "8th edition", "9th edition")
_register("modern", 0.25, "modern horizons", "double masters", "ultimate masters",
          "commander masters", "the brothers war", "lord of the rings", "herr der ringe",
          "kaldheim", "eldraine", "bloomburrow", "duskmourn", "foundations", "aetherdrift",
          "final fantasy", "assassin's creed", "spider-man", "avatar")

VINTAGE_ERAS = {"vintage", "oldschool"}

# ------------------------------------------------------------------ versiegelt
SEALED_PATTERNS: Dict[str, str] = {
    "display": r"\b(displays?|booster ?box(es)?|boosterbox(en)?)\b",
    "collector_booster_box": r"\bcollector ?booster ?(box(es)?|displays?)\b",
    "bundle": r"\b(bundles?|fat ?packs?|gift ?box(es)?|geschenkbox(en)?)\b",
    "booster": r"\b(boosters?|boosterpacks?|draft boosters?|set boosters?|play boosters?)\b",
    "precon_deck": r"\b(commander ?decks?|precons?|theme ?decks?|planeswalker ?decks?|challenger ?decks?)\b",
    "starter_deck": r"\b(starter ?(decks?|sets?)|tournament ?packs?|einsteiger ?sets?)\b",
}
SEALED_CONTEXT = r"\b(sealed|versiegelt|originalverpackt|ovp|neu und ungeoffnet|ungeoffnet|new sealed)\b"

# --------------------------------------------------------------------- Zustand
CONDITION_PATTERNS: Dict[str, str] = {
    "mint": r"\b(mint|gem ?mint|psa ?10|bgs ?9\.5)\b",
    "near_mint": r"\b(near ?mint|nm|neuwertig|top ?zustand|einwandfrei)\b",
    "excellent": r"\b(excellent|ex\+?|sehr gut(er)? zustand|leicht gespielt|light(ly)? played|lp)\b",
    "good": r"\b(good|gut(er)? zustand|gespielt|played|moderately played|mp)\b",
    "played": r"\b(stark gespielt|heavily played|hp|abgegriffen|gebraucht)\b",
    "poor": r"\b(poor|damaged|beschadigt|wasserschaden|geknickt|zerkratzt|risse?|bemalt)\b",
}

# ---------------------------------------------------------------------- Risiken
RISK_PATTERNS: Dict[str, str] = {
    "Proxys/Fakes erwaehnt": r"\b(proxys?|proxies|fake|falschung|nachdruck|counterfeit|kopie[n]?|repro)\b",
    "Nur Massenware/Commons": r"\b(nur commons|nur gemeine|bulk|wuhlkiste|restposten|aussortiert|keine rares|ohne rares)\b",
    "Beschaedigte Karten": r"\b(beschadigt|wasserschaden|schimmel|geknickt|bemalt|zerschnitten|kindergekritzel)\b",
    "Blindkauf ohne Details": r"\b(blind ?kauf|ohne gewahr|wie gesehen|as ?is|unbesehen)\b",
    "Zahlung ohne Kaeuferschutz": r"\b(paypal freunde|freunde und familie|friends ?& ?family|vorkasse|uberweisung only|western union)\b",
    "Nur Abholung": r"\b(nur abholung|abholung only|kein versand|selbstabholer)\b",
    "Auktion laeuft noch": r"\b(auktion|gebot|startgebot|bieten)\b",
    "Sammlung unsortiert": r"\b(unsortiert|ungesichtet|nie gesichtet|nicht gesichtet|dachbodenfund ungesichtet)\b",
}

# --------------------------------------------------------------- gute Signale
SIGNAL_PATTERNS: Dict[str, str] = {
    "Sammlungsaufloesung": r"\b(sammlung(sauflosung)?|auflosung|nachlass|erbe|komplette sammlung|lebenswerk)\b",
    "Dachbodenfund": r"\b(dachbodenfund|kellerfund|scheunenfund|attic find)\b",
    "Rares/Mythics genannt": r"\b(rares?|mythics?|seltene karten|rare karten)\b",
    "Foils genannt": r"\b(foil[s]?|glitzer|holo)\b",
    "Reserved List": r"\b(reserved ?list|reservierte liste)\b",
    "Dual Lands": r"\b(dual ?lands?|duals)\b",
    "Power 9": r"\b(power ?9|power ?nine)\b",
    "Fetch-/Shocklands": r"\b(fetch ?lands?|shock ?lands?|fetchies)\b",
    "Karten sortiert": r"\b(sortiert|nach farben sortiert|nach editionen sortiert|in ordnern|toploader|sleeves)\b",
    "Liste/Bilder vorhanden": r"\b(liste|inventar|alle karten fotografiert|bilder aller|scan)\b",
    "Graded": r"\b(psa|bgs|cgc) ?(\d{1,2}(\.\d)?)\b",
    "Erstauflage/Sammlerkarten": r"\b(erstauflage|first edition|schwarze rander|black border|deutsch limitiert)\b",
}

# ------------------------------------------------------------- Kartenmengen
_COUNT_PATTERNS = [
    r"(?:ca\.?|circa|uber|rund|etwa|mehr als|~|>)?\s*(\d{1,3}(?:[.\s]\d{3})+|\d{2,6})\s*(?:\+)?\s*"
    r"(?:weitere\s+|verschiedene\s+)?(?:magic[- ]?)?"
    r"(?:karten|cards|stuck|st\.|kartenexemplare|rares?|commons?|uncommons?|mythics?)",
    r"(\d{1,3})\s*[k]\s*(?:karten|cards)",
]
_BINDER_PATTERN = r"(\d{1,3})\s*(?:ordner|sammelordner|binder|alben|album|kisten|kartons|boxen|boxes|schachteln)"
# grobe Faustwerte pro Behaelter
BINDER_CARDS = 360
BOX_CARDS = 800

WANTED_PATTERN = r"\b(suche|gesucht|kaufe|ankauf|tausche|wtb|looking for|biete an tausch)\b"


@dataclass
class ListingFacts:
    """Was sich aus dem Anzeigentext ableiten laesst."""

    card_count: Optional[int] = None
    card_count_source: str = ""
    eras: Dict[str, float] = field(default_factory=dict)
    sealed: Dict[str, int] = field(default_factory=dict)
    condition: str = "unknown"
    risks: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    is_wanted_ad: bool = False
    graded: bool = False
    language: str = ""

    @property
    def top_era(self) -> Optional[str]:
        if not self.eras:
            return None
        return max(self.eras.items(), key=lambda kv: kv[1])[0]

    @property
    def era_weight(self) -> float:
        return max(self.eras.values(), default=0.0)


def _to_int(token: str) -> Optional[int]:
    digits = re.sub(r"[^\d]", "", token)
    return int(digits) if digits else None


def parse_card_count(text: str) -> tuple[Optional[int], str]:
    """Kartenanzahl schaetzen - direkt genannt oder ueber Ordner/Kisten hochgerechnet."""
    norm = normalize(text)
    best: Optional[int] = None
    source = ""
    for pattern_index, pattern in enumerate(_COUNT_PATTERNS):
        for match in re.finditer(pattern, norm):
            value = _to_int(match.group(1))
            if value is None:
                continue
            if pattern_index == 1:      # Schreibweise "5k Karten"
                value *= 1000
            if 10 <= value <= 500000 and (best is None or value > best):
                best, source = value, "im Text genannt"
    if best is not None:
        return best, source

    containers = 0
    for match in re.finditer(_BINDER_PATTERN, norm):
        count = _to_int(match.group(1)) or 0
        if 1 <= count <= 200:
            per = BOX_CARDS if re.search(r"kiste|karton|box|schachtel", match.group(0)) else BINDER_CARDS
            containers += count * per
    if containers:
        return containers, "aus Ordnern/Kisten hochgerechnet"
    return None, ""


def parse_listing(text: str) -> ListingFacts:
    """Vollstaendige Textanalyse eines Angebots."""
    facts = ListingFacts()
    norm = normalize(text)
    if not norm:
        return facts

    facts.card_count, facts.card_count_source = parse_card_count(text)

    for keyword, (era, weight) in ERA_KEYWORDS.items():
        if re.search(rf"\b{re.escape(keyword)}\b", norm):
            facts.eras[era] = max(facts.eras.get(era, 0.0), weight)

    sealed_context = re.search(SEALED_CONTEXT, norm) is not None
    for kind, pattern in SEALED_PATTERNS.items():
        matches = list(re.finditer(pattern, norm))
        if not matches:
            continue
        if kind in ("booster", "display", "collector_booster_box") and not sealed_context:
            # "Booster" ohne Versiegelt-Hinweis ist oft nur eine Erwaehnung
            continue
        quantity = 1
        for match in matches:
            prefix = norm[max(0, match.start() - 12) : match.start()]
            number = re.search(r"(\d{1,3})\s*[x]?\s*$", prefix)
            if number:
                quantity = max(quantity, min(50, int(number.group(1))))
        facts.sealed[kind] = quantity

    for condition, pattern in CONDITION_PATTERNS.items():
        if re.search(pattern, norm):
            facts.condition = condition
            break

    for label, pattern in RISK_PATTERNS.items():
        if re.search(pattern, norm):
            facts.risks.append(label)
    for label, pattern in SIGNAL_PATTERNS.items():
        if re.search(pattern, norm):
            facts.signals.append(label)
    if re.search(r"\b(keine|ohne|nur)\s+(\w+\s+)?(rares?|seltene|mythics?)", norm):
        facts.signals = [s for s in facts.signals if s != "Rares/Mythics genannt"]

    facts.graded = bool(re.search(r"\b(psa|bgs|cgc) ?\d{1,2}", norm))
    facts.is_wanted_ad = bool(re.search(WANTED_PATTERN, norm)) and not re.search(
        r"\b(verkaufe|zu verkaufen|biete|abzugeben|verkauf|for sale)\b", norm
    )
    if re.search(r"\b(deutsch|german)\b", norm):
        facts.language = "de"
    elif re.search(r"\b(englisch|english)\b", norm):
        facts.language = "en"
    return facts

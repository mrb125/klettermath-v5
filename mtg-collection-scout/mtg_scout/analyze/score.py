"""Bewertungslogik: aus Fakten + Preisen einen nachvollziehbaren Deal-Score bauen."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from ..currency import CurrencyConverter
from ..models import CardHit, Evaluation, Listing, ValueEstimate
from ..pricing.index import CardIndex
from ..util import money
from ..vision.facts import PhotoFacts
from .parse import VINTAGE_ERAS, ListingFacts, parse_listing

GRADES = [
    (85.0, "A+", "Top-Deal - sofort ansehen"),
    (75.0, "A", "Sehr attraktiv"),
    (65.0, "B", "Guenstig, Details pruefen"),
    (55.0, "C", "Fair bepreist"),
    (45.0, "D", "Eher teuer"),
    (30.0, "E", "Teuer / duenne Angaben"),
    (0.0, "F", "Finger weg"),
]


class Evaluator:
    def __init__(
        self,
        config: Dict[str, Any],
        card_index: CardIndex,
        converter: Optional[CurrencyConverter] = None,
    ) -> None:
        self.config = config
        self.valuation = config.get("valuation", {})
        self.scoring = config.get("scoring", {})
        self.index = card_index
        self.converter = converter or CurrencyConverter()

    # ------------------------------------------------------------------ public
    def evaluate(self, listing: Listing, photos: Optional[PhotoFacts] = None) -> Evaluation:
        """Ein Angebot bewerten - optional mit den Fakten aus der Fotoauswertung."""
        facts = parse_listing(listing.text)
        price_eur = self.converter.to_eur(listing.price, listing.currency)
        shipping_eur = self.converter.to_eur(listing.shipping, listing.currency) or 0.0
        total_eur = None if price_eur is None else round(price_eur + shipping_eur, 2)

        card_hits = self.index.find(listing.text)
        if photos:
            self._merge_photo_facts(facts, photos)
            card_hits = self._merge_photo_cards(card_hits, photos)
        estimate = self._estimate_value(facts, card_hits, listing)
        if photos and photos.images_analyzed:
            estimate.confidence = round(min(0.95, estimate.confidence + 0.15), 2)
            if photos.summary:
                estimate.breakdown.append(f"Fotobefund: {photos.summary[:200]}")

        evaluation = Evaluation(
            listing=listing,
            price_eur=total_eur,
            estimate=estimate,
            card_hits=card_hits,
            signals=list(facts.signals),
            risks=list(facts.risks),
            card_count=facts.card_count,
        )
        self._score(evaluation, facts)
        return evaluation

    # -------------------------------------------------------------- Fotobefunde
    @staticmethod
    def _merge_photo_facts(facts: ListingFacts, photos: PhotoFacts) -> None:
        """Erkenntnisse aus den Bildern in die Textfakten uebernehmen."""
        for kind, quantity in photos.sealed.items():
            facts.sealed[kind] = max(facts.sealed.get(kind, 0), quantity)
        if facts.card_count is None and photos.card_count:
            facts.card_count = photos.card_count
            facts.card_count_source = "auf Fotos geschaetzt"
        if facts.condition == "unknown" and photos.condition:
            facts.condition = photos.condition
        for flag in photos.flags:
            label = f"Foto: {flag}"
            if label not in facts.risks:
                facts.risks.append(label)
        if photos.images_analyzed:
            facts.signals.append(f"{photos.images_analyzed} Foto(s) ausgewertet")

    def _merge_photo_cards(self, hits: List[CardHit], photos: PhotoFacts) -> List[CardHit]:
        """Auf Fotos erkannte Karten bepreisen und mit den Textreffern zusammenfuehren."""
        merged = {hit.name: hit for hit in hits}
        for card in photos.cards:
            entry = self.index.lookup(card.name)
            if entry is None:
                continue
            name, price, reserved = entry
            candidate = CardHit(
                name=name, price_eur=price,
                confidence=round(min(0.95, card.confidence * 0.85), 2),
                count=card.count, reserved=reserved, source="foto",
            )
            existing = merged.get(name)
            if existing is None or candidate.weighted_eur > existing.weighted_eur:
                merged[name] = candidate
        return sorted(merged.values(), key=lambda h: h.weighted_eur, reverse=True)

    # ------------------------------------------------------------ Wertermittlung
    def _estimate_value(self, facts: ListingFacts, hits: List[CardHit],
                        listing: Listing) -> ValueEstimate:
        v = self.valuation
        condition_factor = v.get("condition_factor", {}).get(facts.condition, 0.8)
        breakdown: List[str] = []
        total = 0.0
        confidence = 0.2

        # 1) Namentlich genannte Karten
        if hits:
            named = sum(h.weighted_eur for h in hits) * float(v.get("card_hit_discount", 0.65))
            named *= condition_factor
            total += named
            top = ", ".join(f"{h.count}x {h.name}" if h.count > 1 else h.name for h in hits[:4])
            breakdown.append(f"Einzelkarten ({len(hits)} erkannt: {top}): {money(named)}")
            confidence += min(0.35, 0.08 * len(hits))

        # 2) Masse an Karten
        if facts.card_count:
            per_card = self._per_card_rate(facts)
            bulk = facts.card_count * per_card * condition_factor
            total += bulk
            breakdown.append(
                f"{facts.card_count:,}".replace(",", ".")
                + f" Karten x {per_card:.2f} €/Karte ({facts.top_era or 'gemischt'},"
                f" Zustand {facts.condition}): {money(bulk)}"
            )
            confidence += 0.25 if facts.card_count_source == "im Text genannt" else 0.12

        # 3) Versiegelte Ware
        sealed_prices = v.get("sealed", {})
        for kind, quantity in facts.sealed.items():
            unit = float(sealed_prices.get(kind, 0.0))
            if unit <= 0:
                continue
            value = unit * quantity
            total += value
            breakdown.append(f"{quantity}x {kind.replace('_', ' ')}: {money(value)}")
            confidence += 0.1

        # 4) Aera-Zuschlag, wenn keine Stueckzahl bekannt ist
        if not facts.card_count and not facts.sealed and facts.era_weight >= 0.7:
            fallback = 150.0 * facts.era_weight
            total += fallback
            breakdown.append(
                f"Pauschale fuer alte Editionen ({facts.top_era}), Stueckzahl unbekannt:"
                f" {money(fallback)}"
            )
            confidence += 0.05

        if facts.graded:
            confidence += 0.05
        if len(listing.description) > 200:
            confidence += 0.05

        confidence = max(0.05, min(0.95, confidence))
        return ValueEstimate(
            low=round(total * float(v.get("spread_low", 0.6)), 2),
            mid=round(total, 2),
            high=round(total * float(v.get("spread_high", 1.7)), 2),
            breakdown=breakdown,
            confidence=round(confidence, 2),
        )

    def _per_card_rate(self, facts: ListingFacts) -> float:
        """EUR pro Karte - Aera-Preis nur anteilig, weil selten die ganze Sammlung alt ist."""
        v = self.valuation
        mixed = float(v.get("mixed_per_card", 0.08))
        if "Nur Massenware/Commons" in facts.risks:
            return float(v.get("bulk_per_card", 0.03))

        era = facts.top_era
        if era in VINTAGE_ERAS:
            target = float(v.get("vintage_per_card", 1.2)) * (0.6 + 0.4 * facts.era_weight)
        elif {"Reserved List", "Dual Lands", "Power 9"} & set(facts.signals):
            # Ohne Editionsangabe, aber mit klaren Wertsignalen
            target = float(v.get("vintage_per_card", 1.2)) * 0.6
        elif era == "retro" or {"Rares/Mythics genannt", "Foils genannt",
                                "Fetch-/Shocklands"} & set(facts.signals):
            target = float(v.get("rare_per_card", 0.35))
        else:
            return mixed

        share = float(v.get("era_share", 0.4))
        if {"Reserved List", "Dual Lands", "Power 9"} & set(facts.signals):
            share = min(1.0, share + 0.2)
        return mixed + share * (target - mixed)

    # --------------------------------------------------------------- Bewertung
    def _score(self, ev: Evaluation, facts: ListingFacts) -> None:
        if facts.is_wanted_ad:
            ev.score = 0.0
            ev.grade = "-"
            ev.verdict = "Gesuch/Tauschanzeige - kein Verkaufsangebot"
            return

        ratio = ev.ratio
        if ev.estimate.mid <= 0:
            ev.score = 32.0
            ev.verdict = "Zu wenig Information fuer eine Schaetzung - manuell pruefen"
        elif ratio is None:
            ev.score = 35.0
            ev.verdict = "Kein Preis angegeben (Auktion/VB) - manuell pruefen"
        else:
            raw = 50.0 + 25.0 * math.log2(max(ratio, 0.05))
            # Unsichere Schaetzungen Richtung neutral ziehen
            trust = 0.4 + 0.6 * ev.estimate.confidence
            ev.score = 50.0 + (raw - 50.0) * trust

        ev.score += min(10.0, 2.0 * len(ev.signals))
        ev.score -= float(self.scoring.get("risk_penalty", 8.0)) * len(ev.risks)

        seller_rating = ev.listing.seller_rating
        if seller_rating is not None and seller_rating < 95:
            ev.score -= 10.0
            ev.risks.append(f"Verkaeuferbewertung nur {seller_rating:.0f}%")
        if ev.listing.seller_feedback is not None and ev.listing.seller_feedback < 5:
            ev.score -= 5.0
            ev.risks.append("Verkaeufer fast ohne Bewertungen")

        countries = {c.upper() for c in self.scoring.get("distance_penalty_countries", [])}
        if ev.listing.country and ev.listing.country.upper() in countries:
            ev.score -= 5.0
            ev.signals.append(f"Versand aus {ev.listing.country}")

        ev.score = max(0.0, min(100.0, ev.score))
        for threshold, grade, verdict in GRADES:
            if ev.score >= threshold:
                ev.grade = grade
                if ratio is not None and ev.estimate.mid > 0:
                    ev.verdict = verdict
                break

        if ratio is not None and ev.estimate.mid > 0:
            ev.verdict += f" (Wert/Preis ≈ {ratio:.1f}x, Sicherheit {ev.estimate.confidence:.0%})"

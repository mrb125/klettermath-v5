"""kleinanzeigen.de (ehemals eBay Kleinanzeigen) - HTML-Suche.

Es gibt keine oeffentliche API. Die Quelle liest die Suchergebnisseite,
haelt sich an robots.txt (abschaltbar mit --ignore-robots) und drosselt
die Abrufe. Selektoren koennen sich jederzeit aendern - dann meldet die
Quelle 0 Treffer statt zu crashen.
"""

from __future__ import annotations

import logging
import re
import urllib.parse
from typing import List, Tuple

from ..htmlparse import (attr, element_with_id, image_sources, iter_tag_blocks,
                         meta_contents, text_of_class)
from ..models import Listing
from ..net import FetchError
from ..util import parse_price, strip_html
from .base import SearchQuery, Source

log = logging.getLogger("mtg_scout.sources.kleinanzeigen")

BASE = "https://www.kleinanzeigen.de"


class KleinanzeigenSource(Source):
    name = "kleinanzeigen"
    label = "kleinanzeigen.de"
    countries = ["DE"]

    def search(self, query: SearchQuery) -> List[Listing]:
        listings: List[Listing] = []
        for term in query.terms:
            for page in range(1, max(1, query.max_pages) + 1):
                url = self._search_url(term, page, query)
                try:
                    html = self.client.fetch(url)
                except FetchError as exc:
                    log.warning("kleinanzeigen '%s' Seite %s: %s", term, page, exc)
                    break
                page_listings = self.parse(html)
                listings.extend(page_listings)
                if len(page_listings) < 5:      # letzte Seite erreicht
                    break
        return self._dedupe(listings)[: query.limit]

    def _search_url(self, term: str, page: int, query: SearchQuery) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        parts = [BASE, "s"]
        if page > 1:
            parts.append(f"seite:{page}")
        if query.min_price_eur or query.max_price_eur:
            low = int(query.min_price_eur or 0)
            high = int(query.max_price_eur) if query.max_price_eur else ""
            parts.append(f"preis:{low}:{high}")
        if query.postal_code:
            parts.append(f"l{query.postal_code}")
        if query.radius_km:
            parts.append(f"r{query.radius_km}")
        parts.append(slug)
        parts.append("k0")
        return "/".join(parts)

    # ---------------------------------------------------------------- Parsing
    def parse(self, html: str) -> List[Listing]:
        """Suchergebnisseite in Angebote umwandeln (auch offline testbar)."""
        listings: List[Listing] = []
        for block in iter_tag_blocks(html, "article", attr_contains="aditem"):
            ad_id = attr(block, "data-adid")
            href = attr(block, "data-href")
            title = text_of_class(block, "text-module-begin") or text_of_class(block, "ellipsis")
            if not title:
                continue
            price_text = text_of_class(block, "price-shipping--price") or text_of_class(block, "--price")
            price, currency = parse_price(price_text, "EUR")
            if price_text and re.search(r"zu verschenken|gratis", price_text, re.I):
                price = 0.0
            listings.append(
                Listing(
                    source=self.name,
                    title=title,
                    url=urllib.parse.urljoin(BASE, href) if href else BASE,
                    price=price,
                    currency=currency or "EUR",
                    description=text_of_class(block, "middle--description"),
                    country="DE",
                    location=text_of_class(block, "top--left"),
                    posted_at=text_of_class(block, "top--right"),
                    images=image_sources(block)[:3],
                    listing_id=f"kleinanzeigen:{ad_id}" if ad_id else "",
                    raw={"price_text": price_text},
                )
            )
        return listings

    # ----------------------------------------------------------- Detailseite
    def fetch_detail(self, listing) -> bool:
        """Anzeigenseite nachladen: vollstaendiger Text und alle Fotos.

        Die Trefferliste kuerzt die Beschreibung und zeigt nur ein Bild - fuer die
        Fotoauswertung lohnt sich der zusaetzliche Abruf. Gibt False zurueck, wenn
        die Seite nicht geladen werden konnte.
        """
        if not listing.url.startswith("http"):
            return False
        try:
            html = self.client.fetch(listing.url)
        except FetchError as exc:
            log.info("Detailseite %s nicht ladbar: %s", listing.url, exc)
            return False
        description, images = self.parse_detail(html)
        if description and len(description) > len(listing.description):
            listing.description = description
        for url in images:
            if url not in listing.images:
                listing.images.append(url)
        if listing.images and not listing.image_url:
            listing.image_url = listing.images[0]
        return True

    @staticmethod
    def parse_detail(html: str) -> Tuple[str, List[str]]:
        """(Beschreibung, Bild-URLs) einer Anzeigenseite."""
        description = strip_html(element_with_id(html, "viewad-description-text"))
        images: List[str] = []
        seen: set[str] = set()
        for url in meta_contents(html, "og:image") + image_sources(html):
            if not any(marker in url for marker in
                       ("/api/v1/prod-ads/images", "ebayimg", "img.kleinanzeigen")):
                continue
            # Dieselbe Aufnahme taucht in mehreren Groessen auf (?rule=...)
            key = url.split("?")[0]
            if key in seen:
                continue
            seen.add(key)
            images.append(url)
        return description, images

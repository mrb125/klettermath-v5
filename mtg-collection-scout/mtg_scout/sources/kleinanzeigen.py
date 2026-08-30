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
from typing import List

from ..htmlparse import attr, iter_tag_blocks, text_of_class
from ..models import Listing
from ..net import FetchError
from ..util import parse_price
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
                    image_url=attr(block, "data-imgsrc") or attr(block, "src"),
                    listing_id=f"kleinanzeigen:{ad_id}" if ad_id else "",
                    raw={"price_text": price_text},
                )
            )
        return listings

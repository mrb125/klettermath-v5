"""Profilgesteuerte Quelle fuer weitere (auch auslaendische) Marktplaetze.

Ein Profil ist eine JSON-Datei in mtg_scout/profiles/. Gelesen wird primaer
JSON-LD (schema.org/Product), das die meisten Marktplaetze fuer Suchmaschinen
ausliefern - das ist deutlich stabiler als CSS-Selektoren. Optional koennen
im Profil zusaetzlich HTML-Klassen als Fallback hinterlegt werden.
"""

from __future__ import annotations

import json
import logging
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List

from ..htmlparse import attr, iter_tag_blocks, json_ld_products, offer_price, text_of_class
from ..models import Listing
from ..net import FetchError
from ..util import parse_price, strip_html
from .base import SearchQuery, Source

log = logging.getLogger("mtg_scout.sources.profile")

PROFILE_DIR = Path(__file__).resolve().parent.parent / "profiles"


def load_profiles() -> Dict[str, Dict[str, Any]]:
    profiles: Dict[str, Dict[str, Any]] = {}
    if not PROFILE_DIR.exists():
        return profiles
    for path in sorted(PROFILE_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text("utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("Profil %s ist fehlerhaft: %s", path.name, exc)
            continue
        profiles[data.get("name") or path.stem] = data
    return profiles


class ProfileSource(Source):
    """Generische Quelle, die ihr Verhalten aus einem JSON-Profil bezieht."""

    def __init__(self, config: Dict[str, Any], client, profile: Dict[str, Any]) -> None:
        super().__init__(config, client)
        self.profile = profile
        self.name = profile.get("name", "profil")
        self.label = profile.get("label", self.name)
        self.countries = profile.get("countries", [])
        self.base_url = profile.get("base_url", "")
        self.currency = profile.get("currency", "EUR")

    def available(self) -> tuple[bool, str]:
        if not self.profile.get("search_url"):
            return False, f"Profil {self.name} hat keine search_url"
        note = self.profile.get("note", "")
        return True, note

    def search(self, query: SearchQuery) -> List[Listing]:
        listings: List[Listing] = []
        for term in query.terms:
            for page in range(1, max(1, query.max_pages) + 1):
                url = self.profile["search_url"].format(
                    query=urllib.parse.quote_plus(term), page=page
                )
                try:
                    html = self.client.fetch(url)
                except FetchError as exc:
                    log.warning("%s '%s': %s", self.name, term, exc)
                    break
                found = self.parse(html)
                listings.extend(found)
                if not found:
                    break
        return self._dedupe(listings)[: query.limit]

    # ---------------------------------------------------------------- Parsing
    def parse(self, html: str) -> List[Listing]:
        listings = [self._from_json_ld(node) for node in json_ld_products(html)]
        listings = [l for l in listings if l is not None]        # type: ignore[misc]
        if listings:
            return listings                                       # type: ignore[return-value]
        return self._from_html(html)

    def _from_json_ld(self, node: Dict[str, Any]):
        name = strip_html(str(node.get("name") or ""))
        url = node.get("url") or ""
        if isinstance(url, dict):
            url = url.get("@id", "")
        if not name or not url:
            return None
        price, currency = offer_price(node)
        image = node.get("image")
        if isinstance(image, list):
            image = image[0] if image else ""
        if isinstance(image, dict):
            image = image.get("url", "")
        return Listing(
            source=self.name,
            title=name,
            url=urllib.parse.urljoin(self.base_url, str(url)),
            price=price,
            currency=currency or self.currency,
            description=strip_html(str(node.get("description") or "")),
            country=(self.countries or [""])[0],
            image_url=str(image or ""),
            raw={"profile": self.name, "via": "json-ld"},
        )

    def _from_html(self, html: str) -> List[Listing]:
        selectors = self.profile.get("html") or {}
        item_tag = selectors.get("item_tag")
        item_class = selectors.get("item_class")
        if not item_tag or not item_class:
            return []
        listings: List[Listing] = []
        for block in iter_tag_blocks(html, item_tag, attr_contains=item_class):
            title = text_of_class(block, selectors.get("title_class", ""))
            if not title:
                continue
            href = attr(block, "href") or attr(block, "data-href")
            price, currency = parse_price(
                text_of_class(block, selectors.get("price_class", "")), self.currency
            )
            listings.append(
                Listing(
                    source=self.name,
                    title=title,
                    url=urllib.parse.urljoin(self.base_url, href),
                    price=price,
                    currency=currency or self.currency,
                    description=text_of_class(block, selectors.get("description_class", "")),
                    country=(self.countries or [""])[0],
                    location=text_of_class(block, selectors.get("location_class", "")),
                    raw={"profile": self.name, "via": "html"},
                )
            )
        return listings

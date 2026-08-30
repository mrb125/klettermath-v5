"""eBay Browse API - offizieller Zugang, laenderuebergreifend.

Zugangsdaten: kostenlos im eBay Developer Program (developer.ebay.com) anlegen,
dann `EBAY_CLIENT_ID` / `EBAY_CLIENT_SECRET` setzen oder in die Config schreiben.
"""

from __future__ import annotations

import base64
import logging
import time
import urllib.parse
from typing import Any, Dict, List, Optional

from ..currency import CurrencyConverter
from ..models import Listing
from ..net import FetchError, HttpClient
from ..util import strip_html
from .base import SearchQuery, Source

log = logging.getLogger("mtg_scout.sources.ebay")

MARKET_CURRENCY = {
    "EBAY_DE": "EUR", "EBAY_AT": "EUR", "EBAY_FR": "EUR", "EBAY_IT": "EUR",
    "EBAY_ES": "EUR", "EBAY_NL": "EUR", "EBAY_BE": "EUR", "EBAY_IE": "EUR",
    "EBAY_CH": "CHF", "EBAY_GB": "GBP", "EBAY_US": "USD", "EBAY_CA": "CAD",
    "EBAY_AU": "AUD", "EBAY_PL": "PLN", "EBAY_HK": "HKD", "EBAY_SG": "SGD",
}
MARKET_COUNTRY = {market: market.split("_")[1] for market in MARKET_CURRENCY}

HOSTS = {
    "production": "https://api.ebay.com",
    "sandbox": "https://api.sandbox.ebay.com",
}


class EbaySource(Source):
    name = "ebay"
    label = "eBay (Browse API)"
    countries = sorted({country for country in MARKET_COUNTRY.values()})

    def __init__(self, config: Dict[str, Any], client: HttpClient,
                 converter: Optional[CurrencyConverter] = None) -> None:
        super().__init__(config, client)
        settings = config.get("ebay", {})
        self.client_id = settings.get("client_id", "")
        self.client_secret = settings.get("client_secret", "")
        self.host = HOSTS.get(settings.get("environment", "production"), HOSTS["production"])
        self.converter = converter or CurrencyConverter()
        self._token: Optional[str] = None
        self._token_expiry = 0.0

    # ------------------------------------------------------------ Verfuegbarkeit
    def available(self) -> tuple[bool, str]:
        if not self.client_id or not self.client_secret:
            return False, (
                "eBay-Zugangsdaten fehlen - EBAY_CLIENT_ID/EBAY_CLIENT_SECRET setzen "
                "(kostenlos unter developer.ebay.com) oder in die Config eintragen"
            )
        return True, ""

    # -------------------------------------------------------------------- OAuth
    def _access_token(self) -> str:
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("ascii")
        body = urllib.parse.urlencode(
            {
                "grant_type": "client_credentials",
                "scope": "https://api.ebay.com/oauth/api_scope",
            }
        ).encode("utf-8")
        payload = self.client.fetch_json(
            f"{self.host}/identity/v1/oauth2/token",
            method="POST",
            data=body,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            use_cache=False,
        )
        self._token = payload["access_token"]
        self._token_expiry = time.time() + float(payload.get("expires_in", 7200))
        return self._token

    # ------------------------------------------------------------------- Suche
    def search(self, query: SearchQuery) -> List[Listing]:
        ok, reason = self.available()
        if not ok:
            log.warning("eBay uebersprungen: %s", reason)
            return []
        markets = query.markets or ["EBAY_DE"]
        listings: List[Listing] = []
        per_request = min(100, max(10, query.limit))
        for market in markets:
            for term in query.terms:
                try:
                    listings.extend(self._search_market(market, term, per_request, query))
                except FetchError as exc:
                    log.warning("eBay %s / '%s': %s", market, term, exc)
        return self._dedupe(listings)

    def _search_market(self, market: str, term: str, limit: int,
                       query: SearchQuery) -> List[Listing]:
        currency = MARKET_CURRENCY.get(market, "EUR")
        filters = ["buyingOptions:{FIXED_PRICE|AUCTION}"]
        price_filter = self._price_filter(query, currency)
        if price_filter:
            filters.append(price_filter)
            filters.append(f"priceCurrency:{currency}")
        params = {
            "q": term,
            "limit": str(limit),
            "sort": "newlyListed",
            "filter": ",".join(filters),
        }
        url = f"{self.host}/buy/browse/v1/item_summary/search?" + urllib.parse.urlencode(params)
        payload = self.client.fetch_json(
            url,
            headers={
                "Authorization": f"Bearer {self._access_token()}",
                "X-EBAY-C-MARKETPLACE-ID": market,
            },
        )
        items = payload.get("itemSummaries") or []
        return [self._to_listing(item, market, currency) for item in items]

    def _price_filter(self, query: SearchQuery, currency: str) -> str:
        low = query.min_price_eur
        high = query.max_price_eur
        if low is None and high is None:
            return ""
        rate = self.converter.rates.get(currency, 1.0) or 1.0
        low_local = f"{low / rate:.0f}" if low is not None else ""
        high_local = f"{high / rate:.0f}" if high is not None else ""
        return f"price:[{low_local}..{high_local}]"

    @staticmethod
    def _to_listing(item: Dict[str, Any], market: str, currency: str) -> Listing:
        price_block = item.get("price") or {}
        shipping = None
        for option in item.get("shippingOptions") or []:
            cost = (option.get("shippingCost") or {}).get("value")
            if cost is not None:
                shipping = float(cost)
                break
        images: List[str] = []
        for candidate in [(item.get("image") or {}).get("imageUrl")] + [
            entry.get("imageUrl")
            for entry in (item.get("thumbnailImages") or []) + (item.get("additionalImages") or [])
        ]:
            if candidate and candidate not in images:
                images.append(candidate)
        seller = item.get("seller") or {}
        location = item.get("itemLocation") or {}
        return Listing(
            source="ebay",
            title=item.get("title") or "",
            url=item.get("itemWebUrl") or "",
            price=float(price_block["value"]) if price_block.get("value") else None,
            currency=price_block.get("currency") or currency,
            description=strip_html(item.get("shortDescription") or ""),
            country=location.get("country") or MARKET_COUNTRY.get(market, ""),
            location=", ".join(
                part for part in [location.get("postalCode"), location.get("country")] if part
            ),
            seller=seller.get("username") or "",
            seller_rating=_as_float(seller.get("feedbackPercentage")),
            seller_feedback=_as_int(seller.get("feedbackScore")),
            condition=item.get("condition") or "",
            image_url=images[0] if images else "",
            images=images,
            posted_at=item.get("itemCreationDate") or "",
            shipping=shipping,
            listing_id=f"ebay:{item.get('itemId') or item.get('legacyItemId') or ''}",
            raw={"market": market, "buyingOptions": item.get("buyingOptions")},
        )


def _as_float(value: object) -> Optional[float]:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None


def _as_int(value: object) -> Optional[int]:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None

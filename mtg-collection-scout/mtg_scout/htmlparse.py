"""Genuegsame HTML-Hilfen ohne Fremdbibliotheken.

Kein vollstaendiger Parser - bewusst tolerant gegenueber kaputtem Markup,
weil Marktplatz-HTML sich staendig aendert.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Iterator, List, Optional

from .util import strip_html

_JSON_LD_RE = re.compile(
    r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
_ATTR_RE_CACHE: Dict[str, re.Pattern[str]] = {}


def iter_tag_blocks(html: str, tag: str, attr_contains: str = "") -> Iterator[str]:
    """Alle <tag ...> ... </tag>-Bloecke liefern (nicht verschachtelt gedacht)."""
    open_re = re.compile(rf"<{tag}\b[^>]*>", re.IGNORECASE)
    close = f"</{tag}>"
    for match in open_re.finditer(html):
        start = match.start()
        end = html.find(close, match.end())
        block = html[start : end + len(close)] if end != -1 else html[start : start + 20000]
        if attr_contains and attr_contains not in block[: len(match.group(0))]:
            continue
        yield block


def attr(block: str, name: str) -> str:
    """Attributwert aus dem ersten Tag des Blocks (oder irgendwo im Block)."""
    pattern = _ATTR_RE_CACHE.setdefault(
        name, re.compile(rf'{re.escape(name)}\s*=\s*["\']([^"\']*)["\']', re.IGNORECASE)
    )
    match = pattern.search(block)
    return match.group(1) if match else ""


def element_with_class(block: str, class_fragment: str) -> str:
    """Inhalt des ersten Elements, dessen class-Attribut das Fragment enthaelt."""
    return _element_with_attr(block, "class", class_fragment)


def element_with_id(block: str, element_id: str) -> str:
    """Inhalt des ersten Elements mit dieser id."""
    return _element_with_attr(block, "id", element_id, exact=True)


def _element_with_attr(block: str, attribute: str, value: str, exact: bool = False) -> str:
    inner = re.escape(value) if exact else f'[^"]*{re.escape(value)}[^"]*'
    pattern = re.compile(
        rf'<(?P<tag>[a-z0-9]+)\b[^>]*{attribute}="{inner}"[^>]*>',
        re.IGNORECASE,
    )
    match = pattern.search(block)
    if not match:
        return ""
    tag = match.group("tag")
    depth = 1
    pos = match.end()
    token_re = re.compile(rf"<(/?){tag}\b", re.IGNORECASE)
    while depth > 0:
        token = token_re.search(block, pos)
        if not token:
            return block[match.end() :]
        depth += -1 if token.group(1) else 1
        pos = token.end()
        if depth == 0:
            return block[match.end() : token.start()]
    return ""


def text_of_class(block: str, class_fragment: str) -> str:
    return strip_html(element_with_class(block, class_fragment))


def meta_contents(html: str, property_name: str) -> List[str]:
    """Alle <meta property="..." content="..."> Werte einer Seite."""
    pattern = re.compile(
        rf'<meta[^>]+(?:property|name)="{re.escape(property_name)}"[^>]+content="([^"]+)"',
        re.IGNORECASE,
    )
    alternate = re.compile(
        rf'<meta[^>]+content="([^"]+)"[^>]+(?:property|name)="{re.escape(property_name)}"',
        re.IGNORECASE,
    )
    return pattern.findall(html) + alternate.findall(html)


def image_sources(html: str) -> List[str]:
    """Bild-URLs einer Seite in Reihenfolge des Auftretens, ohne Duplikate."""
    found: List[str] = []
    for match in re.finditer(r'<img\b[^>]*?(?:data-imgsrc|data-src|src)="([^"]+)"',
                             html, re.IGNORECASE):
        url = match.group(1)
        if url.startswith("data:") or url in found:
            continue
        found.append(url)
    return found


def first_link(block: str, prefix: str = "") -> str:
    for match in re.finditer(r'<a\b[^>]*href="([^"]+)"', block, re.IGNORECASE):
        href = match.group(1)
        if not prefix or href.startswith(prefix):
            return href
    return ""


def iter_json_ld(html: str) -> Iterator[Any]:
    """Alle JSON-LD-Bloecke einer Seite dekodieren."""
    for match in _JSON_LD_RE.finditer(html):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            yield json.loads(raw)
        except json.JSONDecodeError:
            # Manche Seiten packen mehrere Objekte ohne Array hintereinander
            for chunk in re.findall(r"\{.*?\}(?=\s*\{|\s*$)", raw, re.DOTALL):
                try:
                    yield json.loads(chunk)
                except json.JSONDecodeError:
                    continue


def walk_json(node: Any) -> Iterator[Dict[str, Any]]:
    """Alle Dictionaries eines verschachtelten JSON-Baums."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk_json(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_json(value)


def json_ld_products(html: str) -> List[Dict[str, Any]]:
    """Produkt-/Angebotsobjekte aus JSON-LD einsammeln."""
    products: List[Dict[str, Any]] = []
    for document in iter_json_ld(html):
        for node in walk_json(document):
            types = node.get("@type")
            types = [types] if isinstance(types, str) else (types or [])
            if any(t in ("Product", "Offer", "IndividualProduct", "ProductCollection") for t in types):
                if node.get("name") or node.get("url"):
                    products.append(node)
    return products


def offer_price(node: Dict[str, Any]) -> tuple[Optional[float], str]:
    """Preis + Waehrung aus einem JSON-LD-Objekt ziehen."""
    offers = node.get("offers") or node
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    if not isinstance(offers, dict):
        return None, ""
    price = offers.get("price") or offers.get("lowPrice") or offers.get("highPrice")
    currency = offers.get("priceCurrency") or ""
    try:
        return (float(price), currency) if price is not None else (None, currency)
    except (TypeError, ValueError):
        return None, currency

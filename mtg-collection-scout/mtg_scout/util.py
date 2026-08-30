"""Kleine Helfer: Textnormalisierung, Zahlen-/Preis-Parsing, Terminal-Formatierung."""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from typing import Iterable, List, Optional

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Preise wie "1.234,50 EUR", "€ 1 234,50", "$1,234.50", "1234.50"
_PRICE_RE = re.compile(
    r"(?<![\d,.])(\d{1,3}(?:[.,\s  ]\d{3})+(?:[.,]\d{1,2})?|\d+(?:[.,]\d{1,2})?)(?![\d])"
)

CURRENCY_SYMBOLS = {
    "€": "EUR", "eur": "EUR", "euro": "EUR",
    "$": "USD", "usd": "USD", "us $": "USD",
    "£": "GBP", "gbp": "GBP",
    "chf": "CHF", "fr.": "CHF",
    "zł": "PLN", "pln": "PLN",
    "kč": "CZK", "czk": "CZK",
    "sek": "SEK", "dkk": "DKK", "nok": "NOK",
    "c $": "CAD", "cad": "CAD", "aud": "AUD", "jpy": "JPY", "¥": "JPY",
}


def strip_html(raw: str) -> str:
    """HTML-Fragment in lesbaren Text verwandeln."""
    if not raw:
        return ""
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>", "\n", text)
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return collapse_ws(text)


def collapse_ws(text: str) -> str:
    return _WS_RE.sub(" ", (text or "").replace("\xa0", " ")).strip()


def normalize(text: str) -> str:
    """Kleinschreibung ohne Diakritika - fuer robustes Keyword-Matching."""
    text = unicodedata.normalize("NFKD", (text or "").lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.replace("ß", "ss")


def normalize_de(text: str) -> str:
    """Wie normalize(), zusaetzlich mit Umlaut-Umschriften: "beschaedigt" == "beschädigt".

    Nur fuer deutschsprachige Schluesselwoerter gedacht - Kartennamen werden
    bewusst mit normalize() behandelt, damit englische Namen intakt bleiben.
    """
    text = normalize(text)
    for digraph, plain in (("ae", "a"), ("oe", "o"), ("ue", "u")):
        text = text.replace(digraph, plain)
    return text


def parse_number(token: str) -> Optional[float]:
    """'1.234,50' / '1,234.50' / '1234' -> float."""
    if not token:
        return None
    t = token.strip().replace(" ", "").replace(" ", "").replace(" ", "")
    if "," in t and "." in t:
        # das hintere Zeichen ist das Dezimaltrennzeichen
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")
        else:
            t = t.replace(",", "")
    elif "," in t:
        # ",50" = Dezimal, ",000" = Tausender
        t = t.replace(",", ".") if re.search(r",\d{1,2}$", t) else t.replace(",", "")
    elif re.search(r"\.\d{3}(?:\D|$)", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def parse_price(text: str, default_currency: str = "EUR") -> tuple[Optional[float], str]:
    """Preis + Waehrung aus Freitext ziehen ('VB 250 €' -> (250.0, 'EUR'))."""
    if not text:
        return None, default_currency
    low = text.lower()
    currency = default_currency
    for token, code in CURRENCY_SYMBOLS.items():
        if token in low:
            currency = code
            break
    m = _PRICE_RE.search(text.replace(" ", " "))
    if not m:
        return None, currency
    return parse_number(m.group(1)), currency


def money(value: Optional[float], currency: str = "EUR") -> str:
    if value is None:
        return "-"
    symbol = {"EUR": "€", "USD": "$", "GBP": "£"}.get(currency, currency + " ")
    if symbol in ("€",):
        return f"{value:,.0f} {symbol}".replace(",", ".")
    return f"{symbol}{value:,.0f}".replace(",", ".")


def truncate(text: str, width: int) -> str:
    text = collapse_ws(text)
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def ngrams(tokens: List[str], size: int) -> Iterable[tuple[int, str]]:
    for i in range(len(tokens) - size + 1):
        yield i, " ".join(tokens[i : i + size])


def supports_color(stream=sys.stdout) -> bool:
    return bool(getattr(stream, "isatty", lambda: False)())


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def __call__(self, text: str, *codes: str) -> str:
        if not self.enabled or not codes:
            return text
        return "".join(codes) + text + self.RESET

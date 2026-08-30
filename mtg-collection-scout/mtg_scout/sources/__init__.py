"""Registry aller Angebotsquellen."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..currency import CurrencyConverter
from ..net import HttpClient
from .base import DEFAULT_TERMS, SearchQuery, Source
from .ebay import EbaySource
from .kleinanzeigen import KleinanzeigenSource
from .local import DemoSource, FileSource, load_listings_file
from .profile import ProfileSource, load_profiles

log = logging.getLogger("mtg_scout.sources")

__all__ = [
    "DEFAULT_TERMS", "SearchQuery", "Source", "EbaySource", "KleinanzeigenSource",
    "DemoSource", "FileSource", "ProfileSource", "load_listings_file",
    "available_source_names", "build_sources",
]

BUILTIN = {
    "ebay": EbaySource,
    "kleinanzeigen": KleinanzeigenSource,
    "demo": DemoSource,
    "datei": FileSource,
}


def available_source_names() -> List[str]:
    return sorted(set(BUILTIN) | set(load_profiles()))


def build_sources(
    names: List[str],
    config: Dict[str, Any],
    client: HttpClient,
    converter: Optional[CurrencyConverter] = None,
    file_path: Optional[Path] = None,
) -> List[Source]:
    """Quellen anhand ihrer Namen instanziieren. Unbekannte Namen werden gemeldet."""
    profiles = load_profiles()
    sources: List[Source] = []
    for name in names:
        key = name.strip().lower()
        if key == "alle":
            sources.extend(build_sources(available_source_names(), config, client,
                                         converter, file_path))
            continue
        if key == "ebay":
            sources.append(EbaySource(config, client, converter))
        elif key == "datei":
            sources.append(FileSource(config, client, file_path or ""))
        elif key in BUILTIN:
            sources.append(BUILTIN[key](config, client))
        elif key in profiles:
            sources.append(ProfileSource(config, client, profiles[key]))
        else:
            log.warning("Unbekannte Quelle '%s' - verfuegbar: %s",
                        name, ", ".join(available_source_names()))
    # Doppelte Quellen (z.B. durch "alle") entfernen
    unique: List[Source] = []
    seen: set[str] = set()
    for source in sources:
        if source.name not in seen:
            seen.add(source.name)
            unique.append(source)
    return unique

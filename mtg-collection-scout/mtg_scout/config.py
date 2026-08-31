"""Konfiguration: Standardwerte, Datei (~/.config/mtg-scout/config.json) und Umgebungsvariablen."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, List

APP_NAME = "mtg-scout"

DEFAULT_QUERIES: List[str] = [
    "magic the gathering sammlung",
    "magic the gathering konvolut",
    "mtg collection lot",
]

DEFAULTS: Dict[str, Any] = {
    "sources": ["ebay", "kleinanzeigen"],
    "queries": DEFAULT_QUERIES,
    "markets": ["EBAY_DE", "EBAY_AT", "EBAY_CH", "EBAY_GB", "EBAY_US"],
    "limit_per_source": 50,
    "min_price_eur": 20.0,
    "max_price_eur": 5000.0,
    "http": {
        "delay_seconds": 1.5,
        "timeout_seconds": 20.0,
        "retries": 3,
        "cache_ttl_seconds": 900,
        "respect_robots": True,
        "host_failure_limit": 2,      # danach wird ein toter Host im Lauf uebersprungen
    },
    "ebay": {
        "client_id": "",
        "client_secret": "",
        "environment": "production",
    },
    "valuation": {
        # EUR pro Karte fuer unspezifizierte Massenware, nach erkannter Qualitaet
        "bulk_per_card": 0.03,
        "mixed_per_card": 0.08,
        "rare_per_card": 0.35,
        "vintage_per_card": 1.20,
        # Pauschalwerte fuer versiegelte Ware (EUR)
        "sealed": {
            "display": 130.0,
            "collector_booster_box": 220.0,
            "bundle": 40.0,
            "booster": 4.0,
            "precon_deck": 25.0,
            "starter_deck": 30.0,
        },
        # Sicherheitsabschlag auf Einzelkartentreffer (Verkaufsgebuehren, Zustand, Unsicherheit)
        "card_hit_discount": 0.75,
        # Anteil der Sammlung, der wirklich aus der erkannten Aera stammt
        "era_share": 0.4,
        "condition_factor": {
            "mint": 1.0, "near_mint": 0.95, "excellent": 0.85,
            "good": 0.7, "played": 0.55, "poor": 0.35, "unknown": 0.8,
        },
        "spread_low": 0.6,     # untere Grenze der Wertspanne = mid * 0.6
        "spread_high": 1.7,
    },
    "vision": {
        "enabled": False,              # Fotoauswertung standardmaessig aus (API-Kosten)
        "model": "claude-opus-5",
        "max_listings": 8,             # nur die besten Treffer werden bebildert geprueft
        "max_images_per_listing": 3,
        "use_ocr": False,              # netzfreie Alternative via tesseract
        "fetch_detail_pages": True,    # Anzeigenseite fuer mehr Fotos/Text nachladen
    },
    "scoring": {
        "min_score_report": 0.0,
        "risk_penalty": 8.0,
        "distance_penalty_countries": [],
    },
}


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config")
    return Path(base) / APP_NAME


def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share")
    return Path(base) / APP_NAME


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / APP_NAME


def config_path() -> Path:
    return Path(os.environ.get("MTG_SCOUT_CONFIG") or (config_dir() / "config.json"))


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for key, value in (overlay or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config(path: Path | None = None) -> Dict[str, Any]:
    """Defaults + Konfigurationsdatei + Umgebungsvariablen zusammenfuehren."""
    cfg = copy.deepcopy(DEFAULTS)
    target = Path(path) if path else config_path()
    if target.exists():
        cfg = _deep_merge(cfg, json.loads(target.read_text("utf-8")))
    if os.environ.get("EBAY_CLIENT_ID"):
        cfg["ebay"]["client_id"] = os.environ["EBAY_CLIENT_ID"]
    if os.environ.get("EBAY_CLIENT_SECRET"):
        cfg["ebay"]["client_secret"] = os.environ["EBAY_CLIENT_SECRET"]
    return cfg


def write_example_config(path: Path | None = None) -> Path:
    target = Path(path) if path else config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    example = copy.deepcopy(DEFAULTS)
    example["ebay"]["client_id"] = "<eBay App-ID / Client-ID>"
    example["ebay"]["client_secret"] = "<eBay Cert-ID / Client-Secret>"
    target.write_text(json.dumps(example, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return target

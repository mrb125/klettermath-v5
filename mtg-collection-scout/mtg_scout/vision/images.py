"""Bilder besorgen und fuer die Bildanalyse aufbereiten."""

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Iterable, List, Tuple

from ..net import FetchError, HttpClient

log = logging.getLogger("mtg_scout.vision.images")

# Von der Anthropic-API akzeptierte Bildformate
MEDIA_TYPES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"GIF8": "image/gif",
    b"RIFF": "image/webp",
}
MAX_IMAGE_BYTES = 4_500_000      # API-Grenze liegt bei 5 MB je Bild


def media_type(payload: bytes) -> str:
    """Bildformat anhand der Magic Bytes bestimmen ('' = unbekannt)."""
    for magic, mime in MEDIA_TYPES.items():
        if payload.startswith(magic):
            return mime
    return ""


def encode(payload: bytes) -> Tuple[str, str]:
    """(media_type, base64) - leerer media_type heisst: nicht verwendbar."""
    mime = media_type(payload)
    if not mime or len(payload) > MAX_IMAGE_BYTES:
        return "", ""
    return mime, base64.standard_b64encode(payload).decode("ascii")


def to_blocks(payloads: Iterable[bytes]) -> List[Tuple[str, str]]:
    """Rohdaten in (media_type, base64) umwandeln und Untaugliches aussortieren."""
    blocks: List[Tuple[str, str]] = []
    for payload in payloads:
        mime, data = encode(payload)
        if not mime:
            log.info("Bild uebersprungen: nicht unterstuetztes Format oder zu gross")
            continue
        blocks.append((mime, data))
    return blocks


def load_local(paths: Iterable[Path]) -> List[bytes]:
    """Bilddateien von der Platte lesen."""
    payloads: List[bytes] = []
    for path in paths:
        path = Path(path)
        try:
            payloads.append(path.read_bytes())
        except OSError as exc:
            log.warning("Bild %s nicht lesbar: %s", path, exc)
    return payloads


def download(client: HttpClient, urls: Iterable[str], limit: int = 4) -> List[bytes]:
    """Bild-URLs laden (gedrosselt und zwischengespeichert wie alle Abrufe)."""
    payloads: List[bytes] = []
    for url in urls:
        if len(payloads) >= limit:
            break
        if not url or not url.startswith("http"):
            continue
        try:
            payloads.append(client.fetch_bytes(url, max_bytes=MAX_IMAGE_BYTES))
        except FetchError as exc:
            log.info("Bild uebersprungen: %s", exc)
    return payloads

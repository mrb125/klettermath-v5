"""Netzfreie Alternative: Kartennamen per OCR aus den Fotos lesen.

Braucht das Programm `tesseract` (Debian/Ubuntu: `apt install tesseract-ocr
tesseract-ocr-deu`, macOS: `brew install tesseract`). Liest die Namenszeile
gedruckter Karten oft gut genug, um Wertkarten zu erkennen - erreicht aber
nicht die Qualitaet der Bildanalyse mit Claude.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Sequence, Tuple

from ..pricing.index import CardIndex
from .facts import PhotoCard, PhotoFacts

log = logging.getLogger("mtg_scout.vision.ocr")


class OcrVision:
    """Erkennt Kartennamen ueber Tesseract und den vorhandenen Preisindex."""

    def __init__(self, index: CardIndex, binary: str = "tesseract",
                 languages: str = "deu+eng", timeout: float = 60.0) -> None:
        self.index = index
        self.binary = binary
        self.languages = languages
        self.timeout = timeout

    def available(self) -> Tuple[bool, str]:
        if shutil.which(self.binary) is None:
            return False, (f"OCR-Programm '{self.binary}' nicht gefunden "
                           "(z.B. 'apt install tesseract-ocr tesseract-ocr-deu')")
        return True, ""

    def analyze(self, payloads: Sequence[bytes], context: str = "") -> PhotoFacts:
        ok, reason = self.available()
        if not ok:
            log.warning("OCR uebersprungen: %s", reason)
            return PhotoFacts(source="ocr")

        texts = []
        for index, payload in enumerate(payloads):
            text = self._read(payload, index)
            if text:
                texts.append(text)

        facts = PhotoFacts(source="ocr", images_analyzed=len(texts))
        if not texts:
            return facts
        combined = "\n".join(texts)
        for hit in self.index.find(combined):
            facts.cards.append(
                PhotoCard(name=hit.name, count=hit.count,
                          confidence=min(0.6, hit.confidence))
            )
        facts.summary = " ".join(combined.split())[:400]
        return facts

    def _read(self, payload: bytes, index: int) -> str:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"bild{index}.img"
            path.write_bytes(payload)
            try:
                result = subprocess.run(
                    [self.binary, str(path), "stdout", "-l", self.languages],
                    capture_output=True, text=True, timeout=self.timeout, check=False,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                log.warning("OCR fehlgeschlagen: %s", exc)
                return ""
        if result.returncode != 0:
            log.info("OCR-Fehler: %s", (result.stderr or "").strip()[:200])
            return ""
        return result.stdout or ""


def build_ocr(index: CardIndex, binary: str = "tesseract") -> Optional[OcrVision]:
    ocr = OcrVision(index, binary=binary)
    return ocr if ocr.available()[0] else None

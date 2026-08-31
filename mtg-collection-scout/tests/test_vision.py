import base64
import json
import unittest

from mtg_scout.analyze import Evaluator
from mtg_scout.config import DEFAULTS
from mtg_scout.models import Listing
from mtg_scout.pricing import CardIndex
from mtg_scout.vision import ClaudeVision, PhotoCard, PhotoFacts, VisionError
from mtg_scout.vision import images as vision_images
from mtg_scout.vision.facts import normalize_sealed
from mtg_scout.vision.ocr import OcrVision

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPEG = b"\xff\xd8\xff\xe0" + b"0" * 32

ANTWORT = {
    "erkannte_karten": [
        {"name": "Underground Sea", "anzahl": 1, "sicherheit": 0.9},
        {"name": "Force of Will", "anzahl": 4, "sicherheit": 0.8},
        {"name": "", "anzahl": 1, "sicherheit": 0.4},
    ],
    "versiegelte_produkte": [{"produkt": "Booster Box (Display)", "anzahl": 2}],
    "geschaetzte_kartenzahl": 1200,
    "zustand": "played",
    "auffaelligkeiten": ["Eine Karte wirkt wie ein Proxy"],
    "beschreibung": "Mehrere Ordnerseiten mit alten Karten.",
}


class _Block:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class _Response:
    def __init__(self, payload, stop_reason="end_turn"):
        self.content = [_Block(json.dumps(payload))]
        self.stop_reason = stop_reason
        self.stop_details = None


class _Messages:
    def __init__(self, response, record):
        self._response = response
        self._record = record

    def create(self, **kwargs):
        self._record.append(kwargs)
        return self._response


class _FakeClient:
    """Minimaler Ersatz fuer anthropic.Anthropic in den Tests."""

    def __init__(self, response, beta_works=True):
        self.calls = []
        self.messages = _Messages(response, self.calls)
        self.beta = type("Beta", (), {})()
        if beta_works:
            self.beta.messages = _Messages(response, self.calls)
        else:
            class _Broken:
                def create(self, **kwargs):
                    raise TypeError("unerwartetes Argument fallbacks")
            self.beta.messages = _Broken()


class TestBildhelfer(unittest.TestCase):
    def test_format_erkennung(self):
        self.assertEqual(vision_images.media_type(PNG), "image/png")
        self.assertEqual(vision_images.media_type(JPEG), "image/jpeg")
        self.assertEqual(vision_images.media_type(b"nix"), "")

    def test_kodierung_und_filter(self):
        mime, data = vision_images.encode(PNG)
        self.assertEqual(mime, "image/png")
        self.assertEqual(base64.standard_b64decode(data), PNG)
        self.assertEqual(vision_images.encode(b"nix"), ("", ""))
        self.assertEqual(len(vision_images.to_blocks([PNG, b"nix", JPEG])), 2)

    def test_zu_grosse_bilder_werden_aussortiert(self):
        riesig = PNG + b"0" * vision_images.MAX_IMAGE_BYTES
        self.assertEqual(vision_images.encode(riesig), ("", ""))


class TestClaudeVision(unittest.TestCase):
    def test_antwort_wird_uebersetzt(self):
        facts = ClaudeVision.parse_payload(ANTWORT)
        self.assertEqual([c.name for c in facts.cards], ["Underground Sea", "Force of Will"])
        self.assertEqual(facts.cards[1].count, 4)
        self.assertEqual(facts.sealed, {"display": 2})
        self.assertEqual(facts.card_count, 1200)
        self.assertEqual(facts.condition, "played")
        self.assertTrue(facts.flags)
        self.assertTrue(bool(facts))

    def test_unbekannter_zustand_bleibt_leer(self):
        facts = ClaudeVision.parse_payload({**ANTWORT, "zustand": "unbekannt"})
        self.assertEqual(facts.condition, "")

    def test_produktbezeichnungen(self):
        self.assertEqual(normalize_sealed("2 Collector Booster Box"), "collector_booster_box")
        self.assertEqual(normalize_sealed("Commander Deck"), "precon_deck")
        self.assertEqual(normalize_sealed("irgendwas"), "")

    def test_analyse_mit_fake_client(self):
        client = _FakeClient(_Response(ANTWORT))
        vision = ClaudeVision(client=client, max_images=2)
        facts = vision.analyze(vision_images.to_blocks([PNG, JPEG, PNG]), context="Magic Sammlung")
        self.assertEqual(facts.images_analyzed, 2)
        self.assertEqual(len(client.calls), 1)
        request = client.calls[0]
        self.assertEqual(request["model"], "claude-opus-5")
        self.assertEqual(len([b for b in request["messages"][0]["content"]
                              if b["type"] == "image"]), 2)
        self.assertIn("json_schema", json.dumps(request["output_config"]))
        self.assertIn("Magic Sammlung", request["messages"][0]["content"][-1]["text"])

    def test_faellt_auf_standardaufruf_zurueck(self):
        client = _FakeClient(_Response(ANTWORT), beta_works=False)
        facts = ClaudeVision(client=client).analyze(vision_images.to_blocks([PNG]))
        self.assertEqual(facts.card_count, 1200)
        self.assertEqual(len(client.calls), 1)      # nur der Standardaufruf zaehlt

    def test_ablehnung_wird_gemeldet(self):
        client = _FakeClient(_Response(ANTWORT, stop_reason="refusal"))
        with self.assertRaises(VisionError):
            ClaudeVision(client=client).analyze(vision_images.to_blocks([PNG]))

    def test_ohne_bilder_kein_aufruf(self):
        client = _FakeClient(_Response(ANTWORT))
        self.assertFalse(bool(ClaudeVision(client=client).analyze([])))
        self.assertEqual(client.calls, [])

    def test_schluessel_aus_der_konfiguration(self):
        """Der Schluessel darf in der Config stehen, nicht nur in der Umgebung."""
        from mtg_scout.config import DEFAULTS
        self.assertIn("api_key", DEFAULTS["vision"])
        vision = ClaudeVision(api_key="sk-ant-test")
        self.assertEqual(vision.api_key, "sk-ant-test")

    def test_ohne_sdk_nicht_verfuegbar(self):
        ok, reason = ClaudeVision(api_key="").available()
        self.assertFalse(ok)
        self.assertTrue(reason)


class TestOcr(unittest.TestCase):
    def test_fehlendes_programm_wird_gemeldet(self):
        ocr = OcrVision(CardIndex.from_fallback(), binary="tesseract-gibts-nicht")
        ok, reason = ocr.available()
        self.assertFalse(ok)
        self.assertIn("nicht gefunden", reason)
        self.assertEqual(ocr.analyze([PNG]).cards, [])


class TestBewertungMitFotos(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator(DEFAULTS, CardIndex.from_fallback())
        self.listing = Listing(source="test", title="Magic Sammlung", url="https://x",
                               price=400, description="Konvolut, wenig Angaben")

    def test_fotos_erhoehen_wert_und_sicherheit(self):
        ohne = self.evaluator.evaluate(self.listing)
        photos = ClaudeVision.parse_payload(ANTWORT)
        photos.images_analyzed = 2
        mit = self.evaluator.evaluate(self.listing, photos)
        self.assertGreater(mit.estimate.mid, ohne.estimate.mid)
        self.assertGreater(mit.estimate.confidence, ohne.estimate.confidence)
        self.assertTrue(any(h.source == "foto" for h in mit.card_hits))
        self.assertEqual(mit.card_count, 1200)

    def test_auffaelligkeiten_werden_zu_risiken(self):
        photos = PhotoFacts(flags=["Proxy erkennbar"], images_analyzed=1)
        ev = self.evaluator.evaluate(self.listing, photos)
        self.assertIn("Foto: Proxy erkennbar", ev.risks)

    def test_textangaben_haben_vorrang_vor_fotoschaetzung(self):
        listing = Listing(source="test", title="Magic Sammlung 5000 Karten",
                          url="https://x", price=400)
        ev = self.evaluator.evaluate(listing, PhotoFacts(card_count=1200, images_analyzed=1))
        self.assertEqual(ev.card_count, 5000)

    def test_unbekannte_karten_werden_ignoriert(self):
        photos = PhotoFacts(cards=[PhotoCard(name="Gibt Es Nicht", count=1, confidence=0.9)],
                            images_analyzed=1)
        ev = self.evaluator.evaluate(self.listing, photos)
        self.assertEqual([h for h in ev.card_hits if h.source == "foto"], [])


if __name__ == "__main__":
    unittest.main()

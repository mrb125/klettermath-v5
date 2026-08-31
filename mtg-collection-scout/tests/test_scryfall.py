"""Preisspiegel: Adresse der Bulk-Datei robust ermitteln."""

import json
import tempfile
import unittest
from pathlib import Path

from mtg_scout.net import FetchError
from mtg_scout.pricing.scryfall import BULK_ENDPOINT, ScryfallPrices
from mtg_scout.store import Store

KATALOG_OK = {"data": [
    {"type": "rulings", "download_uri": "https://data.example/rulings.json"},
    {"type": "oracle_cards", "name": "Oracle Cards", "size": 12345678,
     "download_uri": "https://data.example/oracle-cards.json"},
]}
KATALOG_OHNE_URI = {"data": [{"type": "oracle_cards", "name": "Oracle Cards", "size": 1}]}
KARTEN = [
    {"name": "Underground Sea", "set": "lea", "rarity": "rare", "reserved": True,
     "prices": {"eur": "900.00", "usd": "1100.00"}},
    {"name": "Nur Dollar", "set": "m21", "rarity": "mythic",
     "prices": {"eur": None, "usd": "100.00"}},
    {"prices": {"eur": "5.00"}},                     # ohne Namen -> wird uebersprungen
]


class _Client:
    """HTTP-Ersatz: liefert vorgegebene Antworten, merkt sich die Aufrufe."""

    def __init__(self, katalog=None, katalog_fehler=False):
        self.katalog = katalog
        self.katalog_fehler = katalog_fehler
        self.geholt = []

    def fetch_json(self, url, **kwargs):
        self.geholt.append(url)
        if self.katalog_fehler:
            raise FetchError("Netz weg")
        return self.katalog

    def fetch(self, url, **kwargs):
        self.geholt.append(url)
        return json.dumps(KARTEN)


class TestBulkAdresse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / "test.sqlite3")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_nutzt_download_uri_aus_dem_katalog(self):
        prices = ScryfallPrices(self.store, _Client(KATALOG_OK))
        self.assertEqual(prices.download_uri(), "https://data.example/oracle-cards.json")

    def test_direktabruf_wenn_download_uri_fehlt(self):
        """Genau der Fall, der frueher mit KeyError abgebrochen ist."""
        prices = ScryfallPrices(self.store, _Client(KATALOG_OHNE_URI))
        self.assertEqual(prices.download_uri(),
                         "https://api.scryfall.com/bulk-data/oracle-cards?format=file")

    def test_direktabruf_wenn_katalog_nicht_erreichbar(self):
        prices = ScryfallPrices(self.store, _Client(katalog_fehler=True))
        self.assertIn("format=file", prices.download_uri())

    def test_direktabruf_wenn_typ_unbekannt(self):
        prices = ScryfallPrices(self.store, _Client({"data": []}))
        self.assertIn("bulk-data/oracle-cards", prices.download_uri())

    def test_refresh_schreibt_preise(self):
        client = _Client(KATALOG_OK)
        prices = ScryfallPrices(self.store, client)
        self.assertEqual(prices.refresh(), 2)          # Eintrag ohne Namen faellt raus
        self.assertEqual(self.store.card_count(), 2)
        self.assertEqual(self.store.lookup_card("Underground Sea")["eur"], 900.0)
        # Ohne EUR-Preis wird aus dem Dollarpreis umgerechnet
        self.assertAlmostEqual(self.store.lookup_card("Nur Dollar")["eur"], 92.0, places=1)
        self.assertIn(BULK_ENDPOINT, client.geholt)

    def test_kaputte_bulk_datei_meldet_klaren_fehler(self):
        class _Kaputt(_Client):
            def fetch(self, url, **kwargs):
                return "<html>Wartungsarbeiten</html>"

        prices = ScryfallPrices(self.store, _Kaputt(KATALOG_OK))
        with self.assertRaises(FetchError) as fehler:
            prices.refresh()
        self.assertIn("lesen", str(fehler.exception))

    def test_index_faellt_auf_katalog_zurueck(self):
        prices = ScryfallPrices(self.store, _Client(KATALOG_OK))
        index = prices.index()                          # leere Datenbank
        self.assertTrue(index.lookup("Black Lotus"))


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from pathlib import Path

from mtg_scout.config import DEFAULTS
from mtg_scout.net import HttpClient
from mtg_scout.sources import available_source_names, build_sources
from mtg_scout.sources.kleinanzeigen import KleinanzeigenSource
from mtg_scout.sources.local import load_listings_file
from mtg_scout.sources.profile import ProfileSource, load_profiles

FIXTURES = Path(__file__).parent / "fixtures"


class TestKleinanzeigen(unittest.TestCase):
    def setUp(self):
        self.source = KleinanzeigenSource(DEFAULTS, HttpClient(offline=True))

    def test_parst_suchergebnisse(self):
        listings = self.source.parse((FIXTURES / "kleinanzeigen_search.html").read_text("utf-8"))
        self.assertEqual(len(listings), 2)
        first = listings[0]
        self.assertEqual(first.title, "Magic Sammlung ca. 3000 Karten Revised")
        self.assertEqual(first.price, 350.0)
        self.assertEqual(first.currency, "EUR")
        self.assertEqual(first.location, "50667 Köln")
        self.assertEqual(first.listing_id, "kleinanzeigen:2871234567")
        self.assertTrue(first.url.startswith("https://www.kleinanzeigen.de/s-anzeige/"))
        self.assertIn("Ordnern", first.description)

    def test_zu_verschenken_ist_preis_null(self):
        listings = self.source.parse((FIXTURES / "kleinanzeigen_search.html").read_text("utf-8"))
        self.assertEqual(listings[1].price, 0.0)

    def test_kaputtes_html_wirft_nicht(self):
        self.assertEqual(self.source.parse("<html><body>nichts</body></html>"), [])

    def test_such_url_enthaelt_filter(self):
        from mtg_scout.sources.base import SearchQuery
        url = self.source._search_url("magic sammlung", 2,
                                      SearchQuery(min_price_eur=50, max_price_eur=800,
                                                  postal_code="50667", radius_km=100))
        self.assertIn("seite:2", url)
        self.assertIn("preis:50:800", url)
        self.assertIn("l50667", url)
        self.assertIn("r100", url)
        self.assertTrue(url.endswith("magic-sammlung/k0"))


class TestProfilQuelle(unittest.TestCase):
    def test_json_ld_wird_gelesen(self):
        profile = {"name": "testmarkt", "label": "Testmarkt", "countries": ["NL"],
                   "base_url": "https://markt.example", "search_url": "https://markt.example/q/{query}/{page}"}
        source = ProfileSource(DEFAULTS, HttpClient(offline=True), profile)
        listings = source.parse((FIXTURES / "jsonld_search.html").read_text("utf-8"))
        self.assertEqual(len(listings), 2)
        self.assertEqual(listings[0].price, 420.0)
        self.assertEqual(listings[0].url, "https://markt.example/annonce/1")
        self.assertEqual(listings[1].currency, "CHF")
        self.assertEqual(listings[0].country, "NL")

    def test_ausgelieferte_profile_sind_gueltig(self):
        profiles = load_profiles()
        self.assertIn("willhaben", profiles)
        for name, profile in profiles.items():
            self.assertIn("search_url", profile, name)
            self.assertIn("{query}", profile["search_url"], name)
            self.assertTrue(profile.get("base_url", "").startswith("https://"), name)


class TestRegistry(unittest.TestCase):
    def test_alle_quellen_baubar(self):
        sources = build_sources(["alle"], DEFAULTS, HttpClient(offline=True))
        self.assertEqual(len(sources), len(available_source_names()))

    def test_unbekannte_quelle_wird_ignoriert(self):
        self.assertEqual(build_sources(["gibtsnicht"], DEFAULTS, HttpClient(offline=True)), [])


class TestDateiQuelle(unittest.TestCase):
    def test_json_und_csv(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "l.json"
            json_path.write_text(json.dumps([
                {"title": "Magic Sammlung", "price": "250 €", "url": "https://x/1"}
            ]), "utf-8")
            csv_path = Path(tmp) / "l.csv"
            csv_path.write_text("title;price;url\nMTG Lot;120;https://x/2\n".replace(";", ","), "utf-8")
            self.assertEqual(load_listings_file(json_path)[0].price, 250.0)
            self.assertEqual(load_listings_file(csv_path)[0].price, 120.0)


if __name__ == "__main__":
    unittest.main()

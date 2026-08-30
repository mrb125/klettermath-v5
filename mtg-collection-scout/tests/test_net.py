import tempfile
import unittest
from pathlib import Path

from mtg_scout.net import FetchError, HttpClient


class TestHttpClient(unittest.TestCase):
    def test_offline_ohne_cache_wirft(self):
        client = HttpClient(offline=True)
        with self.assertRaises(FetchError):
            client.fetch("https://example.invalid/x")

    def test_cache_wird_offline_genutzt(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = HttpClient(cache_dir=Path(tmp), offline=True)
            key = "GET https://example.invalid/x "
            client._cache_write(key, "<html>hallo</html>")
            self.assertEqual(client.fetch("https://example.invalid/x"), "<html>hallo</html>")

    def test_cache_kann_uebersprungen_werden(self):
        with tempfile.TemporaryDirectory() as tmp:
            client = HttpClient(cache_dir=Path(tmp), offline=True)
            client._cache_write("GET https://example.invalid/x ", "alt")
            with self.assertRaises(FetchError):
                client.fetch("https://example.invalid/x", use_cache=False)

    def test_robots_abschaltbar(self):
        self.assertTrue(HttpClient(respect_robots=False).robots_allows("https://example.invalid/x"))


class TestWaehrung(unittest.TestCase):
    def test_fallback_kurse_ohne_netz(self):
        from mtg_scout.currency import CurrencyConverter
        converter = CurrencyConverter(client=None, cache_file=None)
        self.assertEqual(converter.to_eur(100, "EUR"), 100.0)
        self.assertLess(converter.to_eur(100, "USD"), 100.0)
        self.assertIsNone(converter.to_eur(None, "USD"))
        self.assertEqual(converter.to_eur(100, "XYZ"), 100.0)   # unbekannt -> 1:1


if __name__ == "__main__":
    unittest.main()

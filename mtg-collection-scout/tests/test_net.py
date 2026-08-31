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


class TestAusfallzaehler(unittest.TestCase):
    """Ein nicht erreichbarer Host wird im laufenden Durchgang uebersprungen."""

    def test_toter_host_bricht_sofort_ab(self):
        client = HttpClient(host_failure_limit=2, retries=1)
        client._note_failure("www.example.invalid")
        self.assertFalse(client._host_is_dead("www.example.invalid"))
        client._note_failure("www.example.invalid")
        self.assertTrue(client._host_is_dead("www.example.invalid"))

        with self.assertRaises(FetchError) as fehler:
            client.fetch("https://www.example.invalid/suche")
        self.assertIn("nicht erreichbar", str(fehler.exception))
        with self.assertRaises(FetchError):
            client.fetch_bytes("https://www.example.invalid/bild.jpg")

    def test_andere_hosts_bleiben_unberuehrt(self):
        client = HttpClient(host_failure_limit=1)
        client._note_failure("tot.example")
        self.assertTrue(client._host_is_dead("tot.example"))
        self.assertFalse(client._host_is_dead("lebt.example"))

    def test_robots_pruefung_entfaellt_fuer_tote_hosts(self):
        client = HttpClient(host_failure_limit=1, respect_robots=True)
        client._note_failure("tot.example")
        self.assertTrue(client.robots_allows("https://tot.example/x"))


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

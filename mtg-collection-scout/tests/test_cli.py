import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from mtg_scout.cli import main


class TestCli(unittest.TestCase):
    """End-to-End ueber die Demo-Quelle - kein Netzzugriff noetig."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self._env = {}
        for key, sub in (("XDG_CONFIG_HOME", "config"), ("XDG_DATA_HOME", "data"),
                         ("XDG_CACHE_HOME", "cache")):
            self._env[key] = os.environ.get(key)
            os.environ[key] = str(base / sub)
        self.base = base

    def tearDown(self):
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def _run(self, *argv):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(list(argv))
        return code, buffer.getvalue()

    def test_demo_suche_liefert_bewertungen(self):
        code, out = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben")
        self.assertEqual(code, 0)
        self.assertIn("Angebote bewertet", out)
        self.assertIn("Magic", out)

    def test_ausgabedateien_werden_geschrieben(self):
        json_path = self.base / "r.json"
        html_path = self.base / "r.html"
        csv_path = self.base / "r.csv"
        code, _ = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben",
                            "--json", str(json_path), "--html", str(html_path),
                            "--csv", str(csv_path))
        self.assertEqual(code, 0)
        payload = json.loads(json_path.read_text("utf-8"))
        self.assertGreater(len(payload["angebote"]), 3)
        self.assertTrue(html_path.exists() and csv_path.exists())

    def test_notenfilter(self):
        _, alle = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben")
        _, nur_gute = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben",
                                "--min-note", "B")
        self.assertGreater(alle.count("https://example.invalid"),
                           nur_gute.count("https://example.invalid"))

    def test_nur_neue_blendet_bekannte_aus(self):
        code, erste = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben",
                                "--nur-neue")
        self.assertEqual(code, 0)
        _, zweite = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben",
                              "--nur-neue")
        self.assertIn("Magic", erste)
        self.assertIn("Keine Angebote gefunden", zweite)

    def test_einzelbewertung(self):
        code, out = self._run("bewerten", "--text", "Magic Sammlung 4000 Karten Revised",
                              "--preis", "300", "--keine-farben")
        self.assertEqual(code, 0)
        self.assertIn("Karten x", out)

    def test_fotos_ohne_sdk_bricht_nicht_ab(self):
        code, out = self._run("suchen", "--quelle", "demo", "--offline", "--keine-farben",
                              "--fotos")
        self.assertEqual(code, 0)
        self.assertIn("Angebote bewertet", out)

    def test_bewerten_mit_unlesbarem_bild(self):
        bild = self.base / "kaputt.jpg"
        bild.write_bytes(b"kein bild")
        code, out = self._run("bewerten", "--text", "Magic Sammlung 2000 Karten",
                              "--preis", "200", "--bild", str(bild), "--keine-farben")
        self.assertEqual(code, 0)
        self.assertIn("Karten x", out)

    def test_quellen_und_status(self):
        code, out = self._run("quellen")
        self.assertEqual(code, 0)
        self.assertIn("kleinanzeigen", out)
        code, out = self._run("status")
        self.assertEqual(code, 0)
        self.assertIn("Kartenpreise", out)

    def test_config_beispiel(self):
        target = self.base / "config.json"
        code, out = self._run("--config", str(target), "config", "--beispiel")
        self.assertEqual(code, 0)
        self.assertTrue(target.exists())
        self.assertIn("valuation", json.loads(target.read_text("utf-8")))

    def test_hilfe_ohne_befehl(self):
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("mtg-scout", out)


if __name__ == "__main__":
    unittest.main()

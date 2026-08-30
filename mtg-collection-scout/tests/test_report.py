import json
import tempfile
import unittest
from pathlib import Path

from mtg_scout.analyze import Evaluator
from mtg_scout.config import DEFAULTS
from mtg_scout.models import Listing
from mtg_scout.pricing import CardIndex
from mtg_scout.report import render_console, summary_line, write_csv, write_html, write_json


class TestReport(unittest.TestCase):
    def setUp(self):
        evaluator = Evaluator(DEFAULTS, CardIndex.from_fallback())
        self.evaluations = [
            evaluator.evaluate(Listing(source="demo", title="Magic Sammlung 4000 Karten Revised",
                                       url="https://x/1", price=300)),
            evaluator.evaluate(Listing(source="demo", title="MTG Bulk nur Commons 5000 Karten",
                                       url="https://x/2", price=400)),
        ]

    def test_konsolenausgabe(self):
        text = render_console(self.evaluations, color=False, details=True)
        self.assertIn("Magic Sammlung", text)
        self.assertIn("https://x/1", text)
        self.assertNotIn("\033[", text)
        self.assertIn("Angebote bewertet", summary_line(self.evaluations, color=False))

    def test_dateiausgaben(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            payload = json.loads(write_json(tmp / "r.json", self.evaluations).read_text("utf-8"))
            self.assertEqual(len(payload["angebote"]), 2)
            self.assertIn("grade", payload["angebote"][0])

            csv_text = write_csv(tmp / "r.csv", self.evaluations).read_text("utf-8")
            self.assertIn("grade;score", csv_text)
            self.assertEqual(len(csv_text.strip().splitlines()), 3)

            html_text = write_html(tmp / "r.html", self.evaluations, {"Angebote": 2}).read_text("utf-8")
            self.assertIn("<!doctype html>", html_text)
            self.assertIn("Magic Sammlung", html_text)
            self.assertIn("prefers-color-scheme", html_text)

    def test_html_maskiert_sonderzeichen(self):
        evaluator = Evaluator(DEFAULTS, CardIndex.from_fallback())
        boese = evaluator.evaluate(Listing(source="demo", title="<script>alert(1)</script>",
                                           url="https://x/3", price=10))
        with tempfile.TemporaryDirectory() as tmp:
            text = write_html(Path(tmp) / "r.html", [boese]).read_text("utf-8")
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;", text)


if __name__ == "__main__":
    unittest.main()

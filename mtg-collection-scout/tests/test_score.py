import unittest

from mtg_scout.analyze import Evaluator
from mtg_scout.config import DEFAULTS
from mtg_scout.currency import CurrencyConverter
from mtg_scout.models import Listing
from mtg_scout.pricing import CardIndex


def _offline_converter() -> CurrencyConverter:
    """Fester Kurs, damit Tests nicht vom Netz abhaengen."""
    converter = CurrencyConverter(client=None, cache_file=None)
    converter.rates.update({"EUR": 1.0, "USD": 0.9, "CHF": 1.05})
    return converter


class TestBewertung(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator(DEFAULTS, CardIndex.from_fallback(), _offline_converter())

    def _eval(self, title, price=None, description="", currency="EUR", **kwargs):
        return self.evaluator.evaluate(
            Listing(source="test", title=title, url="https://x", price=price,
                    currency=currency, description=description, **kwargs)
        )

    def test_guenstige_alte_sammlung_wird_hoch_bewertet(self):
        ev = self._eval("Magic Sammlung Revised ca. 4000 Karten", price=300)
        self.assertGreater(ev.score, 70)
        self.assertIn(ev.grade, ("A+", "A", "B"))
        self.assertGreater(ev.ratio, 1.5)

    def test_teures_angebot_faellt_durch(self):
        ev = self._eval("Magic Sammlung 500 Karten gemischt", price=2000)
        self.assertLess(ev.score, 45)

    def test_gesuch_wird_erkannt(self):
        ev = self._eval("Suche Magic Sammlung", price=None)
        self.assertEqual(ev.grade, "-")
        self.assertEqual(ev.score, 0.0)

    def test_risiken_senken_den_score(self):
        ohne = self._eval("Magic Sammlung 4000 Karten Revised", price=300)
        mit = self._eval("Magic Sammlung 4000 Karten Revised",
                         price=300, description="Enthält Proxys und beschädigte Karten")
        self.assertLess(mit.score, ohne.score)
        self.assertTrue(mit.risks)

    def test_fremdwaehrung_wird_umgerechnet(self):
        ev = self._eval("MTG collection 2000 cards", price=1000, currency="USD")
        self.assertEqual(ev.price_eur, 900.0)

    def test_versandkosten_zaehlen_zum_preis(self):
        ev = self._eval("Magic Sammlung 1000 Karten", price=100, shipping=9.9)
        self.assertAlmostEqual(ev.price_eur, 109.9, places=2)

    def test_schwacher_verkaeufer_wird_abgewertet(self):
        gut = self._eval("Magic Sammlung 4000 Karten", price=200, seller_rating=99.5)
        schwach = self._eval("Magic Sammlung 4000 Karten", price=200, seller_rating=88.0)
        self.assertLess(schwach.score, gut.score)
        self.assertTrue(any("Verkaeuferbewertung" in r for r in schwach.risks))

    def test_ohne_preis_bleibt_neutral(self):
        ev = self._eval("Magic Sammlung 3000 Karten Legends", price=None)
        self.assertIsNone(ev.ratio)
        self.assertIn("Kein Preis", ev.verdict)

    def test_ohne_information_keine_schaetzung(self):
        ev = self._eval("Magic Karten", price=100)
        self.assertEqual(ev.estimate.mid, 0.0)
        self.assertIn("Zu wenig Information", ev.verdict)

    def test_wertsignale_ohne_edition_erhoehen_den_kartenpreis(self):
        schlicht = self._eval("MTG lot 1500 cards", price=500)
        mit_duals = self._eval("MTG lot 1500 cards with dual lands", price=500)
        self.assertGreater(mit_duals.estimate.mid, schlicht.estimate.mid * 2)

    def test_neunziger_jahre_zaehlen_als_alte_sammlung(self):
        ev = self._eval("Magic Sammlung 1000 Karten aus den 90ern", price=100)
        self.assertIn("oldschool", " ".join(ev.estimate.breakdown))

    def test_wertherleitung_ist_nachvollziehbar(self):
        ev = self._eval("Magic Sammlung 2000 Karten mit Underground Sea", price=500)
        self.assertTrue(ev.estimate.breakdown)
        self.assertTrue(any("Underground Sea" in line for line in ev.estimate.breakdown))
        self.assertLess(ev.estimate.low, ev.estimate.mid)
        self.assertGreater(ev.estimate.high, ev.estimate.mid)


if __name__ == "__main__":
    unittest.main()

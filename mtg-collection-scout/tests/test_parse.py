import unittest

from mtg_scout.analyze.parse import parse_card_count, parse_listing


class TestKartenzahl(unittest.TestCase):
    def test_direkt_genannt(self):
        self.assertEqual(parse_card_count("ca. 3.500 Karten")[0], 3500)
        self.assertEqual(parse_card_count("5000 cards mixed")[0], 5000)
        self.assertEqual(parse_card_count("ungefähr 5k Karten")[0], 5000)

    def test_aus_behaeltern_hochgerechnet(self):
        count, source = parse_card_count("Konvolut mit 5 Sammelordnern")
        self.assertEqual(count, 5 * 360)
        self.assertIn("Ordner", source)

    def test_unrealistische_zahlen_ignoriert(self):
        self.assertIsNone(parse_card_count("Baujahr 1993, Postleitzahl 50667")[0])


class TestAnzeigenanalyse(unittest.TestCase):
    def test_aera_und_zustand(self):
        facts = parse_listing("Magic Sammlung Revised und Legends, Zustand gespielt")
        self.assertEqual(facts.top_era, "vintage")
        self.assertEqual(facts.condition, "good")

    def test_versiegelte_ware(self):
        facts = parse_listing("2x Display Modern Horizons versiegelt OVP")
        self.assertEqual(facts.sealed.get("display"), 2)

    def test_booster_ohne_versiegelt_zaehlt_nicht(self):
        self.assertNotIn("booster", parse_listing("Karten aus Boostern gezogen").sealed)

    def test_risiken(self):
        facts = parse_listing("Sammlung mit Proxys, teilweise beschädigt, nur Abholung")
        self.assertIn("Proxys/Fakes erwaehnt", facts.risks)
        self.assertIn("Beschaedigte Karten", facts.risks)
        self.assertIn("Nur Abholung", facts.risks)

    def test_gesuch_erkannt(self):
        self.assertTrue(parse_listing("Suche Magic Sammlung, zahle bar").is_wanted_ad)
        self.assertFalse(parse_listing("Verkaufe Sammlung, suche neue Besitzer").is_wanted_ad)

    def test_keine_rares_ist_kein_positives_signal(self):
        facts = parse_listing("Bulk Konvolut, keine Rares enthalten")
        self.assertNotIn("Rares/Mythics genannt", facts.signals)
        self.assertIn("Nur Massenware/Commons", facts.risks)


if __name__ == "__main__":
    unittest.main()

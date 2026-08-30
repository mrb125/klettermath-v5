import unittest

from mtg_scout.pricing import CardIndex


class TestKartenerkennung(unittest.TestCase):
    def setUp(self):
        self.index = CardIndex.from_fallback()

    def test_findet_mehrwortnamen(self):
        hits = {h.name: h for h in self.index.find("Sammlung mit Underground Sea und Force of Will")}
        self.assertIn("Underground Sea", hits)
        self.assertIn("Force of Will", hits)

    def test_playset_multiplikator(self):
        hits = {h.name: h for h in self.index.find("Verkaufe 4x Force of Will")}
        self.assertEqual(hits["Force of Will"].count, 4)

    def test_einzelwort_nur_gross_geschrieben(self):
        self.assertFalse(any(h.name == "Tundra" for h in self.index.find("landschaft tundra im winter")))
        self.assertTrue(any(h.name == "Tundra" for h in self.index.find("Dabei ist eine Tundra")))

    def test_alltagswoerter_werden_ignoriert(self):
        self.assertEqual(self.index.find("Island Mountain Forest Swamp Plains"), [])

    def test_billige_karten_unter_schwelle(self):
        self.assertEqual(self.index.find("Mishra's Factory", min_eur=50), [])


if __name__ == "__main__":
    unittest.main()

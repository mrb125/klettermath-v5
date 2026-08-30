import unittest

from mtg_scout.util import money, normalize, parse_number, parse_price, strip_html, truncate


class TestUtil(unittest.TestCase):
    def test_parse_number_varianten(self):
        self.assertEqual(parse_number("1.234,50"), 1234.50)
        self.assertEqual(parse_number("1,234.50"), 1234.50)
        self.assertEqual(parse_number("2.000"), 2000)
        self.assertEqual(parse_number("1500"), 1500)
        self.assertIsNone(parse_number("keine Zahl"))

    def test_parse_price_mit_waehrung(self):
        self.assertEqual(parse_price("VB 1.250,50 €"), (1250.5, "EUR"))
        self.assertEqual(parse_price("$1,234.50"), (1234.5, "USD"))
        self.assertEqual(parse_price("CHF 90.-"), (90.0, "CHF"))
        self.assertEqual(parse_price("Zu verschenken")[0], None)

    def test_strip_html(self):
        self.assertEqual(strip_html("<p>Hallo<br>Welt</p><script>x=1</script>"), "Hallo Welt")

    def test_normalize_entfernt_umlaute(self):
        self.assertEqual(normalize("Größe ÄÖÜ"), "grosse aou")

    def test_money_und_truncate(self):
        self.assertEqual(money(1234.0), "1.234 €")
        self.assertEqual(money(None), "-")
        self.assertTrue(truncate("abcdefghij", 5).endswith("…"))


if __name__ == "__main__":
    unittest.main()

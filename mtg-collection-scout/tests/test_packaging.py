"""Wacht darueber, dass alle Unterpakete auch wirklich mitinstalliert werden."""

from __future__ import annotations

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPaketierung(unittest.TestCase):
    def test_alle_unterpakete_werden_erfasst(self):
        """Entweder automatische Suche - oder jedes Verzeichnis steht in der Liste.

        Hintergrund: mtg_scout.vision fehlte in einer handgepflegten Paketliste,
        wodurch das installierte Paket beim Start abbrach.
        """
        try:
            import tomllib
        except ImportError:                      # Python < 3.11
            self.skipTest("tomllib erst ab Python 3.11 verfuegbar")
        config = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text("utf-8"))
        setuptools_cfg = config.get("tool", {}).get("setuptools", {})
        vorhandene = {
            str(path.parent.relative_to(PROJECT_ROOT)).replace("/", ".")
            for path in (PROJECT_ROOT / "mtg_scout").rglob("__init__.py")
        }
        self.assertIn("mtg_scout.vision", vorhandene)

        if "packages" in setuptools_cfg and isinstance(setuptools_cfg["packages"], list):
            fehlend = vorhandene - set(setuptools_cfg["packages"])
            self.assertEqual(fehlend, set(), f"nicht paketiert: {sorted(fehlend)}")
        else:
            gefunden = setuptools_cfg.get("packages", {}).get("find", {})
            self.assertTrue(gefunden.get("include"), "weder Liste noch automatische Suche")

    def test_paketdaten_sind_eingetragen(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest("tomllib erst ab Python 3.11 verfuegbar")
        config = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text("utf-8"))
        muster = config["tool"]["setuptools"]["package-data"]["mtg_scout"]
        self.assertIn("profiles/*.json", muster)
        self.assertIn("data/*.json", muster)


if __name__ == "__main__":
    unittest.main()

// ══════════════════════════════════════════════════════
// RIFFEL — Phase-0-Testring
//
// Kleinstes Prüfteil der Serie. Vor dem Druck irgendeines großen
// Objekts wird hier validiert:
//   • Rillenteilung & -tiefe (sieht die Riffelung gut aus?)
//   • Nahtlage im Rillental (Slicer: Naht „hinten/ausgerichtet")
//   • Material/Optik (PETG matt vs. PLA matt)
//   • Verzahnungs-Flankenspiel 0,25 mm  →  TEIL = 2 (Clip)
//
// TEIL = 0 : Ring + Clip nebeneinander
// TEIL = 1 : nur Ring (Ø56 / H24)
// TEIL = 2 : nur Verzahnungs-Clip (greift in die Rillen des Rings)
// TEIL = 3 : Rillen-Vergleichsreihe (4 Ringe, versch. Rillentiefen)
// ══════════════════════════════════════════════════════
use <riffel-lib.scad>

TEIL = 0;
$fn = 96;

D = 56;     // Ringdurchmesser (Familienmaß)
H = 24;     // Ringhöhe (3 × 8-mm-Raster)

// Variable Rille des Testrings (überschreibt die Lib-Defaults).
// 0 lässt den Lib-Standard greifen.
RILLE_T = 1.2;   // Tiefe
RILLE_R = 2.4;   // Radius/Breite

module testring() {
    riffel_round(D, H, hohl = true, sig = true, t = RILLE_T, r = RILLE_R);
}

// Phase-0-Entscheidungshilfe: vier flache Ringe mit unterschiedlicher
// Rillentiefe in EINEM Druck vergleichen (tiefer = kräftiger Look,
// flacher = leichter zu reinigen).
TIEFEN = [0.8, 1.0, 1.2, 1.5];
module rillen_vergleich() {
    for (k = [0 : len(TIEFEN) - 1])
        translate([k * (D + 12), 0, 0])
            riffel_round(D, 16, hohl = true, sig = false,
                         t = TIEFEN[k], r = RILLE_R);
}

// Clip: 90°-Bogenband, dessen Innenrippen mit 0,25 mm Spiel in die
// Rillen greifen. Bestätigt die Passung für alle Kombi-Module.
module test_clip() {
    R = D / 2;
    band_h = 12;
    difference() {
        // Bogenband außen
        intersection() {
            difference() {
                cylinder(h = band_h, r = R + 3.5);
                translate([0, 0, -0.1])
                    cylinder(h = band_h + 0.2, r = R + 0.25);  // Spiel zur Kammfläche
            }
            // auf ~100° begrenzen
            rotate([0, 0, -50])
                linear_extrude(band_h) polygon([[0,0],[R+6,0],
                    [ (R+6)*cos(100), (R+6)*sin(100) ]]);
        }
    }
    // Eingreifende Rippen (Negativ der Rillen) — gleiche Rille wie der Ring
    riffel_negativ_arc(D, band_h, winkel = 100, t = RILLE_T, r = RILLE_R);
}

if (TEIL == 0) {
    testring();
    translate([D + 25, 0, 0]) test_clip();
} else if (TEIL == 1) {
    testring();
} else if (TEIL == 2) {
    test_clip();
} else if (TEIL == 3) {
    rillen_vergleich();
}

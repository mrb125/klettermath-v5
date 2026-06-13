// ══════════════════════════════════════════════════════
// RIFFEL — Phase-0-Testring
//
// Kleinstes Prüfteil der Serie. Vor dem Druck irgendeines großen
// Objekts wird hier validiert:
//   • Rillenteilung & -tiefe (sieht die Riffelung gut aus?)
//   • Nahtlage im Rillental (Slicer: Naht „hinten/ausgerichtet")
//   • Material/Optik (PETG matt vs. PLA matt)
//   • Verzahnungs-Flankenspiel  →  TEIL = 2 (Clip) / TEIL = 4 (Reihe)
//
// TEIL = 0 : Ring + Clip nebeneinander
// TEIL = 1 : nur Ring (Ø56 / H24)
// TEIL = 2 : nur Verzahnungs-Clip (greift in die Rillen des Rings)
// TEIL = 3 : Rillen-Vergleichsreihe (4 Ringe, versch. Rillentiefen)
// TEIL = 4 : Spielmaß-Vergleichsreihe (3 Clips, versch. Flankenspiel)
// ══════════════════════════════════════════════════════
use <riffel-lib.scad>

TEIL = 0;
$fn = 96;

D = 56;     // Ringdurchmesser (Familienmaß)
H = 24;     // Ringhöhe (3 × 8-mm-Raster)

// Variable Rille des Testrings (überschreibt die Lib-Defaults).
RILLE_T = 1.2;        // Tiefe
RILLE_R = 2.4;        // Radius/Breite
RILLE_SPIEL = 0.25;   // Flankenspiel des Einzel-Clips (TEIL 0/2)

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

// Clip: ~100°-Bogenband, dessen Innenrippen mit `spiel` in die Rillen
// greifen. Bestätigt die Passung für alle Kombi-Module. `label` wird
// (falls gesetzt) oben in das Band graviert → Teile bleiben zuordenbar.
module test_clip(spiel = 0.25, label = "") {
    R = D / 2;
    band_h = 12;
    difference() {
        union() {
            // Bogenband außen, innen mit `spiel` Abstand zur Kammfläche
            intersection() {
                difference() {
                    cylinder(h = band_h, r = R + 3.5);
                    translate([0, 0, -0.1])
                        cylinder(h = band_h + 0.2, r = R + spiel);
                }
                rotate([0, 0, -50])
                    linear_extrude(band_h) polygon([[0,0],[R+6,0],
                        [ (R+6)*cos(100), (R+6)*sin(100) ]]);
            }
            // Eingreifende Rippen (Negativ der Rillen)
            riffel_negativ_arc(D, band_h, winkel = 100,
                               t = RILLE_T, r = RILLE_R, spiel = spiel);
        }
        // Beschriftung mit dem Spielmaß, am Bogen-Scheitel eingraviert
        if (label != "")
            translate([(R + 1.9) * cos(50), (R + 1.9) * sin(50), band_h - 0.5])
                linear_extrude(0.6)
                    rotate(50 - 90)
                        text(label, size = 3.6, halign = "center",
                             valign = "center", font = "Arial:style=Bold");
    }
}

// Phase-0-Entscheidungshilfe: drei Clips mit unterschiedlichem
// Flankenspiel. Jeden auf denselben Testring (TEIL 1) aufstecken und den
// schönsten Sitz wählen (kleiner = strammer, größer = leichtgängiger).
SPIELE = [0.15, 0.25, 0.35];
module spiel_vergleich() {
    for (k = [0 : len(SPIELE) - 1])
        translate([k * (D + 24), 0, 0])
            test_clip(SPIELE[k], str(SPIELE[k]));
}

if (TEIL == 0) {
    testring();
    translate([D + 25, 0, 0]) test_clip(RILLE_SPIEL);
} else if (TEIL == 1) {
    testring();
} else if (TEIL == 2) {
    test_clip(RILLE_SPIEL);
} else if (TEIL == 3) {
    rillen_vergleich();
} else if (TEIL == 4) {
    spiel_vergleich();
}

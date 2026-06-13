// ══════════════════════════════════════════════════════
// RIFFEL — Seifenschale
//
// Welle 1, Bad-Basics.  106 × 56 / H24, Stadion-Grundriss (R28),
// 66 Rillen.  Mit höherem Rand (H40) und gleicher Geometrie wird
// daraus der Schwammhalter (Welle 4).
//   • Schale (geriffelt, dicht)        → TEIL 1
//   • Abtropfeinsatz (Kontrastfarbe)   → TEIL 2
//
// TEIL = 0 : beide nebeneinander (Vorschau)
// ══════════════════════════════════════════════════════
use <riffel-lib.scad>

TEIL = 0;
$fn = 96;

L  = 106;   // Gesamtlänge
Wd = 56;    // Breite (= 2 × R28)
H  = 24;

module schale_koerper() { riffel_stadion(L, Wd, H, hohl = true, sig = true); }
module schale_einsatz() { abtropf_stadion(L, Wd); }

if (TEIL == 0) {
    schale_koerper();
    translate([0, Wd + 20, 0]) schale_einsatz();
} else if (TEIL == 1) {
    schale_koerper();
} else if (TEIL == 2) {
    schale_einsatz();
}

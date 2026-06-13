// ══════════════════════════════════════════════════════
// RIFFEL — Becher (Zahnbürsten / Stiftebecher)
//
// Welle 1, Bad-Basics.  Ø56 / H96, Rundgrundriss, 42 Rillen.
// Zwei Druckteile in EINER Serienfarbe + Kontrast:
//   • Schale (geriffelt, dicht)            → TEIL 1
//   • Abtropfeinsatz (Kontrastfarbe)       → TEIL 2
// Ohne Einsatz ist es der Stiftebecher (Welle 4) — gleiche Geometrie.
//
// TEIL = 0 : beide nebeneinander (Vorschau)
// ══════════════════════════════════════════════════════
use <riffel-lib.scad>

TEIL = 0;
$fn = 96;

D = 56;
H = 96;

module becher_schale() { riffel_round(D, H, hohl = true, sig = true); }
module becher_einsatz() { abtropf_round(D); }

if (TEIL == 0) {
    becher_schale();
    translate([D + 20, 0, 0]) becher_einsatz();
} else if (TEIL == 1) {
    becher_schale();
} else if (TEIL == 2) {
    becher_einsatz();
}

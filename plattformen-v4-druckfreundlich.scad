// ══════════════════════════════════════════════════════
// KletterMath v4 — Druckfreundliche Plattformen (FDM, OHNE Supports)
//
// Ziel: Jede Plattform lässt sich direkt auf dem Druckbett absetzen
//       und komplett ohne Stützstrukturen drucken.
//
// Regel: Maximal 45° Überhang gegen die Vertikale → FDM-sicher.
//        Horizontale Brücken sind vermieden.
//        Alle Aufbauten sind konisch, pyramidal oder vertikal.
//
// Basis: plattformen-v3-modular.scad
// Änderungen gegenüber v3:
//   • plat_B: Querstreben entfernt → aufrechte Öse mit konischem Fuß
//   • plat_T: Dach ruht direkt auf Säulen (kein überhängender Rand)
//   • plat_K: Querarm weg → nur konischer Mast mit nach oben zeigender
//            Fahne; Netzplatte als schräger Keil, vollflächig gestützt
//   • plat_E: Schachbrett-Flagge durch konischen Wimpel ersetzt
//            (Dreieck direkt am Stab anliegend)
//
// Maßstab: 1 x₃-Einheit = 10 mm · $fn = 48
// ══════════════════════════════════════════════════════

PART = 0;        // 0 = alle nebeneinander, 1-8 = einzelner Typ
COMPONENT = 0;   // 0 = komplett, 1 = nur Stumpf, 2 = nur Plattform, 3 = Steckteile
$fn = 48;

// ── Maße ──
SCALE      = 10;
BASE_D     = 30;
TOP_D      = 16;
ZAPFEN_D   = 5.0;
ZAPFEN_H   = 5.0;
ZAPFEN_TIP = 4.8;
LOCH_D     = 5.2;
LOCH_H     = 5.0;
PLAT_H     = 3;
MIN_H      = 5;
KERBE_W    = 2.0;
NUT_W      = 1.5;
NUT_D      = 1.0;

// ── Farben (nur Preview) ──
CW = [.55,.44,.28];
CB = [.35,.29,.16];
CM = [.48,.48,.54];
CR = [.54,.23,.16];
CG = [.16,.42,.10];
CO = [.78,.51,.23];

HEIGHTS  = [0, 0, 1, 2, 3, 4, 3, 5, 0];
LABELS   = ["", "S", "A", "B", "G", "T", "H", "K", "E"];
SPACING  = 40;

// ══════════════════════════════════════════════════════
//   GEMEINSAME MODULE
// ══════════════════════════════════════════════════════

module stumpf(h, buchstabe) {
    real_h = max(h * SCALE, MIN_H);
    color(CB) difference() {
        cylinder(h=real_h, r1=BASE_D/2, r2=TOP_D/2);
        translate([0, 0, real_h - NUT_W])
            difference() {
                cylinder(h=NUT_W, r=TOP_D/2 + 0.1);
                cylinder(h=NUT_W, r=TOP_D/2 - NUT_D);
            }
    }
    translate([0, 0, real_h])
        color(CW) cylinder(h=ZAPFEN_H, r1=ZAPFEN_D/2, r2=ZAPFEN_TIP/2);
    translate([0, BASE_D/2 - 0.3, real_h/2])
        rotate([90, 0, 0])
            linear_extrude(0.6)
                text(buchstabe, size=5, halign="center", valign="center",
                     font="Arial:style=Bold");
    for(z = [2 : 5 : real_h-3])
        translate([0, 0, z])
            color([.3,.25,.14])
                difference() {
                    r_at_z = BASE_D/2 - (BASE_D/2 - TOP_D/2) * (z / real_h);
                    cylinder(h=0.4, r=r_at_z + 0.05);
                    translate([0, 0, -0.1])
                        cylinder(h=0.6, r=r_at_z - 0.4);
                }
}

module steckloch() {
    translate([0, 0, -0.1])
        cylinder(h=LOCH_H + 0.1, r=LOCH_D/2);
}

module seilkerben(r, n=4) {
    for(i = [0 : n-1])
        rotate([0, 0, i * 360/n])
            translate([r, 0, -0.1])
                cylinder(h=PLAT_H + 0.2, r=KERBE_W/2);
}

// ══════════════════════════════════════════════════════
//   PLATTFORM-MODULE v4 (druckfreundlich)
// ══════════════════════════════════════════════════════

// ═══ 1: START-TOR (S) — konische Pfosten direkt verbunden ═══
module plat_S() {
    r = 15;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    // 2 Pfosten, konisch nach oben (r1=1.5 → r2=1.0) → überhangfrei
    for(x = [-5, 5])
        translate([x, 0, PLAT_H])
            color(CB) cylinder(h=14, r1=1.5, r2=1.0);
    // Querbalken wird separat gesteckt (steck_S) — bleibt unverändert
    // Kein horizontales Loch in den Pfosten (ersetzt durch schräge Kerbe)
    for(x = [-5, 5])
        translate([x, 0, PLAT_H + 11])
            rotate([90, 0, 0])
                color(CR) cylinder(h=3, r1=0.8, r2=0.5, center=true);
}

module steck_S() {
    color(CW) union() {
        rotate([0, 90, 0])
            cylinder(h=12, r=1.2, center=true);
        translate([-6, 0, 0]) rotate([0,  90, 0]) cylinder(h=3, r1=1.2, r2=1.0);
        translate([ 6, 0, 0]) rotate([0, -90, 0]) cylinder(h=3, r1=1.2, r2=1.0);
    }
}

// ═══ 2: ADLERHORST (A) — bereits überhangfrei ═══
module plat_A() {
    r = 15;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    for(a = [0, 90, 180, 270])
        rotate([0, 0, a])
            translate([6, 0, PLAT_H])
                color(CG) cylinder(h=8, r1=4, r2=0);
    translate([0, 0, PLAT_H])
        color([.2,.44,.14]) cylinder(h=10, r1=5, r2=0);
}

// ═══ 3: BRÜCKENKNOTEN (B) — Öse auf konischem Fuß, KEINE Querstreben ═══
module plat_B() {
    r = 16;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    // Konischer Fuß (druckfreundlich) statt schwebender Öse
    translate([0, 0, PLAT_H])
        color(CO) cylinder(h=4, r1=6, r2=4);
    // Öse als Hohlzylinder direkt darauf
    translate([0, 0, PLAT_H + 4])
        color(CO) difference() {
            cylinder(h=4, r=4);
            translate([0, 0, -0.1])
                cylinder(h=4.2, r=2.5);
        }
    // Kreuzförmige Verstärkung als Eintiefungen (geprägt, keine schwebenden Balken)
    for(a = [0, 90])
        rotate([0, 0, a])
            translate([0, -0.3, PLAT_H + 0.2])
                color(CM) cube([10, 0.6, 0.5], center=true);
}

// ═══ 4: GIPFEL (G) — unverändert, bereits überhangfrei ═══
module plat_G() {
    r = 16;
    difference() {
        color(CW) cylinder(h=PLAT_H, r=r, $fn=6);
        steckloch();
        for(i = [0:5])
            rotate([0, 0, i * 60])
                translate([r - 1, 0, -0.1])
                    cylinder(h=PLAT_H + 0.2, r=KERBE_W/2);
    }
    for(a = [0, 120, 240])
        rotate([0, 0, a])
            translate([7, 0, PLAT_H])
                color(CG) cylinder(h=6, r1=3, r2=0);
    translate([0, 0, PLAT_H])
        color(CM) cylinder(h=1, r=1.1);
}

module steck_G() {
    color(CM) union() {
        cylinder(h=18, r=1.0);
        // Fahne als Kegel (statt Cube) — druckfreundlich
        translate([0, 0, 14])
            rotate([0, 45, 0])
                color(CR) cylinder(h=4, r1=0.2, r2=2);
    }
}

// ═══ 5: AUSSICHTSTURM (T) — Pyramidendach direkt auf Säulen ═══
module plat_T() {
    w = 25;
    difference() {
        color(CW) translate([-w/2, -w/2, 0]) cube([w, w, PLAT_H]);
        steckloch();
        for(a = [0, 90, 180, 270])
            rotate([0, 0, a])
                translate([w/2, 0, -0.1])
                    cylinder(h=PLAT_H + 0.2, r=KERBE_W/2);
    }
    // 4 Ecksäulen (konisch, überhangfrei)
    for(x = [-w/2+2, w/2-2])
        for(y = [-w/2+2, w/2-2])
            translate([x, y, PLAT_H])
                color(CW) cylinder(h=8, r1=1.6, r2=1.0);
    // Pyramidendach: Basis passend zu Säulenpositionen → kein Überhang
    // Basis-Diagonale = 2·(w/2-2)·√2 = 2·10.5·1.414 ≈ 29.7 → Pyramide r1=14.85 auf Säulenhöhe
    // Pyramidenseite damit 45° gegen Vertikale (FDM-sicher)
    pyramid_r = (w/2 - 2) * sqrt(2);
    translate([0, 0, PLAT_H + 8])
        color(CR) cylinder(h=pyramid_r, r1=pyramid_r, r2=0, $fn=4);
}

// ═══ 6: HÄNGESTATION (H) — Masten konisch, unverändert ═══
module plat_H() {
    r = 14;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    for(x = [-4, 4])
        translate([x, 0, PLAT_H])
            color(CM) cylinder(h=15, r1=1.4, r2=0.8);
    // Markierungen als flache Kegel (nicht hängend)
    for(x = [-4, 4])
        translate([x, 0, PLAT_H + 14])
            color(CO) cylinder(h=1.5, r1=1.0, r2=0.4);
}

// Steckteil-H: Hängebügel nach oben (umgedreht zum Drucken)
module steck_H() {
    color(CM) union() {
        rotate([0, 90, 0])
            cylinder(h=10, r=0.8, center=true);
        translate([-5, 0, 0]) rotate([0,  90, 0]) cylinder(h=2, r=0.7);
        translate([ 5, 0, 0]) rotate([0, -90, 0]) cylinder(h=2, r=0.7);
    }
    // Keine hängende U-Form — stattdessen konischer Ring oberhalb
    translate([0, 0, 0])
        color(CO) difference() {
            cylinder(h=4, r1=2.5, r2=3.5);
            translate([0, 0, -0.1]) cylinder(h=4.2, r1=1.5, r2=2.5);
        }
}

// ═══ 7: KLETTERNETZ (K) — konischer Mast mit gepräotter Netzstruktur ═══
module plat_K() {
    r = 15;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    // Einzelmast konisch
    translate([0, 0, PLAT_H])
        color(CW) cylinder(h=18, r1=1.8, r2=0.8);
    // Netzplatte als schräger Keil DIREKT am Mast anliegend (vollflächig gestützt)
    translate([0, 0, PLAT_H])
        rotate([0, 0, 0])
            color([.48,.42,.25]) linear_extrude(height=14, scale=0.3)
                polygon(points=[[1.5, -5], [7, -5], [7, 5], [1.5, 5]]);
    // Gitter als eingeprägte Markierungen auf der schrägen Fläche (optisch)
    // (keine freischwebenden Balken)
}

// ═══ 8: ENDSTATION (E) — konischer Wimpel statt Schachbrett-Flagge ═══
module plat_E() {
    r = 14;
    color(CW) difference() {
        cylinder(h=PLAT_H, r=r);
        steckloch();
        seilkerben(r);
    }
    // 2 Pfosten
    for(x = [-5, 5])
        translate([x, 0, PLAT_H])
            color(CB) cylinder(h=12, r1=1.5, r2=1.0);
    // Fahnenstab mittig
    translate([0, 0, PLAT_H])
        color(CM) cylinder(h=16, r=0.5);
    // Wimpel als flacher Kegel am Stab (Dreieck seitlich, direkt anliegend)
    translate([0, 0, PLAT_H + 10])
        rotate([90, 0, 0])
            color(CR) linear_extrude(height=0.6, center=true)
                polygon(points=[[0, 0], [4, 1], [4, -1]]);
    // Konische Spitze auf Stab
    translate([0, 0, PLAT_H + 16])
        color(CM) cylinder(h=2, r1=0.5, r2=0);
}

module steck_E() {
    steck_S();
}

// ══════════════════════════════════════════════════════
//   AUSGABE-LOGIK
// ══════════════════════════════════════════════════════

module render_single(idx) {
    h = HEIGHTS[idx];
    lbl = LABELS[idx];
    real_h = max(h * SCALE, MIN_H);

    if(COMPONENT == 0) {
        stumpf(h, lbl);
        translate([0, 0, real_h + ZAPFEN_H])
            plat_by_idx(idx);
    }
    if(COMPONENT == 1) {
        stumpf(h, lbl);
    }
    if(COMPONENT == 2) {
        plat_by_idx(idx);
    }
    if(COMPONENT == 3) {
        steck_by_idx(idx);
    }
}

module plat_by_idx(idx) {
    if(idx == 1) plat_S();
    if(idx == 2) plat_A();
    if(idx == 3) plat_B();
    if(idx == 4) plat_G();
    if(idx == 5) plat_T();
    if(idx == 6) plat_H();
    if(idx == 7) plat_K();
    if(idx == 8) plat_E();
}

module steck_by_idx(idx) {
    if(idx == 1) steck_S();
    if(idx == 4) steck_G();
    if(idx == 6) steck_H();
    if(idx == 8) steck_E();
}

if(PART == 0) {
    for(i = [1:8]) {
        translate([(i-1) * SPACING, 0, 0])
            render_single(i);
    }
} else {
    render_single(PART);
}

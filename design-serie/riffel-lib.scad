// ══════════════════════════════════════════════════════
// RIFFEL — Design-System-Bibliothek
//
// Serie 3D-gedruckter Organizer (Bad, Dusche, Schreibtisch, Küche).
// Diese Datei enthält KEIN fertiges Objekt, nur die wiederverwendbaren
// Module der Serie. Jedes Objekt (becher.scad, seifenschale.scad …)
// bindet sie per  use <riffel-lib.scad>  ein und erbt damit den Look.
//
// Siehe KONZEPT.md, Abschnitt 1 (Designsprache) und 2 (Maßsystem).
//
// Einheiten: mm. Druck: aufrecht, supportfrei, Naht ins Rillental.
// ══════════════════════════════════════════════════════

// ── Serien-Konstanten (verbindlich, nicht pro Objekt ändern) ──
RIFFEL_P      = 4 * PI / 3;   // Teilung ≈ 4,189 mm  → ganzzahlige Rillen
RIFFEL_R      = 2.4;          // Rillenradius (Hohlkehle)
RIFFEL_T      = 1.2;          // Rillentiefe
RIFFEL_WALL   = 2.0;          // Mindest-Wandstärke im Rillental
SOCKEL_H      = 8.0;          // Höhe glattes Sockelband
SOCKEL_SET    = 0.8;          // Sockel-Rücksprung ggü. Rillenkamm
LIPPE_H       = 4.0;          // Höhe glatte Lippe oben
LIPPE_FAS     = 1.2;          // Fasen-/Rundungsmaß der Lippe
LIPPE_STUFEN  = 6;            // Stufen der Stadion-Lippenfase
BODEN         = 3.2;          // Bodendicke
FLANKE_SPIEL  = 0.25;         // Verzahnungs-Flankenspiel (Kombi-Module)

// Gesamt-Wandstärke Kamm→innen = WALL + T = 3,2 mm
RIFFEL_DW     = RIFFEL_WALL + RIFFEL_T;   // 3,2

$fn = 96;

// Rillenanzahl aus Umfang: n = round(Umfang / p)
function riffel_n(umfang) = round(umfang / RIFFEL_P);
// Cutter-Achse liegt (R - T) außerhalb der Kammfläche
RIFFEL_OFF    = RIFFEL_R - RIFFEL_T;      // 1,2

// ══════════════════════════════════════════════════════
//   1 · EIN-RILLE-CUTTER (vertikal, mit gerundetem Auslauf)
// ══════════════════════════════════════════════════════
// Vertikaler Halbkanal von z=zlo bis z=zhi, an beiden Enden durch
// eine Kugel rund auslaufend → kein harter Absatz an Sockel/Lippe.
module riffel_cut(zlo, zhi) {
    translate([0, 0, zlo]) sphere(RIFFEL_R);
    translate([0, 0, zlo]) cylinder(h = zhi - zlo, r = RIFFEL_R);
    translate([0, 0, zhi]) sphere(RIFFEL_R);
}

// ══════════════════════════════════════════════════════
//   2 · SIGNATUR — drei Kerben ins Sockelband (Rückseite −Y)
// ══════════════════════════════════════════════════════
// y_face = Außenmaß an der Rückseite (−Y). Drei horizontale Kerben
// 8 (breit) × 0,8 (hoch) × 0,4 (tief), vertikal um 1,6 mm gestapelt.
module signatur(y_face) {
    for (i = [-1, 0, 1])
        // y um +0,2 nach innen → 0,4 mm der 0,8-tiefen Box schneiden
        translate([0, -y_face + 0.2, SOCKEL_H / 2 + i * 1.6])
            cube([8, 0.8, 0.8], center = true);
}

// ══════════════════════════════════════════════════════
//   3 · RUNDKÖRPER — geriffelter Behälter (Becher, Dose, Stiftebecher)
// ══════════════════════════════════════════════════════
// D = Außen-Ø über Kämme, H = Gesamthöhe.
// hohl = true  → offener Behälter mit Boden BODEN.
// sig  = true  → Signaturkerben im Sockel.
module riffel_round(D, H, hohl = true, sig = true) {
    R  = D / 2;
    Ri = R - RIFFEL_DW;            // Innenradius
    n  = riffel_n(PI * D);         // Rillenanzahl (z.B. Ø56 → 42)
    zlo = SOCKEL_H + RIFFEL_R;     // Rillen-Auslauf über dem Sockel
    zhi = H - LIPPE_H - RIFFEL_R;  // Auslauf unter der Lippe

    difference() {
        union() {
            // Sockelband: glatt, um SOCKEL_SET zurückgesetzt
            cylinder(h = SOCKEL_H, r = R - SOCKEL_SET);
            // Hauptkörper bis Oberkante (Lippe entsteht oben automatisch,
            // weil dort keine Rillen geschnitten werden)
            translate([0, 0, SOCKEL_H - 0.01])
                cylinder(h = H - SOCKEL_H, r = R);
        }
        // Rillen rundum, nur im Mittelbereich
        for (i = [0 : n - 1])
            rotate([0, 0, i * 360 / n])
                translate([R + RIFFEL_OFF, 0, 0])
                    riffel_cut(zlo, zhi);
        // Lippe: 45°-Fase an der oberen Außenkante. Das abgezogene
        // Profil deckt alles oberhalb der 45°-Geraden (R-FAS,H)→(R,H-FAS)
        // ab und lässt damit eine saubere Fase stehen.
        rotate_extrude()
            polygon([[R - LIPPE_FAS, H],
                     [R,             H - LIPPE_FAS],
                     [R + 2,         H - LIPPE_FAS],
                     [R + 2,         H + 2],
                     [R - LIPPE_FAS, H + 2]]);
        // Innenraum
        if (hohl)
            translate([0, 0, BODEN])
                cylinder(h = H, r = Ri);
        if (sig) signatur(R - SOCKEL_SET);
    }
}

// ══════════════════════════════════════════════════════
//   4 · STADIONKÖRPER — geriffelter Behälter mit Stadion-Grundriss
// ══════════════════════════════════════════════════════
// L = Gesamtlänge, Wd = Breite (= 2·Eckradius). Stadion = zwei
// Halbkreise (R = Wd/2) verbunden durch gerade Seiten.
// sx = halbe Länge der geraden Seite.
function stadion_sx(L, Wd) = (L - Wd) / 2;
function stadion_perim(L, Wd) = 4 * stadion_sx(L, Wd) + 2 * PI * (Wd / 2);

// Punkt + Außennormale auf der KAMM-Kontur bei Bogenlänge s.
// Rückgabe [x, y, nx, ny].
function stadion_pt(s, sx, Rc) =
    let (L1 = 2 * sx, L2 = PI * Rc)
    (s < L1)
        ? [-sx + s, Rc, 0, 1]
    : (s < L1 + L2)
        ? let (a = 90 - (s - L1) / L2 * 180)
          [ sx + Rc * cos(a), Rc * sin(a), cos(a), sin(a) ]
    : (s < 2 * L1 + L2)
        ? [ sx - (s - L1 - L2), -Rc, 0, -1 ]
        : let (a = -90 - (s - 2 * L1 - L2) / L2 * 180)
          [ -sx + Rc * cos(a), Rc * sin(a), cos(a), sin(a) ];

module riffel_stadion(L, Wd, H, hohl = true, sig = true) {
    Rc  = Wd / 2;
    sx  = stadion_sx(L, Wd);
    per = stadion_perim(L, Wd);
    n   = riffel_n(per);
    zlo = SOCKEL_H + RIFFEL_R;
    zhi = H - LIPPE_H - RIFFEL_R;

    // 2D-Grundriss als Hülle zweier Kreise
    module grundriss(off = 0)
        hull() {
            translate([ sx, 0]) circle(Rc + off);
            translate([-sx, 0]) circle(Rc + off);
        }

    difference() {
        union() {
            linear_extrude(SOCKEL_H) grundriss(-SOCKEL_SET);
            translate([0, 0, SOCKEL_H - 0.01])
                linear_extrude(H - SOCKEL_H) grundriss(0);
        }
        // Rillen entlang der Kammkontur, Cutter um RIFFEL_OFF nach außen
        for (i = [0 : n - 1]) {
            p = stadion_pt(i * per / n, sx, Rc);
            translate([p[0] + p[2] * RIFFEL_OFF,
                       p[1] + p[3] * RIFFEL_OFF, 0])
                riffel_cut(zlo, zhi);
        }
        // Lippe: umlaufende 45°-Fase oben. Da ein gleichmäßiger Versatz
        // eines Stadions per linear_extrude(scale) verzerren würde, wird
        // die Fase als gestufter Offset-Stapel gebaut (für jede konvexe
        // Grundform exakt). LIPPE_STUFEN bestimmt die Feinheit.
        for (k = [0 : LIPPE_STUFEN - 1]) {
            zl = (k + 0.5) / LIPPE_STUFEN * LIPPE_FAS;   // Abtrag-Tiefe
            translate([0, 0, H - LIPPE_FAS + k / LIPPE_STUFEN * LIPPE_FAS])
                linear_extrude(LIPPE_FAS / LIPPE_STUFEN + 0.02)
                    difference() { grundriss(0.02); grundriss(-zl); }
        }
        // Innenraum
        if (hohl)
            translate([0, 0, BODEN])
                linear_extrude(H) grundriss(-RIFFEL_DW);
        if (sig) signatur(Rc - SOCKEL_SET);
    }
}

// ══════════════════════════════════════════════════════
//   5 · ABTROPFEINSATZ — herausnehmbare Rippenplatte
// ══════════════════════════════════════════════════════
// Liegt im Behälter, Spiel 0,4 mm umlaufend, mit Grifflasche 12×8.
// rippe_h = 2 mm hohe Querrippen, Teilung 8 mm; Wasser sammelt darunter.
EINSATZ_SPIEL = 0.4;
EINSATZ_RIPPE = 2.0;
EINSATZ_TEIL  = 8.0;
EINSATZ_PLATTE = 1.6;

module abtropf_rippen(bbox, h0) {
    // Querrippen über die Bounding-Box-Breite bbox=[bx,by]
    bx = bbox[0]; by = bbox[1];
    n = floor(by / EINSATZ_TEIL);
    for (j = [0 : n])
        translate([0, -by/2 + j * EINSATZ_TEIL, h0])
            cube([bx, 1.2, EINSATZ_RIPPE * 2], center = true);
}

module abtropf_round(D) {
    Ri = D/2 - RIFFEL_DW - EINSATZ_SPIEL;   // passt in den Innenraum
    difference() {
        union() {
            cylinder(h = EINSATZ_PLATTE, r = Ri);
            intersection() {
                abtropf_rippen([2*Ri, 2*Ri], EINSATZ_PLATTE);
                cylinder(h = EINSATZ_RIPPE * 2 + EINSATZ_PLATTE, r = Ri);
            }
            translate([0, 0, EINSATZ_PLATTE/2])
                cube([12, 8, EINSATZ_PLATTE], center = true);
        }
        // Wasserlöcher: Schlitze zwischen den Rippen. Mit 6-mm-Randsteg
        // (Schnitt mit eingerücktem Umriss) → Platte bleibt als Ring stabil.
        m = floor(2*Ri / EINSATZ_TEIL);
        intersection() {
            for (j = [0 : m])
                translate([0, -Ri + j * EINSATZ_TEIL + EINSATZ_TEIL/2, -0.1])
                    cube([2*Ri, EINSATZ_TEIL - 3.5, EINSATZ_PLATTE + 0.2], center = true);
            translate([0, 0, -0.2])
                cylinder(h = EINSATZ_PLATTE + 0.4, r = Ri - 6);
        }
    }
}

module abtropf_stadion(L, Wd) {
    Rc = Wd/2 - RIFFEL_DW - EINSATZ_SPIEL;
    sx = stadion_sx(L, Wd);
    module gr(off = 0) hull() {
        translate([ sx, 0]) circle(Rc + off);
        translate([-sx, 0]) circle(Rc + off);
    }
    difference() {
        union() {
            linear_extrude(EINSATZ_PLATTE) gr();
            intersection() {
                abtropf_rippen([2*(sx+Rc), 2*Rc], EINSATZ_PLATTE);
                linear_extrude(EINSATZ_RIPPE*2 + EINSATZ_PLATTE) gr();
            }
            translate([0, 0, EINSATZ_PLATTE/2])
                cube([12, 8, EINSATZ_PLATTE], center = true);
        }
        // Wasserlöcher mit 6-mm-Randsteg ringsum (Platte bleibt stabil)
        m = floor(2*Rc / EINSATZ_TEIL);
        intersection() {
            for (j = [0 : m])
                translate([0, -Rc + j * EINSATZ_TEIL + EINSATZ_TEIL/2, -0.1])
                    cube([2*(sx+Rc), EINSATZ_TEIL - 3.5, EINSATZ_PLATTE + 0.2], center = true);
            translate([0, 0, -0.2])
                linear_extrude(EINSATZ_PLATTE + 0.4) gr(-6);
        }
    }
}

// ══════════════════════════════════════════════════════
//   6 · VERZAHNUNGS-NEGATIV — Rippen, die in Rillen greifen
// ══════════════════════════════════════════════════════
// Für Kombi-Module (Tablett-Mulden, Clips, Tabletts). Erzeugt n
// Rippen über einen Bogen, die mit FLANKE_SPIEL in die Rillen eines
// Rund-Körpers (Ø=D) eingreifen. Als Phase-0-Prüfteil verwendet.
module riffel_negativ_arc(D, h, winkel = 90) {
    R = D / 2;
    n = riffel_n(PI * D);
    schritt = 360 / n;
    anz = floor(winkel / schritt);
    for (i = [0 : anz])
        rotate([0, 0, i * schritt])
            translate([R + RIFFEL_OFF - FLANKE_SPIEL, 0, 0])
                cylinder(h = h, r = RIFFEL_R - FLANKE_SPIEL);
}

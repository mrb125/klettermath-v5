# RIFFEL — Designserie (OpenSCAD)

Parametrische 3D-Druck-Serie mit durchgängiger Riffel-Designsprache.
Konzept, Maßsystem und Objektprogramm stehen in **[KONZEPT.md](KONZEPT.md)**.

## Dateien

| Datei | Inhalt |
|-------|--------|
| `riffel-lib.scad` | Design-System-Bibliothek (nur Module, kein Objekt) |
| `testring.scad` | Phase-0-Prüfteil: Testring + Verzahnungs-Clip |
| `becher.scad` | Becher / Stiftebecher Ø56 + Abtropfeinsatz |
| `seifenschale.scad` | Seifenschale 106×56 (Stadion) + Abtropfeinsatz |

## Öffnen / Rendern

[OpenSCAD](https://openscad.org/) installieren, dann z. B.:

```bash
openscad becher.scad            # GUI-Vorschau
openscad -o becher.stl becher.scad   # STL für den Slicer
```

Jede Objektdatei hat oben eine Variable `TEIL`:

- `TEIL = 0` — alle Teile nebeneinander (Vorschau)
- `TEIL = 1` — nur die Schale/der Körper (zum Drucken)
- `TEIL = 2` — nur den Abtropfeinsatz bzw. Clip (Kontrastfarbe)

In der GUI über *Customizer* umschaltbar, oder per CLI:
`openscad -D TEIL=1 -o becher-schale.stl becher.scad`.

## Rille einstellen

Die Riffelung ist frei einstellbar — global im Customizer-Block oben in
`riffel-lib.scad` (`RILLE_TIEFE`, `RILLE_RADIUS`, `RILLE_TEILUNG`) oder
pro Objekt als Parameter:

```scad
riffel_round(56, 96, t = 1.0, r = 2.2, p = 4.18879);  // t=Tiefe, r=Breite, p=Teilung
```

`testring.scad` mit `TEIL = 3` druckt vier Ringe mit Tiefen
0,8/1,0/1,2/1,5 mm nebeneinander — zum direkten Vergleich. Hinweis: Die
ganzzahlige Rillenzahl über die ganze Ø-Familie ergibt sich nur bei der
Standard-Teilung `4*PI/3`; andere Teilungen werden je Objekt einzeln auf
eine ganze Zahl gerundet.

## Farbe

Kommt allein übers **Filament** — die Modelle setzen kein `color()`.
Jede Farbwahl funktioniert; einheitlich wirkt es, wenn Schalen in einer
und Einsätze/Clips in einer zweiten Filamentfarbe gedruckt werden.

## Druckeinstellungen (Kurzfassung)

- Aufrecht drucken, **ohne Supports** (Rillen stehen vertikal).
- Naht ins Rillental legen (Slicer: Naht „hinten/ausgerichtet").
- 0,4er Düse · 0,2 mm Schichten · 3 Perimeter · 4 Boden-/Deckschichten.
- Bad & Dusche: **PETG matt**; Schreibtisch/Küche: PLA matt.
- Schale in Serienfarbe, Abtropfeinsatz/Clip in Kontrastfarbe.

## Reihenfolge

1. **Erst** `testring.scad` (`TEIL=0`) drucken — bestätigt Optik der
   Riffelung und ob der Clip mit 0,25 mm Flankenspiel sauber greift.
2. Stimmt das, sind `becher.scad` und `seifenschale.scad` dran.
3. Maße/Konstanten zentral in `riffel-lib.scad` (oben) anpassbar — alle
   Objekte erben die Änderung.

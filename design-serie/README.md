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

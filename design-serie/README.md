# RIFFEL — Designserie (OpenSCAD)

Parametrische 3D-Druck-Serie mit durchgängiger Riffel-Designsprache.
Konzept, Maßsystem und Objektprogramm stehen in **[KONZEPT.md](KONZEPT.md)**.

## Dateien

| Datei | Inhalt |
|-------|--------|
| `konfigurator.html` | **Web-Konfigurator**: Parameter live einstellen, 3D-Vorschau, STL-Export — ganz ohne OpenSCAD |
| `riffel-lib.scad` | Design-System-Bibliothek (nur Module, kein Objekt) |
| `testring.scad` | Phase-0-Prüfteil: Testring + Verzahnungs-Clip |
| `becher.scad` | Becher / Stiftebecher Ø56 + Abtropfeinsatz |
| `seifenschale.scad` | Seifenschale 106×56 (Stadion) + Abtropfeinsatz |

## Schnellster Weg: der Web-Konfigurator

`konfigurator.html` einfach im Browser öffnen (Doppelklick) — kein OpenSCAD,
keine Lib-Datei, keine Installation nötig. Vorlage wählen oder Maße per
Schieberegler einstellen, das Objekt dreht sich live in 3D, dann
**„STL herunterladen"** → fertige Datei für den Slicer.

> Three.js liegt lokal im `vendor/`-Ordner mit → die Seite läuft komplett
> **offline**, ganz ohne Internet. (Nur falls die HTML allein, ohne
> `vendor/`, weiterkopiert wird, greift ein CDN-Fallback.)
> Die Vorschau rechnet gröber, der Export immer in Druckqualität.

## Der OpenSCAD-Weg (parametrisch, voller Funktionsumfang)

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

## Verzahnungs-Spielmaß einstellen

Das Flankenspiel der Kombi-Module steht in `FLANKE_SPIEL`
(`riffel-lib.scad`) und ist an `riffel_negativ_arc(..., spiel = …)` pro
Objekt überschreibbar. `testring.scad` mit `TEIL = 4` druckt drei Clips
mit 0,15/0,25/0,35 mm (Wert ist ins Band graviert): zusammen mit einem
Ring aus `TEIL = 1` drucken, jeden aufstecken und den strammsten mit
sauberem Sitz als `FLANKE_SPIEL` übernehmen.

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

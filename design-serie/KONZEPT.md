# Serie „RIFFEL" — Design-Briefing & Maßsystem

3D-gedruckte Organizer-Serie für Bad, Dusche, Schreibtisch und Küche.
Alle Objekte freistehend, alle ohne Supports druckbar, alle sofort als
Teil der Serie erkennbar.

> **Arbeitstitel:** RIFFEL (Alternativen: LAMELLE, KANNELÜR, WELLE).
> Status: Konzeptphase — noch kein CAD.

---

## 1. Designsprache: Das Riffel-Prinzip

Das Wiedererkennungsmerkmal der Serie sind **vertikale, konkave Rillen**
(Kanneluren) auf allen Außenflächen — wie bei skandinavischer Keramik.
Nebeneffekt beim FDM-Druck: Die Rillen kaschieren Layerlinien und die
Naht fast vollständig; die Objekte wirken wie gegossen.

Fünf feste Gestaltungselemente, die **jedes** Objekt trägt:

| # | Element | Definition |
|---|---------|-----------|
| 1 | **Riffelung** | Vertikale konkave Rillen, Teilung p, über die gesamte Mantelfläche |
| 2 | **Sockel** | Unten 8 mm glattes Band, 0,8 mm gegenüber den Rillenkämmen zurückgesetzt → Objekt wirkt „schwebend" |
| 3 | **Lippe** | Oben 4 mm glatter Rand mit 1,2 mm Rundung — angenehm zu greifen, sauberer Abschluss |
| 4 | **Grundformen** | Nur Kreis und Rundrechteck mit Eckradien aus der Radienfamilie (R20/R28/R36/R44) — keine scharfen Ecken |
| 5 | **Signatur** | Drei kurze horizontale Kerben (je 8 × 0,8 × 0,4 mm) ins Sockelband geprägt, mittig auf der Rückseite |

### Riffel-Geometrie (verbindlich für alle Objekte)

```
Teilung      p = 4π/3 ≈ 4,19 mm   (konstant über die ganze Serie!)
Rillenradius r = 2,4 mm            (konkaver Hohlkehlen-Schnitt)
Rillentiefe  t = 1,2 mm
Wandstärke   ≥ 2,0 mm im Rillental (Außenkontur = Innen + 3,2 mm)
```

**Warum p = 4π/3?** Bei Durchmesser-Schritten von 16 mm wächst der
Umfang um exakt 12 Rillen. Damit hat jeder Durchmesser der Familie eine
ganzzahlige Rillenanzahl bei identischer Teilung — die Serie sieht von
klein bis groß absolut einheitlich aus:

| Außen-Ø | Rillenanzahl |
|---------|--------------|
| 40 mm   | 30 |
| 56 mm   | 42 |
| 72 mm   | 54 |
| 88 mm   | 66 |

**Regel für Rundrechtecke:** Eckradien aus der Familie (R = Ø/2), gerade
Seiten immer ein ganzzahliges Vielfaches von p. Dadurch läuft die
Riffelung nahtlos um die Ecken und der Gesamtumfang bleibt ganzzahlig.

---

## 2. Maßsystem

- **Höhenraster:** 8 mm. Alle Objekthöhen = n × 8 mm (24, 40, 64, 80, 96, 120 …)
- **Durchmesserfamilie:** Ø 40 / 56 / 72 / 88 mm (16-mm-Schritte)
- **Standard-Geraden** für Rundrechtecke: 8p ≈ 33,5 mm · 12p ≈ 50,3 mm · 24p ≈ 100,5 mm
- **Bodendicke:** 3,2 mm einheitlich

### Nass-System (Bad & Dusche)

Da alles freistehend ist, gibt es **keine Durchgangslöcher** im Boden
(außer Dusch-Objekten) — Wasser würde sonst auf die Ablage laufen.
Stattdessen ein zweiteiliges Prinzip, das selbst zum Serienelement wird:

- **Außenschale:** geriffelt, dicht.
- **Abtropfeinsatz:** herausnehmbare glatte Platte mit Querrippen
  (Rippen 2 mm hoch, Teilung 8 mm) und 2° Gefälle zur Mitte. Nasses
  Zeug liegt auf den Rippen, Wasser sammelt sich darunter, Einsatz wird
  zum Ausgießen einfach herausgenommen.
- Einsatz-Spielmaß: 0,4 mm umlaufend; Grifflasche 12 × 8 mm.

### Riffel-Verzahnung (Kombi-Prinzip)

Weil die Teilung p serienweit konstant ist, ist die Riffelung selbst die
Verbindungs-Schnittstelle: **Kamm greift in Rille.** Zwei geriffelte
Flächen, die sich berühren, verzahnen sich formschlüssig — rutschfest
und ohne sichtbare Verbinder. Daraus folgen drei verbindliche Regeln:

1. **Negativ-Profil:** Aufnahmen (Tablett-Mulden, Clips) tragen das
   exakte Riffel-Negativ (Rippenradius 2,4 mm, Tiefe 1,2 mm) plus
   0,25 mm Flankenspiel.
2. **Andock-Geraden:** Die geraden Seiten aller Rundrechtecke liegen im
   p-Raster → zwei Objekte verzahnen sich Seite an Seite zu einer
   durchgehenden Einheit (z. B. zwei Organizer in der Schublade).
3. **Stapel-Schnittstelle:** Stapelbare Objekte nutzen die 4-mm-Lippe
   als Schulter: oben 6 mm hoher Stülprand (Außen-Ø = Innen-Ø − 0,4 mm),
   unten passende Aufnahme im Boden.

---

## 3. Objektprogramm

Benennung: `RIFFEL <Name> <Ø oder L×B>/<H>`. Alle Maße außen, in mm.

### Welle 1 — Bad-Basics

| Objekt | Grundform | Maße | Besonderheit |
|--------|-----------|------|--------------|
| **Becher** (Zahnbürsten) | Kreis Ø56 | Ø56 / H96 | Mit Abtropfeinsatz rund |
| **Tubenstand** | Rundrechteck R20 | 141 × 40 / H64 | Deckplatte mit 3 konischen Schlüsselloch-Schlitzen (8→24 mm), Tuben hängen kopfüber → Inhalt läuft zur Kappe |
| **Seifenschale** | Rundrechteck R28 | 106 × 56 / H24 | Mit Abtropfeinsatz |
| **Rasierstand** | Kreis Ø40 | Ø40 / H64 | Seitliche Gabelaussparung (22 mm breit) für den Griff, Kopf liegt auf der Lippe auf |

### Welle 2 — Bad-Organizer groß

| Objekt | Grundform | Maße | Besonderheit |
|--------|-----------|------|--------------|
| **Organizer L** | Rundrechteck R28 | 157 × 90 / H40 | 2 glatte Steckwände (Nut im Boden, 3 Raster-Positionen) → 1–3 Kammern |
| **Dose mit Deckel** (Wattestäbchen) | Kreis Ø72 | Ø72 / H80 | Stülpdeckel, glatt mit geriffelter Griffzone Ø40 obenauf — Negativ-Zitat der Serie |
| **Pad-Spender** | Kreis Ø88 | Ø88 / H120 | Entnahmeöffnung unten 70 × 30 mm (R8), Pads rutschen nach |
| **Haargummi-Turm** | Kreis Ø88 (Teller) | Ø88 / H120 | Geriffelter Sockelteller H24 + glatter Kegelstumpf Ø36→Ø24 |

### Welle 3 — Dusche (fürs Duschregal, freistehend)

| Objekt | Grundform | Maße | Besonderheit |
|--------|-----------|------|--------------|
| **Abtropfständer** | Kreis Ø88 | Ø88 / H104 | Flaschen kopfüber: Sammelmulde im Sockel (H24), zentraler Trichter Ø45, 3 konische Stützrippen — letzte Reste laufen zur Öffnung |
| **Dusch-Caddy** | Rundrechteck R28 | 157 × 90 / H64 | Wie Organizer L, aber mit Bodenschlitzen (hier ok — steht in der Dusche) und Grifföffnung 80 × 25 mm an beiden Stirnseiten |

### Welle 4 — Schreibtisch & Küche (Serien-Streckung)

| Objekt | Grundform | Maße | Besonderheit |
|--------|-----------|------|--------------|
| **Stiftebecher** | Kreis Ø56 | Ø56 / H96 | = Becher ohne Einsatz (reine Variante, kein neues Teil) |
| **Schale flach** (Catch-all) | Rundrechteck R28 | 106 × 90 / H24 | Schlüssel, Münzen, Kabel |
| **Schwammhalter** | Rundrechteck R28 | 106 × 56 / H40 | = Seifenschale mit höherem Rand + Einsatz |

### Welle 5 — Kombi-Module (verbinden Bestehendes)

| Objekt | Grundform | Maße | Besonderheit |
|--------|-----------|------|--------------|
| **Basis-Tablett S** | Rundrechteck R28 | 157 × 90 / H24 | 4 mm tiefe Mulden im 8-mm-Raster mit Riffel-Negativ: 1× Ø56 + 1× Ø72 + 1× Ø40 — Becher, Dose und Rasierstand docken rutschfest an |
| **Basis-Tablett L** | Rundrechteck R28 | 207 × 106 / H24 | Wie S, zusätzlich Ø88-Mulde + freies Ablagefeld 50 × 90 mit Abtropfrippen |
| **Stapeldose** | Kreis Ø72 | Ø72 / H64 je Modul | Stülprand oben (6 mm, Ø −0,4), Aufnahme im Boden → beliebig turmbar; nur der oberste Deckel (H16) wird gebraucht. 3er-Turm = H208 |
| **Verkettungs-Clip** | Brückenstück | 13 × 12 / H16 | Beidseitig Riffel-Negativ über 3 Rillen (3p ≈ 12,6 mm); Varianten Ø56↔Ø56 und Ø56↔Ø72 — koppelt Becher/Dosen zum Cluster, sieht aus wie aus einem Guss |
| **Etagere** | Kombi | Fuß 106 × 90, Gesamt-H ≈ 168 | Schale flach unten + Säule Ø16/H120 mit Zapfen Ø8 (Steckprinzip wie KletterMath-Plattformen) + Ø88-Schale H24 oben |

### Welle 6 — Ideenspeicher (Streckung, noch ohne Priorität)

| Objekt | Maße (Vorschlag) | Notiz |
|--------|------------------|-------|
| **Übertopf + Untersetzer** | Ø104 / H96 | Erweitert die Ø-Familie um eine Stufe (78 Rillen); Untersetzer = Abtropfeinsatz-Prinzip als Teller Ø112 |
| **Teelicht-/LED-Votiv** | Ø56 / H64 | Transluzentes PETG — Rillen erzeugen vertikales Lichtspiel; Schmuckstück der Serie |
| **Kopfhörer-Ständer** | Teller Ø88 + Säule Ø40 / H192 | Konstruktion = Haargummi-Turm, oben 45°-Bügelarme (supportfrei) |
| **Handy-Ständer** | 80 × 70 / H64 | Geriffelter Keil, Auflage 65°, Ladekabel-Schlitz im Rillental |
| **Kabelbox** | 157 × 90 / H64 + Deckel H16 | = Organizer L mit Stülpdeckel; Kabelschlitze 8 × 12 mm in Rillentälern — verschwinden optisch in der Riffelung |
| **Teebeutel-/Pad-Spender Küche** | Ø88 / H120 | = Pad-Spender aus Welle 2, reine Variante |
| **Untersetzer-Set** | 4× Ø88 / H8 + Ständer Ø96 / H56 | Scheiben mit geriffelter Kante, gestapelt im eigenen Köcher |

Bewusste Wiederverwendung: Becher/Stiftebecher, Seifenschale/Schwammhalter,
Organizer/Caddy/Kabelbox und Pad-Spender/Küchen-Spender teilen sich die
Geometrie — weniger Konstruktionsaufwand, mehr Serienwirkung.

---

## 4. Druckvorgaben

- **Orientierung:** Immer aufrecht — die Rillen stehen vertikal und
  drucken dadurch perfekt ohne Supports; gleichzeitig verschwinden
  Layerlinien optisch.
- **Naht:** In ein Rillental legen (Slicer: Naht „hinten/ausgerichtet") —
  praktisch unsichtbar.
- **Überhänge:** Max. 45° (Trichter, Konen, Fasen); Entnahmeöffnungen
  als Bogen oder mit 45°-Dach. Keine horizontalen Brücken > 20 mm.
- **Material:** Bad & Dusche **PETG matt** (feuchtraum- und duschwarm-fest),
  Schreibtisch/Küche auch PLA matt. Matte Filamente verstärken den
  Keramik-Look deutlich.
- **Profil:** 0,4er Düse, 0,2 mm Schichten, 3 Perimeter, 4 Boden-/Deckschichten.
- **Farbkonzept:** Eine Serienfarbe für alle Schalen (z. B. Warmweiß oder
  Salbeigrün), Abtropfeinsätze und Steckwände einheitlich in einer
  Kontrastfarbe (z. B. Anthrazit) — zweites Wiedererkennungsmerkmal.

---

## 5. Geplante OpenSCAD-Architektur (Phase 1+)

```
design-serie/
├── KONZEPT.md            ← dieses Dokument
├── README.md             ← Kurzanleitung zu den .scad-Dateien
├── riffel-lib.scad       ← Design-System (Module, siehe unten)  ✓ Phase 1
├── testring.scad         ← Phase-0-Prüfteil: Ring + Verzahnungs-Clip  ✓
├── becher.scad           ← Pilot: Becher/Stiftebecher Ø56  ✓
├── seifenschale.scad     ← Pilot: Stadion 106×56  ✓
└── …                     ← weitere Objekte je eine Datei
```

`riffel-lib.scad` stellt die Serien-Module bereit, aus denen sich jedes
Objekt zusammensetzt:

| Modul | Zweck |
|-------|-------|
| `riffel_round(D, H)` | Geriffelter Rundbehälter (Becher, Dose, Stiftebecher) |
| `riffel_stadion(L, Wd, H)` | Geriffelter Behälter mit Stadion-Grundriss |
| `signatur(...)` | Drei Kerben ins Sockelband |
| `abtropf_round/stadion(...)` | Herausnehmbarer Abtropfeinsatz mit Rippen |
| `riffel_negativ_arc(D, h)` | Verzahnungs-Negativ für Kombi-Module/Clip |

Beide Körper-Module bauen Sockel (zurückgesetzt) + geriffelten Mantel +
Lippe (Fase) + optionale Signatur aus den Serien-Konstanten oben in der
Datei. Neue Objekte erben den Look automatisch, indem sie nur diese
Module aufrufen.

---

## 6. Roadmap

| Phase | Inhalt | Ziel |
|-------|--------|------|
| **0 — Riffel-Test** | `testring.scad` (Ring Ø56/H24 + Verzahnungs-Clip) | Teilung, Rillentiefe, Naht, Material & Flankenspiel validieren — **CAD fertig, Druck offen** |
| **1 — Pilot** | `riffel-lib.scad` + `becher.scad` + `seifenschale.scad` | Design-System im CAD bewiesen ✓ — Einsatz-Spielmaß am Druck testen |
| **2 — Bad-Basics** | Tubenstand, Rasierstand | Welle 1 komplett |
| **3 — Organizer** | Organizer L, Dose, Pad-Spender, Haargummi-Turm | Welle 2 |
| **4 — Dusche & Streckung** | Abtropfständer, Caddy, Schreibtisch-Varianten | Wellen 1–4 komplett |
| **5 — Kombi-Module** | Basis-Tablett S, Stapeldose, Verkettungs-Clip | Kombinierbarkeit sichtbar machen — Tablett L und Etagere danach |
| **6 — Ideenspeicher** | Nach Bedarf aus Welle 6 ziehen | Serie lebt weiter |

**Offene Entscheidungen für Phase 0/1:**
1. Serienfarbe + Kontrastfarbe festlegen
2. Serienname endgültig wählen (→ Signatur ggf. als Monogramm statt drei Kerben)
3. Rillentiefe 1,2 mm am Testring bestätigen oder auf 1,0 mm reduzieren
   (Abwägung: Tiefe = stärkerer Look, flacher = leichter zu reinigen)
4. Verzahnungs-Spielmaß validieren: Zum Testring (Phase 0) gehört ein
   Gegenstück mit Riffel-Negativ — Flankenspiel 0,25 mm bestätigen oder
   auf 0,15/0,35 mm korrigieren (entscheidet über alle Kombi-Module)

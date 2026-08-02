# Ausfüllhilfe — eine Seite, 30 Sekunden

Für Lehrkräfte. Die vollständigen Regeln stehen in der [Spezifikation](SPEZIFIKATION.md);
diese Seite reicht für den Alltag.

---

## In vier Schritten

**1 · Kategorien durchgehen.** Für jede: Wo kam generative KI ins Spiel?

**2 · Je Kategorie eine Stufe vergeben** — zwei Fragen genügen:

```
Generative KI eingesetzt?                       nein → 0
                                                 ja  ↓
Steht KI-Wortlaut / KI-Bild im Material?        nein → 1
                                                 ja  ↓
Substanziell verändert (mehr als Korrektur)?     ja  → 2
                                                nein → 3
```

**3 · Gesamtstufe = die höchste Einzelstufe.** Nicht mitteln.

**4 · Name und Datum eintragen.** Immer, auch bei 0/3.

---

## Die Kategorien

**Kern — überall gleich:**

| | umfasst |
|---|---|
| **Text/Aufgaben** | Aufgabenstellungen, Erklärtexte, Kontexte, Arbeitsaufträge |
| **Bild/Grafik** | Illustrationen, Fotos, Diagramme, Schaubilder |
| **Audio/Video** | Vertonung, Erklärvideos, Podcasts, Avatare |
| **Lösungen** | Musterlösungen, Erwartungshorizont, Lösungswege |
| **Bewertung** | Bewertungsraster, Niveauzuordnung, Kompetenzeinschätzung |

**Profil — höchstens zwei, von der Schule oder Fachschaft festgelegt:**
Daten/Kontexte · Feedback · Sprache · Code/Interaktiv · Didaktik/Aufbau

Nicht vorhandene Kategorie → **weglassen**. Ein Blatt ohne Bilder bekommt keine Bildangabe,
ein Arbeitsblatt ohne Ton keine Audio-Angabe. `0` heißt „geprüft, ohne KI"; weglassen heißt
„gibt es hier nicht". In der Praxis füllst du selten mehr als drei Zeilen aus.

**Lösungen oder Bewertung?** Die Musterlösung sagt, *was* richtig ist — die Bewertung sagt,
*wie viel es zählt*. Ein Erwartungshorizont mit Punkteverteilung gehört zu beidem: Inhalt
unter Lösungen, Punkteschlüssel unter Bewertung.

---

## Zählt nicht als KI — bleibt Stufe 0

- Rechtschreib- und Grammatikprüfung
- Suchmaschinen, Bibliothekskataloge, OCR
- Übersetzungsspeicher, regelbasierte Übersetzung
- **Aufgabengeneratoren, die Zahlen oder Varianten nach festen Regeln erzeugen**

Maßgeblich ist nicht, ob ein Computer beteiligt war, sondern ob ein **generatives Modell
Inhalte hervorgebracht** hat.

---

## Häufige Fälle

| Was du getan hast | Stufe |
|---|---|
| KI nach Ideen für einen Aufgabenkontext gefragt, dann selbst geschrieben | 1 |
| KI um eine Gliederung gebeten, Inhalte selbst verfasst | 1 |
| Eigenen Text von KI umformulieren lassen, Ergebnis übernommen | 2 |
| KI-Entwurf einer Textaufgabe, Zahlen und Kontext angepasst, sprachlich überarbeitet | 2 |
| KI-Bild ohne Nachbearbeitung eingefügt | 3 |
| KI-Musterlösung geprüft, für richtig befunden, unverändert übernommen | 3 |

**Die letzte Zeile ist die, bei der sich die meisten vertun: Prüfen ist kein Verändern.**
Eine geprüfte, aber unveränderte KI-Ausgabe bleibt Stufe 3. Deine Prüfung steht in der
Freigabezeile — sie senkt die Stufe nicht.

**Im Zweifel die höhere Stufe.** Zu hoch angeben kostet nichts. Zu niedrig angeben
untergräbt das ganze System.

---

## Zwei Sachen, die du nicht übersehen darfst

**Bei `Bild/Grafik` oder `Audio/Video` auf 3** beantworte zusätzlich diese Frage:

> Könnte jemand das für echt halten — für eine Fotografie, eine reale Stimme, eine reale Person?

Wenn ja, kann die Kennzeichnungspflicht nach Art. 50 EU AI Act greifen (Deepfake-Regel).
Faustformel aus dem EU-Verhaltenskodex: eine Sphinx über dem Eiffelturm — nein. Das
fotorealistische Porträt einer Person, die es nicht gibt — ja. Für synthetische Stimmen und
KI-Avatare gilt dasselbe.

Halte die Antwort im [Prüfprotokoll](SPEZIFIKATION.md#12-prüfprotokoll) fest.

**Bei `Bewertung` auf 2 oder 3** halte kurz inne. Ein KI-entworfenes Bewertungsraster, das du
prüfst und anwendest, ist unproblematisch. Eine KI, die **Schülerarbeiten selbst bewertet**,
ist etwas anderes — der AI Act stuft solche Systeme als Hochrisiko ein. Die Kategorie ist
dazu da, dass dieser Schritt eine bewusste Entscheidung bleibt.

---

## So sieht es aus

```
KI-Transparenz 3/3 · im Wesentlichen KI-erzeugt, freigegeben
Text/Aufgaben 2/3, Bild/Grafik 3/3, Lösungen 0/3, Bewertung 1/3, Daten/Kontexte 1/3
Geprüft und freigegeben: S. Blankenagel, 02.08.2026
```

Als Kurzcode für Dateinamen und Datenbanken:

```
ktx:3|txt:2|bld:3|loe:0|bew:1|dat:1
```

Grafik erzeugen:

```bash
node ki-badge.mjs "txt:2|bld:3|loe:0|bew:1|dat:1" \
     --name="S. Blankenagel" --datum=02.08.2026 > badge.svg
```

---

## Drei Missverständnisse

**„Drei Sterne sind schlecht."** Nein. Die Sterne zählen KI-Anteil, sie bewerten nicht.
Ein vollständig KI-erzeugtes Übungsblatt kann exzellent sein, ein handgeschriebenes mies.

**„Dann schreibe ich lieber alles selbst."** Auch nicht. Das Badge soll KI-Einsatz sichtbar
machen, nicht verhindern.

**„Das prüft ja ohnehin niemand."** Stimmt. Es ist eine Selbstauskunft — wie die
Quellenangabe unter einem Zitat. Sie funktioniert, weil man sie ernst nimmt, nicht weil
jemand kontrolliert.

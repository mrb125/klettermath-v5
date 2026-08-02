# KI-Transparenz-Badge

Kennzeichnungssystem, mit dem Lehrkräfte den KI-Anteil an selbst erstelltem
Unterrichtsmaterial ausweisen. Zwei Dimensionen: **Kategorie** (wo) × **Sterne** (wie viel).

Die Kategorien folgen den **Schritten der Unterrichtsvorbereitung** und sind fachunspezifisch:
`rec` Recherche · `pla` Planung · `erk` Erklärung · `auf` Aufgaben · `dif` Differenzierung ·
`prf` Überprüfung. Dazu die Zusatzangabe `real` für realistisch wirkende KI-Darstellungen —
Ja/Nein, ohne Stufe, außerhalb der Gesamtwertung.

- **[AUSFUELLHILFE.md](AUSFUELLHILFE.md)** — eine Seite für den Alltag, 30 Sekunden
- **[SPEZIFIKATION.md](SPEZIFIKATION.md)** — Skala, Kategorien, Entscheidungsregeln, Rechtsbezug
- **[vorschau.html](vorschau.html)** — alle Darstellungsvarianten im Browser
- `assets/` — vorgenerierte SVGs, Stylesheet, Text- und HTML-Beispiel
- `ki-badge.mjs` — Generator · `ki-badge.test.mjs` — Tests

## Verwendung

```bash
# Beispielsatz nach assets/ schreiben
node ki-badge.mjs

# Einzelnes Badge auf stdout
node ki-badge.mjs "rec:1|erk:2|auf:2|dif:3|prf:0|real:1" \
     --variante=voll --name="S. Blankenagel" --datum=02.08.2026 > badge.svg

node --test          # 15 Tests
```

Varianten: `voll` (Fußzeile A4), `kompakt` (einzeilig), `mini` (nur Gesamtstufe),
`text` (Word, LaTeX, E-Mail), `html` (Lernplattform).

Als Modul:

```js
import { parseCode, badgeVoll, badgeHTML, badgeCSS, altText } from './ki-badge.mjs';

const daten = parseCode('rec:1|erk:2|auf:2|real:1');   // → { ktx: 2, rec: 1, erk: 2, auf: 2, real: 1 }
const svg   = badgeVoll(daten, { name: 'S. Blankenagel', datum: '02.08.2026' });
```

Für die Einbettung in eine Lernplattform: `badgeCSS()` einmal ins Dokument, dann
`badgeHTML(daten, opts)` je Material. Die Komponente erbt Farbe und Schriftart und
skaliert mit der Schriftgröße.

Die Gesamtstufe `ktx` wird immer als **Maximum** der Kategorien berechnet, nie als
Durchschnitt — ein im Kurzcode mitgegebener `ktx`-Wert wird ignoriert.

## Weitergabe

Keine Standardlizenz, vier Regeln in eigenen Worten
(→ [Spezifikation 14](SPEZIFIKATION.md#14-weitergabe-und-anpassung)): frei verwendbar und
anpassbar; die Bedeutung der Stufen 0–3 und die Maximum-Regel bleiben unverändert; kein
Gütesiegel; wer die Stufen doch ändert, gibt dem Ergebnis einen eigenen Namen.

## Status

Entwurf v0.1, nicht erprobt. Es ist unbekannt, wie Lernende und Eltern auf das Badge
reagieren — mehrere Studien zeigen, dass ein „KI-generiert"-Label die wahrgenommene
Genauigkeit senkt. Vor dem Rollout das Erprobungsdesign aus
[Spezifikation 13](SPEZIFIKATION.md#13-erprobung-vor-dem-rollout) durchlaufen.

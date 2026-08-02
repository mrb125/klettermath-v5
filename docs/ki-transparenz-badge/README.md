# KI-Transparenz-Badge

Kennzeichnungssystem, mit dem Lehrkräfte den KI-Anteil an selbst erstelltem
Unterrichtsmaterial ausweisen. Zwei Dimensionen: **Kategorie** (wo) × **Sterne** (wie viel).

- **[SPEZIFIKATION.md](SPEZIFIKATION.md)** — Skala, Kategorien, Entscheidungsregeln, Rechtsbezug
- **[vorschau.html](vorschau.html)** — alle Darstellungsvarianten im Browser
- `assets/` — vorgenerierte SVGs
- `ki-badge.mjs` — Generator

## Verwendung

```bash
# Beispielsatz nach assets/ schreiben
node ki-badge.mjs

# Einzelnes Badge auf stdout
node ki-badge.mjs "txt:2|bld:3|did:1|loe:0" \
     --variante=voll --name="S. Blankenagel" --datum=02.08.2026 > badge.svg
```

Varianten: `voll` (Fußzeile A4), `kompakt` (einzeilig), `mini` (nur Gesamtstufe).

Als Modul:

```js
import { parseCode, badgeVoll, altText } from './ki-badge.mjs';

const daten = parseCode('txt:2|bld:3|did:1|loe:0');   // → { ktx: 3, txt: 2, ... }
const svg   = badgeVoll(daten, { name: 'S. Blankenagel', datum: '02.08.2026' });
```

Die Gesamtstufe `ktx` wird immer als **Maximum** der Kategorien berechnet, nie als
Durchschnitt — ein im Kurzcode mitgegebener `ktx`-Wert wird ignoriert.

## Status

Entwurf v0.1. Offene Punkte in [SPEZIFIKATION.md](SPEZIFIKATION.md#10-offene-punkte) —
insbesondere fehlt jede Erprobung mit Lernenden und Eltern.

#!/usr/bin/env node
/**
 * KI-Transparenz-Badge – SVG-Generator
 *
 * Erzeugt Badges nach docs/ki-transparenz-badge/SPEZIFIKATION.md
 *
 *   node ki-badge.mjs "ktx:3|txt:2|bld:3|loe:0|bew:1|dat:1" \
 *        --variante=voll --name="S. Blankenagel" --datum=02.08.2026
 *
 * Varianten: voll | kompakt | mini | text | html
 * Ohne Argumente: schreibt den Beispielsatz nach ./assets/
 */

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HIER = dirname(fileURLToPath(import.meta.url));

export const MAX = 3;

/** Kern — überall gleich, macht Materialien vergleichbar (Spezifikation 4.1). */
export const KERN = {
  txt: 'Text/Aufgaben',
  bld: 'Bild/Grafik',
  med: 'Audio/Video',
  loe: 'Lösungen',
  bew: 'Bewertung',
};

/** Profil — je Fach oder Einrichtung frei wählbar, höchstens MAX_PROFIL (4.2). */
export const PROFIL = {
  dat: 'Daten/Kontexte',
  fbk: 'Feedback',
  spr: 'Sprache',
  cod: 'Code/Interaktiv',
  did: 'Didaktik/Aufbau',
};

export const MAX_PROFIL = 2;

export const KATEGORIEN = { ...KERN, ...PROFIL };

export const STUFEN = [
  'ohne generative KI',
  'KI als Werkzeug im Prozess',
  'KI-Entwurf, überarbeitet und geprüft',
  'im Wesentlichen KI-erzeugt, freigegeben',
];

// Fünfzackiger Stern, Außenradius 5, Innenradius 2.1, Spitze oben, um (0,0) zentriert.
const STERN =
  'M0,-5 L1.234,-1.699 L4.755,-1.545 L1.997,0.649 L2.939,4.045 ' +
  'L0,2.1 L-2.939,4.045 L-1.997,0.649 L-4.755,-1.545 L-1.234,-1.699 Z';

const esc = (s) =>
  String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

/** Kurzcode -> {ktx, txt, bld, ...}. Gesamtstufe wird immer neu als Maximum berechnet. */
export function parseCode(code) {
  const daten = {};
  for (const teil of String(code).split('|')) {
    const [k, v] = teil.trim().split(':');
    if (!k) continue;
    const n = Number(v);
    if (!Number.isInteger(n) || n < 0 || n > MAX) {
      throw new Error(`Ungültiger Wert für "${k}": "${v}" (erlaubt: 0–${MAX})`);
    }
    if (k === 'ktx') continue; // redundant, wird abgeleitet
    if (!(k in KATEGORIEN)) throw new Error(`Unbekannte Kategorie: "${k}"`);
    daten[k] = n;
  }
  const werte = Object.values(daten);
  if (!werte.length) throw new Error('Kurzcode enthält keine Kategorie.');

  // Die Obergrenze ist kein Formalismus: Das System scheitert an Ausfüllzeit,
  // nicht an zu grober Differenzierung (Spezifikation 4.2).
  const profil = Object.keys(daten).filter((k) => k in PROFIL);
  if (profil.length > MAX_PROFIL) {
    throw new Error(
      `Höchstens ${MAX_PROFIL} Profilkategorien erlaubt, ${profil.length} angegeben: ${profil.join(', ')}`,
    );
  }
  return { ktx: Math.max(...werte), ...daten };
}

export function formatCode({ ktx, ...kat }) {
  const teile = Object.keys(KATEGORIEN)
    .filter((k) => k in kat)
    .map((k) => `${k}:${kat[k]}`);
  return [`ktx:${ktx}`, ...teile].join('|');
}

export function altText(daten) {
  const kat = Object.keys(KATEGORIEN)
    .filter((k) => k in daten)
    .map((k) => `${KATEGORIEN[k]} ${daten[k]} von ${MAX}`)
    .join(', ');
  return `KI-Transparenz Stufe ${daten.ktx} von ${MAX}: ${STUFEN[daten.ktx]}. ${kat}.`;
}

/**
 * Drei Sterne ab x, vertikal zentriert auf y. Gefüllt = KI-Anteil.
 * `skala` = 1 entspricht 10 px Sternbreite; die Konturstärke wird mitskaliert,
 * damit gefüllte und leere Sterne bei jeder Größe gleich schwer wirken.
 */
function sterne(x, y, stufe, abstand = 12, skala = 1) {
  let out = '';
  for (let i = 0; i < MAX; i++) {
    const cx = x + 5 * skala + i * abstand;
    const t = `translate(${+cx.toFixed(2)} ${y})${skala === 1 ? '' : ` scale(${skala})`}`;
    out +=
      `<path d="${STERN}" transform="${t}" ` +
      (i < stufe
        ? 'fill="currentColor"/>'
        : `fill="none" stroke="currentColor" stroke-width="${+(1 / skala).toFixed(2)}" stroke-linejoin="round"/>`);
  }
  return out;
}

function huelle(w, h, daten, inhalt, rahmen = true) {
  const beschriftung = esc(altText(daten));
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"
     role="img" aria-label="${beschriftung}" fill="none" color="#111111"
     font-family="system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif">
  <title>KI-Transparenz ${daten.ktx}/${MAX}</title>
  <desc>${beschriftung}</desc>
${rahmen ? `  <rect x="0.5" y="0.5" width="${w - 1}" height="${h - 1}" rx="5" fill="none" stroke="currentColor" stroke-width="1" opacity="0.35"/>\n` : ''}${inhalt}
</svg>
`;
}

function freigabezeile(x, y, name, datum) {
  if (!name) return '';
  const text = `Geprüft und freigegeben: ${name}${datum ? `, ${datum}` : ''}`;
  return `  <text x="${x}" y="${y}" font-size="8" fill="currentColor" opacity="0.75">${esc(text)}</text>\n`;
}

export function badgeVoll(daten, { name = '', datum = '' } = {}) {
  const W = 344;
  const KOPF = 46; // Titelzeile + Stufentext + Trennlinie
  const keys = Object.keys(KATEGORIEN).filter((k) => k in daten);
  const zeilen = Math.ceil(keys.length / 2);
  const H = KOPF + zeilen * 18 + (name ? 18 : 6);

  let s = '';
  s += `  <text x="13" y="21" font-size="11" font-weight="600" fill="currentColor">KI-Transparenz</text>\n`;
  s += `  ${sterne(112, 17, daten.ktx)}\n`;
  s += `  <text x="152" y="21" font-size="11" font-weight="600" fill="currentColor">${daten.ktx}/${MAX}</text>\n`;
  s += `  <text x="13" y="34" font-size="8.5" fill="currentColor" opacity="0.75">${esc(STUFEN[daten.ktx])}</text>\n`;
  s += `  <line x1="13" y1="41" x2="${W - 13}" y2="41" stroke="currentColor" stroke-width="1" opacity="0.25"/>\n`;

  keys.forEach((k, i) => {
    const spalte = i % 2;
    const zeile = Math.floor(i / 2);
    const x = 13 + spalte * 166;
    const y = KOPF + 10 + zeile * 18;
    s += `  <text x="${x}" y="${y + 4}" font-size="9" fill="currentColor" opacity="0.85">${esc(KATEGORIEN[k])}</text>\n`;
    s += `  ${sterne(x + 92, y, daten[k], 11)}\n`;
    s += `  <text x="${x + 128}" y="${y + 4}" font-size="9" fill="currentColor">${daten[k]}/${MAX}</text>\n`;
  });

  s += freigabezeile(13, KOPF + zeilen * 18 + 12, name, datum);
  return huelle(W, H, daten, s);
}

export function badgeKompakt(daten, { name = '', datum = '' } = {}) {
  const W = 344;
  const H = name ? 42 : 28;
  let s = '';
  s += `  <text x="13" y="19" font-size="10" font-weight="600" fill="currentColor">KI</text>\n`;
  s += `  ${sterne(30, 15, daten.ktx, 11)}\n`;
  s += `  <text x="68" y="19" font-size="10" font-weight="600" fill="currentColor">${daten.ktx}/${MAX}</text>\n`;
  s += `  <text x="92" y="19" font-size="8.5" fill="currentColor" opacity="0.7" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">${esc(formatCode(daten))}</text>\n`;
  s += freigabezeile(13, 34, name, datum);
  return huelle(W, H, daten, s);
}

export function badgeMini(daten) {
  const W = 74;
  const H = 22;
  let s = '';
  s += `  <text x="8" y="15" font-size="9" font-weight="600" fill="currentColor">KI</text>\n`;
  s += `  ${sterne(22, 11, daten.ktx, 10)}\n`;
  s += `  <text x="55" y="15" font-size="9" fill="currentColor">${daten.ktx}/${MAX}</text>\n`;
  return huelle(W, H, daten, s);
}

export function badge(daten, variante = 'voll', opts = {}) {
  if (variante === 'mini') return badgeMini(daten);
  if (variante === 'kompakt') return badgeKompakt(daten, opts);
  if (variante === 'text') return badgeText(daten, opts);
  if (variante === 'html') return badgeHTML(daten, opts);
  return badgeVoll(daten, opts);
}

// ---------------------------------------------------------------- Text

/** Reiner Text für Word, LaTeX, E-Mail (Spezifikation 11). */
export function badgeText(daten, { name = '', datum = '' } = {}) {
  const kat = Object.keys(KATEGORIEN)
    .filter((k) => k in daten)
    .map((k) => `${KATEGORIEN[k]} ${daten[k]}/${MAX}`)
    .join(', ');
  const zeilen = [`KI-Transparenz ${daten.ktx}/${MAX} · ${STUFEN[daten.ktx]}`, kat];
  if (name) zeilen.push(`Geprüft und freigegeben: ${name}${datum ? `, ${datum}` : ''}`);
  return zeilen.join('\n') + '\n';
}

// ---------------------------------------------------------------- HTML

/** Stylesheet für badgeHTML. Erbt Farbe und Schrift vom umgebenden Kontext. */
export function badgeCSS() {
  // Kategorien bewusst einspaltig: Das Badge ist shrink-to-fit, ein mehrspaltiges
  // Raster hätte keine verlässliche Breite und würde die Labels überlaufen lassen.
  return `.ki-badge{display:inline-block;min-width:15em;border:1px solid currentColor;
  border-radius:5px;padding:.5em .7em;font-size:.8rem;line-height:1.5;
  color:inherit;font-family:inherit}
.ki-badge__kopf{font-weight:600}
.ki-badge__stufe,.ki-badge__freigabe{opacity:.75}
.ki-badge__freigabe{font-size:.9em}
.ki-badge__kat{display:flex;flex-direction:column;gap:.1em;
  margin:.4em 0;padding-top:.4em;border-top:1px solid currentColor}
.ki-badge__zeile{display:flex;align-items:center;gap:.6em;justify-content:space-between}
.ki-badge__zeile>span:first-child{min-width:0}
.ki-badge__wert{display:inline-flex;align-items:center;gap:.35em;white-space:nowrap;flex:none}
.ki-badge svg{flex:none}`;
}

/** Eingebettetes HTML-Fragment für Lernplattformen. Nutzt badgeCSS(). */
export function badgeHTML(daten, { name = '', datum = '' } = {}) {
  const st = (stufe, px = 10) => {
    const s = px / 10; // Sternbreite 10 px bei skala 1
    const abstand = 1.2 * px;
    const w = +(abstand * (MAX - 1) + px).toFixed(1);
    return (
      `<svg width="${w}" height="${px}" viewBox="0 0 ${w} ${px}" aria-hidden="true" fill="none">` +
      `${sterne(0, px / 2, stufe, abstand, s)}</svg>`
    );
  };
  const keys = Object.keys(KATEGORIEN).filter((k) => k in daten);
  const zeilen = keys
    .map(
      (k) =>
        `    <span class="ki-badge__zeile"><span>${esc(KATEGORIEN[k])}</span>` +
        `<span class="ki-badge__wert">${st(daten[k], 9)} ${daten[k]}/${MAX}</span></span>`,
    )
    .join('\n');

  return `<div class="ki-badge" role="group" aria-label="${esc(altText(daten))}">
  <div class="ki-badge__kopf"><span class="ki-badge__wert">KI-Transparenz ${st(daten.ktx)} ${daten.ktx}/${MAX}</span></div>
  <div class="ki-badge__stufe">${esc(STUFEN[daten.ktx])}</div>
  <div class="ki-badge__kat">
${zeilen}
  </div>${name ? `\n  <div class="ki-badge__freigabe">Geprüft und freigegeben: ${esc(name)}${datum ? `, ${esc(datum)}` : ''}</div>` : ''}
</div>
`;
}

// ---------------------------------------------------------------- CLI

function cli(argv) {
  const flags = {};
  const rest = [];
  for (const a of argv) {
    const m = a.match(/^--([^=]+)(?:=(.*))?$/);
    if (m) flags[m[1]] = m[2] ?? 'true';
    else rest.push(a);
  }

  if (rest.length) {
    process.stdout.write(
      badge(parseCode(rest[0]), flags.variante ?? 'voll', {
        name: flags.name ?? '',
        datum: flags.datum ?? '',
      }),
    );
    return;
  }

  // Ohne Argumente: Beispielsatz für die Vorschau erzeugen.
  const ziel = join(HIER, 'assets');
  mkdirSync(ziel, { recursive: true });
  const opts = { name: 'S. Blankenagel', datum: '02.08.2026' };
  const beispiel = 'txt:2|bld:3|loe:0|bew:1|dat:1';

  const dateien = {
    'badge-voll.svg': badgeVoll(parseCode(beispiel), opts),
    'badge-kompakt.svg': badgeKompakt(parseCode(beispiel), opts),
    'badge.txt': badgeText(parseCode(beispiel), opts),
    'badge.html': badgeHTML(parseCode(beispiel), opts),
    'ki-badge.css': badgeCSS() + '\n',
  };
  for (let i = 0; i <= MAX; i++) {
    dateien[`badge-mini-${i}.svg`] = badgeMini(parseCode(`txt:${i}`));
  }
  for (const [datei, inhalt] of Object.entries(dateien)) {
    writeFileSync(join(ziel, datei), inhalt);
  }
  console.log(`${Object.keys(dateien).length} Dateien geschrieben nach ${ziel}`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) cli(process.argv.slice(2));

/** node --test docs/ki-transparenz-badge/ */
import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  MAX,
  STUFEN,
  parseCode,
  formatCode,
  altText,
  badgeText,
  badgeVoll,
  badgeKompakt,
  badgeMini,
  badgeHTML,
} from './ki-badge.mjs';

test('Gesamtstufe ist das Maximum, nicht der Durchschnitt', () => {
  assert.equal(parseCode('txt:0|bld:3|did:0|loe:0').ktx, 3);
  assert.equal(parseCode('txt:1|bld:1|did:1|loe:1').ktx, 1);
  assert.equal(parseCode('txt:0').ktx, 0);
});

test('mitgegebenes ktx wird ignoriert und neu berechnet', () => {
  assert.equal(parseCode('ktx:0|txt:2|bld:3').ktx, 3);
});

test('Kurzcode überlebt einen Rundlauf, Reihenfolge normalisiert', () => {
  const code = 'ktx:3|txt:2|bld:3|did:1|loe:0';
  assert.equal(formatCode(parseCode(code)), code);
  assert.equal(formatCode(parseCode('loe:0|did:1|bld:3|txt:2')), code);
});

test('nicht zutreffende Kategorien fehlen, statt auf 0 zu stehen', () => {
  const daten = parseCode('txt:2');
  assert.equal(formatCode(daten), 'ktx:2|txt:2');
  assert.ok(!('bld' in daten));
  assert.ok(!badgeText(daten).includes('Bild/Grafik'));
});

test('ungültige Eingaben werden abgewiesen', () => {
  for (const code of ['txt:4', 'txt:-1', 'txt:x', 'xyz:1', 'ktx:2', '']) {
    assert.throws(() => parseCode(code), undefined, `angenommen: ${JSON.stringify(code)}`);
  }
});

test('Alternativtext nennt Stufe und jede Kategorie', () => {
  const t = altText(parseCode('txt:2|bld:3'));
  assert.match(t, /Stufe 3 von 3/);
  assert.match(t, /Text\/Aufgaben 2 von 3/);
  assert.match(t, /Bild\/Grafik 3 von 3/);
});

test('jede Stufe hat genau so viele gefüllte Sterne wie ihr Wert', () => {
  for (let i = 0; i <= MAX; i++) {
    const svg = badgeMini(parseCode(`txt:${i}`));
    assert.equal(svg.match(/fill="currentColor"\/>/g)?.length ?? 0, i, `Stufe ${i}`);
  }
});

test('Zahl steht immer neben den Sternen — nie Symbol ohne Text', () => {
  const daten = parseCode('txt:2|bld:3|did:1|loe:0');
  for (const svg of [badgeVoll(daten), badgeKompakt(daten), badgeMini(daten)]) {
    assert.match(svg, /3\/3/);
  }
});

test('Badges tragen keine Eigenfarbe außer der vererbten Textfarbe', () => {
  const svg = badgeVoll(parseCode('txt:2|bld:3'), { name: 'A. B.', datum: '01.01.2026' });
  const farben = svg.match(/(fill|stroke)="(?!none|currentColor)[^"]+"/g) ?? [];
  assert.deepEqual(farben, [], `Eigenfarbe gefunden: ${farben.join(', ')}`);
});

test('Freigabezeile erscheint nur mit Namen, dann vollständig', () => {
  const daten = parseCode('txt:0');
  assert.ok(!badgeVoll(daten).includes('Geprüft'));
  assert.match(badgeVoll(daten, { name: 'S. B.', datum: '02.08.2026' }), /Geprüft und freigegeben: S\. B\., 02\.08\.2026/);
});

test('Textvariante ist vollwertig und maschinell wieder lesbar', () => {
  const t = badgeText(parseCode('txt:2|bld:3'), { name: 'S. B.', datum: '02.08.2026' });
  assert.match(t, /KI-Transparenz 3\/3/);
  assert.match(t, new RegExp(STUFEN[3].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(t, /Geprüft und freigegeben/);
});

test('HTML-Fragment ist beschriftet und enthält alle Kategorien', () => {
  const html = badgeHTML(parseCode('txt:2|bld:3|did:1|loe:0'), { name: 'S. B.' });
  assert.match(html, /role="group"/);
  assert.match(html, /aria-label="KI-Transparenz Stufe 3 von 3/);
  for (const label of ['Text/Aufgaben', 'Bild/Grafik', 'Didaktik/Aufbau', 'Lösungen']) {
    assert.ok(html.includes(label), `fehlt: ${label}`);
  }
  assert.equal(html.match(/<svg /g).length, 5); // Gesamt + 4 Kategorien
});

test('Sonderzeichen in Namen werden maskiert', () => {
  const böse = 'A & B <script>';
  assert.ok(!badgeVoll(parseCode('txt:0'), { name: böse }).includes('<script>'));
  assert.ok(!badgeHTML(parseCode('txt:0'), { name: böse }).includes('<script>'));
});

/** node --test docs/ki-transparenz-badge/ */
import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  MAX,
  FLAGS,
  KATEGORIEN,
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
  assert.equal(parseCode('rec:0|erk:3|auf:0|prf:0').ktx, 3);
  assert.equal(parseCode('rec:1|erk:1|auf:1|prf:1').ktx, 1);
  assert.equal(parseCode('auf:0').ktx, 0);
});

test('mitgegebenes ktx wird ignoriert und neu berechnet', () => {
  assert.equal(parseCode('ktx:0|erk:2|auf:3').ktx, 3);
});

test('Kurzcode überlebt einen Rundlauf, Reihenfolge normalisiert', () => {
  const code = 'ktx:3|erk:2|auf:3|dif:0|prf:1';
  assert.equal(formatCode(parseCode(code)), code);
  assert.equal(formatCode(parseCode('prf:1|dif:0|auf:3|erk:2')), code);
});

test('nicht zutreffende Kategorien fehlen, statt auf 0 zu stehen', () => {
  const daten = parseCode('erk:2');
  assert.equal(formatCode(daten), 'ktx:2|erk:2');
  assert.ok(!('auf' in daten));
  assert.ok(!badgeText(daten).includes('Aufgaben'));
});

test('Flags gehen nicht in die Gesamtstufe ein', () => {
  const daten = parseCode('erk:1|real:1');
  assert.equal(daten.ktx, 1, 'real:1 darf die Stufe nicht auf 1 heben oder verfälschen');
  assert.equal(daten.real, 1);
  assert.equal(formatCode(daten), 'ktx:1|erk:1|real:1', 'Flag steht hinter den Kategorien');
  assert.equal(formatCode(parseCode('erk:1|real:0')), 'ktx:1|erk:1', 'gesetztes 0-Flag entfällt');
  assert.match(altText(daten), new RegExp(FLAGS.real));
});

test('sechs Kategorien, alle fachunspezifisch', () => {
  assert.deepEqual(Object.keys(KATEGORIEN), ['rec', 'pla', 'erk', 'auf', 'dif', 'prf']);
});

test('ungültige Eingaben werden abgewiesen', () => {
  for (const code of ['auf:4', 'auf:-1', 'auf:x', 'auf:', 'auf: ', 'auf:1.5', 'xyz:1', 'real:2', 'ktx:2', '']) {
    assert.throws(() => parseCode(code), undefined, `angenommen: ${JSON.stringify(code)}`);
  }
});

test('Alternativtext nennt Stufe und jede Kategorie', () => {
  const t = altText(parseCode('erk:2|auf:3'));
  assert.match(t, /Stufe 3 von 3/);
  assert.match(t, /Erklärung 2 von 3/);
  assert.match(t, /Aufgaben 3 von 3/);
});

test('jede Stufe hat genau so viele gefüllte Sterne wie ihr Wert', () => {
  for (let i = 0; i <= MAX; i++) {
    const svg = badgeMini(parseCode(`auf:${i}`));
    assert.equal(svg.match(/fill="currentColor"\/>/g)?.length ?? 0, i, `Stufe ${i}`);
  }
});

test('Zahl steht immer neben den Sternen — nie Symbol ohne Text', () => {
  const daten = parseCode('erk:2|auf:3|dif:0|prf:1');
  for (const svg of [badgeVoll(daten), badgeKompakt(daten), badgeMini(daten)]) {
    assert.match(svg, /3\/3/);
  }
});

test('Badges tragen keine Eigenfarbe außer der vererbten Textfarbe', () => {
  const svg = badgeVoll(parseCode('erk:2|auf:3'), { name: 'A. B.', datum: '01.01.2026' });
  const farben = svg.match(/(fill|stroke)="(?!none|currentColor)[^"]+"/g) ?? [];
  assert.deepEqual(farben, [], `Eigenfarbe gefunden: ${farben.join(', ')}`);
});

test('Freigabezeile erscheint nur mit Namen, dann vollständig', () => {
  const daten = parseCode('auf:0');
  assert.ok(!badgeVoll(daten).includes('Geprüft'));
  assert.match(badgeVoll(daten, { name: 'S. B.', datum: '02.08.2026' }), /Geprüft und freigegeben: S\. B\., 02\.08\.2026/);
});

test('Textvariante ist vollwertig und maschinell wieder lesbar', () => {
  const t = badgeText(parseCode('erk:2|auf:3'), { name: 'S. B.', datum: '02.08.2026' });
  assert.match(t, /KI-Transparenz 3\/3/);
  assert.match(t, new RegExp(STUFEN[3].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
  assert.match(t, /Geprüft und freigegeben/);
});

test('HTML-Fragment ist beschriftet und enthält alle Kategorien', () => {
  const html = badgeHTML(parseCode('erk:2|auf:3|dif:0|prf:1'), { name: 'S. B.' });
  assert.match(html, /role="group"/);
  assert.match(html, /aria-label="KI-Transparenz Stufe 3 von 3/);
  for (const label of ['Erklärung', 'Aufgaben', 'Differenzierung', 'Überprüfung']) {
    assert.ok(html.includes(label), `fehlt: ${label}`);
  }
  assert.equal(html.match(/<svg /g).length, 5); // Gesamt + 4 Kategorien
});

test('Sonderzeichen in Namen werden maskiert', () => {
  const böse = 'A & B <script>';
  assert.ok(!badgeVoll(parseCode('auf:0'), { name: böse }).includes('<script>'));
  assert.ok(!badgeHTML(parseCode('auf:0'), { name: böse }).includes('<script>'));
});

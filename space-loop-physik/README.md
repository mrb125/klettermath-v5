# 🎢 Space Loop Physik — Achterbahn im Physikunterricht (EF, NRW)

Unterrichtsmaterial rund um die **Mould King „Space Loop"**-Achterbahn für das Inhaltsfeld **Mechanik**
der Einführungsphase (EF) in NRW: **Energieerhaltung**, **Kreisbewegung** und **Zentripetalkraft** am Looping.

Dieses Repo enthält **vier verschiedene Herangehensweisen an dieselbe Einheit — zum direkten Vergleich**.
Alle bauen auf demselben roten Faden auf:

> *„Wie hoch muss die Startrampe mindestens sein, damit der Wagen den Looping schafft?"*
> (Antwort: `h ≥ 2,5 · r` — die ganze Einheit in einer Frage.)

➡️ **Zum Loslegen:** [`index.html`](index.html) im Browser öffnen — Übersicht mit Links zu allen vier Ansätzen.

---

## Die vier Ansätze im Vergleich

| | Ansatz | Kern-Idee | Format | Stärke | Vorbereitung |
|---|---|---|---|---|---|
| **A** | [Interaktive Simulation](ansatz-a-simulation/) | Looping am Bildschirm erleben, Starthöhe/Radius/Reibung live variieren | HTML (Canvas) | Intuition & Exploration, „was-wäre-wenn" | keine (nur Browser) |
| **B** | [Looping-Rechner](ansatz-b-rechner/) | Starthöhe ↔ v ↔ g-Kräfte berechnen, mit Herleitung | HTML (KaTeX) | Quantitativ, Selbstkontrolle, Formeln | keine (nur Browser) |
| **C** | [Experiment / Videoanalyse](ansatz-c-experiment/) | Echte Fahrt filmen, vermessen, mit Theorie vergleichen | HTML → Druck/PDF | Erkenntnisgewinnung, Messkompetenz, Reibung | Modell + Tablets/Tracker |
| **D** | [Klassischer Unterrichtsverlauf](ansatz-d-unterrichtsverlauf/) | Ausgearbeitete Doppelstunde + Arbeitsblatt + Lösungen | Markdown | Direkt einsetzbar, KLP-Bezug, Erwartungshorizont | Kopien/Tafel |

### Welcher Ansatz wann?

- **Wenig Zeit, digital ausgestattet →** A + B (Explorieren + Rechnen, ohne physisches Modell).
- **Modell vorhanden, forschend-entdeckend →** C als Herzstück, A/B zur Kontrolle.
- **Klassisch, prüfungsnah →** D als Gerüst, A/B/C als Bausteine zum Differenzieren.
- **Ideal:** kombinieren — D liefert den Ablauf, A/B/C sind die Stationen darin.

---

## Physikalischer Kern (alle Ansätze)

**Bedingung am Scheitel** (Zentripetalkraft = Gewichtskraft im Grenzfall):

```
v_top,min = √(g · r)
```

**Energieerhaltung** Start (Höhe h) → Scheitel (Höhe 2r):

```
m·g·h = ½·m·v_top² + m·g·(2r)   ⟹   h_min = 2,5 · r
```

**g-Kräfte** (Andruck als Vielfaches von g):

```
n_unten = 2h/r + 1        n_top = 2h/r − 5
```

Bei `h = 2,5·r`: unten **6 g**, am Scheitel **0 g** (Schwerelosigkeit).

---

## Bezug zum Kernlehrplan (KLP Physik SII NRW · EF)

Inhaltsfeld **Mechanik** — abgedeckte Schwerpunkte:

- Kinematik (v-t-/s-t-Diagramme aus der Videoanalyse)
- Energie, Energieerhaltung & **Energieentwertung** (Reibung)
- Newton'sche Gesetze, Kraft und Beschleunigung
- **Kreisbewegung und Zentripetalkraft** (der Looping)
- Kompetenzbereiche UF, E, K und **B** (Modellkritik LEGO ↔ reale Achterbahn)

Details und Kompetenzerwartungen: siehe [`ansatz-d-unterrichtsverlauf/unterrichtsverlauf.md`](ansatz-d-unterrichtsverlauf/unterrichtsverlauf.md).

---

## Benutzung

Alles ist **self-contained**: einfach die jeweilige `index.html` im Browser öffnen — keine Installation,
kein Server. Die Simulation und der Rechner laufen offline (KaTeX wird per CDN geladen).

Empfohlene externe Tools für Ansatz C: [Tracker](https://physlets.org/tracker/) (Videoanalyse) und
[phyphox](https://phyphox.org/) (Smartphone-Sensorik) — beide kostenlos.

## Als eigenes GitHub-Repo auslagern

Dieses Projekt ist bereits repo-fertig strukturiert. Zum Herauslösen in ein eigenständiges Repo:

```bash
cd space-loop-physik
git init && git add . && git commit -m "Space Loop Physik – Unterrichtsmaterial EF"
git branch -M main
git remote add origin git@github.com:<user>/space-loop-physik.git
git push -u origin main
```

---

## Struktur

```
space-loop-physik/
├─ index.html                    Übersicht & Einstieg (Vergleich der Ansätze)
├─ ansatz-a-simulation/          A · interaktive Looping-Simulation
├─ ansatz-b-rechner/             B · Looping-Rechner mit Herleitung
├─ ansatz-c-experiment/          C · Experiment-/Videoanalyse-Laborblatt (druckbar)
└─ ansatz-d-unterrichtsverlauf/  D · Unterrichtsverlauf, Arbeitsblatt, Erwartungshorizont
```

---

*Erstellt für den Physikunterricht der EF (NRW). Didaktisches Material — physikalische Werte sind
Modellwerte der Space Loop und je nach Aufbau anzupassen.*

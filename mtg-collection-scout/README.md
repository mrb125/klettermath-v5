# MTG Collection Scout

Durchsucht Online-Marktplätze nach **Magic-the-Gathering-Sammlungen** (Konvolute, Nachlässe,
Dachbodenfunde, versiegelte Ware) und **bewertet jedes Angebot automatisch**: geschätzter
Sammlungswert, Verhältnis Wert/Preis, Risikohinweise und eine Schulnote von A+ bis F.

Läuft mit **reiner Python-Standardbibliothek** – kein `pip install` von Fremdpaketen nötig.

```
Note  Score      Preis   Wert ca.     x  Quelle        Land Titel
──────────────────────────────────────────────────────────────────────────────────────────
A+       87      450 €    1.894 €  4.2x  demo          DE   Magic Sammlung Auflösung – ca. 4.500 Karten
      Top-Deal – sofort ansehen (Wert/Preis ≈ 4.2x, Sicherheit 66%)
      ! Nur Abholung
      · Einzelkarten (2 erkannt: Tundra, Scrubland): 231 €
      · 4.500 Karten x 0.53 €/Karte (vintage, Zustand good): 1.663 €
      + Sammlungsauflösung; Karten sortiert
```

## Inhalt

- [Schnellstart](#schnellstart)
- [Quellen (auch Ausland)](#quellen-auch-ausland)
- [eBay-Zugang einrichten](#ebay-zugang-einrichten)
- [Echte Kartenpreise laden](#echte-kartenpreise-laden)
- [Wie bewertet wird](#wie-bewertet-wird)
- [Alle Befehle](#alle-befehle)
- [Konfiguration](#konfiguration)
- [Eigene Marktplätze ergänzen](#eigene-marktplätze-ergänzen)
- [Fairness, robots.txt und Recht](#fairness-robotstxt-und-recht)
- [Grenzen der Schätzung](#grenzen-der-schätzung)
- [Entwicklung](#entwicklung)

## Schnellstart

```bash
cd mtg-collection-scout

# 1) Ohne alles ausprobieren (Demo-Daten, kein Netz):
python3 -m mtg_scout suchen --quelle demo --details

# 2) Kleinanzeigen durchsuchen und HTML-Report schreiben:
python3 -m mtg_scout suchen -q kleinanzeigen -s "magic sammlung" -s "magic konvolut" \
    --max-preis 800 --html report.html

# 3) Einzelne Anzeige bewerten (Text einfach reinkopieren):
python3 -m mtg_scout bewerten --preis 250 \
    --text "Magic Sammlung ca. 3000 Karten aus Revised und Legends, gespielt"

# 4) Dauerbeobachtung: alle 30 Minuten suchen, nur neue Treffer melden
python3 -m mtg_scout beobachten -q kleinanzeigen,ebay --intervall 30 --min-note B
```

Optional installieren (dann heißt der Befehl einfach `mtg-scout`):

```bash
pip install -e .
mtg-scout suchen --quelle demo
```

Python ab 3.9. Sonst nichts.

## Quellen (auch Ausland)

`python3 -m mtg_scout quellen` zeigt jederzeit den aktuellen Stand.

| Quelle | Marktplatz | Länder | Zugang |
|---|---|---|---|
| `ebay` | eBay Browse API | DE, AT, CH, GB, US, FR, IT, ES, NL, BE, IE, PL, CA, AU, HK, SG | kostenlose API-Zugangsdaten |
| `kleinanzeigen` | kleinanzeigen.de | DE | direkt (HTML) |
| `willhaben` | willhaben.at | AT | direkt (JSON-LD) |
| `tutti` | tutti.ch | CH | direkt (JSON-LD) |
| `marktplaats` | marktplaats.nl | NL | direkt (JSON-LD) |
| `2dehands` | 2dehands.be | BE | direkt (JSON-LD) |
| `subito` | subito.it | IT | direkt (JSON-LD) |
| `leboncoin` | leboncoin.fr | FR | direkt, starker Bot-Schutz |
| `gumtree` | gumtree.com | GB | direkt (JSON-LD) |
| `datei` | eigene JSON/CSV-Liste | – | lokal |
| `demo` | Beispieldaten | – | lokal, offline |

Mehrere Quellen kombinieren: `-q ebay,kleinanzeigen,willhaben` oder `-q alle`.
Preise fremder Währungen (USD, GBP, CHF, PLN …) werden für den Vergleich automatisch
in Euro umgerechnet – live über die EZB-Referenzkurse, mit statischer Fallback-Tabelle.

eBay-Marktplätze wählst du gezielt:

```bash
python3 -m mtg_scout suchen -q ebay --markt EBAY_DE,EBAY_AT,EBAY_US,EBAY_GB
```

## eBay-Zugang einrichten

Die eBay-Quelle nutzt die **offizielle Browse-API** (kein Scraping), dafür braucht es
einmalig kostenlose Zugangsdaten:

1. Konto auf [developer.ebay.com](https://developer.ebay.com) anlegen.
2. Unter *Application Keys* einen **Production**-Keyset erzeugen.
3. App-ID (Client-ID) und Cert-ID (Client-Secret) setzen:

```bash
export EBAY_CLIENT_ID="DeineAppId"
export EBAY_CLIENT_SECRET="DeinCertId"
```

Alternativ dauerhaft in die Konfigurationsdatei (siehe unten) unter `ebay`.

## Echte Kartenpreise laden

Ohne weitere Einrichtung nutzt das Tool einen eingebauten Katalog mit rund 120 bekannten
Wertkarten (Power 9, Dual Lands, Reserved List, moderne Staples) – grobe Hausnummern.
Für echte Marktpreise spiegelst du einmalig die Preisdaten von
[Scryfall](https://scryfall.com/docs/api):

```bash
python3 -m mtg_scout preise --aktualisieren      # lädt die Bulk-Datei "oracle_cards"
python3 -m mtg_scout preise --karte "Force of Will"
```

Danach erkennt der Scout jeden Kartennamen aus dem Anzeigentext und rechnet mit
aktuellen Cardmarket-/TCGplayer-Preisen (EUR bevorzugt, sonst USD umgerechnet).
Die Daten landen in einer lokalen SQLite-Datei, ein erneuter Lauf ist jederzeit möglich.

## Wie bewertet wird

Jede Anzeige durchläuft dieselben vier Schritte, und jeder Beitrag steht mit `--details`
sichtbar in der Ausgabe – keine Blackbox.

**1. Fakten aus dem Text ziehen**

- Kartenanzahl: „ca. 3.500 Karten“, „5k Karten“, „5 Sammelordner“ (→ 360 Karten je Ordner,
  800 je Kiste)
- Edition/Ära: Alpha, Beta, Revised, Legends, Arabian Nights … bis hin zu „aus den 90ern“
- Versiegelte Ware: Displays, Bundles, Commander-Decks, „OVP“, „sealed“
- Zustand: near mint, gespielt, beschädigt, PSA/BGS-Grading
- Kartennamen: „4x Force of Will“, „Underground Sea“ … inklusive Playset-Erkennung

**2. Wert schätzen**

```
Wert ≈ erkannte Einzelkarten (× Trefferwahrscheinlichkeit × Sicherheitsabschlag)
      + Kartenanzahl × €/Karte (abhängig von Ära, Rares-Hinweisen, Zustand)
      + versiegelte Ware × Pauschalpreis
```

Alle Stellschrauben stehen in der Konfiguration (`valuation`). Ein Ära-Treffer wirkt nur
anteilig (Standard 40 %), weil in einer „Revised-Sammlung“ selten alle Karten aus Revised
stammen. Ausgegeben wird eine Spanne (`low`/`mid`/`high`) plus eine **Sicherheit** in
Prozent, die mit der Menge belastbarer Angaben steigt.

**3. Deal-Score**

`Score = 50 + 25 · log2(Wert / Preis)`, zur Neutrale hin gedämpft, wenn die Schätzung
unsicher ist. Danach Zuschläge für gute Signale (Sammlungsauflösung, sortiert, Liste
vorhanden, Reserved List …) und Abzüge für Risiken (Proxys, „nur Commons“, Beschädigung,
Zahlung ohne Käuferschutz, schwache Verkäuferbewertung).

**4. Note**

| Note | Score | Bedeutung |
|---|---|---|
| A+ / A | ≥ 75 | deutlich unter geschätztem Wert – sofort ansehen |
| B | ≥ 65 | günstig, Details prüfen |
| C | ≥ 55 | fair bepreist |
| D / E | ≥ 30 | eher teuer oder zu dünne Angaben |
| F | < 30 | überteuert oder erkennbar problematisch |
| – | – | Gesuch/Tauschanzeige, kein Verkaufsangebot |

Gesuche („Suche Magic Sammlung“, „Ankauf“) werden automatisch als solche erkannt und
nicht als Angebot bewertet.

## Alle Befehle

```
mtg-scout suchen        Marktplätze durchsuchen und bewerten
mtg-scout beobachten    wiederholt suchen, nur neue Treffer melden
mtg-scout bewerten      einzelnen Anzeigentext oder eine JSON/CSV-Datei bewerten
mtg-scout preise        Kartenpreise von Scryfall spiegeln / einzelne Karte abfragen
mtg-scout quellen       verfügbare Quellen und deren Status anzeigen
mtg-scout config        Beispiel-Konfiguration anlegen
mtg-scout status        Datenbank, Cache und Wechselkurse prüfen
```

Wichtige Optionen von `suchen` / `beobachten`:

| Option | Wirkung |
|---|---|
| `-q, --quelle` | Quellen, kommagetrennt (`alle` nimmt alles) |
| `-s, --suchbegriff` | Suchbegriff, mehrfach angebbar |
| `--markt` | eBay-Marktplätze, z. B. `EBAY_DE,EBAY_US` |
| `--min-preis`, `--max-preis` | Preisfenster in Euro |
| `--plz`, `--umkreis` | regionale Suche (kleinanzeigen.de) |
| `--min-note`, `--min-score` | nur interessante Treffer anzeigen |
| `--nur-neue` | bereits gesehene Anzeigen ausblenden |
| `--sortierung` | `score`, `preis`, `wert`, `verhaeltnis` |
| `--details` | vollständige Wertherleitung |
| `--json`, `--csv`, `--html` | Ergebnisse in Datei schreiben |
| `--offline` | nur Cache und lokale Daten nutzen |
| `--ignore-robots` | robots.txt bewusst übergehen (Standard: beachten) |

Der HTML-Report ist eine eigenständige Datei mit Hell-/Dunkel-Modus und lässt sich
direkt im Browser öffnen oder weitergeben.

## Konfiguration

```bash
python3 -m mtg_scout config --beispiel      # legt ~/.config/mtg-scout/config.json an
```

Dort stellst du dauerhaft ein: Standardquellen und Suchbegriffe, eBay-Marktplätze,
Preisfenster, HTTP-Verhalten (Pause zwischen Abrufen, Timeouts, robots.txt) und vor
allem die Bewertungsparameter:

```jsonc
"valuation": {
  "bulk_per_card": 0.03,        // reine Massenware
  "mixed_per_card": 0.08,       // gemischte Sammlung
  "rare_per_card": 0.35,        // mit Rares/Foils
  "vintage_per_card": 1.20,     // 1993–1995
  "era_share": 0.4,             // Anteil der Sammlung aus der erkannten Ära
  "card_hit_discount": 0.75,    // Abschlag auf erkannte Einzelkarten
  "sealed": { "display": 130.0, "bundle": 40.0, "precon_deck": 25.0 }
}
```

Dateien und Verzeichnisse (XDG-konform):

- Konfiguration: `~/.config/mtg-scout/config.json`
- Datenbank (Kartenpreise, gesehene Anzeigen): `~/.local/share/mtg-scout/mtg-scout.sqlite3`
- HTTP-Cache und Wechselkurse: `~/.cache/mtg-scout/`

## Eigene Marktplätze ergänzen

Weitere Portale brauchen keinen Code, sondern nur eine JSON-Datei in
`mtg_scout/profiles/`:

```json
{
  "name": "meinmarkt",
  "label": "meinmarkt.example (Land)",
  "countries": ["DK"],
  "currency": "DKK",
  "base_url": "https://www.meinmarkt.example",
  "search_url": "https://www.meinmarkt.example/suche?q={query}&seite={page}",
  "note": "Best effort: liest JSON-LD der Suchseite."
}
```

Gelesen wird primär das JSON-LD (`schema.org/Product`), das die meisten Marktplätze
für Suchmaschinen ausliefern – das ist deutlich stabiler als CSS-Selektoren. Optional
lassen sich HTML-Klassen als Fallback ergänzen (`"html": { "item_tag": "article",
"item_class": "listing", "title_class": "title", "price_class": "price" }`).

Alternativ Anzeigen manuell sammeln und bewerten lassen:

```bash
python3 -m mtg_scout bewerten --datei samples/beispiel-anzeigen.csv --details
```

## Fairness, robots.txt und Recht

Das Tool ist für den **privaten Gebrauch** gedacht und verhält sich entsprechend:

- **eBay** wird ausschließlich über die offizielle API abgefragt, nicht gescrapt.
- Für HTML-Quellen wird **robots.txt geprüft** und respektiert; ein Abruf, den die Seite
  untersagt, wird abgebrochen (bewusst übergehbar mit `--ignore-robots`).
- Zwischen zwei Abrufen liegt eine Pause (Standard 1,5 s), Antworten werden 15 Minuten
  zwischengespeichert, damit wiederholte Läufe keine unnötige Last erzeugen.
- Der User-Agent identifiziert das Tool ehrlich.

Trotzdem gilt: Die AGB der Portale erlauben automatisiertes Auslesen nicht überall. Prüfe
das für deinen Anwendungsfall selbst, halte die Frequenz niedrig und nutze die Daten nicht
kommerziell weiter. Bot-Schutz (Cloudflare & Co.) kann jederzeit dafür sorgen, dass eine
Quelle 0 Treffer liefert – das ist kein Fehler des Tools, sondern die Antwort der Seite.

## Grenzen der Schätzung

Die Bewertung liest **nur den Anzeigentext**, nicht die Bilder. Sie ist ein Filter für die
Frage „welche der 200 Treffer schaue ich mir überhaupt an?“ – keine Wertermittlung.

- Ohne Stückzahl, Edition oder Kartennamen bleibt nur „zu wenig Information“.
- Verkäufer nennen gern die drei besten Karten und verschweigen den Rest.
- Bilder, in denen die eigentlichen Schätze liegen, wertet das Tool nicht aus.
- Die Sicherheit in Prozent sagt, wie belastbar eine Schätzung ist – bei < 40 % ist sie
  kaum mehr als eine Vermutung.
- Preise für versiegelte Ware sind Pauschalen und altern schnell; sie stehen deshalb in
  der Konfiguration.

## Entwicklung

```bash
python3 -m unittest discover -s tests -t . -v     # 56 Tests, ohne Netzzugriff
python3 -m mtg_scout suchen --quelle demo --details
```

Projektstruktur:

```
mtg_scout/
  cli.py             Kommandozeile (argparse, alle Unterbefehle)
  models.py          Listing, CardHit, ValueEstimate, Evaluation
  net.py             HTTP mit Rate-Limit, Retries, Cache, robots.txt
  htmlparse.py       genügsame HTML-/JSON-LD-Hilfen (ohne Fremdbibliotheken)
  currency.py        Umrechnung nach EUR (EZB-Kurse + Fallback)
  store.py           SQLite: Kartenpreise und gesehene Anzeigen
  config.py          Defaults, Konfigurationsdatei, Umgebungsvariablen
  report.py          Terminal-Tabelle, JSON, CSV, HTML-Report
  analyze/
    parse.py         Fakten aus dem Anzeigentext (Menge, Ära, Zustand, Risiken)
    score.py         Wertschätzung und Deal-Score
  pricing/
    scryfall.py      Preisspiegel von Scryfall
    index.py         Kartennamen im Freitext erkennen
    catalog.py       eingebauter Notfall-Katalog
  sources/
    ebay.py          eBay Browse API (16 Marktplätze)
    kleinanzeigen.py kleinanzeigen.de
    profile.py       profilgesteuerte Quellen (JSON-LD)
    local.py         eigene Dateien und Demo-Daten
  profiles/          je eine JSON-Datei pro Marktplatz
```

Lizenz: MIT.

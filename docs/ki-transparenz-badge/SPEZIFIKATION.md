# KI-Transparenz-Badge für Unterrichtsmaterial

**Spezifikation v0.1 · Stand: 2. August 2026**

Ein Kennzeichnungssystem, mit dem **Lehrkräfte den KI-Anteil an selbst erstelltem
Unterrichtsmaterial ausweisen**. Zwei Dimensionen: *Kategorie* (wo) × *Sterne* (wie viel).

Grundlage: [Recherche zu Icons für KI-Transparenz in Unterrichtsmaterial](../recherche-ki-transparenz-icons.md)

---

## 1. Geltungsbereich

**Im Geltungsbereich:** Material, das eine Lehrkraft (oder ein Team, eine Schule, ein Verlag)
selbst erstellt und an Lernende ausgibt — Arbeitsblätter, Aufgabensammlungen, Präsentationen,
Erklärvideos, Lernpfade, Feedbacktexte.

**Ausdrücklich nicht im Geltungsbereich:**

| | wofür stattdessen |
|---|---|
| Deklaration der KI-Nutzung **durch Lernende** | [Attribution 4 AI](https://attribution4ai.org/), CC BY-SA 4.0 |
| Festlegung, **wie viel KI in einer Aufgabe erlaubt** ist | [AI Assessment Scale](https://aiassessmentscale.com/), CC BY-NC-SA 4.0 |
| Kennzeichnung KI-**generierter Inhalte gegenüber der Öffentlichkeit** | [EU-Icons](https://digital-strategy.ec.europa.eu/en/policies/eu-icons-labelling-ai-generated-content) |

Diese drei Systeme existieren, sind erprobt und werden hier **nicht nachgebaut**. Das Badge
schließt die Lücke, die keines von ihnen abdeckt.

Die Trennung ist Absicht: Wer alles in ein System presst, bekommt ein System, das nichts
davon gut macht. Die drei Fälle haben verschiedene Adressaten, verschiedene Sprache und
verschiedene Risiken.

---

## 2. Grundsätze

1. **Deskriptiv, nicht wertend.** Das Badge beantwortet „wie viel KI?", nicht „wie gut?".
   Drei Sterne sind weder besser noch schlechter als null.
2. **Nie Symbol ohne Text.** Sterne erscheinen immer mit Zahl (`★★☆ 2/3`). Begründung:
   Die Nielsen Norman Group hat gezeigt, dass KI-Iconografie isoliert nicht verstanden wird —
   und auf Papier gibt es keinen Tooltip als Rückfallebene.
3. **Monochrom.** Keine Goldfarbe, kein Verlauf, keine Ampelfarben. Farbe transportiert
   Wertung; das AIAS-Redesign 2025 hat die Ampel genau deshalb verworfen. Das Badge erbt
   die Textfarbe (`currentColor`) und funktioniert in Schwarz-Weiß-Kopie.
4. **Verantwortung wird benannt.** Jedes Badge trägt Name und Datum der fachlichen Freigabe.
   Das ist nicht Dekoration, sondern das rechtlich tragende Element (→ Abschnitt 7).
5. **Rechtsanschlussfähig.** Die Stufen mappen ohne Umweg auf das EU-Icon-Set. Kein
   Parallelvokabular.
6. **Verhältnismäßig.** Das Scoping-Review zu Transparenzmechanismen (*Computers* 15(2):111)
   findet: Transparenz gelingt, wenn sie verhältnismäßig ist und klare Erwartungen hat.
   Ein Badge, dessen Ausfüllen länger dauert als eine Minute, wird nicht ausgefüllt.

---

## 3. Die Skala

Vier Stufen, 0–3.

| Stufe | Kurzform | Bedeutung |
|---|---|---|
| **☆☆☆ 0/3** | *ohne generative KI* | Keine generative KI beteiligt |
| **★☆☆ 1/3** | *KI als Werkzeug im Prozess* | KI half beim Entstehen, steht aber nicht im Ergebnis |
| **★★☆ 2/3** | *KI-Entwurf, überarbeitet und geprüft* | KI-Ausgabe ist im Ergebnis enthalten, wurde substanziell verändert |
| **★★★ 3/3** | *im Wesentlichen KI-erzeugt, freigegeben* | KI-Ausgabe weitgehend unverändert übernommen, fachlich freigegeben |

### 3.1 Entscheidungsregeln

Die Stufe wird über zwei Ja/Nein-Fragen bestimmt — bewusst so, weil das Scoping-Review bei
45,5 % der untersuchten Systeme *unzureichend spezifizierte Anforderungen* fand. Wer eine
Skala ohne Entscheidungsregel veröffentlicht, bekommt Rauschen zurück.

```
Wurde generative KI eingesetzt?
├── nein ──────────────────────────────────────────► Stufe 0
└── ja
    │
    Steht KI-erzeugter Wortlaut / Bildinhalt im ausgegebenen Material?
    ├── nein ──────────────────────────────────────► Stufe 1
    └── ja
        │
        Wurde die KI-Ausgabe substanziell verändert
        (mehr als Korrektur und Kürzung)?
        ├── ja ─────────────────────────────────────► Stufe 2
        └── nein ───────────────────────────────────► Stufe 3
```

### 3.2 Abgrenzungen

**Stufe 0 gilt ausdrücklich weiterhin bei:**

- Rechtschreib- und Grammatikprüfung
- Suchmaschinen, Bibliothekskatalogen, OCR
- Übersetzungsspeichern und regelbasierter Übersetzung
- **prozeduraler Aufgabengenerierung** — ein Generator, der Zahlenwerte variiert oder
  Aufgabenvarianten nach festen Regeln erzeugt, ist keine generative KI

Der letzte Punkt ist für rechnerisch erzeugtes Material entscheidend. Ohne diese Abgrenzung
trägt am Ende jedes generierte Arbeitsblatt drei Sterne, und das Badge sagt nichts mehr aus.
Maßgeblich ist nicht, ob ein Computer beteiligt war, sondern ob ein **generatives Modell**
Inhalte hervorgebracht hat.

**Typische Zuordnungen:**

| Vorgang | Stufe |
|---|---|
| KI um Ideen für einen Aufgabenkontext gebeten, dann selbst geschrieben | 1 |
| KI um Gliederungsvorschlag gebeten, Inhalte selbst verfasst | 1 |
| Eigenen Text von KI umformulieren lassen, Ergebnis übernommen | 2 |
| KI-Entwurf einer Textaufgabe, Zahlen und Kontext angepasst, sprachlich überarbeitet | 2 |
| KI-generiertes Bild ohne Nachbearbeitung eingefügt | 3 |
| KI-generierte Musterlösung geprüft, für richtig befunden, übernommen | 3 |

Die letzte Zeile ist die unbequemste und deshalb wichtig: **Prüfen ist kein Verändern.**
Eine geprüfte, aber unveränderte KI-Ausgabe bleibt Stufe 3. Die Prüfung wird in der
Freigabezeile dokumentiert, nicht durch Absenken der Stufe belohnt.

---

## 4. Kategorien

Vier Kategorien. Der Mehrwert des Systems liegt hier: Eine einzige Skala verdeckt, *wo* die
KI im Spiel war — genau die Kritik, die Micallef & Petrovska (arXiv 2606.13389) und der
Faceted-Attribution-Ansatz an binären Deklarationen üben.

| Code | Kategorie | umfasst |
|---|---|---|
| `txt` | **Text/Aufgaben** | Aufgabenstellungen, Erklärtexte, Kontexte, Arbeitsaufträge |
| `bld` | **Bild/Grafik** | Illustrationen, Fotos, Diagramme, Schaubilder |
| `did` | **Didaktik/Aufbau** | Reihenfolge, Progression, Schwierigkeitsstufen, Differenzierung, Lernziele |
| `loe` | **Lösungen** | Musterlösungen, Erwartungshorizonte, Lösungswege, Bewertungsraster |

Nicht zutreffende Kategorien werden **weggelassen**, nicht auf 0 gesetzt. Ein Arbeitsblatt
ohne Bilder trägt keine Bild-Angabe. `0` heißt „geprüft, ohne KI"; Weglassen heißt „nicht
vorhanden".

**Optionale fünfte Kategorie:** `spr` — *Sprache* (Übersetzung, sprachliche Vereinfachung,
DaZ-Anpassung). Empfehlung: nur einführen, wo sprachliche Differenzierung ein eigener
Arbeitsschritt ist. Sonst fällt sie unter `txt`.

### 4.1 Warum `bld` gesondert zählt

Die Bildkategorie ist die einzige mit unmittelbarer Rechtsfolge. Nach Art. 50 EU AI Act
können **fotorealistische** KI-Bilder unter die Deepfake-Kennzeichnungspflicht fallen —
die Faustformel aus dem EU-Verhaltenskodex: eine Sphinx über dem Eiffelturm nicht, das
fotorealistische Porträt einer Person, die nie existiert hat, schon. Wer `bld:3` einträgt,
sollte diese Frage bewusst beantwortet haben.

---

## 5. Gesamtstufe

> **Die Gesamtstufe ist das Maximum der Kategorien, nicht der Durchschnitt.**

Ein Arbeitsblatt mit `txt:0 bld:3 did:0 loe:0` trägt gesamt **3/3**, nicht 0,75.

Beim Durchschnitt verschwindet ein vollständig KI-generiertes Bild hinter vier menschlichen
Kategorien — das Badge würde dann genau das verbergen, was es zeigen soll. Die Maximum-Regel
macht das Gesamtbadge zur ehrlichen Obergrenze: *„Irgendwo in diesem Material steckt KI auf
Stufe X."*

Aus demselben Grund gibt es **keine Prozentangaben**. Die Transparency Badges des ABC Unified
School District arbeiten mit „ca. 60 % KI-Anteil"; das ist nicht messbar und suggeriert eine
Präzision, die es nicht gibt.

---

## 6. Kurzcode

Ein maschinenlesbarer String, der sich in Metadaten, Dateinamen, Datenbankfelder und
HTML-Attribute schreiben lässt:

```
ktx:2|txt:2|bld:3|did:1|loe:0
```

- `ktx` — Gesamtstufe (redundant, aber erlaubt Filtern ohne Parsen der Kategorien)
- Kategorien in fester Reihenfolge `txt, bld, did, loe`, nicht zutreffende weggelassen
- Werte `0`–`3`
- Grammatik: `ktx:[0-3](\|(txt|bld|did|loe|spr):[0-3])*`

Anschlussfähig an C2PA-Assertions und an das Metadatenfeld einer Materialdatenbank. Der
Kurzcode ist die **normative Datenform**; das Badge ist die Darstellung davon.

---

## 7. Rechtliche Einordnung

### 7.1 Mapping auf die EU-Icons

| Stufe | EU-Icon |
|---|---|
| 0 | — (kein EU-Icon; optional eigener „ohne KI"-Marker) |
| 1 | — bzw. *AI Modified* |
| 2 | *AI Modified* |
| 3 | *AI Generated* |

Die EU-Icons sind **nicht verpflichtend** — Alternativen sind zulässig, solange sie gleich
klar erkennbar sind. Empfehlung trotzdem: das EU-Set verwenden, wo eine Kennzeichnungspflicht
greift. Es ist attributionsfrei nutzbar, liegt in SVG vor, und jede Eigenkreation schwächt
den ohnehin fragilen Wiedererkennungswert weiter (→ Kritik netzpolitik.org).

### 7.2 Die Freigabezeile

```
Geprüft und freigegeben: [Name], [Datum]
```

Nach Art. 50 EU AI Act entfällt die Kennzeichnungspflicht für KI-generierte Texte, wenn eine
**menschliche Prüfung oder redaktionelle Kontrolle** stattgefunden hat und eine natürliche
oder juristische Person die **redaktionelle Verantwortung** trägt. Genau das dokumentiert
diese Zeile. Sie ist deshalb **nicht optional**, auch nicht auf Stufe 0.

### 7.3 Was das Badge rechtlich nicht leistet

Es ersetzt keine Kennzeichnung nach Art. 50, wo diese greift — insbesondere nicht bei
fotorealistischen Bildern, synthetischen Stimmen und KI-Avataren. Es ist eine
**pädagogische Selbstauskunft**, die daneben steht und die Prüfung dokumentiert.

Für digitale Lernumgebungen kommt eine separate Pflicht hinzu, die dieses Badge nicht abdeckt:
Art. 50 Abs. 1 verlangt einen Hinweis, wenn Lernende **mit einem KI-System interagieren** —
KI-Tutor, Chat, automatisch erzeugtes Feedback. Formulierungsmuster:

> „Dieses Feedback wurde von einem KI-Werkzeug erzeugt und von deiner Lehrkraft geprüft."

---

## 8. Darstellung

### 8.1 Varianten

| Variante | Inhalt | Einsatz |
|---|---|---|
| **Voll** | Gesamtstufe + alle Kategorien + Freigabezeile | Fußzeile A4, Materialdatenbank |
| **Kompakt** | Gesamtstufe + Kurzcode + Freigabezeile, einzeilig | Foliensatz, Kopfzeile, enge Layouts |
| **Mini** | nur Gesamtstufe | Karten, Listen, Übersichten — **nur** mit Verweis auf die Vollangabe |

Die Mini-Variante darf nie allein stehen. Ohne Kategorien ist sie genau die eindimensionale
Deklaration, deren Unzulänglichkeit dieses System behebt.

### 8.2 Gestaltung

- **Sterne:** gefüllt = KI-Anteil, Kontur = Rest. Gleiche Größe, gleiche Strichstärke.
- **Farbe:** `currentColor`, keine Eigenfarbe. Kein Gold, keine Ampelfarben.
- **Zahl:** immer `n/3` neben den Sternen.
- **Mindestgröße:** Sternhöhe 8 px bzw. 2,5 mm im Druck. Darunter Mini-Variante ohne Sterne,
  nur `KI 2/3`.
- **Platzierung:** Fußzeile, gleiche Position auf allen Materialien einer Sammlung.

### 8.3 Barrierefreiheit

SVG mit `role="img"`, `<title>` und `<desc>`. Alternativtext nach Muster:

```
KI-Transparenz Stufe 2 von 3: KI-Entwurf, überarbeitet und geprüft.
Text/Aufgaben 2 von 3, Bild/Grafik 3 von 3, Didaktik/Aufbau 1 von 3, Lösungen 0 von 3.
```

Die Sternform ist nie alleiniger Bedeutungsträger — die Zahl steht immer daneben. Damit
funktioniert das Badge bei Sehbeeinträchtigung, in Graustufen und im Fax.

---

## 9. Was das Badge nicht ist

- **Keine Qualitätsaussage.** Drei Sterne sind kein Mangel und kein Gütesiegel.
- **Kein Detektionsergebnis.** Es ist eine Selbstauskunft. KI-Detektoren sind unzuverlässig;
  das System verlässt sich bewusst nicht auf sie.
- **Keine Prozentangabe.** Siehe Abschnitt 5.
- **Keine Rangfolge.** Die Kategorien sind gleichrangig, die Stufen sind Mengen, keine Noten.

---

## 10. Offene Punkte

1. **Keine Wirkungsforschung im Schulkontext.** Studien zu KI-Labels stammen aus Social-Media-
   und Nachrichtenkontexten; mehrere finden, dass „KI-generiert" die *wahrgenommene
   Genauigkeit senkt* (u. a. arXiv 2506.16202). Wie Lernende und Eltern auf ein Badge auf dem
   Arbeitsblatt reagieren, ist unerforscht. Vor breitem Rollout: kleine Erprobung mit
   Rückmeldung von Lernenden und Eltern.
2. **Selbstauskunft bleibt ungeprüft.** Das ist laut Scoping-Review der häufigste Schwachpunkt
   (18,2 % ungeprüfte Selbstauskunft). Das System nimmt das bewusst in Kauf — die Alternative
   wäre eine Kontrollinstanz, die niemand finanzieren wird.
3. **Grenze 1 | 2 bleibt Ermessen.** Die Entscheidungsregel reduziert den Spielraum, beseitigt
   ihn nicht. Im Zweifel die höhere Stufe.
4. **Verlagsanschluss offen.** Kein deutscher Bildungsverlag hat bislang ein öffentliches
   Kennzeichnungsschema. Die naheliegende Andockstelle im deutschen System wäre
   **EduCheck digital**, das um einen Prüfbereich KI erweitert wird.

---

## 11. Lizenz

Vorschlag: **CC BY-SA 4.0** — wie Attribution 4 AI. Erlaubt Anpassung ans Corporate Design
einer Schule, hält Weiterentwicklungen aber offen.

Bewusst *nicht* CC BY-NC-SA (wie AIAS): Der NC-Baustein schließt Schulbuchverlage und
kommerzielle Plattformen aus — also genau die Akteure, deren Beteiligung das System
überhaupt erst wirksam machen würde.

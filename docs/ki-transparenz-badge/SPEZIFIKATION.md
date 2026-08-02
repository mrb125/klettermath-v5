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
| Deklaration der KI-Nutzung **durch Lernende** | [Attribution 4 AI](https://attribution4ai.org/) |
| Festlegung, **wie viel KI in einer Aufgabe erlaubt** ist | [AI Assessment Scale](https://aiassessmentscale.com/) |
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

Der Mehrwert des Systems liegt hier: Eine einzige Skala verdeckt, *wo* die KI im Spiel war —
genau die Kritik, die Micallef & Petrovska (arXiv 2606.13389) und der
Faceted-Attribution-Ansatz an binären Deklarationen üben.

Die Kategorien sind zweistufig: ein **Kern**, der überall gleich ist und Materialien
vergleichbar macht, und ein **Profil** aus höchstens zwei Zusatzkategorien je Fach oder
Einrichtung.

### 4.1 Kern — immer, unverändert

| Code | Kategorie | umfasst |
|---|---|---|
| `txt` | **Text/Aufgaben** | Aufgabenstellungen, Erklärtexte, Kontexte, Arbeitsaufträge |
| `bld` | **Bild/Grafik** | Illustrationen, Fotos, Diagramme, Schaubilder |
| `med` | **Audio/Video** | Vertonung, Erklärvideos, Podcasts, Avatare, synthetische Stimmen |
| `loe` | **Lösungen** | Musterlösungen, Erwartungshorizonte, Lösungswege |
| `bew` | **Bewertung** | Bewertungsraster, Niveauzuordnung, Kompetenz- und Diagnoseeinschätzung |

Nicht zutreffende Kategorien werden **weggelassen**, nicht auf 0 gesetzt. Ein Arbeitsblatt
ohne Bilder trägt keine Bild-Angabe. `0` heißt „geprüft, ohne KI"; Weglassen heißt „nicht
vorhanden".

### 4.2 Profil — höchstens zwei, frei gewählt

| Code | Kategorie | lohnt sich, wenn |
|---|---|---|
| `dat` | **Daten/Kontexte** | Zahlenwerte, Statistiken und Sachkontexte eigenes Risiko sind (Mathematik, Sachfächer) |
| `fbk` | **Feedback** | die Umgebung automatische Rückmeldungen an Lernende erzeugt |
| `spr` | **Sprache** | sprachliche Differenzierung ein eigener Arbeitsschritt ist (DaZ, Leichte Sprache) |
| `cod` | **Code/Interaktiv** | Applets, Simulationen oder Auswertungslogik zum Material gehören |
| `did` | **Didaktik/Aufbau** | die Reihenfolge- und Progressionsentscheidung dokumentiert werden soll |

**Warum die Obergrenze zwei.** Das System scheitert nicht an zu wenig Differenzierung,
sondern an Ausfüllzeit — genau das findet das Scoping-Review als häufigste Ursache
wirkungsloser Transparenzsysteme (→ 7 und 10.2). Sieben Kategorien werden nicht ausgefüllt,
und ein nicht ausgefülltes Badge ist schlechter als ein grobes.

**Warum `did` nicht im Kern steht.** „Die KI hat die Progression vorgeschlagen" ist die am
schwersten zu entscheidende Angabe des ganzen Systems; in der Praxis landet sie fast immer
auf 0 oder 1. Wer sie führen will, führt sie als Profilkategorie — für die Vergleichbarkeit
zwischen Materialien trägt sie zu wenig.

### 4.3 Warum `bld` und `med` gesondert zählen

Diese beiden Kategorien haben unmittelbare Rechtsfolge. Nach Art. 50 EU AI Act können
**fotorealistische** KI-Bilder unter die Deepfake-Kennzeichnungspflicht fallen — die
Faustformel aus dem EU-Verhaltenskodex: eine Sphinx über dem Eiffelturm nicht, das
fotorealistische Porträt einer Person, die nie existiert hat, schon. Für synthetische
Stimmen und KI-Avatare gilt dasselbe; sie sind im Kodex ausdrücklich erfasst.

Wer `bld:3` oder `med:3` einträgt, sollte diese Frage bewusst beantwortet und im
Prüfprotokoll festgehalten haben (→ 12).

### 4.4 Warum `bew` von `loe` getrennt ist

Musterlösungen und Bewertung sehen verwandt aus, sind es aber nicht. Der AI Act stuft
KI-Systeme, die **Lernergebnisse bewerten** oder Lernende Bildungsgängen zuordnen, als
**Hochrisiko** ein (Anhang III Nr. 3).

Das trifft eine Lehrkraft nicht, die sich ein Bewertungsraster entwerfen lässt — sie
betreibt kein Hochrisikosystem. Aber die eigene Kategorie macht sichtbar, wo diese Grenze
verläuft, und macht den Schritt von „KI half beim Raster" zu „KI bewertet Schülerarbeiten"
zu einer bewussten Entscheidung statt zu einem Abgleiten.

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
ktx:3|txt:2|bld:3|loe:0|bew:1|dat:1
```

- `ktx` — Gesamtstufe (redundant, aber erlaubt Filtern ohne Parsen der Kategorien)
- Kategorien in fester Reihenfolge: erst der Kern `txt, bld, med, loe, bew`, dann das Profil
  `dat, fbk, spr, cod, did`; nicht zutreffende weggelassen
- Werte `0`–`3`, höchstens zwei Profilkategorien
- Grammatik: `ktx:[0-3](\|(txt|bld|med|loe|bew|dat|fbk|spr|cod|did):[0-3])*`

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
Text/Aufgaben 2 von 3, Bild/Grafik 3 von 3, Lösungen 0 von 3, Bewertung 1 von 3,
Daten/Kontexte 1 von 3.
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
   Arbeitsblatt reagieren, ist unerforscht. → Erprobungsdesign in Abschnitt 13.
2. **Selbstauskunft bleibt ungeprüft.** Das ist laut Scoping-Review der häufigste Schwachpunkt
   (18,2 % ungeprüfte Selbstauskunft). Das System nimmt das bewusst in Kauf — die Alternative
   wäre eine Kontrollinstanz, die niemand finanzieren wird.
3. **Grenze 1 | 2 bleibt Ermessen.** Die Entscheidungsregel reduziert den Spielraum, beseitigt
   ihn nicht. Im Zweifel die höhere Stufe.
4. **Verlagsanschluss offen.** Kein deutscher Bildungsverlag hat bislang ein öffentliches
   Kennzeichnungsschema. Die naheliegende Andockstelle im deutschen System wäre
   **EduCheck digital**, das um einen Prüfbereich KI erweitert wird.

---

## 11. Textbausteine ohne Grafik

Nicht jedes Material bekommt eine SVG-Fußzeile. Für Word, LaTeX, E-Mail und Elternbriefe
gelten dieselben Regeln in reinem Text. Die Angabe ist gleichwertig — das Badge ist die
Darstellung, nicht die Sache.

**Einzeilig, Minimum:**

```
KI-Transparenz 2/3 · Text 2, Bild 3, Lösungen 0, Bewertung 1
Geprüft und freigegeben: S. Blankenagel, 02.08.2026
```

**Fließtext, für Elternbriefe und Materialbeschreibungen:**

> Bei der Erstellung dieses Materials wurde generative KI eingesetzt (Stufe 2 von 3:
> KI-Entwurf, überarbeitet und geprüft). Betroffen sind Aufgabentexte und Abbildungen;
> Lösungswege und Bewertungsraster stammen ohne KI-Beteiligung von mir.
> Geprüft und freigegeben: S. Blankenagel, 02.08.2026.

**Stufe 0, ausdrücklich benannt:**

```
KI-Transparenz 0/3 · ohne generative KI erstellt
Geprüft und freigegeben: S. Blankenagel, 02.08.2026
```

Stufe 0 wegzulassen ist zulässig, aber schwächer: Wer nur kennzeichnet, wenn KI im Spiel war,
macht das Badge zum Warnzeichen. Wer immer kennzeichnet, macht es zur Routineangabe — und
genau das ist das Ziel.

---

## 12. Prüfprotokoll

Die Freigabezeile behauptet eine Prüfung. Damit die Behauptung trägt — und im Streitfall die
redaktionelle Kontrolle nach Art. 50 belegt (→ 7.2) — braucht es einen minimalen Nachweis.
Bewusst minimal: Alles, was länger dauert als eine Zeile pro Material, wird nicht geführt.

Eine Zeile je Material, z. B. als CSV in der Materialablage:

```csv
datum;material;kurzcode;werkzeug;geprueft_von;anmerkung
2026-08-02;lineare-gleichungen-ub3;ktx:3|txt:2|bld:3|loe:0|bew:1|dat:1;<Modell/Werkzeug>;S. Blankenagel;Bild nicht fotorealistisch
```

- `werkzeug` — welches KI-Werkzeug, in welcher Version. Wichtig, weil sich Ausgabequalität
  und Rechtslage je Werkzeug unterscheiden.
- `anmerkung` — Freitext. Pflicht bei `bld:3`: Festhalten, ob das Bild fotorealistisch ist
  (→ Deepfake-Frage, 4.1).

**Aufbewahrung:** so lange, wie das Material im Einsatz ist, mindestens aber ein Schuljahr.
Personenbezogene Daten von Lernenden gehören nicht ins Protokoll.

---

## 13. Erprobung vor dem Rollout

Der ungeklärteste Punkt des Systems (→ 10.1): Es ist unbekannt, wie Lernende und Eltern auf
das Badge reagieren. Mehrere Studien zeigen, dass ein „KI-generiert"-Label die *wahrgenommene
Genauigkeit* von Inhalten senkt. Auf einem Arbeitsblatt könnte das erwünscht sein (kritisches
Lesen) oder schädlich (Vertrauensverlust in die Lehrkraft). Niemand weiß es.

Deshalb: nicht flächendeckend einführen, sondern erst messen.

**Minimaldesign, eine Lerngruppe, vier Wochen**

| | |
|---|---|
| **Umfang** | eine Klasse, alle Materialien einer Unterrichtsreihe gekennzeichnet |
| **Vergleich** | Parallelklasse ohne Kennzeichnung, sonst identisches Material |
| **Erhebung** | vorher/nachher, je 5 Minuten, anonym |

**Vier Fragen an die Lernenden** (vierstufige Skala, keine Mitte):

1. Ich verstehe, was die Sterne auf dem Arbeitsblatt bedeuten.
2. Ich vertraue darauf, dass die Aufgaben fachlich richtig sind.
3. Die Angabe verändert, wie genau ich das Material lese.
4. Ich finde es gut, dass die Angabe da steht.

**Zwei an die Lehrkraft:** Wie lange dauert das Ausfüllen im Schnitt? Bei welchem Material
war die Stufe unklar?

**Abbruchkriterium:** Sinkt Frage 2 in der Badge-Gruppe deutlich gegenüber der
Vergleichsgruppe, ist die Darstellung das Problem, nicht die Transparenz. Dann zuerst
Wortlaut und Platzierung ändern — nicht das Kennzeichnen aufgeben.

**Was die Erprobung nicht leistet:** Sie ist keine Studie. Eine Klasse, vier Wochen,
kein Zufallsdesign. Sie soll grobe Fehlgriffe finden, bevor sie in 300 Materialien stecken.

---

## 14. Weitergabe und Anpassung

Keine Standardlizenz. Stattdessen vier Regeln in eigenen Worten:

1. **Frei verwendbar.** Schulen, Lehrkräfte, Verlage und Plattformen dürfen das System
   einsetzen, weitergeben und ans eigene Erscheinungsbild anpassen — ohne Rückfrage,
   ohne Gebühr, ohne Unterscheidung zwischen kommerziell und nichtkommerziell.
2. **Bedeutung der Stufen bleibt unverändert.** Wer Aussehen, Sprache oder Kategorien
   anpasst, darf die Definition der Stufen 0–3 und die Maximum-Regel nicht verändern.
   Sonst entstehen gleich aussehende Badges mit verschiedener Bedeutung — der Schaden wäre
   größer als der Nutzen.
3. **Kein Gütesiegel.** Das System darf nicht als Zertifizierung, Prüfsiegel oder
   Qualitätsnachweis dargestellt werden. Es ist eine Selbstauskunft, und nur das.
4. **Abweichungen kennzeichnen.** Wer die Stufen doch verändert, nennt das Ergebnis nicht
   mehr „KI-Transparenz-Badge", sondern gibt ihm einen eigenen Namen.

Punkt 2 und 4 sind der einzige Grund, warum hier überhaupt Regeln stehen: Ein
Kennzeichnungssystem lebt davon, dass dasselbe Zeichen überall dasselbe bedeutet.

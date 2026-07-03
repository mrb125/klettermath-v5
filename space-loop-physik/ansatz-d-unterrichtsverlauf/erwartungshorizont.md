# Erwartungshorizont · Achterbahn-Looping (EF)

Konstanten: `g = 9,81 m/s²`, Beispiel-Radius `r = 0,08 m`.

---

## Aufgabe 1 — Bedingung am Scheitel

**a)** Skizze: Gewichtskraft `F_G = m·g` nach unten (Richtung Kreismittelpunkt), Normalkraft `F_N` der Bahn
ebenfalls nach unten (Bahn drückt von außen). Beide zusammen bilden die Zentripetalkraft.

**b)** Grenzfall `F_N = 0`, also `F_Z = F_G`:

$$\frac{m\,v_{\text{top}}^2}{r} = m\,g \;\Rightarrow\; v_{\text{top,min}} = \sqrt{g\,r}$$

Zahlenwert: `v_top,min = √(9,81 · 0,08) ≈ 0,89 m/s`.

---

## Aufgabe 2 — Mindest-Starthöhe

**a)** Energieerhaltung Start (Ruhe, Höhe h) → Scheitel (Höhe 2r, Geschwindigkeit v_top):

$$m\,g\,h = \tfrac12 m\,v_{\text{top}}^2 + m\,g\,(2r)$$

**b)** Mit `v_top² = g·r` (Grenzfall) einsetzen:

$$g\,h_{\min} = \tfrac12 g r + 2 g r = \tfrac52 g r \;\Rightarrow\; h_{\min} = 2{,}5\,r$$

Zahlenwert: `h_min = 2,5 · 0,08 = 0,20 m`.

**c)** `h = 0,25 m > 0,20 m = h_min` → **ja**, der Wagen schafft den Looping (reibungsfrei, mit Reserve).

---

## Aufgabe 3 — g-Kräfte

**a)** Am tiefsten Punkt: `F_N − F_G = m v²/r`, also `F_N = m(v²/r + g)`.
Andruck `n = F_N/(m g) = v²/(g r) + 1`. Mit `v² = 2gh` (Energieerhaltung von h):

$$n_{\text{unten}} = \frac{2gh}{g r} + 1 = \frac{2h}{r} + 1$$

**b)** Für `h = 2,5·r`:
- unten: `n = 2·(2,5r)/r + 1 = 5 + 1 = 6` → **6 g**
- oben: `n_top = 2h/r − 5 = 5 − 5 = 0` → **0 g** (Schwerelosigkeit; genau der Grenzfall).

Interpretation: Am Scheitel spürt ein Fahrgast im Grenzfall Schwerelosigkeit — die Bahn übt keine Kraft aus.

**c)** Im Kreis-Looping wäre die g-Kraft unten sehr hoch (6 g) und der Übergang abrupt. Reale Loopings sind
**klothoidenförmig**: oben kleiner Radius (dort ist v klein → für ausreichende Zentripetalkraft nötig),
unten großer Radius (dort ist v groß → begrenzt die g-Kraft). So bleiben die g-Kräfte über die ganze Fahrt
in einem für Menschen erträglichen Bereich (≈ 3–4 g).

---

## Aufgabe 4 — Reibung

**a)** `v = √(2·9,81·0,25) ≈ 2,21 m/s`.

**b)** Energie ∝ v². Relativer Verlust:

$$1 - \frac{v_{\text{gemessen}}^2}{v_{\text{theorie}}^2} = 1 - \frac{1,9^2}{2,21^2} \approx 1 - 0,74 = 0{,}26$$

→ rund **26 %** der Energie sind bis zum tiefsten Punkt durch Reibung entwertet.

**c)** Energieentwertung: Die Energie ist nicht „verschwunden" (Energieerhaltung gilt weiter), sondern in
**thermische Energie** (Reibungswärme in Lagern/Bahn, Luftwiderstand) umgewandelt. Diese Wärme ist stark
„entwertet": über die Umgebung verteilt und praktisch nicht mehr in nutzbare Bewegungsenergie rückführbar.

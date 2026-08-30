"""Ausgabe: Terminaltabelle, JSON, CSV und ein HTML-Bericht."""

from __future__ import annotations

import csv
import datetime as dt
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from .models import Evaluation
from .util import Color, money, truncate

GRADE_COLORS = {
    "A+": (Color.GREEN, Color.BOLD), "A": (Color.GREEN,), "B": (Color.CYAN,),
    "C": (Color.YELLOW,), "D": (Color.YELLOW,), "E": (Color.MAGENTA,),
    "F": (Color.RED,), "-": (Color.DIM,),
}


def render_console(evaluations: Sequence[Evaluation], color: bool = True,
                   details: bool = False, width: int = 118) -> str:
    c = Color(color)
    lines: List[str] = []
    header = (
        f"{'Note':<5}{'Score':>6}  {'Preis':>9} {'Wert ca.':>10} {'x':>5}  "
        f"{'Quelle':<14}{'Land':<5}Titel"
    )
    lines.append(c(header, Color.BOLD))
    lines.append("─" * width)
    for ev in evaluations:
        ratio = ev.ratio
        title_width = max(20, width - 60)
        row = (
            f"{c(f'{ev.grade:<5}', *GRADE_COLORS.get(ev.grade, ()))}"
            f"{ev.score:>6.0f}  {money(ev.price_eur):>9} {money(ev.estimate.mid):>10} "
            f"{(f'{ratio:.1f}x' if ratio else '  -'):>5}  "
            f"{ev.listing.source[:13]:<14}{(ev.listing.country or '--')[:4]:<5}"
            f"{truncate(ev.listing.title, title_width)}"
        )
        lines.append(row)
        lines.append(c(f"      {ev.verdict}", Color.DIM))
        if ev.risks:
            lines.append(c(f"      ! {'; '.join(ev.risks)}", Color.RED))
        if details:
            for entry in ev.estimate.breakdown:
                lines.append(c(f"      · {entry}", Color.DIM))
            if ev.signals:
                lines.append(c(f"      + {'; '.join(ev.signals)}", Color.GREEN))
        lines.append(c(f"      {ev.listing.url}", Color.BLUE))
        lines.append("")
    if not evaluations:
        lines.append("Keine Angebote gefunden.")
    return "\n".join(lines)


def summary_line(evaluations: Sequence[Evaluation], color: bool = True) -> str:
    c = Color(color)
    if not evaluations:
        return "0 Angebote"
    good = sum(1 for e in evaluations if e.grade in ("A+", "A", "B"))
    sources = sorted({e.listing.source for e in evaluations})
    return c(
        f"{len(evaluations)} Angebote bewertet · {good} davon interessant (Note B oder besser)"
        f" · Quellen: {', '.join(sources)}",
        Color.BOLD,
    )


def write_json(path: Path, evaluations: Iterable[Evaluation], meta: Dict[str, Any] | None = None) -> Path:
    payload = {
        "erstellt": dt.datetime.now().isoformat(timespec="seconds"),
        "meta": meta or {},
        "angebote": [e.to_dict() for e in evaluations],
    }
    path = Path(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), "utf-8")
    return path


def write_csv(path: Path, evaluations: Iterable[Evaluation]) -> Path:
    path = Path(path)
    fields = ["grade", "score", "preis_eur", "wert_eur", "verhaeltnis", "quelle",
              "land", "titel", "url", "risiken", "signale"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(fields)
        for ev in evaluations:
            writer.writerow([
                ev.grade, round(ev.score, 1), ev.price_eur, ev.estimate.mid,
                round(ev.ratio, 2) if ev.ratio else "", ev.listing.source,
                ev.listing.country, ev.listing.title, ev.listing.url,
                " | ".join(ev.risks), " | ".join(ev.signals),
            ])
    return path


_HTML_TEMPLATE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MTG Sammlungs-Report</title>
<style>
:root {{ color-scheme: light dark; --bg:#fbfaf7; --fg:#1c1b19; --card:#fff; --line:#e4e0d8; --dim:#6b6660; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#16151a; --fg:#eceaf2; --card:#211f28; --line:#332f3d; --dim:#a09aab; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:24px; background:var(--bg); color:var(--fg);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }}
h1 {{ font-size:22px; margin:0 0 4px; }}
.meta {{ color:var(--dim); font-size:13px; margin-bottom:20px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:14px 16px; margin-bottom:12px; }}
.head {{ display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; }}
.grade {{ font-weight:700; font-size:18px; padding:2px 10px; border-radius:6px; color:#fff; }}
.g-Aplus,.g-A {{ background:#1f8a4c; }} .g-B {{ background:#2b7fb8; }}
.g-C,.g-D {{ background:#b4881f; }} .g-E {{ background:#a4562a; }}
.g-F,.g-none {{ background:#9a3232; }}
.title {{ font-weight:600; flex:1 1 320px; }}
.title a {{ color:inherit; text-decoration:none; }} .title a:hover {{ text-decoration:underline; }}
.nums {{ font-variant-numeric:tabular-nums; color:var(--dim); font-size:14px; }}
.verdict {{ margin:8px 0 0; }}
ul {{ margin:8px 0 0; padding-left:18px; color:var(--dim); font-size:13px; }}
.risk {{ color:#c0392b; }} .signal {{ color:#1f8a4c; }}
table.sum {{ border-collapse:collapse; margin-bottom:20px; font-size:14px; }}
table.sum td {{ padding:2px 14px 2px 0; }}
</style></head><body>
<h1>MTG Sammlungs-Report</h1>
<div class="meta">{meta}</div>
{cards}
<div class="meta">Schaetzwerte sind Heuristiken auf Basis des Anzeigentexts - keine Preisgarantie.</div>
</body></html>
"""


def write_html(path: Path, evaluations: Sequence[Evaluation],
               meta: Dict[str, Any] | None = None) -> Path:
    cards: List[str] = []
    for ev in evaluations:
        grade_class = {"A+": "g-Aplus", "-": "g-none"}.get(ev.grade, f"g-{ev.grade}")
        ratio = f"{ev.ratio:.1f}x" if ev.ratio else "–"
        items = "".join(
            f"<li>{html.escape(entry)}</li>" for entry in ev.estimate.breakdown
        )
        risks = "".join(f"<li class='risk'>{html.escape(r)}</li>" for r in ev.risks)
        signals = "".join(f"<li class='signal'>{html.escape(s)}</li>" for s in ev.signals)
        cards.append(
            f"<div class='card'><div class='head'>"
            f"<span class='grade {grade_class}'>{html.escape(ev.grade)}</span>"
            f"<span class='title'><a href='{html.escape(ev.listing.url)}' target='_blank' rel='noopener'>"
            f"{html.escape(ev.listing.title)}</a></span>"
            f"<span class='nums'>{html.escape(money(ev.price_eur))} · Wert ca. "
            f"{html.escape(money(ev.estimate.mid))} · {ratio} · Score {ev.score:.0f}</span>"
            f"</div>"
            f"<p class='verdict'>{html.escape(ev.verdict)}</p>"
            f"<div class='nums'>{html.escape(ev.listing.source)} · "
            f"{html.escape(ev.listing.location or ev.listing.country or '')}</div>"
            f"<ul>{items}{risks}{signals}</ul></div>"
        )
    meta_text = " · ".join(
        f"{key}: {value}" for key, value in (meta or {}).items()
    ) or dt.datetime.now().strftime("%d.%m.%Y %H:%M")
    path = Path(path)
    path.write_text(
        _HTML_TEMPLATE.format(meta=html.escape(meta_text), cards="\n".join(cards)), "utf-8"
    )
    return path

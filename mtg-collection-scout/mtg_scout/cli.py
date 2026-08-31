"""Kommandozeile des MTG Collection Scout."""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from . import __version__
from .analyze import Evaluator
from .config import cache_dir, config_path, data_dir, load_config, write_example_config
from .currency import CurrencyConverter
from .models import Evaluation, Listing
from .net import FetchError, HttpClient
from .pricing import ScryfallPrices
from .report import render_console, summary_line, write_csv, write_html, write_json
from .sources import SearchQuery, available_source_names, build_sources, load_listings_file
from .store import Store
from .vision import ClaudeVision, PhotoFacts, VisionError, build_ocr
from .vision import images as vision_images
from .util import Color, money, supports_color

log = logging.getLogger("mtg_scout")

GRADE_ORDER = ["A+", "A", "B", "C", "D", "E", "F", "-"]


# --------------------------------------------------------------------- Setup
def _common_parser() -> argparse.ArgumentParser:
    """Optionen, die vor und nach dem Unterbefehl erlaubt sind."""
    common = argparse.ArgumentParser(add_help=False, argument_default=argparse.SUPPRESS)
    common.add_argument("-v", "--verbose", action="count", help="mehr Logausgabe")
    common.add_argument("--keine-farben", dest="no_color", action="store_true",
                        help="ANSI-Farben abschalten")
    common.add_argument("--config", type=Path, help="Pfad zur Config-Datei")
    return common


COMMON_DEFAULTS = {"verbose": 0, "no_color": False, "config": None}


def build_parser() -> argparse.ArgumentParser:
    common = _common_parser()
    parser = argparse.ArgumentParser(
        parents=[common],
        prog="mtg-scout",
        description="Findet Magic-Sammlungen auf Online-Marktplaetzen und bewertet sie.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiele:\n"
            "  mtg-scout suchen --quelle demo --details\n"
            "  mtg-scout suchen -q kleinanzeigen -s 'magic sammlung' --max-preis 800 --html report.html\n"
            "  mtg-scout suchen -q ebay --markt EBAY_DE,EBAY_US --min-note B\n"
            "  mtg-scout bewerten --text 'Magic Sammlung 3000 Karten Revised' --preis 250\n"
            "  mtg-scout preise --aktualisieren\n"
        ),
    )
    parser.add_argument("--version", action="version", version=f"mtg-scout {__version__}")

    sub = parser.add_subparsers(dest="command")

    search = sub.add_parser("suchen", parents=[common],
                            help="Marktplaetze durchsuchen und bewerten")
    _add_search_arguments(search)
    search.set_defaults(func=cmd_search)

    watch = sub.add_parser("beobachten", parents=[common], help="wiederholt suchen und nur neue Treffer zeigen")
    _add_search_arguments(watch)
    watch.add_argument("--intervall", type=int, default=30, help="Minuten zwischen Laeufen (Standard 30)")
    watch.add_argument("--laeufe", type=int, default=0, help="Anzahl Durchlaeufe (0 = endlos)")
    watch.set_defaults(func=cmd_watch)

    rate = sub.add_parser("bewerten", parents=[common], help="einzelnen Anzeigentext oder eine Datei bewerten")
    rate.add_argument("--text", default="", help="Anzeigentext (Titel + Beschreibung)")
    rate.add_argument("--preis", type=float, default=None, help="Preis der Anzeige")
    rate.add_argument("--waehrung", default="EUR", help="Waehrung des Preises (Standard EUR)")
    rate.add_argument("--datei", type=Path, default=None, help="JSON/CSV mit Angeboten")
    rate.add_argument("--bild", action="append", type=Path, default=[],
                      help="Foto der Anzeige (mehrfach moeglich)")
    rate.add_argument("--fotos-ocr", action="store_true",
                      help="Fotos per OCR statt mit Claude auswerten")
    rate.add_argument("--vision-modell", default="", help="Claude-Modell fuer die Bildanalyse")
    rate.add_argument("--details", action="store_true", help="Wertherleitung anzeigen")
    rate.add_argument("--json", dest="json_out", type=Path, default=None)
    rate.add_argument("--html", dest="html_out", type=Path, default=None)
    rate.set_defaults(func=cmd_rate)

    prices = sub.add_parser("preise", parents=[common], help="Kartenpreise von Scryfall spiegeln")
    prices.add_argument("--aktualisieren", action="store_true", help="Bulk-Daten neu laden")
    prices.add_argument("--karte", default="", help="Preis einer einzelnen Karte abfragen")
    prices.set_defaults(func=cmd_prices)

    sources = sub.add_parser("quellen", parents=[common], help="verfuegbare Quellen anzeigen")
    sources.set_defaults(func=cmd_sources)

    config_cmd = sub.add_parser("config", parents=[common], help="Beispiel-Konfiguration schreiben")
    config_cmd.add_argument("--beispiel", action="store_true", help="Config-Datei anlegen")
    config_cmd.set_defaults(func=cmd_config)

    status = sub.add_parser("status", parents=[common], help="Datenbank- und Cache-Status")
    status.set_defaults(func=cmd_status)
    return parser


def _add_search_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-q", "--quelle", default="", help="Quellen, kommagetrennt (oder 'alle')")
    parser.add_argument("-s", "--suchbegriff", action="append", default=[],
                        help="Suchbegriff (mehrfach moeglich)")
    parser.add_argument("--markt", default="", help="eBay-Marktplaetze, z.B. EBAY_DE,EBAY_US")
    parser.add_argument("--limit", type=int, default=None, help="max. Angebote je Quelle")
    parser.add_argument("--seiten", type=int, default=2, help="Seiten je Suchbegriff (HTML-Quellen)")
    parser.add_argument("--min-preis", type=float, default=None)
    parser.add_argument("--max-preis", type=float, default=None)
    parser.add_argument("--plz", default="", help="Postleitzahl fuer regionale Suche")
    parser.add_argument("--umkreis", type=int, default=None, help="Umkreis in km")
    parser.add_argument("--min-note", default="", choices=[""] + GRADE_ORDER,
                        help="nur Angebote ab dieser Note anzeigen")
    parser.add_argument("--min-score", type=float, default=None)
    parser.add_argument("--sortierung", default="score", choices=["score", "preis", "wert", "verhaeltnis"])
    parser.add_argument("--nur-neue", action="store_true", help="bereits gesehene Angebote ausblenden")
    parser.add_argument("--details", action="store_true", help="Wertherleitung anzeigen")
    parser.add_argument("--datei", type=Path, default=None, help="Datei fuer die Quelle 'datei'")
    parser.add_argument("--json", dest="json_out", type=Path, default=None)
    parser.add_argument("--csv", dest="csv_out", type=Path, default=None)
    parser.add_argument("--html", dest="html_out", type=Path, default=None)
    parser.add_argument("--fotos", action="store_true",
                        help="Fotos der besten Treffer mit Claude auswerten (API-Kosten)")
    parser.add_argument("--fotos-ocr", action="store_true",
                        help="Fotos per OCR (tesseract) auswerten - ohne API-Schluessel")
    parser.add_argument("--fotos-limit", type=int, default=None,
                        help="wie viele Anzeigen bebildert geprueft werden (Standard 8)")
    parser.add_argument("--fotos-pro-anzeige", type=int, default=None,
                        help="maximale Anzahl Bilder je Anzeige (Standard 3)")
    parser.add_argument("--vision-modell", default="",
                        help="Claude-Modell fuer die Bildanalyse (Standard claude-opus-5)")
    parser.add_argument("--offline", action="store_true", help="nur Cache/lokale Daten nutzen")
    parser.add_argument("--ignore-robots", action="store_true",
                        help="robots.txt ignorieren (bewusste Entscheidung, Standard: beachten)")


# ------------------------------------------------------------------ Kontext
class Context:
    """Gemeinsame Bausteine eines Laufs."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: Dict[str, Any] = load_config(args.config)
        http_cfg = self.config.get("http", {})
        self.client = HttpClient(
            cache_dir=cache_dir() / "http",
            delay=float(http_cfg.get("delay_seconds", 1.5)),
            timeout=float(http_cfg.get("timeout_seconds", 20.0)),
            retries=int(http_cfg.get("retries", 3)),
            cache_ttl=float(http_cfg.get("cache_ttl_seconds", 900)),
            respect_robots=bool(http_cfg.get("respect_robots", True))
            and not getattr(args, "ignore_robots", False),
            offline=bool(getattr(args, "offline", False)),
            host_failure_limit=int(http_cfg.get("host_failure_limit", 2)),
        )
        self.converter = CurrencyConverter(self.client, cache_dir() / "kurse.json")
        self.store = Store(data_dir() / "mtg-scout.sqlite3")
        self.prices = ScryfallPrices(self.store, self.client)
        self.card_index = self.prices.index()
        self.evaluator = Evaluator(self.config, self.card_index, self.converter)
        self.color = not args.no_color and supports_color()
        self.sources_by_name: Dict[str, Any] = {}

    def close(self) -> None:
        self.store.close()

    # ------------------------------------------------------------ Fotoauswertung
    def vision_settings(self) -> Dict[str, Any]:
        args = self.args
        cfg = dict(self.config.get("vision", {}))
        if getattr(args, "fotos", False):
            cfg["enabled"] = True
        if getattr(args, "fotos_ocr", False):
            cfg["use_ocr"] = True
        if getattr(args, "fotos_limit", None):
            cfg["max_listings"] = args.fotos_limit
        if getattr(args, "fotos_pro_anzeige", None):
            cfg["max_images_per_listing"] = args.fotos_pro_anzeige
        if getattr(args, "vision_modell", ""):
            cfg["model"] = args.vision_modell
            cfg["enabled"] = True
        return cfg

    def analyzer(self) -> tuple[Optional[ClaudeVision], Optional[Any]]:
        """(Claude-Bildanalyse, OCR-Alternative) - je None, wenn nicht nutzbar."""
        settings = self.vision_settings()
        claude: Optional[ClaudeVision] = None
        if settings.get("enabled"):
            candidate = ClaudeVision(
                model=settings.get("model", "claude-opus-5"),
                api_key=settings.get("api_key", "") or None,
                max_images=int(settings.get("max_images_per_listing", 3)),
            )
            ok, reason = candidate.available()
            if ok:
                claude = candidate
            else:
                print(f"· Bildanalyse mit Claude nicht moeglich: {reason}", file=sys.stderr)
        ocr = build_ocr(self.card_index) if settings.get("use_ocr") else None
        if settings.get("use_ocr") and ocr is None:
            print("· OCR nicht moeglich: tesseract ist nicht installiert", file=sys.stderr)
        if claude is None and ocr is None and settings.get("enabled"):
            print("· Fotoauswertung wird uebersprungen - Angebote werden nur aus dem "
                  "Text bewertet.", file=sys.stderr)
        return claude, ocr

    def query(self) -> SearchQuery:
        args = self.args
        cfg = self.config
        markets = [m.strip().upper() for m in (args.markt or "").split(",") if m.strip()]
        return SearchQuery(
            terms=args.suchbegriff or list(cfg.get("queries", [])),
            limit=args.limit or int(cfg.get("limit_per_source", 50)),
            min_price_eur=args.min_preis if args.min_preis is not None else cfg.get("min_price_eur"),
            max_price_eur=args.max_preis if args.max_preis is not None else cfg.get("max_price_eur"),
            markets=markets or list(cfg.get("markets", [])),
            postal_code=args.plz,
            radius_km=args.umkreis,
            max_pages=max(1, args.seiten),
        )


# ------------------------------------------------------------------ Befehle
def cmd_search(args: argparse.Namespace) -> int:
    ctx = Context(args)
    try:
        evaluations = run_search(ctx)
        _output(ctx, evaluations)
        return 0 if evaluations else 1
    finally:
        ctx.close()


def run_search(ctx: Context) -> List[Evaluation]:
    args = ctx.args
    names = [n for n in (args.quelle or "").split(",") if n.strip()] or list(
        ctx.config.get("sources", ["demo"])
    )
    sources = build_sources(names, ctx.config, ctx.client, ctx.converter, args.datei)
    ctx.sources_by_name = {source.name: source for source in sources}
    query = ctx.query()

    listings: List[Listing] = []
    for source in sources:
        ok, note = source.available()
        if not ok:
            print(f"· {source.label}: uebersprungen - {note}", file=sys.stderr)
            continue
        if note:
            log.info("%s: %s", source.label, note)
        try:
            found = source.search(query)
        except FetchError as exc:
            print(f"· {source.label}: Fehler - {exc}", file=sys.stderr)
            continue
        log.info("%s: %s Angebote", source.label, len(found))
        listings.extend(found)

    evaluations = [ctx.evaluator.evaluate(listing) for listing in listings]
    evaluations = _filter(ctx, evaluations)
    evaluations = _sort(evaluations, args.sortierung)
    evaluations = analyze_photos(ctx, evaluations)

    for ev in evaluations:
        ctx.store.mark_seen(ev.listing.listing_id, ev.listing.source, ev.listing.title,
                            ev.listing.url, ev.price_eur, ev.score)
    return evaluations


def analyze_photos(ctx: Context, evaluations: List[Evaluation]) -> List[Evaluation]:
    """Die aussichtsreichsten Treffer zusaetzlich anhand ihrer Fotos bewerten.

    Bewusst nur fuer die Spitze der Liste: jede Bildanalyse kostet Zeit und - bei
    Claude - Geld. Die Reihenfolge wird danach neu berechnet.
    """
    settings = ctx.vision_settings()
    if not settings.get("enabled") and not settings.get("use_ocr"):
        return evaluations
    claude, ocr = ctx.analyzer()
    if claude is None and ocr is None:
        return evaluations

    limit = int(settings.get("max_listings", 8))
    per_listing = int(settings.get("max_images_per_listing", 3))
    candidates = [ev for ev in evaluations if ev.grade != "-"][:limit]
    if not candidates:
        return evaluations
    engine = "Claude " + claude.model if claude else "OCR (tesseract)"
    print(f"· Fotoauswertung mit {engine} fuer {len(candidates)} Anzeige(n) ...",
          file=sys.stderr)

    updated: Dict[str, Evaluation] = {}
    for ev in candidates:
        listing = ev.listing
        source = ctx.sources_by_name.get(listing.source)
        if settings.get("fetch_detail_pages", True) and hasattr(source, "fetch_detail"):
            try:
                source.fetch_detail(listing)
            except FetchError as exc:
                log.info("Detailseite nicht ladbar: %s", exc)
        payloads = vision_images.download(ctx.client, listing.images, limit=per_listing)
        if not payloads:
            continue
        photos = _run_analyzers(claude, ocr, payloads, listing.title)
        if not photos:
            continue
        updated[listing.listing_id] = ctx.evaluator.evaluate(listing, photos)

    if not updated:
        return evaluations
    merged = [updated.get(ev.listing.listing_id, ev) for ev in evaluations]
    return _sort(merged, ctx.args.sortierung)


def _run_analyzers(claude: Optional[ClaudeVision], ocr: Optional[Any],
                   payloads: List[bytes], title: str) -> Optional[PhotoFacts]:
    """Erst Claude, bei Fehler OCR - je nachdem, was verfuegbar ist."""
    if claude is not None:
        try:
            return claude.analyze(vision_images.to_blocks(payloads), context=title)
        except VisionError as exc:
            print(f"· Bildanalyse fehlgeschlagen: {exc}", file=sys.stderr)
    if ocr is not None:
        return ocr.analyze(payloads, context=title)
    return None


def _filter(ctx: Context, evaluations: List[Evaluation]) -> List[Evaluation]:
    args = ctx.args
    query = ctx.query()
    result = []
    for ev in evaluations:
        if args.nur_neue and not ctx.store.is_new(ev.listing.listing_id):
            continue
        if args.min_score is not None and ev.score < args.min_score:
            continue
        if args.min_note and GRADE_ORDER.index(ev.grade) > GRADE_ORDER.index(args.min_note):
            continue
        if ev.price_eur is not None:
            if query.min_price_eur and ev.price_eur < query.min_price_eur:
                continue
            if query.max_price_eur and ev.price_eur > query.max_price_eur:
                continue
        result.append(ev)
    return result


def _sort(evaluations: List[Evaluation], key: str) -> List[Evaluation]:
    if key == "preis":
        return sorted(evaluations, key=lambda e: (e.price_eur is None, e.price_eur or 0))
    if key == "wert":
        return sorted(evaluations, key=lambda e: e.estimate.mid, reverse=True)
    if key == "verhaeltnis":
        return sorted(evaluations, key=lambda e: e.ratio or 0, reverse=True)
    return sorted(evaluations, key=lambda e: e.score, reverse=True)


def _output(ctx: Context, evaluations: Sequence[Evaluation]) -> None:
    args = ctx.args
    print(render_console(evaluations, color=ctx.color, details=args.details))
    print(summary_line(evaluations, color=ctx.color))
    meta = {
        "Angebote": len(evaluations),
        "Quellen": ", ".join(sorted({e.listing.source for e in evaluations})) or "-",
        "Kartenpreise": f"{ctx.store.card_count()} Karten im lokalen Spiegel",
    }
    if getattr(args, "json_out", None):
        print(f"JSON geschrieben: {write_json(args.json_out, evaluations, meta)}")
    if getattr(args, "csv_out", None):
        print(f"CSV geschrieben: {write_csv(args.csv_out, evaluations)}")
    if getattr(args, "html_out", None):
        print(f"HTML-Report geschrieben: {write_html(args.html_out, evaluations, meta)}")


def cmd_watch(args: argparse.Namespace) -> int:
    args.nur_neue = True
    runs = 0
    while True:
        ctx = Context(args)
        try:
            evaluations = run_search(ctx)
            stamp = time.strftime("%d.%m.%Y %H:%M")
            if evaluations:
                print(f"\n=== {stamp}: {len(evaluations)} neue Angebote ===")
                _output(ctx, evaluations)
            else:
                print(f"{stamp}: keine neuen Angebote")
        finally:
            ctx.close()
        runs += 1
        if args.laeufe and runs >= args.laeufe:
            return 0
        try:
            time.sleep(max(60, args.intervall * 60))
        except KeyboardInterrupt:
            print("\nBeobachtung beendet.")
            return 0


def cmd_rate(args: argparse.Namespace) -> int:
    args.offline = getattr(args, "offline", False)
    args.ignore_robots = False
    args.fotos = bool(args.bild) and not args.fotos_ocr
    args.fotos_limit = None
    args.fotos_pro_anzeige = None
    ctx = Context(args)
    try:
        listings: List[Listing] = []
        if args.datei:
            listings.extend(load_listings_file(args.datei))
        if args.text:
            title, _, description = args.text.partition("\n")
            listings.append(
                Listing(source="eingabe", title=title, url="", price=args.preis,
                        currency=args.waehrung, description=description)
            )
        if not listings:
            print("Nichts zu bewerten - --text, --datei oder --bild angeben.", file=sys.stderr)
            return 2

        photos = _photos_from_files(ctx, args.bild, listings[0].title if listings else "")
        evaluations = _sort(
            [ctx.evaluator.evaluate(listing, photos if index == 0 else None)
             for index, listing in enumerate(listings)],
            "score",
        )
        args.details = True
        args.csv_out = None
        _output(ctx, evaluations)
        return 0
    finally:
        ctx.close()


def _photos_from_files(ctx: Context, paths: List[Path], title: str) -> Optional[PhotoFacts]:
    """Lokale Bilddateien auswerten (Befehl 'bewerten --bild')."""
    if not paths:
        return None
    ctx.args.fotos = True
    claude, ocr = ctx.analyzer()
    if claude is None and ocr is None:
        return None
    payloads = vision_images.load_local(paths)
    if not payloads:
        print("· Keine lesbaren Bilddateien gefunden.", file=sys.stderr)
        return None
    return _run_analyzers(claude, ocr, payloads, title)


def cmd_prices(args: argparse.Namespace) -> int:
    args.offline = False
    args.ignore_robots = False
    ctx = Context(args)
    try:
        if args.aktualisieren:
            print("Lade Scryfall-Bulkdaten (rund 100-200 MB Download, dauert etwas) ...")
            try:
                count = ctx.prices.refresh()
            except FetchError as exc:
                print(f"Aktualisierung fehlgeschlagen: {exc}", file=sys.stderr)
                return 1
            print(f"{count} Kartenpreise gespeichert in {ctx.store.path}")
        if args.karte:
            price = ctx.prices.price_of(args.karte)
            print(f"{args.karte}: {money(price) if price else 'kein Preis gefunden'}")
        if not args.aktualisieren and not args.karte:
            print(f"{ctx.store.card_count()} Karten im lokalen Spiegel "
                  f"(--aktualisieren laedt sie neu von Scryfall)")
        return 0
    finally:
        ctx.close()


def cmd_sources(args: argparse.Namespace) -> int:
    args.offline = True
    args.ignore_robots = False
    ctx = Context(args)
    c = Color(ctx.color)
    try:
        print(c("Verfuegbare Quellen:", Color.BOLD))
        for source in build_sources(available_source_names(), ctx.config, ctx.client, ctx.converter):
            ok, note = source.available()
            marker = c("✓", Color.GREEN) if ok else c("✗", Color.RED)
            countries = ",".join(source.countries) if source.countries else "-"
            print(f" {marker} {source.name:<14} {source.label:<32} Laender: {countries}")
            if note:
                print(f"     {c(note, Color.DIM)}")
        return 0
    finally:
        ctx.close()


def cmd_config(args: argparse.Namespace) -> int:
    if args.beispiel:
        path = write_example_config(args.config)
        print(f"Beispiel-Konfiguration geschrieben: {path}")
    else:
        print(f"Konfigurationsdatei: {config_path()}"
              f"{'' if config_path().exists() else ' (noch nicht vorhanden)'}")
        print("Anlegen mit: mtg-scout config --beispiel")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    args.offline = True
    args.ignore_robots = False
    ctx = Context(args)
    try:
        stats = ctx.store.stats()
        print(f"Datenbank:       {ctx.store.path}")
        print(f"Kartenpreise:    {stats['karten']}")
        print(f"Gesehene Anzeigen: {stats['gesehene_angebote']}")
        print(f"HTTP-Cache:      {cache_dir() / 'http'}")
        print(f"Wechselkurse:    {'live (EZB)' if ctx.converter.live else 'Fallback-Tabelle'}")
        return 0
    finally:
        ctx.close()


# --------------------------------------------------------------------- main
def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    for key, default in COMMON_DEFAULTS.items():
        if not hasattr(args, key):
            setattr(args, key, default)
    logging.basicConfig(
        level=logging.WARNING - 10 * min(2, args.verbose),
        format="%(levelname)s %(name)s: %(message)s",
    )
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\nAbgebrochen.", file=sys.stderr)
        return 130
    except BrokenPipeError:
        # Ausgabe wurde abgeschnitten (z.B. "| head") - kein Fehlerfall.
        # stdout auf devnull umbiegen, sonst meckert Python beim Beenden.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0

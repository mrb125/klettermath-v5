"""HTTP-Client: hoefliches Rate-Limit, Retries, Disk-Cache, robots.txt-Pruefung.

Bewusst nur Standardbibliothek - das Tool laeuft ohne pip install.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path
from typing import Any, Dict, Optional

from . import USER_AGENT

log = logging.getLogger("mtg_scout.net")


class FetchError(RuntimeError):
    """Netzwerk-/HTTP-Fehler, der nach Retries bestehen bleibt."""


class HttpClient:
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        delay: float = 1.5,
        timeout: float = 20.0,
        retries: int = 3,
        cache_ttl: float = 900.0,
        respect_robots: bool = True,
        offline: bool = False,
        user_agent: str = USER_AGENT,
        host_failure_limit: int = 2,
    ) -> None:
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.cache_ttl = cache_ttl
        self.respect_robots = respect_robots
        self.offline = offline
        self.user_agent = user_agent
        self.host_failure_limit = max(1, host_failure_limit)
        self._last_request: Dict[str, float] = {}
        self._host_failures: Dict[str, int] = {}
        self._robots: Dict[str, Optional[urllib.robotparser.RobotFileParser]] = {}
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- caching
    def _cache_path(self, key: str) -> Optional[Path]:
        if not self.cache_dir:
            return None
        return self.cache_dir / (hashlib.sha1(key.encode("utf-8")).hexdigest() + ".cache")

    def _cache_read(self, key: str) -> Optional[str]:
        path = self._cache_path(key)
        if not path or not path.exists():
            return None
        if not self.offline and (time.time() - path.stat().st_mtime) > self.cache_ttl:
            return None
        try:
            return path.read_text("utf-8")
        except OSError:
            return None

    def _cache_write(self, key: str, body: str) -> None:
        path = self._cache_path(key)
        if not path:
            return
        try:
            path.write_text(body, "utf-8")
        except OSError as exc:      # Cache ist optional - nie fatal
            log.debug("Cache nicht schreibbar: %s", exc)

    # ----------------------------------------------------------------- robots
    def robots_allows(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parts = urllib.parse.urlsplit(url)
        if self._host_is_dead(parts.netloc):
            return True          # der Abruf selbst bricht gleich ohnehin ab
        base = f"{parts.scheme}://{parts.netloc}"
        if base not in self._robots:
            parser: Optional[urllib.robotparser.RobotFileParser] = urllib.robotparser.RobotFileParser()
            parser.set_url(base + "/robots.txt")
            try:
                parser.read()
            except Exception as exc:            # robots nicht erreichbar -> nicht blockieren
                log.debug("robots.txt nicht lesbar fuer %s: %s", base, exc)
                parser = None
            self._robots[base] = parser
        parser = self._robots[base]
        return True if parser is None else parser.can_fetch(self.user_agent, url)

    # ------------------------------------------------------------------ fetch
    def _note_failure(self, host: str) -> None:
        """Fehlgeschlagene Hosts zaehlen - siehe _host_is_dead()."""
        self._host_failures[host] = self._host_failures.get(host, 0) + 1

    def _host_is_dead(self, host: str) -> bool:
        """Nach mehreren erfolglosen Anlaeufen wird ein Host im Lauf uebersprungen.

        Ohne das wartet ein Lauf bei fehlender Internetverbindung fuer jede
        einzelne URL die komplette Retry-Kette ab.
        """
        return self._host_failures.get(host, 0) >= self.host_failure_limit

    def _throttle(self, host: str) -> None:
        last = self._last_request.get(host)
        if last is not None:
            wait = self.delay - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
        self._last_request[host] = time.time()

    def fetch(
        self,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
        method: str = "GET",
        use_cache: bool = True,
    ) -> str:
        cache_key = f"{method} {url} {(data or b'').decode('utf-8', 'replace')}"
        if use_cache and method == "GET":
            cached = self._cache_read(cache_key)
            if cached is not None:
                log.debug("Cache-Treffer: %s", url)
                return cached
        if self.offline:
            raise FetchError(f"Offline-Modus: {url} nicht im Cache")
        if method == "GET" and not self.robots_allows(url):
            raise FetchError(
                f"robots.txt der Seite verbietet den Abruf von {url} "
                f"(bewusste Ausnahme: --ignore-robots)"
            )

        host = urllib.parse.urlsplit(url).netloc
        if self._host_is_dead(host):
            raise FetchError(
                f"{host} ist in diesem Lauf nicht erreichbar - uebersprungen"
            )
        req_headers = {
            "User-Agent": self.user_agent,
            "Accept": "*/*",
            "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip",
        }
        req_headers.update(headers or {})

        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            self._throttle(host)
            request = urllib.request.Request(url, data=data, headers=req_headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                    if response.headers.get("Content-Encoding") == "gzip":
                        raw = gzip.decompress(raw)
                    charset = response.headers.get_content_charset() or "utf-8"
                    body = raw.decode(charset, "replace")
                if use_cache and method == "GET":
                    self._cache_write(cache_key, body)
                self._host_failures.pop(host, None)
                return body
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code in (400, 401, 403, 404):     # kein Retry bei Client-Fehlern
                    detail = exc.read().decode("utf-8", "replace")[:400]
                    raise FetchError(f"HTTP {exc.code} fuer {url}: {detail}") from exc
                log.debug("HTTP %s (Versuch %s/%s)", exc.code, attempt, self.retries)
            except Exception as exc:
                last_error = exc
                log.debug("Netzwerkfehler %s (Versuch %s/%s)", exc, attempt, self.retries)
            time.sleep(min(2 ** (attempt - 1), 8))   # 1s, 2s, 4s ...
        self._note_failure(host)
        raise FetchError(f"Abruf von {url} fehlgeschlagen: {last_error}")

    def fetch_bytes(self, url: str, max_bytes: int = 5_000_000,
                    use_cache: bool = True) -> bytes:
        """Binaerdaten (Bilder, Bulk-Dateien) laden - ohne Textdekodierung."""
        cache_path = None
        if self.cache_dir and use_cache:
            binary_dir = self.cache_dir / "bin"
            binary_dir.mkdir(parents=True, exist_ok=True)
            cache_path = binary_dir / hashlib.sha1(url.encode("utf-8")).hexdigest()
            if cache_path.exists():
                return cache_path.read_bytes()
        if self.offline:
            raise FetchError(f"Offline-Modus: {url} nicht im Cache")
        if not self.robots_allows(url):
            raise FetchError(f"robots.txt verbietet den Abruf von {url}")

        host = urllib.parse.urlsplit(url).netloc
        if self._host_is_dead(host):
            raise FetchError(f"{host} ist in diesem Lauf nicht erreichbar - uebersprungen")
        self._throttle(host)
        request = urllib.request.Request(
            url, headers={"User-Agent": self.user_agent, "Accept": "image/*,*/*"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read(max_bytes + 1)
        except Exception as exc:
            self._note_failure(host)
            raise FetchError(f"Bild {url} nicht ladbar: {exc}") from exc
        if len(payload) > max_bytes:
            raise FetchError(f"Bild {url} groesser als {max_bytes} Bytes")
        if cache_path:
            try:
                cache_path.write_bytes(payload)
            except OSError as exc:
                log.debug("Bildcache nicht schreibbar: %s", exc)
        return payload

    def fetch_json(self, url: str, **kwargs: Any) -> Any:
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("Accept", "application/json")
        body = self.fetch(url, headers=headers, **kwargs)
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise FetchError(f"Ungueltiges JSON von {url}: {exc}") from exc

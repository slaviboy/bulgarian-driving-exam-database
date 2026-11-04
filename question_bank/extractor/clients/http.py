"""A polite HTTP client: per-host rate limiting, retries with back-off, conditional and resumable requests."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import random
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import httpx

from question_bank.config import Settings

log = logging.getLogger(__name__)

RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504})
CHUNK_SIZE = 64 * 1024


class HttpError(RuntimeError):
    """A request failed permanently (after retries) or returned an unexpected status."""

    def __init__(self, message: str, *, url: str, status: int | None = None):
        super().__init__(message)
        self.url = url
        self.status = status


class IntegrityError(HttpError):
    """A downloaded file does not match its expected size or SHA-256."""


class RateLimiter:
    """Guarantees a minimum interval between two requests to the same host."""

    def __init__(
        self,
        host_intervals: Mapping[str, float],
        default_interval: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._intervals = dict(host_intervals)
        self._default = default_interval
        self._clock = clock
        self._sleep = sleep
        self._last: dict[str, float] = {}

    def interval_for(self, host: str) -> float:
        return self._intervals.get(host, self._default)

    def wait(self, host: str) -> float:
        """Block until a request to `host` is allowed; returns the time slept."""
        interval = self.interval_for(host)
        last = self._last.get(host)
        slept = 0.0
        if last is not None:
            remaining = interval - (self._clock() - last)
            if remaining > 0:
                self._sleep(remaining)
                slept = remaining
        self._last[host] = self._clock()
        return slept


@dataclass(frozen=True)
class DownloadResult:
    url: str
    path: Path
    bytes: int
    sha256: str
    etag: str | None
    last_modified: str | None
    resumed: bool


def _retry_after_seconds(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if not value:
        return None
    if value.isdigit():
        return float(value)
    try:
        return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
    except (TypeError, ValueError):
        return None


class HttpClient:
    """Synchronous client used by every extractor; never faster than the configured per-host interval."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._settings = settings
        self._sleep = sleep
        self._limiter = RateLimiter(settings.host_intervals, settings.default_interval_seconds, clock, sleep)
        self._client = httpx.Client(
            headers={"User-Agent": settings.user_agent, "Accept-Language": "bg,en;q=0.5"},
            timeout=httpx.Timeout(settings.timeout_seconds, connect=20.0),
            follow_redirects=True,
            transport=transport,
        )
        self.request_count = 0

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ------------------------------------------------------------------ core

    def _backoff(self, attempt: int) -> float:
        return self._settings.backoff_base_seconds * (2**attempt) + random.uniform(0, 0.5)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
        stream: bool = False,
        ok_status: frozenset[int] = frozenset({200}),
    ) -> httpx.Response:
        """Send a request with retries. Returns a response whose status is in `ok_status`."""
        host = urlsplit(url).hostname or ""
        max_retries = self._settings.max_retries
        for attempt in range(max_retries + 1):
            self._limiter.wait(host)
            self.request_count += 1
            try:
                request = self._client.build_request(method, url, headers=headers, json=json_body)
                response = self._client.send(request, stream=stream)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                if attempt >= max_retries:
                    raise HttpError(f"{method} {url} failed: {exc!r}", url=url) from exc
                delay = self._backoff(attempt)
                log.warning(
                    "transport error, retrying", extra={"url": url, "attempt": attempt, "delay": delay}
                )
                self._sleep(delay)
                continue

            if response.status_code in ok_status:
                return response
            if response.status_code in RETRYABLE_STATUS and attempt < max_retries:
                delay = _retry_after_seconds(response) or self._backoff(attempt)
                log.warning(
                    "retryable status",
                    extra={"url": url, "status": response.status_code, "attempt": attempt, "delay": delay},
                )
                response.close()
                self._sleep(delay)
                continue
            status = response.status_code
            response.close()
            raise HttpError(f"{method} {url} returned HTTP {status}", url=url, status=status)
        raise AssertionError("unreachable")  # pragma: no cover

    # ------------------------------------------------------------- helpers

    def get_text(self, url: str, *, encoding: str = "utf-8") -> str:
        response = self.request("GET", url)
        return response.content.decode(encoding)

    def get_bytes(self, url: str) -> bytes:
        return self.request("GET", url).content

    def get_json(self, url: str) -> Any:
        return self.request("GET", url, headers={"Accept": "application/json"}).json()

    def post_json(self, url: str, payload: Any) -> Any:
        response = self.request(
            "POST",
            url,
            headers={"Accept": "application/json"},
            json_body=payload,
            ok_status=frozenset({200, 201}),
        )
        return response.json()

    def head(self, url: str) -> httpx.Response:
        # Same representation as download(): identity encoding, so Content-Length and ETag match.
        return self.request("HEAD", url, headers={"Accept-Encoding": "identity"})

    def conditional_get(
        self, url: str, *, etag: str | None = None, last_modified: str | None = None
    ) -> httpx.Response:
        """GET that may answer 304 Not Modified when the caller's cached validators still match."""
        headers: dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        return self.request("GET", url, headers=headers, ok_status=frozenset({200, 304}))

    def download(
        self,
        url: str,
        dest: Path,
        *,
        expected_sha256: str | None = None,
        expected_bytes: int | None = None,
    ) -> DownloadResult:
        """Stream `url` to `dest` atomically, resuming an interrupted `.part` file with an HTTP Range request.

        The partial file and its validators (`.part.json`) survive interruptions; a completed download is
        renamed into place only after its size (and SHA-256, if given) has been verified.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + ".part")
        meta_path = dest.with_name(dest.name + ".part.json")
        meta: dict[str, Any] = {}
        offset = 0
        if part.exists() and meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                meta = {}
            if meta.get("url") == url:
                offset = part.stat().st_size
        if offset == 0:
            part.unlink(missing_ok=True)

        digest = hashlib.sha256()
        # Ask for the stored bytes, not a gzip transfer encoding: Content-Length, byte ranges and the
        # SHA-256 must all refer to the file exactly as it exists on the server.
        headers: dict[str, str] = {"Accept-Encoding": "identity"}
        if offset:
            with part.open("rb") as existing:
                for chunk in iter(lambda: existing.read(CHUNK_SIZE), b""):
                    digest.update(chunk)
            headers["Range"] = f"bytes={offset}-"
            if meta.get("etag"):
                headers["If-Range"] = meta["etag"]

        response = self.request(
            "GET", url, headers=headers, stream=True, ok_status=frozenset({200, 206, 416})
        )
        resumed = False
        try:
            if response.status_code == 416:
                # Our partial file is not a prefix the server can continue; start over.
                response.close()
                part.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return self.download(
                    url, dest, expected_sha256=expected_sha256, expected_bytes=expected_bytes
                )
            if response.status_code == 206 and offset:
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {offset}-"):
                    raise HttpError(f"unexpected Content-Range {content_range!r}", url=url, status=206)
                mode = "ab"
                resumed = True
                total = int(content_range.rsplit("/", 1)[-1]) if "/" in content_range else None
            else:  # 200: full body (server ignored or refused the range)
                offset = 0
                digest = hashlib.sha256()
                mode = "wb"
                length = response.headers.get("Content-Length")
                total = int(length) if length and length.isdigit() else None

            etag = response.headers.get("ETag")
            last_modified = response.headers.get("Last-Modified")
            meta_path.write_text(
                json.dumps({"url": url, "etag": etag, "last_modified": last_modified}), encoding="utf-8"
            )
            with part.open(mode) as out:
                for chunk in response.iter_bytes(CHUNK_SIZE):
                    out.write(chunk)
                    digest.update(chunk)
        finally:
            response.close()

        size = part.stat().st_size
        sha256 = digest.hexdigest()
        if total is not None and size != total:
            raise IntegrityError(f"incomplete download: {size} of {total} bytes", url=url)
        if expected_bytes is not None and size != expected_bytes:
            part.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)
            raise IntegrityError(f"size {size} != expected {expected_bytes}", url=url)
        if expected_sha256 is not None and sha256 != expected_sha256.lower():
            part.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)
            raise IntegrityError(f"sha256 {sha256} != expected {expected_sha256}", url=url)
        os.replace(part, dest)
        meta_path.unlink(missing_ok=True)
        return DownloadResult(url, dest, size, sha256, etag, last_modified, resumed)

"""Incremental fetching: download a URL only when it is new or its validators (ETag, size) changed."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from question_bank.extractor.clients.http import HttpClient
from question_bank.extractor.downloaders.state import FetchRecord, StateJournal, now_iso
from question_bank.fsutil import sha256_file

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class FetchOutcome:
    record: FetchRecord
    downloaded: bool  # False when the cached copy was still current
    resumed: bool


def fetch(
    client: HttpClient,
    journal: StateJournal,
    url: str,
    dest: Path,
    *,
    force: bool = False,
    revalidate: bool = True,
) -> FetchOutcome:
    """Return a verified local copy of `url` at `dest`.

    A cached copy is reused when the journal has it, the file on disk still has the recorded SHA-256 and
    (unless `revalidate` is False) a HEAD request reports the same ETag and Content-Length. Otherwise the
    file is (re)downloaded, resuming a partial `.part` download if one exists. `revalidate=False` suits
    edition-specific URLs (media assets) whose content never changes under the same URL.
    """
    relative = dest.relative_to(journal.data_dir).as_posix()
    cached = journal.get(url)
    unchanged_on_disk = (
        cached is not None
        and not force
        and dest.exists()
        and dest.stat().st_size == cached.bytes
        and sha256_file(dest) == cached.sha256
    )
    if unchanged_on_disk and not revalidate:
        return FetchOutcome(cached, downloaded=False, resumed=False)
    if cached and not force and dest.exists() and revalidate:
        head = client.head(url)
        same_etag = head.headers.get("ETag") == cached.etag
        length = head.headers.get("Content-Length")
        same_size = length is None or int(length) == cached.bytes
        if (
            same_etag
            and same_size
            and dest.stat().st_size == cached.bytes
            and sha256_file(dest) == cached.sha256
        ):
            journal.touch(url)
            return FetchOutcome(cached, downloaded=False, resumed=False)
        log.info("source changed, downloading again", extra={"url": url})

    result = client.download(url, dest)
    stamp = now_iso()
    record = FetchRecord(
        url=url,
        path=relative,
        sha256=result.sha256,
        bytes=result.bytes,
        etag=result.etag,
        last_modified=result.last_modified,
        fetched_at=stamp,
        checked_at=stamp,
    )
    journal.put(record)
    return FetchOutcome(record, downloaded=True, resumed=result.resumed)

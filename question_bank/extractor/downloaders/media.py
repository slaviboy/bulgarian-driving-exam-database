"""Download the media (pictures and videos) referenced by the official variant files.

Every variant directory carries its own `assets/` folder; the same file name appears in up to 11 of
them. Each unique name is downloaded once (from the first variant that references it) and copies in
other directories are verified: all video copies (their names, e.g. `5_video.mp4`, are generic) and a
seeded sample of picture copies. A copy that differs in content fails the build.
"""

from __future__ import annotations

import logging
import random
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote, urljoin

from question_bank.config import OFFICIAL_INDEX_URL, Settings
from question_bank.extractor.clients.http import HttpClient
from question_bank.extractor.downloaders.fetch import fetch
from question_bank.extractor.downloaders.state import FetchRecord, StateJournal

log = logging.getLogger(__name__)


def asset_url(directory: str, name: str) -> str:
    return urljoin(OFFICIAL_INDEX_URL, quote(directory) + "/assets/" + quote(name))


@dataclass
class AssetRef:
    name: str
    directories: list[str] = field(default_factory=list)  # in official file order, first = download source

    @property
    def is_video(self) -> bool:
        return self.name.lower().endswith(".mp4")


@dataclass(frozen=True)
class CopyCheck:
    name: str
    directory: str
    method: str  # "head" (same ETag and size) or "sha256" (content compared after download)
    identical: bool
    detail: str = ""


def collect_asset_refs(extracted: Iterable) -> dict[str, AssetRef]:
    refs: dict[str, AssetRef] = {}
    for item in sorted(extracted, key=lambda e: e.source.order):
        for question in item.parsed.questions:
            for name in question.assets:
                ref = refs.setdefault(name, AssetRef(name))
                if item.source.directory not in ref.directories:
                    ref.directories.append(item.source.directory)
    return refs


def asset_path(settings: Settings, directory: str, name: str) -> Path:
    return settings.raw_dir / directory / "assets" / name


def download_assets(
    settings: Settings, client: HttpClient, refs: dict[str, AssetRef], *, progress=None
) -> dict[str, FetchRecord]:
    journal = StateJournal(settings.state_file, settings.data_dir)
    records: dict[str, FetchRecord] = {}
    for name in sorted(refs):
        directory = refs[name].directories[0]
        outcome = fetch(
            client,
            journal,
            asset_url(directory, name),
            asset_path(settings, directory, name),
            revalidate=False,
        )
        records[name] = outcome.record
        if progress is not None:
            progress(name, outcome)
    return records


def records_from_journal(settings: Settings, refs: dict[str, AssetRef]) -> dict[str, FetchRecord]:
    """Downloaded record of every referenced asset (no network). Raises if `qb media` has not run."""
    journal = StateJournal(settings.state_file, settings.data_dir)
    records = {}
    missing = []
    for name, ref in refs.items():
        record = journal.get(asset_url(ref.directories[0], name))
        if record is None or not journal.local_path(record).exists():
            missing.append(name)
        else:
            records[name] = record
    if missing:
        raise FileNotFoundError(f"{len(missing)} assets not downloaded yet (run `qb media`): {missing[:5]}")
    return records


def verify_copies(
    settings: Settings,
    client: HttpClient,
    refs: dict[str, AssetRef],
    records: dict[str, FetchRecord],
    *,
    image_sample: int = 300,
    seed: int = 20261001,
) -> list[CopyCheck]:
    """Compare copies of the same asset name in other variant directories with the downloaded one."""
    pairs = [(ref.name, d) for ref in refs.values() if ref.is_video for d in ref.directories[1:]]
    image_pairs = sorted(
        (ref.name, d) for ref in refs.values() if not ref.is_video for d in ref.directories[1:]
    )
    pairs += random.Random(seed).sample(image_pairs, min(image_sample, len(image_pairs)))

    checks: list[CopyCheck] = []
    for name, directory in sorted(pairs):
        record = records[name]
        head = client.head(asset_url(directory, name))
        size = int(head.headers.get("Content-Length", "-1"))
        if size != record.bytes:
            checks.append(CopyCheck(name, directory, "head", False, f"size {size} != {record.bytes}"))
            continue
        if head.headers.get("ETag") == record.etag:
            checks.append(CopyCheck(name, directory, "head", True))
            continue
        with tempfile.TemporaryDirectory() as tmp:
            copy = client.download(asset_url(directory, name), Path(tmp) / name)
        same = copy.sha256 == record.sha256
        checks.append(CopyCheck(name, directory, "sha256", same, "" if same else "content differs"))
    return checks

"""Persistent download journal: what was fetched, from where, with which validators and checksum."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from question_bank.fsutil import read_json, write_json


@dataclass
class FetchRecord:
    url: str
    path: str  # relative to the data directory
    sha256: str
    bytes: int
    etag: str | None
    last_modified: str | None
    fetched_at: str
    checked_at: str


class StateJournal:
    """JSON file keyed by URL. Saved after every change so an interrupted run loses nothing."""

    def __init__(self, path: Path, data_dir: Path):
        self.path = path
        self.data_dir = data_dir
        self._records: dict[str, FetchRecord] = {}
        if path.exists():
            for url, raw in read_json(path).get("records", {}).items():
                self._records[url] = FetchRecord(**raw)

    def get(self, url: str) -> FetchRecord | None:
        return self._records.get(url)

    def put(self, record: FetchRecord) -> None:
        self._records[record.url] = record
        self.save()

    def touch(self, url: str) -> None:
        record = self._records[url]
        record.checked_at = now_iso()
        self.save()

    def local_path(self, record: FetchRecord) -> Path:
        return self.data_dir / record.path

    def save(self) -> None:
        payload = {"records": {url: asdict(r) for url, r in sorted(self._records.items())}}
        write_json(self.path, payload)

    def __len__(self) -> int:
        return len(self._records)


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")

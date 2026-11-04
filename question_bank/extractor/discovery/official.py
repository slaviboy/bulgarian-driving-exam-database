"""Discovery of the official ИААА question array: the index page and its `manifest.txt` file list."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import quote, urljoin

from question_bank.config import OFFICIAL_INDEX_URL
from question_bank.extractor.clients.http import HttpClient

log = logging.getLogger(__name__)

MANIFEST_NAME = "manifest.txt"
# Stem of an official file name: "<order>_<category token>_<description words>_<DD.MM.YYYY>"
_STEM = re.compile(
    r"^(?P<order>\d+)_(?P<token>[^_]+)_(?P<words>.+)_(?P<d>\d{2})\.(?P<m>\d{2})\.(?P<y>\d{4})$"
)


class LayoutChangedError(RuntimeError):
    """The official site no longer looks like the layout this tool was written for."""


@dataclass(frozen=True)
class OfficialFile:
    order: int  # numeric prefix of the file name, i.e. the order of the manifest
    relative_path: str  # manifest line, e.g. "7_B_…_01.10.2026/7_B_…_01.10.2026.html"
    url: str  # absolute, percent-encoded URL
    directory: str  # directory below the index that also holds the file's assets/
    file_name: str
    category_token: str  # informative only — the HTML <h1> is authoritative
    description_words: str  # file-name form of the description, e.g. "без_правоспособност"
    edition: date

    @property
    def directory_url(self) -> str:
        return urljoin(OFFICIAL_INDEX_URL, quote(self.directory) + "/")

    def asset_url(self, asset_name: str) -> str:
        return urljoin(self.directory_url, "assets/" + quote(asset_name))


@dataclass(frozen=True)
class OfficialManifest:
    index_url: str
    manifest_url: str
    raw_text: str
    sha256: str
    files: tuple[OfficialFile, ...]

    @property
    def editions(self) -> set[date]:
        return {f.edition for f in self.files}


def parse_manifest(text: str, index_url: str = OFFICIAL_INDEX_URL) -> tuple[OfficialFile, ...]:
    """Parse `manifest.txt` (one relative path per line). Raises LayoutChangedError on unknown lines."""
    files: list[OfficialFile] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not line.endswith(".html") or "/" not in line:
            raise LayoutChangedError(f"unexpected manifest line: {line!r}")
        directory, file_name = line.rsplit("/", 1)
        match = _STEM.match(file_name[: -len(".html")])
        if not match:
            raise LayoutChangedError(f"unexpected official file name: {file_name!r}")
        edition = date(int(match["y"]), int(match["m"]), int(match["d"]))
        files.append(
            OfficialFile(
                order=int(match["order"]),
                relative_path=line,
                url=urljoin(index_url, quote(line)),
                directory=directory,
                file_name=file_name,
                category_token=match["token"],
                description_words=match["words"],
                edition=edition,
            )
        )
    if not files:
        raise LayoutChangedError("manifest.txt lists no files")
    orders = [f.order for f in files]
    if len(set(orders)) != len(orders):
        raise LayoutChangedError(f"duplicate order prefixes in manifest: {orders}")
    return tuple(sorted(files, key=lambda f: f.order))


def discover_official(client: HttpClient, index_url: str = OFFICIAL_INDEX_URL) -> OfficialManifest:
    """Fetch the index page, check it still loads `manifest.txt`, and return the parsed file list."""
    index_html = client.get_text(index_url)
    if MANIFEST_NAME not in index_html:
        raise LayoutChangedError(f"{index_url} no longer references {MANIFEST_NAME}")
    manifest_url = urljoin(index_url, MANIFEST_NAME)
    raw = client.get_bytes(manifest_url)
    text = raw.decode("utf-8")
    files = parse_manifest(text, index_url)
    log.info(
        "official manifest discovered",
        extra={"files": len(files), "editions": sorted(str(e) for e in {f.edition for f in files})},
    )
    return OfficialManifest(index_url, manifest_url, text, hashlib.sha256(raw).hexdigest(), files)

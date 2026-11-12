"""Bulgarian road-sign drawings from Wikimedia Commons (vector sources for the sign pictures).

Wikimedia refuses scripts whose User-Agent carries no contact address, and this project sends no personal
data. So the files are fetched by the maintainer's browser instead: ``tools/commons-signs-download.html``
makes the same anonymous requests any Wikipedia visitor makes (one per second) and saves
``bg-road-signs-commons.zip`` with ``svg/<sha1>.svg`` and ``catalogue.json`` (title, URL, SHA-1, revision
time, author and licence of each file).

:func:`import_zip` checks every file against its SHA-1 and puts it into ``data/cache/commons/``; the files a
sign recipe uses are later copied into the committed attribution list ``data/enhance/signs/sources.json``.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from question_bank.fsutil import read_json, sha256_file, write_bytes_atomic, write_json

CATALOGUE = "catalogue.json"
_SHA1 = frozenset("0123456789abcdef")


class CommonsImportError(ValueError):
    """The ZIP is not a sign download made by tools/commons-signs-download.html."""


def import_zip(zip_path: Path, cache_dir: Path) -> dict:
    """Verify and unpack a browser download; returns counts. Existing verified files are kept."""
    try:
        archive = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as exc:
        raise CommonsImportError(f"{zip_path.name} is not a ZIP file") from exc
    with archive:
        try:
            catalogue: dict[str, dict] = json.loads(archive.read(CATALOGUE).decode("utf-8"))
        except KeyError as exc:
            raise CommonsImportError(f"{zip_path.name} has no {CATALOGUE}") from exc
        names = set(archive.namelist())
        imported = missing = rejected = 0
        for title, entry in catalogue.items():
            sha1 = str(entry.get("sha1", ""))
            if len(sha1) != 40 or not set(sha1) <= _SHA1:
                raise CommonsImportError(f"{title}: invalid SHA-1 {sha1!r}")
            member = f"svg/{sha1}.svg"
            if member not in names:
                missing += 1
                continue
            data = archive.read(member)
            if hashlib.sha1(data).hexdigest() != sha1:
                rejected += 1
                entry["import_error"] = "SHA-1 mismatch"
                continue
            target = cache_dir / f"{sha1}.svg"
            if not target.exists() or hashlib.sha1(target.read_bytes()).hexdigest() != sha1:
                write_bytes_atomic(target, data)
            entry["sha256"] = sha256_file(target)
            entry.pop("download_error", None)
            imported += 1
    known = read_json(cache_dir / CATALOGUE) if (cache_dir / CATALOGUE).exists() else {}
    known.update({t: e for t, e in catalogue.items() if "sha256" in e})
    write_json(cache_dir / CATALOGUE, dict(sorted(known.items())))
    return {"files": len(catalogue), "imported": imported, "missing": missing, "rejected": rejected}


def load_catalogue(cache_dir: Path) -> dict[str, dict]:
    return read_json(cache_dir / CATALOGUE)


def svg_path(cache_dir: Path, entry: dict) -> Path:
    return cache_dir / f"{entry['sha1']}.svg"

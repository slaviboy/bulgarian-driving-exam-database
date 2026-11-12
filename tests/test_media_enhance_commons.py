from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from question_bank.media_enhance.commons import CommonsImportError, import_zip, load_catalogue

SVG_A = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
SVG_B = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle r="5" cx="5" cy="5"/></svg>'


def _entry(title: str, data: bytes) -> dict:
    return {"title": title, "sha1": hashlib.sha1(data).hexdigest(), "author": "A", "license": "CC BY-SA 4.0"}


def _zip(path: Path, files: dict[str, bytes], catalogue: dict) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        for name, data in files.items():
            z.writestr(name, data)
        z.writestr("catalogue.json", json.dumps(catalogue))
    return path


def test_import_verifies_and_caches_by_sha1(tmp_path: Path):
    a = _entry("File:BG road sign А1.svg", SVG_A)
    b = _entry("File:BG road sign Б2.svg", SVG_B)
    zp = _zip(
        tmp_path / "d.zip",
        {f"svg/{a['sha1']}.svg": SVG_A, f"svg/{b['sha1']}.svg": b"tampered"},
        {a["title"]: a, b["title"]: b},
    )
    stats = import_zip(zp, tmp_path / "cache")
    assert stats == {"files": 2, "imported": 1, "missing": 0, "rejected": 1}
    assert (tmp_path / "cache" / f"{a['sha1']}.svg").read_bytes() == SVG_A
    catalogue = load_catalogue(tmp_path / "cache")
    assert list(catalogue) == [a["title"]] and "sha256" in catalogue[a["title"]]


def test_import_counts_files_that_were_not_downloaded(tmp_path: Path):
    a = _entry("File:BG road sign А1.svg", SVG_A)
    zp = _zip(tmp_path / "d.zip", {}, {a["title"]: a})
    assert import_zip(zp, tmp_path / "cache")["missing"] == 1


def test_import_refuses_other_archives(tmp_path: Path):
    zp = _zip(tmp_path / "d.zip", {"x.txt": b"x"}, {})
    with zipfile.ZipFile(zp, "a"):
        pass
    bad = tmp_path / "no-catalogue.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("x.txt", b"x")
    with pytest.raises(CommonsImportError):
        import_zip(bad, tmp_path / "cache")
    with pytest.raises(CommonsImportError):
        import_zip(_zip(tmp_path / "e.zip", {}, {"File:x.svg": {"sha1": "../../evil"}}), tmp_path / "cache")

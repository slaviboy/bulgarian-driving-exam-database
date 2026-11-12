from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from question_bank.exporter.packages import PinnedPackMismatch, build_media_release, deterministic_zip
from question_bank.fsutil import sha256_file, write_json
from question_bank.media_enhance.pack import install_pinned
from question_bank.models import Media, MediaDerivative

MID = "m-0123456789abcdef"
WEBP = b"RIFF....WEBPVP8 fake"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>'


def _layout(tmp_path: Path) -> tuple[Path, Path, Path]:
    enhance, media, release = tmp_path / "enhance", tmp_path / "media", tmp_path / "release"
    files = {f"images-webp/{MID}.webp": WEBP, f"images-svg/{MID}.svg": SVG}
    src = tmp_path / "src"
    for name, data in files.items():
        (src / name).parent.mkdir(parents=True, exist_ok=True)
        (src / name).write_bytes(data)
    packs = {}
    for kind, name in (("images-webp", f"images-webp/{MID}.webp"), ("images-svg", f"images-svg/{MID}.svg")):
        archive = release / "media-2026.10.01-r2" / f"{kind}.zip"
        deterministic_zip(archive, [(name, src / name)], compress=kind == "images-svg")
        packs[kind] = {"url": f"https://example.test/{kind}.zip", "bytes": archive.stat().st_size,
                       "sha256": sha256_file(archive), "file_count": 1}  # fmt: skip
    write_json(enhance / "pack.json", {"tag": "media-2026.10.01-r2", "packs": packs})
    record = {
        "process": ["vector-commons"],
        "webp": {"relative_path": f"images-webp/{MID}.webp", "sha256": hashlib.sha256(WEBP).hexdigest()},
        "svg": {"relative_path": f"images-svg/{MID}.svg", "sha256": hashlib.sha256(SVG).hexdigest()},
        "sources": [],
    }
    write_json(enhance / "derivatives.json", {"tag": "media-2026.10.01-r2", "media": {MID: record}})
    return enhance, media, release


def test_install_pinned_extracts_verified_files(tmp_path: Path):
    enhance, media, release = _layout(tmp_path)
    result = install_pinned(enhance, media, release, tmp_path / "cache")
    assert result == {"tag": "media-2026.10.01-r2", "files": 2}
    assert (media / "images-webp" / f"{MID}.webp").read_bytes() == WEBP
    assert (media / "images-svg" / f"{MID}.svg").read_bytes() == SVG


def test_install_pinned_refuses_a_pack_with_unexpected_entries(tmp_path: Path):
    enhance, media, release = _layout(tmp_path)
    archive = release / "media-2026.10.01-r2" / "images-svg.zip"
    with zipfile.ZipFile(archive, "a") as z:
        z.writestr("../evil.svg", b"x")
    with pytest.raises(
        FileNotFoundError
    ):  # the tampered local pack no longer matches; nothing to download from
        install_pinned(enhance, media, release, tmp_path / "cache")


def test_media_release_uses_the_pinned_revision_and_refuses_a_mismatch(tmp_path: Path):
    enhance, media, release = _layout(tmp_path)
    install_pinned(enhance, media, release, tmp_path / "cache")
    original = media / "images" / f"{MID}.png"
    original.parent.mkdir(parents=True)
    original.write_bytes(b"png")
    from question_bank.fsutil import read_json

    pinned = read_json(enhance / "pack.json")

    def derivative(fmt: str, data: bytes) -> MediaDerivative:
        return MediaDerivative(
            format=fmt, relative_path=f"images-{fmt}/{MID}.{fmt}", mime_type="x", bytes=len(data), width=1,
            height=1, sha256=hashlib.sha256(data).hexdigest(),
        )  # fmt: skip

    media_record = Media(
        id=MID, kind="image", original_name="1.png", relative_path=f"images/{MID}.png", mime_type="image/png",
        bytes=3, width=1, height=1, sha256=hashlib.sha256(b"png").hexdigest(), source_url="https://x",
        source_id="iaaa-eis", derivatives=[derivative("webp", WEBP), derivative("svg", SVG)],
    )  # fmt: skip
    out = build_media_release([media_record], media, release, "2026-10-01", pinned=pinned)
    urls = {p.kind: p.url for p in out.packs}
    assert urls["images-webp"] == "https://example.test/images-webp.zip"
    assert urls["images-svg"] == "https://example.test/images-svg.zip"
    assert urls["images-original"].endswith("/media-2026.10.01/images-original.zip")
    (media / "images-svg" / f"{MID}.svg").write_bytes(SVG + b" ")
    with pytest.raises(PinnedPackMismatch):
        build_media_release([media_record], media, release, "2026-10-01", pinned=pinned)

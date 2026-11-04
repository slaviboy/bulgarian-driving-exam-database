"""Deterministic release packages: media packs (media-YYYY.MM.DD) and the dataset core zip (vX.Y.Z)."""

from __future__ import annotations

import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from question_bank.config import PROJECT_URL
from question_bank.fsutil import sha256_file
from question_bank.models import Media, MediaPack

FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def media_release_tag(source_edition: str) -> str:
    return "media-" + source_edition.replace("-", ".")


def release_download_base(tag: str) -> str:
    return f"{PROJECT_URL}/releases/download/{tag}/"


def deterministic_zip(dest: Path, entries: list[tuple[str, Path]], *, compress: bool) -> None:
    """Same input files → byte-identical zip on every OS (sorted names, fixed time and attributes)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    method = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
    with zipfile.ZipFile(tmp, "w", allowZip64=True) as archive:
        for arcname, src in sorted(entries):
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.compress_type = method
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, src.read_bytes(), compresslevel=9 if compress else None)
    tmp.replace(dest)


@dataclass(frozen=True)
class MediaRelease:
    tag: str
    directory: Path
    packs: list[MediaPack]
    single_files: list[Path]


def build_media_release(
    media: list[Media], media_dir: Path, release_root: Path, source_edition: str
) -> MediaRelease:
    tag = media_release_tag(source_edition)
    out = release_root / tag
    base = release_download_base(tag)
    groups: dict[str, list[tuple[str, Path]]] = {"images-original": [], "images-webp": [], "videos": []}
    singles: list[Path] = []
    for m in sorted(media, key=lambda m: m.id):
        if m.kind == "video":
            groups["videos"].append((m.relative_path, media_dir / m.relative_path))
            single = out / f"{m.id}.mp4"
            if not single.exists() or sha256_file(single) != m.sha256:
                single.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(media_dir / m.relative_path, single)
            singles.append(single)
        else:
            groups["images-original"].append((m.relative_path, media_dir / m.relative_path))
            for d in m.derivatives:
                groups["images-webp"].append((d.relative_path, media_dir / d.relative_path))
    packs = []
    for kind, entries in groups.items():
        archive = out / f"{kind}.zip"
        deterministic_zip(archive, entries, compress=False)  # PNG, WebP and MP4 are compressed already
        packs.append(
            MediaPack(
                id=f"{tag}/{kind}",
                kind=kind,
                url=base + archive.name,
                bytes=archive.stat().st_size,
                sha256=sha256_file(archive),
                file_count=len(entries),
            )
        )
    return MediaRelease(tag, out, packs, singles)


def build_core_package(
    exports_dir: Path, release_root: Path, dataset_version: str, extra: list[Path]
) -> Path:
    tag = f"v{dataset_version}"
    out = release_root / tag
    names = ["manifest.json", "categories.json", "questions.json", "exam-configs.json", "master.sqlite"]
    entries = [(name, exports_dir / name) for name in names] + [(p.name, p) for p in extra]
    archive = out / f"dataset-core-{tag}.zip"
    deterministic_zip(archive, entries, compress=True)
    for name in names:
        shutil.copyfile(exports_dir / name, out / name)
    sums = [
        f"{sha256_file(p)}  {p.name}" for p in sorted(out.iterdir()) if p.is_file() and p.name != "SHA256SUMS"
    ]
    (out / "SHA256SUMS").write_bytes(("\n".join(sums) + "\n").encode("utf-8"))
    return archive

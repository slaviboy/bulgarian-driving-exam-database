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


class PinnedPackMismatch(RuntimeError):
    """The local enhanced media differ from the media revision pinned in data/enhance/pack.json."""


def build_media_release(
    media: list[Media],
    media_dir: Path,
    release_root: Path,
    source_edition: str,
    pinned: dict | None = None,
) -> MediaRelease:
    """Packs of the edition's media release, plus the enhanced packs of a pinned media revision.

    ``pinned`` is data/enhance/pack.json: its ``images-webp`` and ``images-svg`` packs replace the edition's
    WebP pack. They are rebuilt here from the local files (deterministically) and must be byte-identical to
    the published ones, so the manifest can point to the revision's URLs.
    """
    tag = media_release_tag(source_edition)
    out = release_root / tag
    base = release_download_base(tag)
    # Videos are published one by one (<media id>.mp4) for on-demand download; no second copy in a zip.
    groups: dict[str, list[tuple[str, Path]]] = {"images-original": [], "images-webp": [], "images-svg": []}
    singles: list[Path] = []
    for m in sorted(media, key=lambda m: m.id):
        if m.kind == "video":
            single = out / f"{m.id}.mp4"
            if not single.exists() or sha256_file(single) != m.sha256:
                single.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(media_dir / m.relative_path, single)
            singles.append(single)
        else:
            groups["images-original"].append((m.relative_path, media_dir / m.relative_path))
            for d in m.derivatives:
                groups[f"images-{d.format}"].append((d.relative_path, media_dir / d.relative_path))
    packs = []
    for kind, entries in groups.items():
        if not entries:
            continue
        spec = (pinned or {}).get("packs", {}).get(kind)
        if spec is not None:
            archive = release_root / pinned["tag"] / f"{kind}.zip"
            deterministic_zip(archive, entries, compress=kind == "images-svg")
            if sha256_file(archive) != spec["sha256"]:
                raise PinnedPackMismatch(
                    f"{kind}.zip built from the local files differs from {spec['url']} (run `qb media`)"
                )
            packs.append(
                MediaPack(
                    id=f"{pinned['tag']}/{kind}",
                    kind=kind,
                    url=spec["url"],
                    bytes=spec["bytes"],
                    sha256=spec["sha256"],
                    file_count=spec["file_count"],
                )
            )
            continue
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
    exports_dir: Path,
    release_root: Path,
    dataset_version: str,
    extra: list[Path],
    translations: list[str] = (),
    explanations: list[str] = (),
) -> Path:
    tag = f"v{dataset_version}"
    out = release_root / tag
    if out.exists():
        shutil.rmtree(out)  # a rebuilt release holds only this build's files (SHA256SUMS lists the folder)
    names = [
        "manifest.json",
        "categories.json",
        "questions.json",
        "exam-configs.json",
        *translations,
        *explanations,
        "master.sqlite",
    ]
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

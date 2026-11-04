"""Prepare the media tree published in the media packs:

    data/media/images/<media-id>.png        original bytes, unchanged
    data/media/images-webp/<media-id>.webp  WebP derivative for apps (format conversion only)
    data/media/videos/<media-id>.mp4        original bytes, unchanged

Media IDs are content-addressed (`m-<sha256[:16]>`), so identical files under different names collapse
into one record. Every picture is decoded with Pillow; every video must carry an MP4 `ftyp` box.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from question_bank.config import Settings
from question_bank.extractor.downloaders.state import FetchRecord
from question_bank.fsutil import sha256_file
from question_bank.models import Media, MediaDerivative
from question_bank.processor.normalization.ids import SOURCE_ID, media_id

log = logging.getLogger(__name__)

WEBP_QUALITY = 85
WEBP_METHOD = 6


class MediaError(ValueError):
    """A downloaded media file is not a valid picture or video."""


@dataclass(frozen=True)
class PreparedMedia:
    by_name: dict[str, str]  # official asset name → media id
    media: dict[str, Media]  # media id → record
    duplicate_names: dict[str, list[str]]  # media id → all asset names with identical bytes


def _copy_if_needed(src: Path, dest: Path, sha256: str) -> None:
    if dest.exists() and dest.stat().st_size == src.stat().st_size and sha256_file(dest) == sha256:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    shutil.copyfile(src, tmp)
    tmp.replace(dest)


def _webp(src: Path, dest: Path) -> MediaDerivative:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as image:
            mode = "RGBA" if (image.mode in ("RGBA", "LA") or "transparency" in image.info) else "RGB"
            converted = image.convert(mode)
            tmp = dest.with_name(dest.name + ".tmp")
            converted.save(tmp, "WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
            tmp.replace(dest)
    with Image.open(dest) as derived:
        width, height = derived.size
    return MediaDerivative(
        format="webp",
        relative_path=f"images-webp/{dest.name}",
        mime_type="image/webp",
        bytes=dest.stat().st_size,
        width=width,
        height=height,
        sha256=sha256_file(dest),
    )


def _check_mp4(path: Path) -> None:
    with path.open("rb") as handle:
        head = handle.read(12)
    if len(head) < 12 or head[4:8] != b"ftyp":
        raise MediaError(f"{path.name}: not an MP4 file (missing ftyp box)")


def prepare_media(settings: Settings, records: dict[str, FetchRecord], *, webp: bool = True) -> PreparedMedia:
    by_name: dict[str, str] = {}
    media: dict[str, Media] = {}
    duplicates: dict[str, list[str]] = {}
    for name in sorted(records):
        record = records[name]
        src = settings.data_dir / record.path
        if sha256_file(src) != record.sha256:
            raise MediaError(f"{name}: local file does not match the recorded SHA-256")
        mid = media_id(record.sha256)
        by_name[name] = mid
        duplicates.setdefault(mid, []).append(name)
        if mid in media:
            continue
        lower = name.lower()
        if lower.endswith(".mp4"):
            _check_mp4(src)
            dest = settings.media_dir / "videos" / f"{mid}.mp4"
            _copy_if_needed(src, dest, record.sha256)
            media[mid] = Media(
                id=mid,
                kind="video",
                original_name=name,
                relative_path=f"videos/{mid}.mp4",
                mime_type="video/mp4",
                bytes=record.bytes,
                width=None,
                height=None,
                sha256=record.sha256,
                source_url=record.url,
                source_id=SOURCE_ID,
            )
        elif lower.endswith(".png"):
            try:
                with Image.open(src) as image:
                    image.verify()
                with Image.open(src) as image:
                    if image.format != "PNG":
                        raise MediaError(f"{name}: format {image.format}, expected PNG")
                    width, height = image.size
            except (OSError, SyntaxError) as exc:
                raise MediaError(f"{name}: cannot be decoded: {exc}") from exc
            dest = settings.media_dir / "images" / f"{mid}.png"
            _copy_if_needed(src, dest, record.sha256)
            derivatives = [_webp(dest, settings.media_dir / "images-webp" / f"{mid}.webp")] if webp else []
            media[mid] = Media(
                id=mid,
                kind="image",
                original_name=name,
                relative_path=f"images/{mid}.png",
                mime_type="image/png",
                bytes=record.bytes,
                width=width,
                height=height,
                sha256=record.sha256,
                source_url=record.url,
                source_id=SOURCE_ID,
                derivatives=derivatives,
            )
        else:
            raise MediaError(f"{name}: unsupported media type")
    return PreparedMedia(by_name, media, {k: v for k, v in duplicates.items() if len(v) > 1})

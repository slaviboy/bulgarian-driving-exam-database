"""The enhanced media packs and the derivative records the dataset publishes for them.

``qb enhance pack`` turns the reviewed results into the files apps use:

* ``images-webp/<id>.webp`` for every picture: the stamp-free picture enlarged by Real-ESRGAN, or, for signs
  and vehicle markings, the vector drawing rendered at 4× (at least 512 px). Same path and media id as before,
  so an installed app simply receives better files with the next dataset. Apps that check only a file's size
  must see a new size, so a WebP that happens to be as large as the previous one is re-encoded at another
  quality.
* ``images-svg/<id>.svg`` for signs and vehicle markings.

The packs are built locally (they need the GPU and the reviewed inputs), published once as the media revision
``media-YYYY.MM.DD-rN`` and pinned in ``data/enhance/pack.json``; ``data/enhance/derivatives.json`` keeps
every file's size, checksum, dimensions, processing and credits, so CI can rebuild the dataset without the
GPU.
"""

from __future__ import annotations

import hashlib
import io
import re
import shutil
from pathlib import Path

from PIL import Image

from question_bank.exporter.packages import deterministic_zip, release_download_base
from question_bank.fsutil import read_json, sha256_file, write_bytes_atomic, write_json

WEBP_QUALITY = 85
WEBP_METHOD = 6
DERIVATIVES = "derivatives.json"
PACK = "pack.json"
VECTOR_CLASSES = {"sign", "vehicle-marking"}


def _webp_bytes(path: Path, quality: int) -> tuple[bytes, int, int]:
    with Image.open(path) as image:
        has_alpha = image.mode in ("RGBA", "LA") or "transparency" in image.info
        converted = image.convert("RGBA" if has_alpha else "RGB")
        if has_alpha and (converted.getchannel("A").getextrema() == (255, 255)):
            converted = converted.convert("RGB")
        buffer = io.BytesIO()
        converted.save(buffer, "WEBP", quality=quality, method=WEBP_METHOD)
        return buffer.getvalue(), converted.width, converted.height


def _process(recipe_layers: list[dict] | None, upscale: dict | None) -> list[str]:
    if recipe_layers is None:
        scale = upscale["scale"] if upscale else 2.0
        return ["stamp-removed", f"enlarged-{scale:g}x"]
    steps = []
    for layer in recipe_layers:
        if layer.get("commons"):
            steps.append("vector-commons")
        elif "traced" in (layer.get("drawing") or ""):
            steps.append("vector-traced")
        else:
            steps.append("vector-drawn")
    return sorted(set(steps))


def build(
    enhance_dir: Path,
    media_dir: Path,
    release_root: Path,
    tag: str,
    *,
    commons_catalogue: dict[str, dict],
) -> dict:
    """Write the pack files, the zips under ``release_root/tag`` and the two committed JSON files."""
    inventory = read_json(enhance_dir / "inventory.json")["pictures"]
    recipes = read_json(enhance_dir / "signs" / "recipes.json")["recipes"]
    upscale = {
        d["media_id"]: d for d in read_json(media_dir / "enhance" / "upscaled" / "report.json")["pictures"]
    }
    out = media_dir / "enhance" / "pack"
    if out.exists():
        shutil.rmtree(out)
    records: dict[str, dict] = {}
    webp_entries, svg_entries = [], []
    for mid, entry in sorted(inventory.items()):
        vector = entry["class"] in VECTOR_CLASSES
        if vector:
            source = media_dir / "enhance" / "signs" / "png" / f"{mid}.png"
            svg = media_dir / "enhance" / "signs" / "svg" / f"{mid}.svg"
            layers = recipes[mid]["layers"]
        else:
            source = media_dir / "enhance" / "upscaled" / f"{mid}.png"
            svg, layers = None, None
        if not source.exists():
            raise FileNotFoundError(f"{mid}: {source} is missing")
        previous = media_dir / "images-webp" / f"{mid}.webp"
        previous_size = previous.stat().st_size if previous.exists() else -1
        quality = WEBP_QUALITY
        data, width, height = _webp_bytes(source, quality)
        while len(data) == previous_size:  # an installed app must notice the new file by its size
            quality -= 1
            data, width, height = _webp_bytes(source, quality)
        webp_path = out / "images-webp" / f"{mid}.webp"
        write_bytes_atomic(webp_path, data)
        webp_entries.append((f"images-webp/{mid}.webp", webp_path))
        credits = sorted({layer["commons"] for layer in (layers or []) if layer.get("commons")})
        record = {
            "class": entry["class"],
            "process": _process(layers, upscale.get(mid)),
            "webp": {
                "relative_path": f"images-webp/{mid}.webp",
                "bytes": len(data),
                "sha256": sha256_file(webp_path),
                "width": width,
                "height": height,
                "quality": quality,
            },
            "sources": [_credit(commons_catalogue[t]) for t in credits],
        }
        if svg is not None:
            svg_path = out / "images-svg" / f"{mid}.svg"
            svg_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(svg, svg_path)
            svg_entries.append((f"images-svg/{mid}.svg", svg_path))
            size = re.search(rb'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg_path.read_bytes())
            record["svg"] = {
                "relative_path": f"images-svg/{mid}.svg",
                "bytes": svg_path.stat().st_size,
                "sha256": sha256_file(svg_path),
                "width": round(float(size.group(1))) if size else None,
                "height": round(float(size.group(2))) if size else None,
            }
        records[mid] = record
    packs = {}
    base = release_download_base(tag)
    for kind, entries, compress in (("images-webp", webp_entries, False), ("images-svg", svg_entries, True)):
        archive = release_root / tag / f"{kind}.zip"
        deterministic_zip(archive, entries, compress=compress)
        packs[kind] = {
            "url": base + archive.name,
            "bytes": archive.stat().st_size,
            "sha256": sha256_file(archive),
            "file_count": len(entries),
        }
    write_json(enhance_dir / DERIVATIVES, {"tag": tag, "media": records})
    write_json(enhance_dir / PACK, {"tag": tag, "packs": packs})
    installed = install_pinned(
        enhance_dir, media_dir, release_root, media_dir.parent / "cache" / "media-packs"
    )
    return {"tag": tag, "packs": packs, "media": len(records), "svg": len(svg_entries), **installed}


def _credit(entry: dict) -> dict:
    return {
        "title": entry["title"].removeprefix("File:").removesuffix(".svg"),
        "author": entry["author"],
        "license": entry["license"],
        "license_url": entry.get("license_url") or None,
        "page": entry["page"],
        "sha1": entry["sha1"],
    }


_MEMBER = re.compile(r"^images-(webp|svg)/m-[0-9a-f]{16}\.(webp|svg)$")


def install_pinned(
    enhance_dir: Path, media_dir: Path, release_root: Path, cache_dir: Path, client=None
) -> dict:
    """Make ``media_dir`` hold the published enhanced files.

    Each pinned pack comes from the local release folder (right after ``qb enhance pack``), the download
    cache or, with ``client``, from its release URL; it must match its SHA-256 before any file is extracted,
    and every extracted file must match data/enhance/derivatives.json.
    """
    import zipfile

    pinned = read_json(enhance_dir / PACK)
    records = read_json(enhance_dir / DERIVATIVES)["media"]
    expected = {
        spec["relative_path"]: spec["sha256"]
        for record in records.values()
        for spec in (record.get("webp"), record.get("svg"))
        if spec
    }
    installed = 0
    for kind, spec in pinned["packs"].items():
        local = release_root / pinned["tag"] / f"{kind}.zip"
        cached = cache_dir / f"{spec['sha256']}.zip"
        if local.exists() and sha256_file(local) == spec["sha256"]:
            archive_path = local
        else:
            if not cached.exists() or sha256_file(cached) != spec["sha256"]:
                if client is None:
                    raise FileNotFoundError(f"{kind}: {spec['url']} is not available locally")
                cached.parent.mkdir(parents=True, exist_ok=True)
                client.download(spec["url"], cached)
                if sha256_file(cached) != spec["sha256"]:
                    cached.unlink()
                    raise ValueError(f"{kind}: download does not match the pinned SHA-256")
            archive_path = cached
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                if not _MEMBER.match(name) or name not in expected:
                    raise ValueError(f"{kind}: unexpected entry {name!r}")
                data = archive.read(name)
                if hashlib.sha256(data).hexdigest() != expected[name]:
                    raise ValueError(f"{name}: does not match data/enhance/derivatives.json")
                target = media_dir / name
                if not target.exists() or sha256_file(target) != expected[name]:
                    write_bytes_atomic(target, data)
                installed += 1
    return {"tag": pinned["tag"], "files": installed}

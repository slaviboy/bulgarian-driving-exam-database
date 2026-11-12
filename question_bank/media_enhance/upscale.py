"""Sharper, larger pictures: Real-ESRGAN (x4plus) on the cleaned pictures, then an exact-size downscale.

The tool is ``realesrgan-ncnn-vulkan`` (BSD-3, xinntao/Real-ESRGAN v0.2.5.0), run locally on the GPU; its
path comes from ``QB_REALESRGAN`` or defaults to ``data/cache/tools/realesrgan/``. It is not part of CI.

Content guard: the enlarged picture, shrunk back to the original size, must keep the cleaned picture's
structure: PSNR after a light blur (σ = 1, so sharper edges are not punished) ≥ :data:`MIN_BLUR_PSNR` dB and
mean SSIM ≥ :data:`MIN_SSIM`. The worst 16 px window's SSIM is recorded for the review sheets, because one
changed label letter (а/б/в), arrow or number can hide in a global average.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

log = logging.getLogger(__name__)

MODEL = "realesrgan-x4plus"
MIN_BLUR_PSNR = 30.0
MIN_SSIM = 0.90
BINARY = "realesrgan-ncnn-vulkan.exe" if os.name == "nt" else "realesrgan-ncnn-vulkan"


@dataclass(frozen=True)
class UpscaleResult:
    media_id: str
    width: int
    height: int
    scale: float
    blur_psnr: float
    ssim: float
    ssim_worst_window: float

    @property
    def ok(self) -> bool:
        return self.blur_psnr >= MIN_BLUR_PSNR and self.ssim >= MIN_SSIM


TARGET_LONG_SIDE = 1400


def scale_for_size(width: int, height: int) -> float:
    """About :data:`TARGET_LONG_SIDE` px on the long side, never below 2× or above the model's 4×."""
    return round(min(4.0, max(2.0, TARGET_LONG_SIDE / max(width, height))), 2)


def find_binary(data_dir: Path) -> Path:
    configured = os.environ.get("QB_REALESRGAN")
    path = Path(configured) if configured else data_dir / "cache" / "tools" / "realesrgan" / BINARY
    if not path.is_file():
        raise FileNotFoundError(f"Real-ESRGAN not found at {path} (set QB_REALESRGAN)")
    return path


def bleed_alpha(rgba: np.ndarray, passes: int = 8) -> np.ndarray:
    """Give fully transparent pixels the colour of nearby visible ones, so no dark or white fringe can appear
    when the colour channels are enlarged separately from the alpha channel. Alpha is unchanged."""
    import cv2

    out = rgba.copy()
    known = rgba[..., 3] > 0
    if known.all() or not known.any():
        return out
    colour = out[..., :3].astype(np.float32)
    weight = known.astype(np.float32)
    colour *= weight[..., None]
    for _ in range(passes):
        blurred = cv2.blur(colour, (3, 3))
        wsum = cv2.blur(weight, (3, 3))
        fill = (wsum > 0) & (weight == 0)
        colour[fill] = blurred[fill] / wsum[fill][:, None]
        weight[fill] = 1.0
    colour[known] = rgba[..., :3][known]
    out[..., :3] = np.rint(colour).clip(0, 255).astype(np.uint8)
    return out


def _premultiplied(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.float32)
    return np.concatenate([x[..., :3] * x[..., 3:4] / 255.0, x[..., 3:4]], axis=-1)


def content_check(back: np.ndarray, cleaned: np.ndarray) -> tuple[float, float, float]:
    """(PSNR after a σ = 1 blur, mean SSIM, worst 16 px window SSIM) of two RGBA pictures of equal size."""
    import cv2

    a, b = _premultiplied(back), _premultiplied(cleaned)
    ba, bb = cv2.GaussianBlur(a, (0, 0), 1.0), cv2.GaussianBlur(b, (0, 0), 1.0)
    mse = float(np.mean((ba - bb) ** 2))
    blur_psnr = 99.0 if mse == 0 else 10 * np.log10(255.0**2 / mse)
    ga = cv2.cvtColor(a[..., :3], cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(b[..., :3], cv2.COLOR_RGB2GRAY)
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1, mu2 = cv2.GaussianBlur(ga, (0, 0), 1.5), cv2.GaussianBlur(gb, (0, 0), 1.5)
    s1 = cv2.GaussianBlur(ga * ga, (0, 0), 1.5) - mu1**2
    s2 = cv2.GaussianBlur(gb * gb, (0, 0), 1.5) - mu2**2
    s12 = cv2.GaussianBlur(ga * gb, (0, 0), 1.5) - mu1 * mu2
    ssim_map = ((2 * mu1 * mu2 + c1) * (2 * s12 + c2)) / ((mu1**2 + mu2**2 + c1) * (s1 + s2 + c2))
    windows = cv2.blur(ssim_map, (16, 16))
    return round(blur_psnr, 2), round(float(ssim_map.mean()), 4), round(float(windows.min()), 4)


def run_realesrgan(binary: Path, src_dir: Path, dst_dir: Path, model: str = MODEL) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(binary), "-i", str(src_dir), "-o", str(dst_dir), "-n", model, "-s", "4", "-f", "png"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=binary.parent, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Real-ESRGAN failed ({result.returncode}): {result.stderr[-2000:]}")


def upscale_all(
    clean_dir: Path, out_dir: Path, binary: Path, ids: list[str], scale_for: dict[str, float]
) -> list[UpscaleResult]:
    """Enlarge the cleaned pictures ``ids`` 4× on the GPU, then resize each to ``scale_for[id]`` × size."""
    results = []
    with tempfile.TemporaryDirectory(prefix="qb-upscale-") as tmp:
        src = Path(tmp) / "in"
        big = Path(tmp) / "out"
        src.mkdir()
        modes = {}
        for mid in ids:
            with Image.open(clean_dir / f"{mid}.png") as image:
                modes[mid] = image.mode
                rgba = np.asarray(image.convert("RGBA"))
            Image.fromarray(bleed_alpha(rgba), "RGBA").save(src / f"{mid}.png")
        run_realesrgan(binary, src, big)
        for mid in ids:
            with Image.open(clean_dir / f"{mid}.png") as image:
                cleaned = np.asarray(image.convert("RGBA"))
            height, width = cleaned.shape[:2]
            with Image.open(big / f"{mid}.png") as image:
                enlarged = image.convert("RGBA")
            scale = scale_for.get(mid, 2.0)
            target = (round(width * scale), round(height * scale))
            final = enlarged.resize(target, Image.LANCZOS) if target != enlarged.size else enlarged
            back = np.asarray(enlarged.resize((width, height), Image.BOX))
            out = out_dir / f"{mid}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            if modes[mid] != "RGBA" and (np.asarray(final)[..., 3] == 255).all():
                final = final.convert("RGB")
            final.save(out, optimize=True)
            results.append(UpscaleResult(mid, width, height, scale, *content_check(back, cleaned)))
    return results


def copy_without_upscaling(clean_dir: Path, out_dir: Path, mid: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(clean_dir / f"{mid}.png", out_dir / f"{mid}.png")

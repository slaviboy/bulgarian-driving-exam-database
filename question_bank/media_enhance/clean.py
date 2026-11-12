"""Remove the stamp from every picture and measure what is left.

``stamp_score`` correlates a picture's fine detail with the fine detail the stamp is expected to add, inside
the stamp's footprint. A stamped picture scores clearly above zero; a clean one scores about zero. The cleaned
pictures are written to ``data/media/enhance/clean/<media id>.png`` in the original's colour mode; pixels the
stamp does not touch stay byte-identical (checked for every picture).
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from question_bank.media_enhance.stamp import StampModel, invert, load_rgba, save_like

log = logging.getLogger(__name__)

CLEAN_LIMIT = 0.06  # |score| after removal above this is reported for review


@dataclass(frozen=True)
class CleanResult:
    media_id: str
    width: int
    height: int
    score_before: float
    score_after: float
    changed_pixels: int

    @property
    def ok(self) -> bool:
        return abs(self.score_after) <= CLEAN_LIMIT


def _premultiplied(rgba: np.ndarray) -> np.ndarray:
    p = rgba.astype(np.float32)
    a = p[..., 3:4] / 255.0
    return np.concatenate([p[..., :3] * a, p[..., 3:4]], axis=-1)


def stamp_score(rgba: np.ndarray, reference: np.ndarray, alpha: np.ndarray, colour: np.ndarray) -> float:
    """Correlation of ``rgba``'s detail with the detail the stamp adds to ``reference`` (as published)."""
    import cv2

    foot = cv2.dilate((alpha > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    if foot.sum() < 50:
        return 0.0
    ref = _premultiplied(reference)
    # wide blur: the expected stamp detail must not inherit the picture's own fine detail
    smooth = cv2.GaussianBlur(ref, (0, 0), 6.0)
    stamp = np.concatenate([colour, np.full((*alpha.shape, 1), 255.0, np.float32)], axis=-1)
    expected = alpha[..., None] * (stamp - smooth)
    expected_hp = expected - cv2.GaussianBlur(expected, (0, 0), 2.0)
    pic = _premultiplied(rgba)
    pic_hp = pic - cv2.GaussianBlur(pic, (0, 0), 2.0)
    e = expected_hp[foot].ravel()
    p = pic_hp[foot].ravel()
    e = e - e.mean()
    p = p - p.mean()
    denom = float(np.sqrt((e * e).sum() * (p * p).sum()))
    return float((e * p).sum() / denom) if denom > 0 else 0.0


def clean_picture(path: Path, model: StampModel, out_dir: Path) -> CleanResult:
    rgba, mode = load_rgba(path)
    height, width = rgba.shape[:2]
    alpha, colour = model.layer(width, height)
    cleaned = invert(rgba, alpha, colour)
    untouched = alpha == 0
    if not np.array_equal(cleaned[untouched], rgba[untouched]):
        raise AssertionError(f"{path.name}: pixels outside the stamp changed")
    save_like(out_dir / path.name, cleaned, mode)
    return CleanResult(
        media_id=path.stem,
        width=width,
        height=height,
        score_before=round(stamp_score(rgba, rgba, alpha, colour), 4),
        score_after=round(stamp_score(cleaned, rgba, alpha, colour), 4),
        changed_pixels=int((cleaned != rgba).any(axis=-1).sum()),
    )


def clean_all(paths: list[Path], model: StampModel, out_dir: Path) -> list[CleanResult]:
    results = []
    for i, path in enumerate(paths, 1):
        results.append(clean_picture(path, model, out_dir))
        if i % 100 == 0:
            log.info("cleaned %d/%d", i, len(paths))
    return results


def summary(results: list[CleanResult]) -> dict:
    before = np.array([r.score_before for r in results])
    after = np.array([r.score_after for r in results])
    flagged = [asdict(r) for r in results if not r.ok]
    return {
        "pictures": len(results),
        "score_before_median": round(float(np.median(before)), 4) if len(before) else None,
        "score_after_median": round(float(np.median(after)), 4) if len(after) else None,
        "score_after_max_abs": round(float(np.abs(after).max()), 4) if len(after) else None,
        "limit": CLEAN_LIMIT,
        "flagged": flagged,
    }

"""Propose Commons drawings for the sign pictures (a starting point for the reviewed recipes).

Every picture and every rendered drawing is cut to its content (transparent or uniform light background
removed), put on white and scaled to 64 × 64; the mean absolute colour difference plus a penalty for a
different aspect ratio ranks the drawings. Pictures with several parts (a sign with plates) usually match no
single drawing well; their recipes are composed by hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 64
ASPECT_WEIGHT = 60.0
INNER_WEIGHT = 2.0  # the symbol inside the frame decides between signs of the same shape
_INNER = slice(SIZE // 5, SIZE - SIZE // 5)


@dataclass(frozen=True)
class Candidate:
    title: str
    score: float


def content_box(rgba: np.ndarray) -> tuple[int, int, int, int] | None:
    """(x0, y0, x1, y1) of what is not background (transparent, or the corner colour of an opaque picture)."""
    import cv2

    alpha = rgba[..., 3]
    if (alpha < 250).mean() > 0.02:
        mask = alpha > 128
    else:
        corner = np.median(
            np.stack([rgba[0, 0, :3], rgba[0, -1, :3], rgba[-1, 0, :3], rgba[-1, -1, :3]]), axis=0
        )
        differs = np.abs(rgba[..., :3].astype(int) - corner).sum(-1) > 30
        flood = (~differs).astype(np.uint8)
        h, w = flood.shape
        seed = np.zeros((h + 2, w + 2), np.uint8)
        background = np.zeros_like(flood)
        for y, x in ((0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)):
            if flood[y, x]:
                filled = flood.copy()
                cv2.floodFill(filled, seed.copy(), (x, y), 2)
                background |= (filled == 2).astype(np.uint8)
        mask = background == 0
    ys, xs = np.nonzero(mask)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def normalised(rgba: np.ndarray) -> tuple[np.ndarray, float] | None:
    """The content on white at SIZE × SIZE (float32) and its aspect ratio (w / h)."""
    box = content_box(rgba)
    if box is None:
        return None
    x0, y0, x1, y1 = box
    crop = Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")
    white = Image.new("RGBA", crop.size, (255, 255, 255, 255))
    white.alpha_composite(crop)
    small = np.asarray(white.convert("RGB").resize((SIZE, SIZE), Image.LANCZOS), dtype=np.float32)
    return small, (x1 - x0) / (y1 - y0)


def load_rgba(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("RGBA"))


def rank(pictures: dict[str, Path], drawings: dict[str, Path], top: int = 3) -> dict[str, list[Candidate]]:
    """For each picture (media id → file) the ``top`` best drawings (title → rendered file)."""
    titles, stack, aspects = [], [], []
    for title, path in drawings.items():
        n = normalised(load_rgba(path))
        if n is not None:
            titles.append(title)
            stack.append(n[0])
            aspects.append(n[1])
    stack_arr = np.stack(stack)
    aspect_arr = np.array(aspects)
    out: dict[str, list[Candidate]] = {}
    for mid, path in pictures.items():
        n = normalised(load_rgba(path))
        if n is None:
            out[mid] = []
            continue
        full = np.abs(stack_arr - n[0]).mean(axis=(1, 2, 3))
        inner = np.abs(stack_arr[:, _INNER, _INNER] - n[0][_INNER, _INNER]).mean(axis=(1, 2, 3))
        penalty = ASPECT_WEIGHT * np.abs(np.log(aspect_arr / n[1]))
        score = (full + INNER_WEIGHT * inner) / (1 + INNER_WEIGHT) + penalty
        order = np.argsort(score)[:top]
        out[mid] = [Candidate(titles[i], round(float(score[i]), 2)) for i in order]
    return out

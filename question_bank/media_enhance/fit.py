"""Measure the stamp model from the official pictures themselves.

1. :func:`measure_tile` — wherever a picture's own background is transparent, the published alpha *is* the
   stamp opacity and the published colour *is* the stamp colour. Folding those pixels onto the 90 × 90 tile
   (positions from the centre anchor) and taking the most frequent exact 8-bit value per tile pixel gives the
   tile exactly.
2. :func:`fit_shifts` — the stamp was one hand-made layer, so whole tiles sit up to a few pixels off the
   regular lattice. For every element instance and candidate shift we remove that element and measure how much
   edge energy is left in its footprint (premultiplied RGBA, so it works on opaque and transparent pixels
   alike). The costs of all pictures that contain the instance are added up; the cheapest shift wins.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from question_bank.media_enhance.stamp import PERIOD, Element, StampModel, load_rgba, tile_origin

log = logging.getLogger(__name__)

SEARCH_DY = range(-3, 4)
SEARCH_DX = range(-2, 3)
MIN_MARGIN = 0.01  # mean cost advantage per picture below which a tile counts as unmeasured
MIN_PICTURES_AT_LIMIT = 20  # a shift at the edge of the search range needs this much support


def _background(rgba: np.ndarray) -> np.ndarray:
    """Pixels that are transparent background, at least 3 px away from the picture's own content."""
    import cv2

    content = (rgba[..., 3] > 230).astype(np.uint8)
    near = cv2.dilate(content, np.ones((7, 7), np.uint8)) > 0
    return ~near


def measure_tile(paths: list[Path]) -> tuple[np.ndarray, dict]:
    """The exact RGBA stamp tile (90, 90, 4 uint8) from transparent-background pixels, plus statistics."""
    keys = []
    pictures = 0
    for path in paths:
        rgba, _ = load_rgba(path)
        if (rgba[..., 3] == 255).all():
            continue
        ys, xs = np.nonzero(_background(rgba))
        if len(ys) == 0:
            continue
        pictures += 1
        height, width = rgba.shape[:2]
        oy, ox = tile_origin(width, height)
        v = (ys - oy) % PERIOD
        u = (xs - ox) % PERIOD
        px = rgba[ys, xs].astype(np.int64)
        alpha = px[:, 3]
        # transparent background shows the stamp colour only where the stamp is; elsewhere it means nothing
        r = np.where(alpha > 0, px[:, 0], 0)
        g = np.where(alpha > 0, px[:, 1], 0)
        b = np.where(alpha > 0, px[:, 2], 0)
        keys.append(((v * PERIOD + u) << 32) | (alpha << 24) | (r << 16) | (g << 8) | b)
    if not keys:
        raise ValueError("no picture with a transparent background: cannot measure the stamp")
    uniq, counts = np.unique(np.concatenate(keys), return_counts=True)
    cell = (uniq >> 32).astype(np.int64)
    alpha = ((uniq >> 24) & 0xFF).astype(np.int64)

    tile = np.zeros((PERIOD, PERIOD, 4), np.uint8)
    tile[..., :3] = 255
    agreement = np.zeros(PERIOD * PERIOD)
    observed = np.zeros(PERIOD * PERIOD, np.int64)
    # modal alpha per cell
    pair = cell * 256 + alpha
    pair_u, inverse = np.unique(pair, return_inverse=True)
    pair_counts = np.bincount(inverse, weights=counts)
    best_alpha: dict[int, tuple[int, float]] = {}
    for p, c in zip(pair_u, pair_counts, strict=True):
        k, a = int(p // 256), int(p % 256)
        if k not in best_alpha or c > best_alpha[k][1]:
            best_alpha[k] = (a, c)
    totals = np.bincount(cell, weights=counts, minlength=PERIOD * PERIOD)
    for k, (a, c) in best_alpha.items():
        observed[k] = totals[k]
        agreement[k] = c / totals[k]
        tile[k // PERIOD, k % PERIOD, 3] = a
    # modal colour among the observations with the modal alpha
    best_colour: dict[int, tuple[int, int]] = {}
    for key, c in zip(uniq, counts, strict=True):
        k = int(key >> 32)
        a = int((key >> 24) & 0xFF)
        if a == 0 or best_alpha[k][0] != a:
            continue
        if k not in best_colour or c > best_colour[k][1]:
            best_colour[k] = (int(key & 0xFFFFFF), int(c))
    for k, (rgb, _) in best_colour.items():
        tile[k // PERIOD, k % PERIOD, :3] = ((rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF)
    stamp = tile[..., 3].ravel() > 0
    stats = {
        "pictures": pictures,
        "observations": int(counts.sum()),
        "min_observations_per_tile_pixel": int(observed.min()),
        "stamp_pixels": int(stamp.sum()),
        "max_opacity": int(tile[..., 3].max()),
        "exact_agreement_median_stamp_pixels": round(float(np.median(agreement[stamp])), 4),
    }
    return tile, stats


def refine_tile(paths: list[Path], model: StampModel) -> tuple[np.ndarray, dict]:
    """Measure every element again in its own coordinates, following the fitted shifts.

    The first measurement folds pixels onto the lattice without shifts; an element that is mostly seen in
    shifted tiles (e.g. a word that only small pictures' corners show) comes out slightly wrong. Here each
    transparent background pixel inside an instance's box is attributed to that element at its local position;
    the most frequent exact value wins. Only pixels of the element's own (1 px dilated) footprint are updated.
    """
    import cv2

    keys = []
    for path in paths:
        rgba, _ = load_rgba(path)
        if (rgba[..., 3] == 255).all():
            continue
        background = _background(rgba)
        height, width = rgba.shape[:2]
        for inst in model.instances(width, height):
            e = inst.element
            h, w = e.shape
            ly, lx = np.mgrid[0:h, 0:w]
            Y, X = ly + inst.y, lx + inst.x
            ok = (Y >= 0) & (height > Y) & (X >= 0) & (width > X)
            ok[ok] &= background[Y[ok], X[ok]]
            if not ok.any():
                continue
            px = rgba[Y[ok], X[ok]].astype(np.int64)
            alpha = px[:, 3]
            rgb = np.where(alpha[:, None] > 0, px[:, :3], 0)
            local = (ly[ok] * 256 + lx[ok]).astype(np.int64)
            keys.append(
                (np.int64(e.index) << 48)
                | (local << 32)
                | (alpha << 24)
                | (rgb[:, 0] << 16)
                | (rgb[:, 1] << 8)
                | rgb[:, 2]
            )
    uniq, counts = np.unique(np.concatenate(keys), return_counts=True)
    # most frequent full value (alpha + colour) per (element, local pixel)
    pixel = uniq >> 32
    order = np.lexsort((-counts, pixel))
    first = np.ones(len(order), bool)
    first[1:] = pixel[order][1:] != pixel[order][:-1]
    best = {
        int(p): (int(v), int(c))
        for p, v, c in zip(pixel[order][first], uniq[order][first], counts[order][first], strict=True)
    }
    totals = np.bincount(np.searchsorted(np.unique(pixel), pixel), weights=counts)
    total_by_pixel = dict(zip(np.unique(pixel).tolist(), totals.tolist(), strict=True))

    tile = np.zeros((PERIOD, PERIOD, 4), np.uint8)
    tile[..., :3] = 255
    changed = 0
    for e in model.elements:
        footprint = cv2.dilate((e.alpha > 0).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        for ly, lx in zip(*np.nonzero(footprint), strict=True):
            key = (e.index << 16) | (int(ly) * 256 + int(lx))
            ty, tx = (e.y + ly) % PERIOD, (e.x + lx) % PERIOD
            old = round(float(e.alpha[ly, lx]) * 255)
            if key not in best:
                value = (old, *(int(v) for v in e.colour[ly, lx])) if old else (0, 255, 255, 255)
            else:
                v, c = best[key]
                if c / total_by_pixel[key] < 0.5:  # no clear majority: keep the first measurement
                    value = (old, *(int(v) for v in e.colour[ly, lx])) if old else (0, 255, 255, 255)
                else:
                    value = ((v >> 24) & 0xFF, (v >> 16) & 0xFF, (v >> 8) & 0xFF, v & 0xFF)
            if value[0] != old:
                changed += 1
            tile[ty, tx, 3] = value[0]
            tile[ty, tx, :3] = value[1:] if value[0] else (255, 255, 255)
    return tile, {"refined_pixels_changed": changed, "stamp_pixels": int((tile[..., 3] > 0).sum())}


# ---------------------------------------------------------------------- shifts


def _premultiplied(patch: np.ndarray) -> np.ndarray:
    a = patch[..., 3:4] / 255.0
    return np.concatenate([patch[..., :3] * a, patch[..., 3:4]], axis=-1)


def _tv(p: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Total variation of premultiplied RGBA patches (N, h, w, 4) inside ``mask`` (h, w) → (N,)."""
    gx = np.abs(np.diff(p, axis=2, append=p[:, :, -1:])).sum(-1)
    gy = np.abs(np.diff(p, axis=1, append=p[:, -1:])).sum(-1)
    return ((gx + gy) * mask).sum(axis=(1, 2))


def _instance_costs(stack: np.ndarray, element: Element, y: int, x: int) -> dict[tuple[int, int], np.ndarray]:
    """Cost per picture of removing ``element`` at (y + dy, x + dx), for every candidate shift.

    All shifts are judged on the same pixels (the union of their footprints inside the picture), so an element
    that slides partly out of the picture is not rewarded for showing less of itself.
    """
    import cv2

    height, width = stack.shape[1:3]
    h, w = element.shape
    pad = 1
    y0 = max(y + min(SEARCH_DY) - pad, 0)
    x0 = max(x + min(SEARCH_DX) - pad, 0)
    y1 = min(y + h + max(SEARCH_DY) + pad, height)
    x1 = min(x + w + max(SEARCH_DX) + pad, width)
    if y0 >= y1 or x0 >= x1:
        return {}
    layers = {}
    union = np.zeros((y1 - y0, x1 - x0), np.uint8)
    for dy in SEARCH_DY:
        for dx in SEARCH_DX:
            a = np.zeros((y1 - y0, x1 - x0), np.float32)
            c = np.zeros((y1 - y0, x1 - x0, 3), np.float32)
            ty, tx = y + dy - y0, x + dx - x0
            sy0, sx0 = max(ty, 0), max(tx, 0)
            sy1, sx1 = min(ty + h, y1 - y0), min(tx + w, x1 - x0)
            if sy0 < sy1 and sx0 < sx1:
                a[sy0:sy1, sx0:sx1] = element.alpha[sy0 - ty : sy1 - ty, sx0 - tx : sx1 - tx]
                c[sy0:sy1, sx0:sx1] = element.colour[sy0 - ty : sy1 - ty, sx0 - tx : sx1 - tx]
            layers[(dy, dx)] = (a, c)
            union |= cv2.dilate((a > 0).astype(np.uint8), np.ones((3, 3), np.uint8))
    if union.sum() < 60:
        return {}
    mask = union.astype(np.float32)
    window = stack[:, y0:y1, x0:x1].astype(np.float32)
    base = np.maximum(_tv(_premultiplied(window), mask), 1.0)
    A = window[..., 3:4] / 255.0
    C = window[..., :3]
    costs = {}
    for shift, (a, c) in layers.items():
        sa = a[None, ..., None]
        A0 = np.clip((A - sa) / (1 - sa), 0, 1)
        premul0 = np.clip(A * C - sa * c[None], 0, None) / (1 - sa)  # = A0 * C0
        costs[shift] = _tv(np.concatenate([premul0, A0 * 255], axis=-1), mask) / base
    return costs


@dataclass
class ShiftEvidence:
    total: dict[tuple[int, int], float]
    pictures: int


def fit_shifts(groups: dict[tuple[int, int], list[Path]], model: StampModel) -> list[dict]:
    """Measure the shift of every tile; ``groups`` maps a picture size to its pictures.

    The logo and both words of a tile always moved together in the measurements, so the evidence of a tile's
    elements is pooled and one shift is chosen per tile (written per element, the format allows more).
    """
    evidence: dict[tuple[int, int], ShiftEvidence] = {}
    elements_seen: dict[tuple[int, int], set[int]] = defaultdict(set)
    for (width, height), paths in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        stack = np.stack([load_rgba(p)[0] for p in paths])
        counted: set[tuple[int, int]] = set()
        for inst in model.instances(width, height, shifts=False):
            costs = _instance_costs(stack, inst.element, inst.y, inst.x)
            if len(costs) < 2:
                continue
            matrix = np.stack(list(costs.values()))  # (shifts, N)
            centred = matrix - matrix.mean(axis=0, keepdims=True)
            key = (inst.row, inst.col)
            ev = evidence.setdefault(key, ShiftEvidence(defaultdict(float), 0))
            for shift, row in zip(costs, centred, strict=True):
                ev.total[shift] += float(row.sum())
            if key not in counted:
                ev.pictures += len(paths)
                counted.add(key)
            elements_seen[key].add(inst.element.index)
        log.info("shift evidence from %d pictures of %dx%d", len(paths), width, height)
    entries = []
    for (row, col), ev in evidence.items():
        ranked = sorted(ev.total.items(), key=lambda kv: kv[1])
        (dy, dx), best = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else best
        margin = (second - best) / max(ev.pictures, 1)
        at_limit = dy in (min(SEARCH_DY), max(SEARCH_DY)) or dx in (min(SEARCH_DX), max(SEARCH_DX))
        if margin < MIN_MARGIN or (at_limit and ev.pictures < MIN_PICTURES_AT_LIMIT):
            log.info("tile (%d, %d): no reliable evidence, kept on the lattice", row, col)
            continue
        for element in sorted(elements_seen[(row, col)]):
            entries.append(
                {
                    "row": row,
                    "col": col,
                    "element": element,
                    "dy": dy,
                    "dx": dx,
                    "pictures": ev.pictures,
                    "margin": round((second - best) / max(ev.pictures, 1), 4),
                }
            )
    return entries

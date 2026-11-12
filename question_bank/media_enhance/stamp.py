"""The ИААА stamp and its exact removal.

Every official picture carries the same semi-transparent stamp: a logo and the word "ИААА" twice, white
letters with a black outline, at most 77/255 opaque, repeated on a 90 × 90 px lattice. It was composited with
straight-alpha "over" at whole-pixel positions, so it can be undone exactly once the stamp's opacity ``a`` and
colour ``W`` and its position in a picture are known:

    A = a + A0 (1 - a)          →   A0 = (A - a) / (1 - a)
    A C = a W + A0 (1 - a) C0   →   C0 = (A C - a W) / (A0 (1 - a))

``A``, ``C`` are the published alpha and colour, ``A0``, ``C0`` the picture before stamping.

Position: the lattice is anchored at the picture centre. The tile whose top-left corner is at ``(ceil(h / 2) -
ANCHOR_Y, floor(w / 2) - ANCHOR_X)`` contains the centre (tile R = 0, C = 0). The stamp was one large
hand-made layer, so some tiles sit a pixel or two away from the regular lattice; those shifts are measured
once per tile element (:mod:`question_bank.media_enhance.fit`) and stored with the tile.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from question_bank.fsutil import read_json, write_json

PERIOD = 90
ANCHOR_Y = 74
ANCHOR_X = 84
TILE_FILE = "stamp-tile.png"
SHIFTS_FILE = "shifts.json"


@dataclass(frozen=True)
class Element:
    """One connected part of the tile (the logo or one word) at (y, x) relative to the tile's top-left."""

    index: int
    y: int
    x: int
    alpha: np.ndarray  # (h, w) float32, 0..1, zero outside the element
    colour: np.ndarray  # (h, w, 3) float32, 0..255

    @property
    def shape(self) -> tuple[int, int]:
        return self.alpha.shape  # type: ignore[return-value]


@dataclass(frozen=True)
class Instance:
    """An element placed in a picture: tile (row, col) relative to the centre tile, top-left (y, x)."""

    row: int
    col: int
    element: Element
    y: int
    x: int


def tile_origin(width: int, height: int) -> tuple[int, int]:
    """Top-left corner (y, x) of the tile that contains the picture centre (tile 0, 0)."""
    return math.ceil(height / 2) - ANCHOR_Y, width // 2 - ANCHOR_X


def split_elements(tile: np.ndarray) -> list[Element]:
    """Split an RGBA tile (90, 90, 4 uint8) into connected parts; parts crossing the tile edge stay whole."""
    import cv2

    alpha = tile[:, :, 3].astype(np.float32) / 255.0
    colour = tile[:, :, :3].astype(np.float32)
    big_a = np.tile(alpha, (3, 3))
    big_c = np.tile(colour, (3, 3, 1))
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(
        (big_a > 0).astype(np.uint8), connectivity=8
    )
    found = []
    for label in range(1, count):
        x, y, w, h, _ = stats[label]
        cx, cy = centroids[label]
        if PERIOD <= cx < 2 * PERIOD and PERIOD <= cy < 2 * PERIOD:
            mask = labels[y : y + h, x : x + w] == label
            found.append(
                (
                    int(y) - PERIOD,
                    int(x) - PERIOD,
                    np.where(mask, big_a[y : y + h, x : x + w], 0.0).astype(np.float32),
                    np.where(mask[..., None], big_c[y : y + h, x : x + w], 0.0).astype(np.float32),
                )
            )
    found.sort(key=lambda e: (e[0], e[1]))
    return [Element(i, y, x, a, c) for i, (y, x, a, c) in enumerate(found)]


@dataclass
class StampModel:
    """The exact stamp tile plus the measured per-element shifts of the hand-made layer."""

    tile: np.ndarray  # (90, 90, 4) uint8: stamp colour in RGB, stamp opacity in A
    shifts: dict[tuple[int, int, int], tuple[int, int]] = field(
        default_factory=dict
    )  # (row, col, el) → (dy, dx)

    def __post_init__(self) -> None:
        if self.tile.shape != (PERIOD, PERIOD, 4) or self.tile.dtype != np.uint8:
            raise ValueError(f"stamp tile must be {PERIOD}x{PERIOD} RGBA uint8, got {self.tile.shape}")
        self.elements = split_elements(self.tile)

    # ------------------------------------------------------------------ geometry

    def instances(self, width: int, height: int, *, shifts: bool = True) -> list[Instance]:
        """Every element instance that touches a picture of the given size."""
        oy, ox = tile_origin(width, height)
        margin = 2 * PERIOD
        rows = range((-oy - margin) // PERIOD, (height - oy + margin) // PERIOD + 1)
        cols = range((-ox - margin) // PERIOD, (width - ox + margin) // PERIOD + 1)
        found = []
        for row in rows:
            for col in cols:
                for element in self.elements:
                    dy, dx = self.shifts.get((row, col, element.index), (0, 0)) if shifts else (0, 0)
                    y = oy + row * PERIOD + element.y + dy
                    x = ox + col * PERIOD + element.x + dx
                    h, w = element.shape
                    if y + h > 0 and x + w > 0 and y < height and x < width:
                        found.append(Instance(row, col, element, y, x))
        return found

    def layer(self, width: int, height: int, *, shifts: bool = True) -> tuple[np.ndarray, np.ndarray]:
        """Stamp opacity (h, w) and colour (h, w, 3) over a picture of the given size."""
        alpha = np.zeros((height, width), np.float32)
        colour = np.zeros((height, width, 3), np.float32)
        for inst in self.instances(width, height, shifts=shifts):
            paste(alpha, colour, inst.element, inst.y, inst.x)
        return alpha, colour

    # ------------------------------------------------------------------ files

    @classmethod
    def load(cls, directory: Path) -> StampModel:
        with Image.open(directory / TILE_FILE) as image:
            tile = np.asarray(image.convert("RGBA")).copy()
        shifts: dict[tuple[int, int, int], tuple[int, int]] = {}
        path = directory / SHIFTS_FILE
        if path.exists():
            payload = read_json(path)
            for entry in payload["shifts"]:
                shifts[(entry["row"], entry["col"], entry["element"])] = (entry["dy"], entry["dx"])
        return cls(tile, shifts)

    def save_tile(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        Image.fromarray(self.tile, "RGBA").save(directory / TILE_FILE, optimize=True)


def save_shifts(directory: Path, entries: list[dict], meta: dict) -> None:
    """Write shifts.json: ``entries`` are dicts with row, col, element, dy, dx plus evidence fields."""
    entries = sorted(entries, key=lambda e: (e["row"], e["col"], e["element"]))
    write_json(
        directory / SHIFTS_FILE,
        {"period": PERIOD, "anchor": {"y": ANCHOR_Y, "x": ANCHOR_X}, **meta, "shifts": entries},
    )


def paste(alpha: np.ndarray, colour: np.ndarray, element: Element, y: int, x: int) -> None:
    """Draw ``element`` with its top-left corner at (y, x) into the layer arrays, clipped to their bounds."""
    height, width = alpha.shape
    h, w = element.shape
    y0, x0, y1, x1 = max(y, 0), max(x, 0), min(y + h, height), min(x + w, width)
    if y0 >= y1 or x0 >= x1:
        return
    a = element.alpha[y0 - y : y1 - y, x0 - x : x1 - x]
    c = element.colour[y0 - y : y1 - y, x0 - x : x1 - x]
    sel = a > 0
    alpha[y0:y1, x0:x1][sel] = a[sel]
    colour[y0:y1, x0:x1][sel] = c[sel]


# ---------------------------------------------------------------------- compositing


def composite(rgba: np.ndarray, alpha: np.ndarray, colour: np.ndarray) -> np.ndarray:
    """Put the stamp layer over a picture (straight alpha "over"); used by the tests and the fitting."""
    A0 = rgba[..., 3:4].astype(np.float32) / 255.0
    C0 = rgba[..., :3].astype(np.float32)
    a = alpha[..., None]
    A = a + A0 * (1 - a)
    premul = a * colour + A0 * (1 - a) * C0
    C = np.where(A > 0, premul / np.maximum(A, 1e-6), 0)
    return np.dstack([np.rint(C), np.rint(A * 255)]).clip(0, 255).astype(np.uint8)


def invert(rgba: np.ndarray, alpha: np.ndarray, colour: np.ndarray) -> np.ndarray:
    """Remove the stamp layer from an RGBA picture (uint8); pixels the layer does not touch stay identical."""
    out = rgba.copy()
    sel = alpha > 0
    if not sel.any():
        return out
    a = alpha[sel][:, None]
    W = colour[sel]
    A = rgba[..., 3][sel].astype(np.float32)[:, None] / 255.0
    C = rgba[..., :3][sel].astype(np.float32)
    A0 = np.clip((A - a) / (1 - a), 0.0, 1.0)
    denom = A0 * (1 - a)
    C0 = np.where(denom > 1e-4, (A * C - a * W) / np.maximum(denom, 1e-4), 0.0)
    out[..., :3][sel] = np.rint(C0).clip(0, 255).astype(np.uint8)
    out[..., 3][sel] = np.rint(A0[:, 0] * 255).clip(0, 255).astype(np.uint8)
    return out


def remove(rgba: np.ndarray, model: StampModel) -> np.ndarray:
    """The picture without the stamp (RGBA uint8 in, RGBA uint8 out)."""
    height, width = rgba.shape[:2]
    alpha, colour = model.layer(width, height)
    return invert(rgba, alpha, colour)


def load_rgba(path: Path) -> tuple[np.ndarray, str]:
    """A picture as RGBA uint8 plus its original mode (to save RGB pictures as RGB again)."""
    with Image.open(path) as image:
        mode = image.mode
        return np.asarray(image.convert("RGBA")).copy(), mode


def save_like(path: Path, rgba: np.ndarray, mode: str) -> None:
    """Save as PNG in the original's colour mode (RGB stays RGB when it is fully opaque)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(rgba, "RGBA")
    if mode != "RGBA" and (rgba[..., 3] == 255).all():
        image = image.convert("RGB")
    tmp = path.with_name(path.name + ".tmp")
    image.save(tmp, "PNG", optimize=True)
    tmp.replace(path)

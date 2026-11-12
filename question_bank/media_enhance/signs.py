"""Sign pictures as SVG: reviewed recipes that place vector drawings where the official picture shows them.

A recipe (``data/enhance/signs/recipes.json``) lists, for one picture, the drawings to place and the box each
one fills, in the picture's own pixel coordinates; the composed SVG keeps the picture's size, so the app's
layout does not change. A drawing is either a Wikimedia Commons file (``"commons": "File:…"``) or one made for
this project (``"drawing": "markings/…svg"``). Each drawing is scaled uniformly so that its visible content
fills its box, centred; ids inside each drawing get a per-layer prefix so several drawings never clash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from lxml import etree

from question_bank.fsutil import read_json, write_json
from question_bank.media_enhance.svg import SVG_NS, XLINK_NS, sanitise

RECIPES = "recipes.json"
_URL_REF = re.compile(r"url\(\s*#([^)\s]+)\s*\)")


@dataclass
class Layer:
    box: tuple[float, float, float, float]  # x0, y0, x1, y1 in picture pixels
    commons: str | None = None
    drawing: str | None = None

    def source_key(self) -> str:
        return self.commons or f"project:{self.drawing}"


@dataclass
class Recipe:
    media_id: str
    width: int
    height: int
    layers: list[Layer]
    reviewed: str | None = None
    notes: list[str] = field(default_factory=list)


def load_recipes(directory: Path) -> dict[str, Recipe]:
    path = directory / RECIPES
    if not path.exists():
        return {}
    out = {}
    for mid, r in read_json(path)["recipes"].items():
        layers = [
            Layer(tuple(layer["box"]), layer.get("commons"), layer.get("drawing")) for layer in r["layers"]
        ]
        out[mid] = Recipe(mid, r["width"], r["height"], layers, r.get("reviewed"), r.get("notes", []))
    return out


def save_recipes(directory: Path, recipes: dict[str, Recipe]) -> None:
    def layer_json(layer: Layer) -> dict:
        key = {"commons": layer.commons} if layer.commons else {"drawing": layer.drawing}
        return {**key, "box": [round(v, 2) for v in layer.box]}

    payload = {
        mid: {
            "width": r.width,
            "height": r.height,
            "layers": [layer_json(layer) for layer in r.layers],
            **({"reviewed": r.reviewed} if r.reviewed else {}),
            **({"notes": r.notes} if r.notes else {}),
        }
        for mid, r in sorted(recipes.items())
    }
    write_json(directory / RECIPES, {"recipes": payload})


# ---------------------------------------------------------------------- geometry


def viewbox(svg: bytes) -> tuple[float, float, float, float]:
    root = etree.fromstring(svg, etree.XMLParser(resolve_entities=False, no_network=True))
    x, y, w, h = (float(v) for v in re.split(r"[\s,]+", root.get("viewBox", "").strip()))
    return x, y, w, h


def content_bounds(svg: bytes, render_px: int = 1024) -> tuple[float, float, float, float]:
    """Visible content of a (sanitised) drawing, in its own viewBox units: (x0, y0, x1, y1)."""
    import tempfile

    from PIL import Image

    from question_bank.media_enhance.svg import render_pngs

    vx, vy, vw, vh = viewbox(svg)
    scale = render_px / max(vw, vh)
    w, h = max(1, round(vw * scale)), max(1, round(vh * scale))
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "b.png"
        render_pngs([(svg, w, h, out)])
        with Image.open(out) as image:
            alpha = np.asarray(image.convert("RGBA"))[..., 3]
    ys, xs = np.nonzero(alpha > 8)
    if len(ys) == 0:
        return vx, vy, vx + vw, vy + vh
    sx, sy = vw / w, vh / h
    return vx + xs.min() * sx, vy + ys.min() * sy, vx + (xs.max() + 1) * sx, vy + (ys.max() + 1) * sy


def fit(
    bounds: tuple[float, float, float, float], box: tuple[float, float, float, float]
) -> tuple[float, float, float]:
    """Uniform scale and translation (s, tx, ty) that centre ``bounds`` in ``box`` as large as possible."""
    bx0, by0, bx1, by1 = bounds
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / (bx1 - bx0), (y1 - y0) / (by1 - by0))
    tx = x0 + ((x1 - x0) - s * (bx1 - bx0)) / 2 - s * bx0
    ty = y0 + ((y1 - y0) - s * (by1 - by0)) / 2 - s * by0
    return s, tx, ty


# ---------------------------------------------------------------------- composition


def _prefix_ids(root: etree._Element, prefix: str) -> None:
    ids = {e.get("id") for e in root.iter() if isinstance(e.tag, str) and e.get("id")}
    if not ids:
        return
    for e in root.iter():
        if not isinstance(e.tag, str):
            continue
        if e.get("id"):
            e.set("id", prefix + e.get("id"))
        for attr, value in list(e.attrib.items()):
            local = etree.QName(attr).localname
            if local == "href" and value.startswith("#") and value[1:] in ids:
                e.set(attr, "#" + prefix + value[1:])
            elif "url(" in value:
                e.set(
                    attr,
                    _URL_REF.sub(
                        lambda m: f"url(#{prefix}{m.group(1)})" if m.group(1) in ids else m.group(0), value
                    ),
                )
        if etree.QName(e.tag).localname == "style" and e.text:
            text = _URL_REF.sub(
                lambda m: f"url(#{prefix}{m.group(1)})" if m.group(1) in ids else m.group(0), e.text
            )
            for i in sorted(ids, key=len, reverse=True):
                text = re.sub(rf"#{re.escape(i)}\b", f"#{prefix}{i}", text)
            e.text = text


def compose(
    recipe: Recipe, sources: dict[str, bytes], bounds: dict[str, tuple[float, float, float, float]]
) -> bytes:
    """The recipe's SVG; ``sources`` (sanitised SVG) and ``bounds`` are keyed by ``Layer.source_key``."""
    nsmap = {None: SVG_NS, "xlink": XLINK_NS}
    out = etree.Element(f"{{{SVG_NS}}}svg", nsmap=nsmap)
    out.set("viewBox", f"0 0 {recipe.width} {recipe.height}")
    out.set("width", str(recipe.width))
    out.set("height", str(recipe.height))
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    for n, layer in enumerate(recipe.layers):
        key = layer.source_key()
        src = etree.fromstring(sources[key], parser)
        _prefix_ids(src, f"l{n}-")
        s, tx, ty = fit(bounds[key], layer.box)
        group = etree.SubElement(out, f"{{{SVG_NS}}}g")
        group.set("transform", f"matrix({s:.6g} 0 0 {s:.6g} {tx:.4f} {ty:.4f})")
        for attr in ("style", "fill", "stroke"):
            if src.get(attr) is not None:
                group.set(attr, src.get(attr))
        for child in list(src):
            group.append(child)
    data = etree.tostring(out, encoding="utf-8")
    check = sanitise(data)
    if check.issues:
        raise ValueError(f"{recipe.media_id}: composed SVG has issues: {check.issues}")
    return check.data


def split_vertical(rgba: np.ndarray, gap_fraction: float = 0.05) -> list[tuple[int, int, int, int]]:
    """Boxes of the parts of a picture stacked top to bottom (a sign above its plates). Parts are separated by
    rows that are empty or almost empty (under ``gap_fraction`` of the widest row: a post or a joining
    edge), or where a narrowing shape (the bottom of a round sign) is directly followed by a much wider one
    (a plate)."""
    alpha = rgba[..., 3] > 128
    rows = alpha.sum(axis=1)
    if rows.max() == 0:
        return []
    gap = rows <= rows.max() * gap_fraction
    for y in range(3, len(rows) - 2):
        window = rows[y - 3 : y + 1]
        if (
            0 < rows[y] < 0.6 * rows.max()
            and rows[y] == window.min()
            and rows[y + 1 : y + 3].max() >= 2.2 * rows[y]
        ):
            gap[y] = True
    parts, start = [], None
    for y, is_gap in enumerate(gap):
        if not is_gap and start is None:
            start = y
        elif is_gap and start is not None:
            parts.append((start, y))
            start = None
    if start is not None:
        parts.append((start, len(rows)))
    parts = [p for p in parts if p[1] - p[0] >= 4]
    if not parts:
        return []
    # the outer edges belong to the parts even where a round sign's first and last rows are nearly empty
    filled = np.nonzero(rows > 0)[0]
    parts[0] = (int(filled.min()), parts[0][1])
    parts[-1] = (parts[-1][0], int(filled.max()) + 1)
    boxes = []
    for y0, y1 in parts:
        cols = np.nonzero(alpha[y0:y1].any(axis=0))[0]
        if y1 - y0 >= 4 and len(cols):
            boxes.append((int(cols.min()), int(y0), int(cols.max()) + 1, int(y1)))
    return boxes

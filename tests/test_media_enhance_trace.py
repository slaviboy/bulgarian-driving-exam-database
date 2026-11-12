from __future__ import annotations

import numpy as np
from lxml import etree
from PIL import Image, ImageDraw

from question_bank.media_enhance.svg import sanitise
from question_bank.media_enhance.trace import fit_cubic, quantise, trace


def _sign(scale: int = 4) -> np.ndarray:
    big = Image.new("RGBA", (120 * scale * 2, 120 * scale * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    c = 120 * scale
    d.ellipse((4 * scale, 4 * scale, 2 * c - 4 * scale, 2 * c - 4 * scale), fill=(227, 30, 36, 255))
    d.ellipse((36 * scale, 36 * scale, 2 * c - 36 * scale, 2 * c - 36 * scale), fill=(255, 255, 255, 255))
    d.rectangle((60 * scale, 110 * scale, 2 * c - 60 * scale, 130 * scale), fill=(20, 20, 20, 255))
    return np.asarray(big.resize((120 * scale, 120 * scale), Image.LANCZOS))


def test_quantise_finds_the_flat_colours():
    palette = quantise(_sign())
    colours = set(palette.colours)
    assert (255, 255, 255) in colours and (0, 0, 0) in colours
    assert any(r > 200 and g < 60 for r, g, _ in colours)
    assert len(colours) == 3


def test_trace_gives_a_compact_clean_svg_in_picture_coordinates():
    svg = trace(_sign(), scale=4)
    check = sanitise(svg)
    assert check.ok and (check.width, check.height) == (120, 120)
    root = etree.fromstring(svg)
    paths = [e for e in root if etree.QName(e.tag).localname == "path"]
    assert len(paths) == 3  # white field, red ring, black bar: no extra edge colours
    assert len(svg) < 4000  # smooth curves, not the pixel staircase


def test_trace_can_keep_only_the_lettering():
    svg = trace(_sign(), scale=4, keep=lambda rgb: sum(rgb) < 240)
    fills = {e.get("fill") for e in etree.fromstring(svg) if etree.QName(e.tag).localname == "path"}
    assert fills == {"#000000"}


def test_fit_cubic_reproduces_a_quarter_circle_closely():
    t = np.linspace(0, np.pi / 2, 60)
    pts = np.stack([100 * np.cos(t), 100 * np.sin(t)], axis=1)
    # the end tangent points back into the curve
    segs = fit_cubic(pts, np.array([0.0, 1.0]), np.array([1.0, 0.0]), tolerance=0.5)
    assert len(segs) <= 2

from __future__ import annotations

from pathlib import Path

import numpy as np
from lxml import etree

from question_bank.media_enhance.signmatch import content_box
from question_bank.media_enhance.signs import (
    Layer,
    Recipe,
    compose,
    fit,
    load_recipes,
    save_recipes,
    split_vertical,
)
from question_bank.media_enhance.svg import sanitise


def _circle_over_plate(gap: int) -> np.ndarray:
    h, w = 160 + gap, 120
    rgba = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    rgba[np.hypot(yy - 50, xx - 60) <= 50] = (220, 30, 30, 255)
    rgba[100 + gap : 150 + gap, 5:115] = (255, 255, 255, 255)
    return rgba


def test_split_vertical_handles_gaps_touching_parts_and_single_signs():
    parts = split_vertical(_circle_over_plate(gap=6))
    assert parts[1] == (5, 106, 115, 156) and parts[0][:3] == (10, 0, 111) and parts[0][3] in (100, 101)
    touching = split_vertical(_circle_over_plate(gap=0))
    assert len(touching) == 2 and touching[1][1] in (99, 100, 101) and touching[0][1] == 0
    single = np.zeros((101, 101, 4), np.uint8)
    yy, xx = np.mgrid[0:101, 0:101]
    single[np.hypot(yy - 50, xx - 50) <= 50] = (0, 0, 255, 255)
    assert split_vertical(single) == [(0, 0, 101, 101)]  # a round sign is never cut at its thin top or bottom


def test_content_box_ignores_a_uniform_opaque_background():
    rgba = np.full((60, 80, 4), (235, 235, 235, 255), np.uint8)
    rgba[10:50, 20:70] = (200, 0, 0, 255)
    assert content_box(rgba) == (20, 10, 70, 50)


def test_fit_centres_content_in_its_box():
    s, tx, ty = fit((10, 10, 110, 60), (0, 0, 100, 100))  # 100 × 50 content into a 100 × 100 box
    assert s == 1.0 and (tx, ty) == (-10.0, 15.0)


SRC = b"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
 viewBox="0 0 10 10">
<defs><linearGradient id="g"><stop offset="0" stop-color="#f00"/></linearGradient></defs>
<rect id="r" width="10" height="10" fill="url(#g)"/><use xlink:href="#r"/></svg>"""


def test_compose_places_layers_and_keeps_their_ids_apart():
    recipe = Recipe("m-1", 40, 60, [Layer((0, 0, 40, 40), commons="A"), Layer((0, 40, 40, 60), commons="B")])
    data = compose(recipe, {"A": SRC, "B": SRC}, {"A": (0, 0, 10, 10), "B": (0, 0, 10, 10)})
    assert sanitise(data).ok
    root = etree.fromstring(data)
    assert root.get("viewBox") == "0 0 40 60"
    ids = [e.get("id") for e in root.iter() if isinstance(e.tag, str) and e.get("id")]
    assert sorted(ids) == ["l0-g", "l0-r", "l1-g", "l1-r"]
    text = data.decode()
    assert "url(#l1-g)" in text and 'href="#l1-r"' in text
    groups = [e for e in root if etree.QName(e.tag).localname == "g"]
    assert groups[0].get("transform") == "matrix(4 0 0 4 0.0000 0.0000)"
    assert groups[1].get("transform") == "matrix(2 0 0 2 10.0000 40.0000)"  # 20 × 20 centred in 40 × 20


def test_recipes_round_trip(tmp_path: Path):
    recipes = {
        "m-2": Recipe(
            "m-2", 50, 80, [Layer((1, 2, 49, 50), drawing="markings/x.svg")], "2026-11-12", ["note"]
        ),
        "m-1": Recipe("m-1", 10, 10, [Layer((0, 0, 10, 10), commons="File:BG road sign А1.svg")]),
    }
    save_recipes(tmp_path, recipes)
    loaded = load_recipes(tmp_path)
    assert list(loaded) == ["m-1", "m-2"]
    assert loaded["m-2"].layers[0].drawing == "markings/x.svg" and loaded["m-2"].reviewed == "2026-11-12"
    assert loaded["m-1"].layers[0].source_key() == "File:BG road sign А1.svg"


def test_compose_rotates_fits_exactly_and_covers():
    src = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 10"><rect width="20" height="10"/></svg>'
    recipe = Recipe(
        "m-3",
        40,
        40,
        [
            Layer((0, 0, 10, 20), commons="A", rotate=90),  # a 20 × 10 drawing turned upright fills 10 × 20
            Layer((20, 0, 40, 10), drawing="t.svg", exact=True, covers=[(1, 2, 3, 4, "#ffffff")]),
        ],
    )
    data = compose(
        recipe, {"A": src, "project:t.svg": src}, {"A": (0, 0, 20, 10), "project:t.svg": (5, 2, 9, 4)}
    )
    root = etree.fromstring(data)
    groups = [e for e in root if etree.QName(e.tag).localname == "g"]
    inner = groups[0][0]
    assert inner.get("transform") == "rotate(90 10.0000 5.0000)"
    assert groups[0].get("transform") == "matrix(1 0 0 1 -5.0000 5.0000)"
    assert groups[1].get("transform") == "matrix(1 0 0 1 20.0000 0.0000)"  # whole viewBox, not the content
    rect = next(e for e in root if etree.QName(e.tag).localname == "rect")
    assert (rect.get("x"), rect.get("width"), rect.get("fill")) == ("1.00", "2.00", "#ffffff")

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from question_bank.media_enhance.clean import clean_picture, stamp_score
from question_bank.media_enhance.fit import fit_shifts, measure_tile
from question_bank.media_enhance.stamp import (
    PERIOD,
    StampModel,
    composite,
    invert,
    split_elements,
    tile_origin,
)


def synthetic_tile() -> np.ndarray:
    """Two parts: a ring (white with a black rim) and a bar that crosses the tile's top edge."""
    yy, xx = np.mgrid[0:PERIOD, 0:PERIOD]
    tile = np.zeros((PERIOD, PERIOD, 4), np.uint8)
    r = np.hypot(yy - 40, xx - 30)
    ring = (r > 8) & (r < 13)
    rim = ((r > 7) & (r <= 8)) | ((r >= 13) & (r < 14))
    tile[ring] = (255, 255, 255, 70)
    tile[rim] = (0, 0, 0, 40)
    bar = (xx >= 60) & (xx < 75) & ((yy < 6) | (yy >= 84))
    tile[bar] = (250, 250, 250, 55)
    return tile


def textured(height: int, width: int, seed: int, *, transparent_margin: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:height, 0:width]
    base = np.stack(
        [
            60 + 120 * np.sin(xx / (17 + seed)) ** 2,
            90 + 80 * np.cos(yy / (23 + seed)) ** 2,
            40 + 150 * ((xx + yy) % 97) / 97,
        ],
        axis=-1,
    )
    base += rng.normal(0, 3, base.shape)
    rgba = np.dstack([base.clip(0, 255), np.full((height, width), 255.0)]).astype(np.uint8)
    if transparent_margin:
        rgba[:transparent_margin] = 0
        rgba[-transparent_margin:] = 0
        rgba[:, :transparent_margin] = 0
        rgba[:, -transparent_margin:] = 0
    return rgba


def test_tile_origin_is_centre_anchored():
    assert tile_origin(169, 147) == (0, 0)
    assert tile_origin(152, 152) == (2, -8)
    assert tile_origin(712, 394) == (123, 272)


def test_split_elements_keeps_parts_that_cross_the_edge_whole():
    elements = split_elements(synthetic_tile())
    assert len(elements) == 2
    bar = next(e for e in elements if e.shape[1] == 15)
    assert (bar.y % PERIOD, bar.x) == (84, 60) and bar.shape == (12, 15)  # one piece across the edge


def test_invert_undoes_composite_on_opaque_transparent_and_soft_pixels():
    rng = np.random.default_rng(1)
    original = rng.integers(0, 256, (60, 80, 4)).astype(np.uint8)
    original[:20, :, 3] = 255
    original[20:40, :, 3] = 0
    alpha = np.zeros((60, 80), np.float32)
    colour = np.zeros((60, 80, 3), np.float32)
    alpha[5:55, 10:70] = rng.uniform(0.05, 0.3, (50, 60))
    colour[5:55, 10:70] = rng.choice([0.0, 255.0], (50, 60))[..., None]
    stamped = composite(original, alpha, colour)
    restored = invert(stamped, alpha, colour)
    untouched = alpha == 0
    assert np.array_equal(restored[untouched], stamped[untouched])
    opaque = (original[..., 3] == 255) & ~untouched
    assert np.abs(restored[opaque].astype(int) - original[opaque].astype(int)).max() <= 2
    clear = (original[..., 3] == 0) & ~untouched
    assert restored[clear][:, 3].max() <= 1


def test_measure_tile_reads_the_stamp_from_transparent_backgrounds(tmp_path: Path):
    model = StampModel(synthetic_tile())
    paths = []
    for i, (w, h) in enumerate([(169, 147), (152, 152), (200, 120), (131, 177)]):
        picture = np.zeros((h, w, 4), np.uint8)
        picture[h // 3 : h // 2, w // 3 : w // 2] = (200, 30, 30, 255)  # some content
        a, c = model.layer(w, h)
        path = tmp_path / f"m-{i:016x}.png"
        Image.fromarray(composite(picture, a, c), "RGBA").save(path)
        paths.append(path)
    tile, stats = measure_tile(paths)
    expected = synthetic_tile()
    stamp = expected[..., 3] > 0
    assert np.array_equal(tile[..., 3], expected[..., 3])
    assert np.array_equal(tile[stamp][:, :3], expected[stamp][:, :3])
    assert stats["stamp_pixels"] == int(stamp.sum())


def test_fit_shifts_finds_a_tile_that_was_placed_one_pixel_lower(tmp_path: Path):
    true_model = StampModel(synthetic_tile())
    shifted = {(0, 1, e.index): (1, 0) for e in true_model.elements}
    true_model.shifts = shifted
    width, height = 260, 200
    paths = []
    for seed in range(6):
        a, c = true_model.layer(width, height)
        path = tmp_path / f"m-{seed:016x}.png"
        Image.fromarray(composite(textured(height, width, seed), a, c), "RGBA").save(path)
        paths.append(path)
    entries = fit_shifts({(width, height): paths}, StampModel(synthetic_tile()))
    found = {(e["row"], e["col"]): (e["dy"], e["dx"]) for e in entries}
    assert found[(0, 1)] == (1, 0)
    assert found[(0, 0)] == (0, 0)


def test_clean_picture_scores_and_keeps_untouched_pixels(tmp_path: Path):
    model = StampModel(synthetic_tile())
    width, height = 240, 180
    a, c = model.layer(width, height)
    original = textured(height, width, 3)
    stamped = composite(original, a, c)
    src = tmp_path / "m-0000000000000001.png"
    Image.fromarray(stamped[..., :3], "RGB").save(src)
    result = clean_picture(src, model, tmp_path / "out")
    assert result.score_before > 0.3
    assert abs(result.score_after) < 0.06
    with Image.open(tmp_path / "out" / src.name) as image:
        assert image.mode == "RGB"
        cleaned = np.asarray(image)
    assert np.abs(cleaned.astype(int) - original[..., :3].astype(int)).max() <= 2


@pytest.mark.parametrize("shift", [(0, 0), (1, 0)])
def test_stamp_score_detects_a_leftover(shift):
    model = StampModel(synthetic_tile())
    width, height = 240, 180
    a, c = model.layer(width, height)
    original = textured(height, width, 5)
    stamped = composite(original, a, c)
    wrong = StampModel(synthetic_tile())
    wrong.shifts = {
        (r, col, e.index): shift for r in range(-3, 4) for col in range(-3, 4) for e in wrong.elements
    }
    wa, wc = wrong.layer(width, height)
    cleaned = invert(stamped, wa, wc)
    score = stamp_score(cleaned, stamped, a, c)
    if shift == (0, 0):
        assert abs(score) < 0.06
    else:
        assert abs(score) > 0.1

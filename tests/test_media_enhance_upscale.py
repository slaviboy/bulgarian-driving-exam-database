from __future__ import annotations

import numpy as np

from question_bank.media_enhance.upscale import bleed_alpha, content_check


def test_bleed_alpha_fills_transparent_colour_and_keeps_alpha():
    rgba = np.zeros((20, 20, 4), np.uint8)
    rgba[5:15, 5:15] = (200, 40, 40, 255)
    out = bleed_alpha(rgba)
    assert np.array_equal(out[..., 3], rgba[..., 3])
    assert np.array_equal(out[5:15, 5:15], rgba[5:15, 5:15])
    assert tuple(out[4, 10, :3]) == (200, 40, 40)  # neighbour of the square took its colour, not black


def test_content_check_accepts_sharpening_but_not_a_changed_detail():
    rng = np.random.default_rng(0)
    yy, xx = np.mgrid[0:120, 0:160]
    base = np.dstack([128 + 60 * np.sin(xx / 9.0), 128 + 60 * np.cos(yy / 7.0), np.full((120, 160), 90.0)])
    picture = np.dstack([base, np.full((120, 160), 255.0)]).clip(0, 255).astype(np.uint8)
    sharper = picture.astype(np.float32)
    sharper[..., :3] += rng.normal(0, 2, sharper[..., :3].shape)
    psnr, ssim, _ = content_check(sharper.clip(0, 255).astype(np.uint8), picture)
    assert psnr > 30 and ssim > 0.9
    changed = picture.copy()
    changed[40:70, 60:100, :3] = 20  # a dark block where there was none: a different "label"
    _, _, worst = content_check(changed, picture)
    assert worst < 0.5

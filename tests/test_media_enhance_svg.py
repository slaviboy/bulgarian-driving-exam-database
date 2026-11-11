from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from question_bank.media_enhance.svg import render_pngs, sanitise

SIGN = b"""<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="200" height="200" onload="alert(1)"
     inkscape:version="1.2">
  <!-- comment -->
  <metadata><rdf/></metadata>
  <script>alert(1)</script>
  <a href="https://example.com"><circle cx="100" cy="100" r="96" fill="#e30613"/></a>
  <circle cx="100" cy="100" r="70" fill="#fff" inkscape:label="inner" onclick="x()"/>
  <use xlink:href="#ok"/>
</svg>"""


def test_sanitise_strips_active_content_and_keeps_the_drawing():
    check = sanitise(SIGN)
    assert check.ok, check.issues
    text = check.data.decode()
    for bad in ("script", "onload", "onclick", "inkscape", "metadata", "comment", "example.com"):
        assert bad not in text
    assert text.count("<circle") == 2  # the circle inside <a> survived the unwrapping
    assert 'viewBox="0 0 200 200"' in text and (check.width, check.height) == (200, 200)


@pytest.mark.parametrize(
    ("body", "issue"),
    [
        ('<text x="1" y="9">5 т</text>', "live text (must become paths)"),
        ('<filter id="f"/><rect width="5" height="5" filter="url(#f)"/>', "filter (AndroidSVG ignores it)"),
        ('<use xlink:href="other.svg#x"/>', "external reference 'other.svg#x'"),
        ("<style>@import url(x.css);</style>", "external reference in <style>"),
    ],
)
def test_sanitise_reports_what_androidsvg_cannot_draw(body: str, issue: str):
    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 10 10">'
        f"{body}</svg>"
    ).encode()
    assert issue in sanitise(doc).issues


def test_sanitise_rejects_non_svg_and_entities():
    assert sanitise(b"<html/>").issues == ["root element is not <svg>"]
    xxe = b'<?xml version="1.0"?><!DOCTYPE s [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><g>&x;</g></svg>'  # noqa: E501
    assert b"passwd" not in sanitise(xxe).data


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="Playwright Chromium is not installed")
def test_render_pngs_draws_the_svg_at_the_requested_size(tmp_path: Path):
    check = sanitise(SIGN)
    out = tmp_path / "sign.png"
    render_pngs([(check.data, 120, 120, out)])
    with Image.open(out) as image:
        rgba = np.asarray(image.convert("RGBA"))
    assert rgba.shape == (120, 120, 4)
    assert rgba[0, 0, 3] == 0  # transparent corner
    assert tuple(rgba[60, 60, :3]) == (255, 255, 255)  # white centre
    assert rgba[60, 8, 0] > 200 and rgba[60, 8, 1] < 40  # red ring

"""SVG sign drawings: make them safe and AndroidSVG-friendly, check them, and render raster fallbacks.

The app draws signs with AndroidSVG (through ``coil-svg``), which supports the static subset of SVG 1.1:
shapes, paths, gradients, clip paths and simple CSS. :func:`sanitise` keeps exactly that: scripts, event
handlers, external references, editor metadata and comments are removed, a ``viewBox`` is guaranteed, and
constructs AndroidSVG cannot draw faithfully (live ``<text>``, filters, embedded raster images) are reported
as issues, so a recipe has to replace them (text becomes paths) before a drawing is accepted.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
_ALLOWED = {
    "svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "defs", "use", "symbol",
    "linearGradient", "radialGradient", "stop", "clipPath", "mask", "style",
    "text", "tspan", "filter", "image",
}  # fmt: skip
_REPORTED = {"text": "live text (must become paths)", "tspan": "live text (must become paths)",
             "filter": "filter (AndroidSVG ignores it)", "image": "embedded raster image"}  # fmt: skip
_DROPPED = {"script", "foreignObject", "metadata", "title", "desc", "animate", "animateTransform", "set",
            "animateMotion", "font", "font-face", "cursor"}  # fmt: skip
_UNWRAPPED = {"a", "switch"}  # keep their children, drop the wrapper
_LENGTH = re.compile(r"^\s*([0-9.]+)\s*(px)?\s*$")
MAX_BYTES = 200_000


@dataclass
class SvgCheck:
    data: bytes
    issues: list[str] = field(default_factory=list)
    width: float = 0.0
    height: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.issues


def _local(tag: object) -> str:
    return etree.QName(tag).localname if isinstance(tag, str) else ""


def sanitise(data: bytes) -> SvgCheck:
    """A cleaned copy of an SVG document plus everything that still keeps it from being accepted."""
    parser = etree.XMLParser(resolve_entities=False, no_network=True, remove_comments=True, remove_pis=True)
    try:
        root = etree.fromstring(data, parser=parser)
    except etree.XMLSyntaxError as exc:
        return SvgCheck(b"", [f"not XML: {exc}"])
    if _local(root.tag) != "svg" or etree.QName(root.tag).namespace != SVG_NS:
        return SvgCheck(b"", ["root element is not <svg>"])
    issues: list[str] = []
    for wrapper in [e for e in root.iter() if isinstance(e.tag, str) and _local(e.tag) in _UNWRAPPED]:
        parent = wrapper.getparent()
        if parent is not None:
            index = parent.index(wrapper)
            for child in list(wrapper):
                parent.insert(index, child)
                index += 1
            parent.remove(wrapper)
    for element in list(root.iter()):
        if not isinstance(element.tag, str):
            continue
        name = etree.QName(element.tag)
        parent = element.getparent()
        if name.namespace != SVG_NS or name.localname in _DROPPED or name.localname not in _ALLOWED:
            if parent is not None:
                parent.remove(element)
            continue
        if name.localname in _REPORTED:
            issues.append(_REPORTED[name.localname])
        if name.localname == "style" and re.search(r"@import|url\((?!#)", element.text or ""):
            issues.append("external reference in <style>")
        for attr in list(element.attrib):
            qname = etree.QName(attr)
            local = qname.localname
            if qname.namespace not in (None, XLINK_NS) or local.lower().startswith("on"):
                del element.attrib[attr]
            elif local == "href" and not element.attrib[attr].startswith("#"):
                if name.localname == "image":
                    del element.attrib[attr]
                else:
                    issues.append(f"external reference {element.attrib[attr][:40]!r}")
                    del element.attrib[attr]
            elif local == "style" and (
                "url(" in element.attrib[attr] and "url(#" not in element.attrib[attr]
            ):
                issues.append("external url() in style")
            elif local == "filter":
                issues.append("filter (AndroidSVG ignores it)")
    width = height = 0.0
    viewbox = root.get("viewBox")
    if viewbox:
        parts = re.split(r"[\s,]+", viewbox.strip())
        if len(parts) == 4:
            width, height = float(parts[2]), float(parts[3])
    if not width or not height:
        w, h = _LENGTH.match(root.get("width", "")), _LENGTH.match(root.get("height", ""))
        if w and h:
            width, height = float(w.group(1)), float(h.group(1))
            root.set("viewBox", f"0 0 {width:g} {height:g}")
        else:
            issues.append("no viewBox and no numeric width/height")
    if width and height:
        root.set("width", f"{width:g}")
        root.set("height", f"{height:g}")
    for attr in list(root.attrib):
        if attr not in (
            "viewBox",
            "width",
            "height",
            "preserveAspectRatio",
            "version",
            "style",
            "fill",
            "stroke",
        ):
            del root.attrib[attr]
    etree.cleanup_namespaces(root, top_nsmap={None: SVG_NS, "xlink": XLINK_NS})
    out = etree.tostring(root, xml_declaration=False, encoding="utf-8")
    if len(out) > MAX_BYTES:
        issues.append(f"too large ({len(out)} bytes)")
    return SvgCheck(out, sorted(set(issues)), width, height)


# ---------------------------------------------------------------------- raster fallbacks


def render_pngs(jobs: list[tuple[bytes, int, int, Path]]) -> None:
    """Render SVG documents to transparent PNGs of exactly (width, height) with headless Chromium.

    The SVG is shown through an ``<img>`` element, where browsers never run scripts or load resources.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        for data, width, height, out in jobs:
            page.set_viewport_size({"width": width, "height": height})
            src = "data:image/svg+xml;base64," + base64.b64encode(data).decode("ascii")
            page.set_content(
                "<html><body style='margin:0;background:transparent'>"
                f"<img id='i' src='{src}' style='display:block;width:{width}px;height:{height}px'>"
                "</body></html>"
            )
            page.wait_for_function("document.getElementById('i').complete")
            out.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(
                path=str(out), omit_background=True, clip={"x": 0, "y": 0, "width": width, "height": height}
            )
        browser.close()

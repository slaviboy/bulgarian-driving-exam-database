"""Static HTML review sheets: every row shows one picture in several versions side by side.

The sheets are local files (they reference the pictures by relative path) and are not published.
"""

from __future__ import annotations

import html
import os
from dataclasses import dataclass, field
from pathlib import Path

from question_bank.fsutil import write_text


@dataclass
class Row:
    title: str
    images: list[tuple[str, Path]]  # (caption, file)
    notes: list[str] = field(default_factory=list)
    width: int | None = None  # CSS width of every image of the row at zoom 1× (so versions compare 1:1)


_CSS = """
:root { color-scheme: light dark; --bg: #f6f6f4; --fg: #1d1d1b; --card: #fff; --muted: #6b6b66;
  --line: #ddd; }
@media (prefers-color-scheme: dark) { :root { --bg: #161615; --fg: #ecece8; --card: #22221f; --muted: #a3a39c;
  --line: #3a3a36; } }
body { margin: 0; padding: 16px; background: var(--bg); color: var(--fg);
  font: 14px/1.4 system-ui, sans-serif; }
h1 { font-size: 20px; margin: 0 0 4px; } p.lead { color: var(--muted); margin: 0 0 16px; }
.controls { position: sticky; top: 0; background: var(--bg); padding: 8px 0; z-index: 1; display: flex;
  gap: 12px; flex-wrap: wrap; align-items: center; border-bottom: 1px solid var(--line);
  margin-bottom: 12px; }
.row { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 10px;
  margin: 0 0 12px; }
.row h2 { font-size: 14px; margin: 0 0 6px; font-weight: 600; }
.row .notes { color: var(--muted); font-size: 12px; }
.imgs { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-start; }
figure { margin: 0; } figcaption { font-size: 12px; color: var(--muted); }
.checker { background-color: #fff; background-image: linear-gradient(45deg, #ccc 25%, transparent 25%),
  linear-gradient(-45deg, #ccc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #ccc 75%),
  linear-gradient(-45deg, transparent 75%, #ccc 75%); background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0; display: inline-block; line-height: 0; }
img { image-rendering: auto; max-width: 100%; } body.pixel img { image-rendering: pixelated; }
"""

_JS = """
const zoom = document.getElementById('zoom');
function apply() {
  document.querySelectorAll('img[data-w]').forEach(i => {
    i.style.width = (i.dataset.w * zoom.value) + 'px';
  });
  document.getElementById('zv').textContent = zoom.value + '×';
}
zoom.addEventListener('input', apply);
document.getElementById('px').addEventListener('change',
  e => document.body.classList.toggle('pixel', e.target.checked));
window.addEventListener('load', () => { document.querySelectorAll('img').forEach(i => {
  i.dataset.w = i.dataset.base || i.naturalWidth; }); apply(); });
"""


def write_sheet(path: Path, title: str, lead: str, rows: list[Row]) -> None:
    """Write the sheet to ``path`` (images are referenced relative to it)."""
    parts = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        f"<title>{html.escape(title)}</title><style>{_CSS}</style></head><body>",
        f"<h1>{html.escape(title)}</h1><p class='lead'>{html.escape(lead)}</p>",
        "<div class='controls'><label>Zoom "
        "<input id='zoom' type='range' min='1' max='6' step='0.5' value='1'> <span id='zv'>1×</span></label>"
        "<label><input id='px' type='checkbox'> show pixels</label></div>",
    ]
    for row in rows:
        parts.append(f"<section class='row'><h2>{html.escape(row.title)}</h2><div class='imgs'>")
        for caption, file in row.images:
            rel = os.path.relpath(file, path.parent).replace(os.sep, "/")
            data = f" data-base='{row.width}'" if row.width else ""
            parts.append(
                f"<figure><div class='checker'><img src='{html.escape(rel)}' loading='lazy'{data} "
                f"alt='{html.escape(caption)}'></div><figcaption>{html.escape(caption)}</figcaption></figure>"
            )
        parts.append("</div>")
        if row.notes:
            parts.append(f"<div class='notes'>{'<br>'.join(html.escape(n) for n in row.notes)}</div>")
        parts.append("</section>")
    parts.append(f"<script>{_JS}</script></body></html>")
    write_text(path, "\n".join(parts))

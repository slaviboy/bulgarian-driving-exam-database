"""Extract the per-section question quotas (Таблица 1–22) from the ИААА exam methodology PDF.

Source: "Методика за провеждане на изпитите за придобиване на правоспособност за управление на МПС",
https://rta.government.bg/upload/13306/Metodika_izpiti.pdf (marked "Проект!", 2024). Research tool:
requires the `dev` extra (pdfplumber). The output is evidence for docs/exam-rules.md and the curated
exam configurations; it is not used at build time.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

METHODOLOGY_URL = "https://rta.government.bg/upload/13306/Metodika_izpiti.pdf"

_TABLE_LABEL = re.compile(r"Таблица\s+(\d+)", re.IGNORECASE)
_SECTION = re.compile(r"^РАЗДЕЛ\s+(\d+)\s*[.:]\s*(.+)$", re.IGNORECASE | re.DOTALL)
_TOTAL = re.compile(r"Общ брой на въпросите", re.IGNORECASE)
_SUBTOPIC = re.compile(r"\s\d+\.\d+\.\s")


def _clean(cell: str | None) -> str:
    return re.sub(r"\s+", " ", (cell or "")).strip()


def _section_title(text: str) -> str:
    """'ОБЩИ СВЕДЕНИЯ ЗА АВТОМОБИЛА 1.1. Основни …' → 'ОБЩИ СВЕДЕНИЯ ЗА АВТОМОБИЛА'."""
    head = _SUBTOPIC.split(" " + text, maxsplit=1)[0]
    return head.strip()


def extract_tables(pdf_path: Path) -> list[dict[str, Any]]:
    import pdfplumber  # research-only dependency

    labels: list[tuple[int, int]] = []  # (page index, table number) in reading order
    raw_tables: list[tuple[int, list[list[str | None]]]] = []
    with pdfplumber.open(pdf_path) as pdf:
        for index, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            labels.extend((index, int(n)) for n in _TABLE_LABEL.findall(text))
            for table in page.extract_tables():
                raw_tables.append((index, table))

    # Merge tables continued on the next page (no header row, previous table has no total yet).
    merged: list[dict[str, Any]] = []
    for page_index, rows in raw_tables:
        cells = [[_clean(c) for c in row] for row in rows if any(row)]
        if not cells:
            continue
        has_header = "брой въпроси" in " ".join(cells[0]).lower()
        if has_header:
            merged.append({"page": page_index + 1, "program": cells[0][0], "rows": cells[1:]})
        elif merged and not any(_TOTAL.search(r[0]) for r in merged[-1]["rows"]):
            merged[-1]["rows"].extend(cells)
        # tables without the "Брой въпроси" header belong to the practical-exam part and are ignored

    # "Таблица N" also occurs in body text ("…съгласно разпределението в Таблица 7"), so labels are only used
    # to check that the captions cover exactly 1..N; the tables themselves are numbered in reading order.
    expected = set(range(1, len(merged) + 1))
    if {n for _page, n in labels} != expected:
        raise ValueError(f"table labels {sorted({n for _p, n in labels})} do not match {len(merged)} tables")

    result = []
    for number, table in enumerate(merged, start=1):
        sections, total = [], None
        for row in table["rows"]:
            label, count = row[0], re.sub(r"\s+", "", row[-1] if len(row) > 1 else "")
            if _TOTAL.search(label):
                total = int(re.sub(r"\D", "", count) or 0)
                continue
            match = _SECTION.match(label)
            if match and count.isdigit():
                sections.append(
                    {
                        "number": int(match.group(1)),
                        "title": _section_title(match.group(2)),
                        "count": int(count),
                    }
                )
        if total is None or not sections:
            raise ValueError(f"Таблица {number}: no sections or no total found")
        sections_sum = sum(s["count"] for s in sections)
        # The draft document is not always internally consistent (Таблица 17 lists 14 questions but states
        # 15). Such tables are reported, never silently corrected.
        result.append(
            {
                "table": number,
                "page": table["page"],
                "program": table["program"],
                "sections": sections,
                "total": total,
                "sections_sum": sections_sum,
                "consistent": sections_sum == total,
            }
        )
    return result

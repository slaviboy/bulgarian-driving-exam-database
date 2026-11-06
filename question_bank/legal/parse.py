"""Split the text of a Bulgarian legal act into addressable units (articles, paragraphs, points, §).

The input is the plain text of a consolidated act as published on government sites (``pdftotext`` of a
PDF, or the paragraphs of a DOCX). The output maps canonical unit IDs to their current text:

* ``чл. 50`` — a whole article; ``чл. 50, ал. 1`` — a paragraph; ``чл. 50, ал. 1, т. 2`` — a point;
* ``§ 6`` and ``§ 6, т. 21`` — the numbered provisions of the act's additional and transitional provisions.

Only the act's own current text is kept:

* earlier wordings ("Редакция към ДВ, бр. …" followed by the old text) are dropped;
* the provisions of amending acts end the text: a final-provisions heading with "към"
  ("… разпоредби КЪМ ЗАКОНА ЗА ИЗМЕНЕНИЕ …") or one of a kind the act already had (exports repeat
  "ПРЕХОДНИ И ЗАКЛЮЧИТЕЛНИ РАЗПОРЕДБИ" for every amending act); so do the annexes ("Приложение № …");
* amendment notes such as "(Изм. - ДВ, бр. 43 от 2002 г.)" are removed from the wording;
* chapter and section headings and the page headers and footers of the export are removed.

Articles may start in the middle of a line (some exports run several articles together), so the structure
is recognised in the running text: a unit marker counts only at the start of a line or after the end of a
sentence, and paragraph and point numbers must follow each other (1, 2, 2а, 3 …).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Lines that are page furniture of the export, not text of the act.
_FURNITURE = [
    re.compile(r"^\s*Страница \d+ от \d+\s*$"),
    re.compile(r"^\s*Източник: Правно-информационни системи .*$"),
    # The print date in the page header of a PDF export ("19/04/2024 г."); acts write dates as 19.04.2024 г.
    re.compile(r"^\s*\d{2}/\d{2}/\d{4} г\.\s*$"),
]
# The same print date when the extraction put it at the end of a line of text.
_PRINT_DATE = re.compile(r"\s+\d{2}/\d{2}/\d{4} г\.\s*$")
# Comparatives whose hyphen the published files lost ("поголяма" for "по-голяма"; the same files write
# "по-голяма" elsewhere). Only stems after which "по" + stem is never a word of its own.
_LOST_HYPHEN = re.compile(
    r"(?i)(?<![а-я])(по|най)(?=(?:голям|голем|малк|висок|ниск|дълг|къс|широк|тесн|бърз|бавн|тежк)[а-я]*)"
)
# The same comparatives with a space after the hyphen ("по- малко"), unlike a suspended hyphen ("дву- или").
_SPACED_HYPHEN = re.compile(r"(?i)(?<![а-я])(по|най)- (?!(?:и|или)\b)(?=[а-я])")
# Text the Constitutional Court struck down stays in the files between two lines of dashes, after a note
# such as "(…; обявена за противоконституционна от КС на РБ - бр. 20 от 2012 г.)". It is no longer law: a
# whole provision goes (and so counts as repealed); "относно предл. второ" removes that sentence and
# "в частта "28 и"" those words.
_FRAME = re.compile(r"^\s*[—–]{8,}\s*$")
_STRUCK = re.compile(r"(?i)обяв\w+ за противоконституцион\w+ от КС(?P<scope>.*?)\s+-\s+бр\.")
_STRUCK_SENTENCE = re.compile(r"(?i)относно предл\.\s*(\w+)")
_STRUCK_WORDS = re.compile(r'в частта\s+["„“]([^"“”]+)["”“]')
_ORDINALS = {"първо": 1, "второ": 2, "трето": 3, "четвърто": 4, "пето": 5}
# A letter whose whole text was struck down: only its marker and note are left ("д) (нова - …)").
_LETTER_NOTE_ONLY = re.compile(r"^\s*[а-я]\)\s*\(.*\)\s*$")
# Editor's notes of the files ("(*) Бел. ред. - …") and their "(*)" markers are not text of the act.
_EDITOR_NOTE = re.compile(r"^\s*(?:\(\*\)\s*)?Бел\. ред\.")
_STAR = re.compile(r"\s*\(\*\)")
# Final provisions ("Допълнителни разпоредби", "ПРЕХОДНИ И ЗАКЛЮЧИТЕЛНИ РАЗПОРЕДБИ", "Заключителна …").
_FINAL = re.compile(r"(?i)^\s*(допълнителн|преходн|заключителн)\w*(?:\s+и\s+(\w+))?\s+разпоредб[аи]\b(.*)$")
_ANNEX = re.compile(r"^\s*Приложение №")
_REDACTION = re.compile(r"^\s*Редакция към ДВ")
# Chapter and section headings: "Глава втора. ПРАВИЛА …" on one line, or "Глава втора" / "Раздел I" with
# the title on the next line. Latin and Cyrillic look-alikes occur in section numbers ("Раздел ХIV", "IXa").
_CHAPTER = re.compile(r"(?i)^\s*(?:Глава\s+\S+(?:\s+\"?[а-я]\"?)?|Раздел\s+[IVXLCХІ]+[a-zа-я]?)(?:\.|\s*$)")
_TOP = re.compile(
    r"(?:(?<=\n)|(?<=^)|(?<=[.;:!?\"”“»)]\s))(?:Чл\.\s(?P<art>\d+[а-я]?)\.|§\s(?P<par>\d+[а-я]?)\.)\s"
)
_TOP_LINE = re.compile(r"^\s*(?:Чл\.\s(\d+[а-я]?)\.|§\s(\d+[а-я]?)\.)\s")
_UNIT_START = re.compile(r"^\s*(?:Чл\.|§|\(|\d)")
# Amendment notes: "(Изм. - ДВ, бр. 43 от 2002 г.)", "(нова – ДВ, бр. …)", and "(В сила от 1.01.2000 г.)".
_NOTE = re.compile(r"\s*\((?:(?=[^()]*ДВ,?\s*бр\.)|(?=[Вв] сила от \d))[^()]*\)")
# A repealed paragraph is left as "(1)." once its note is removed; it still counts in the numbering.
_PARAGRAPH = re.compile(r"(?:(?<=\n)|(?<=^)|(?<=[.;:!?\"”“»]\s))\((\d+[а-я]?)\)(?:\s|(?=[.;])|$)")
# A repealed point is left as "42.." or "3.;" once its note is removed; it still counts in the numbering.
_POINT = re.compile(r"(?:(?<=\n)|(?<=^)|(?<=[.;:!?\"”“»]\s))(\d+[а-я]?)\.(?:\s|(?=[.;])|$)")
_SPACES = re.compile(r"\s+")
_MONTHS = {
    m: i + 1
    for i, m in enumerate(
        ["яну", "фев", "мар", "апр", "май", "юни", "юли", "авг", "сеп", "окт", "ное", "дек"]
    )
}
_DATE = re.compile(
    r"ДВ\.?,?\s*бр\.\s*\d+\s+от\s+(?:\d+\s+\S+\s+\d{4}\s*г\.?|\d{1,2}\.\d{1,2}\.\d{4}\s*г\.?)"
    r"|(?<=[,\s])бр\.\s*\d+\s+от\s+\d{1,2}\.\d{1,2}\.\d{4}\s*г\."
)


@dataclass
class ParsedAct:
    title: str
    header: list[str]
    units: dict[str, str] = field(default_factory=dict)
    order: list[str] = field(default_factory=list)
    repealed: list[str] = field(default_factory=list)

    @property
    def last_amendment(self) -> str | None:
        """The last State Gazette issue named in the header: the consolidation date of the published text."""
        found = _DATE.findall(" ".join(self.header))
        if not found:
            return None
        last = _SPACES.sub(" ", found[-1])
        m = re.search(r"бр\.\s*(\d+)\s+от\s+(\d+)[.\s]+(\S+?)[.\s]+(\d{4})", last)
        if not m:
            return last.strip()
        issue, day, month, year = m.groups()
        month_number = int(month) if month.isdigit() else _MONTHS.get(month.lower()[:3])
        if month_number is None:
            return last.strip()
        return f"ДВ, бр. {issue} от {int(day):02d}.{month_number:02d}.{year} г."


def _number_key(number: str) -> tuple[int, str]:
    m = re.match(r"(\d+)([а-я]?)", number)
    return (int(m.group(1)), m.group(2)) if m else (0, "")


def _follows(previous: str | None, candidate: str) -> bool:
    """1 → 2, 2 → 2а, 2а → 2б or 3: consecutive numbering of paragraphs and points."""
    n, suffix = _number_key(candidate)
    if previous is None:
        return n == 1 and suffix == ""
    pn, ps = _number_key(previous)
    if n == pn:
        return suffix > ps
    return n == pn + 1 and suffix == ""


def _split_numbered(text: str, marker: re.Pattern[str]) -> tuple[str, list[tuple[str, str]]]:
    """Lead-in text and the consecutive numbered parts that follow it."""
    accepted: list[tuple[str, int, int]] = []
    previous: str | None = None
    for m in marker.finditer(text):
        if _follows(previous, m.group(1)):
            accepted.append((m.group(1), m.start(), m.end()))
            previous = m.group(1)
    if not accepted:
        return text, []
    lead = text[: accepted[0][1]]
    parts = []
    for i, (number, _, end) in enumerate(accepted):
        stop = accepted[i + 1][1] if i + 1 < len(accepted) else len(text)
        parts.append((number, text[end:stop]))
    return lead, parts


def clean(text: str) -> str:
    """Text without amendment notes and with single spaces."""
    return _SPACES.sub(" ", _NOTE.sub("", text)).strip()


def _is_heading(line: str) -> bool:
    return bool(_CHAPTER.match(line) or _FINAL.match(line))


def _final_kinds(match: re.Match[str]) -> set[str]:
    kinds = {match.group(1).lower()[:5]}
    if match.group(2):
        kinds.add(match.group(2).lower()[:5])
    return kinds


def _end_of_act(lines: list[str]) -> int:
    """The index of the first line that no longer belongs to the act's own text."""
    seen: set[str] = set()
    for i, line in enumerate(lines):
        if _ANNEX.match(line):
            return i
        final = _FINAL.match(line)
        if final:
            kinds = _final_kinds(final)
            if "към" in final.group(3).lower() or kinds & seen:
                return i
            seen |= kinds
    return len(lines)


def _blank_headings(lines: list[str]) -> list[str]:
    """Headings become empty lines (unit boundaries), with everything up to the next unit: the title line
    after a bare "Глава …" / "Раздел …" and the second line of a heading that wraps. A unit always starts
    with "Чл." or "§"."""
    out: list[str] = []
    in_heading = False
    for line in lines:
        if _is_heading(line):
            out.append("")
            in_heading = True
            continue
        if in_heading and line and not _UNIT_START.match(line):
            out.append("")
            continue
        if line:
            in_heading = False
        out.append(line)
    return out


def _unit_of(match: re.Match[str]) -> str:
    return match.group(1) if match.group(1) else "§" + match.group(2)


def _drop_redactions(lines: list[str]) -> list[str]:
    """Remove every earlier wording: a "Редакция към ДВ, бр. …" line and the old unit after it."""
    kept: list[str] = []
    skipping: str | None = None  # the unit whose old wording is being skipped
    awaiting = False  # a redaction line was seen, its unit has not started yet
    for line in lines:
        if _REDACTION.match(line):
            awaiting, skipping = True, None
            continue
        top = _TOP_LINE.match(line)
        if awaiting:
            if top:
                skipping, awaiting = _unit_of(top), False
            continue
        if skipping is not None:
            unit = _unit_of(top) if top else None
            if (unit is None or unit == skipping) and not _is_heading(line):
                continue
            skipping = None
        kept.append(line)
    return kept


def _valid_part(text: str, scope: str) -> str:
    """What remains of struck-down text: nothing, or the text without the sentence or words it names."""
    sentence = _STRUCK_SENTENCE.search(scope)
    if sentence and sentence.group(1).lower() in _ORDINALS:
        number = _ORDINALS[sentence.group(1).lower()]
        sentences = re.split(r"(?<=\.)\s+(?=[А-Я])", text)
        return " ".join(s for i, s in enumerate(sentences, 1) if i != number)
    words = _STRUCK_WORDS.search(scope)
    if words:
        return re.sub(r"\s*" + re.escape(words.group(1)) + r"\s*", " ", text, count=1).strip()
    return ""


def _drop_struck_down(lines: list[str]) -> list[str]:
    """The lines without struck-down text, frames, editor's notes and their markers."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _EDITOR_NOTE.match(line):
            i += 1
            continue
        if not _FRAME.match(line):
            out.append(_STAR.sub("", line))
            i += 1
            continue
        close = next((j for j in range(i + 1, len(lines)) if _FRAME.match(lines[j])), None)
        note_at = next((k for k in range(len(out) - 1, -1, -1) if out[k].strip()), None)
        struck = _STRUCK.search(out[note_at]) if note_at is not None else None
        if close is None or struck is None:  # a separator line, not a frame around struck-down text
            i += 1
            continue
        framed = " ".join(x.strip() for x in lines[i + 1 : close] if x.strip())
        valid = _valid_part(framed, struck.group("scope"))
        if valid:
            out.append(valid)
        elif _LETTER_NOTE_ONLY.match(out[note_at]):
            del out[note_at]
        i = close + 1
    return out


def parse(text: str) -> ParsedAct:
    raw = text.replace("\f", "\n").replace("­", "").replace(" ", " ").split("\n")
    lines = [
        _SPACED_HYPHEN.sub(r"\1-", _LOST_HYPHEN.sub(r"\1-", _PRINT_DATE.sub("", line))).strip()
        for line in raw
        if not any(p.match(line) for p in _FURNITURE)
    ]
    lines = _drop_struck_down(lines)
    # The header: everything before the first chapter, section or article.
    first = next(
        (i for i, line in enumerate(lines) if _is_heading(line) or _TOP_LINE.match(line)), len(lines)
    )
    header = [line for line in lines[:first] if line]
    body = lines[first:]
    body = _drop_redactions(body[: _end_of_act(body)])
    running = "\n".join(_blank_headings(body))

    act = ParsedAct(title=header[0] if header else "", header=header)
    matches = list(_TOP.finditer(running))
    for i, m in enumerate(matches):
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(running)
        unit = f"чл. {m.group('art')}" if m.group("art") else f"§ {m.group('par')}"
        if unit in act.units or unit in act.repealed:  # a later duplicate never replaces the current text
            continue
        _add_unit(act, unit, running[m.end() : stop])
    return act


def _add_unit(act: ParsedAct, unit: str, text: str) -> None:
    whole = clean(text)
    if not whole or re.fullmatch(r"\(?Отм\.?.*\)?", whole, flags=re.IGNORECASE):
        act.repealed.append(unit)
        return
    act.units[unit] = whole
    act.order.append(unit)
    # Paragraphs are split on the text with its notes removed, so "(1) (Изм. …) Текст" reads "(1) Текст".
    without_notes = _NOTE.sub("", text).strip()
    _, paragraphs = _split_numbered(without_notes, _PARAGRAPH)
    if not paragraphs:
        _add_points(act, unit, without_notes)
        return
    for number, paragraph in paragraphs:
        paragraph_unit = f"{unit}, ал. {number}"
        paragraph_text = clean(paragraph).lstrip(".;").strip()
        if not paragraph_text:
            act.repealed.append(paragraph_unit)
            continue
        act.units[paragraph_unit] = paragraph_text
        act.order.append(paragraph_unit)
        _add_points(act, paragraph_unit, paragraph)


def _add_points(act: ParsedAct, unit: str, text: str) -> None:
    _, points = _split_numbered(text, _POINT)
    for number, point in points:
        point_text = clean(point).lstrip(".;").strip()
        if point_text:
            act.units[f"{unit}, т. {number}"] = point_text
            act.order.append(f"{unit}, т. {number}")
        else:
            act.repealed.append(f"{unit}, т. {number}")

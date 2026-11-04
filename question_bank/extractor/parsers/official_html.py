"""Strict parser for one official ИААА variant file (see docs/source-investigation.md §1.2).

The parser never guesses: any structure it does not recognise raises `ParseError`, so a layout change
on the official site fails the build instead of producing silently incomplete data.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, Tag

from question_bank.processor.normalization.text import normalize_text

_H1 = re.compile(r"^(?P<category>[^.]+?)\.\s+(?P<description>.+)$", re.DOTALL)
_SECTION = re.compile(r"^Раздел\s+(?P<number>\d+)\s*[.:]", re.IGNORECASE)
_ASSET_URL = re.compile(r"url\(\s*['\"]?\./assets/(?P<name>[^)'\"]+?)['\"]?\s*\)")
_ASSET_SRC = re.compile(r"^\./assets/(?P<name>[^/]+)$")
_RAW_QUESTION = re.compile(r'<table\s+class="tg question"\s+id="q\d+"')
_RAW_SECTION = re.compile(r'class="sectionTitle"')
_FORBIDDEN_TAGS = ("img", "audio", "iframe", "object", "embed", "canvas", "svg")


class ParseError(ValueError):
    """The file does not match the known structure of the official array."""


@dataclass(frozen=True)
class ParsedAnswer:
    position: int  # 1-based, source order
    text: str | None
    image: str | None  # asset file name, e.g. "334684.png"
    correct: bool


@dataclass(frozen=True)
class ParsedQuestion:
    original_id: str
    points: int
    section_number: int
    position: int  # 1-based order of the question inside the file
    text: str
    answers: tuple[ParsedAnswer, ...]
    images: tuple[str, ...]  # question pictures (asset names), in source order
    videos: tuple[str, ...]  # question videos (asset names), in source order

    @property
    def assets(self) -> tuple[str, ...]:
        return self.images + self.videos + tuple(a.image for a in self.answers if a.image)


@dataclass(frozen=True)
class ParsedSection:
    number: int
    title: str  # full official title, "Раздел N. …"
    position: int


@dataclass(frozen=True)
class ParsedVariantFile:
    title: str
    category_label: str
    description: str
    sections: tuple[ParsedSection, ...]
    questions: tuple[ParsedQuestion, ...]
    warnings: tuple[str, ...] = field(default=())


def _asset_from_style(tag: Tag) -> str:
    match = _ASSET_URL.search(tag.get("style", ""))
    if not match:
        raise ParseError(f"picture without ./assets/ URL: {tag!s:.200}")
    return match["name"]


def _classes(tag: Tag) -> set[str]:
    return set(tag.get("class") or [])


def _answer_container(check: Tag) -> Tag:
    """Smallest ancestor holding exactly this answer marker plus its text or picture."""
    node = check.parent
    while node is not None:
        if len(node.select("i.check")) > 1:
            break
        if node.select_one("var.f-13") is not None or node.select_one("th.qpictureWrp div.qpicture"):
            return node
        node = node.parent
    raise ParseError("answer marker without answer text or picture")


def _parse_question(table: Tag, section_number: int, position: int) -> ParsedQuestion:
    table_id = table.get("id", "")
    row = table.find("tr")
    cells = row.find_all("td", recursive=False) if row else []
    if len(cells) != 3:
        raise ParseError(f"{table_id}: expected 3 cells (id, points, content), found {len(cells)}")
    original_id = cells[0].get_text(strip=True)
    if not original_id.isdigit() or table_id != f"q{original_id}":
        raise ParseError(f"question id {original_id!r} does not match table id {table_id!r}")
    points_tag = cells[1].find("var")
    points_text = points_tag.get_text(strip=True) if points_tag else ""
    if points_text not in {"1", "2", "3"}:
        raise ParseError(f"{table_id}: unexpected points {points_text!r}")
    content = cells[2]
    for forbidden in _FORBIDDEN_TAGS:
        if content.find(forbidden) is not None:
            raise ParseError(f"{table_id}: unsupported <{forbidden}> element")

    text_tag = content.select_one('th.p-b-14[colspan="2"]')
    text = normalize_text(text_tag.get_text(" ")) if text_tag else ""
    if not text:
        raise ParseError(f"{table_id}: missing question text")

    answers = []
    for index, check in enumerate(content.select("i.check"), start=1):
        container = _answer_container(check)
        var = container.select_one("var.f-13")
        picture = container.select_one("th.qpictureWrp div.qpicture")
        answer_text = normalize_text(var.get_text(" ")) if var else None
        answer_image = _asset_from_style(picture) if picture else None
        if not answer_text and not answer_image:
            raise ParseError(f"{table_id}: answer {index} has neither text nor picture")
        answers.append(ParsedAnswer(index, answer_text or None, answer_image, "correct" in _classes(check)))
    if not answers:
        raise ParseError(f"{table_id}: no answers")

    images = tuple(
        _asset_from_style(div)
        for div in content.select("div.qpicture")
        if div.parent is not None and div.parent.name == "td" and "w-30" in _classes(div.parent)
    )
    videos = []
    for source in content.select("video source"):
        match = _ASSET_SRC.match(source.get("src", ""))
        if not match:
            raise ParseError(f"{table_id}: unexpected video source {source.get('src')!r}")
        videos.append(match["name"])

    all_pictures = len(content.select("div.qpicture"))
    answer_pictures = sum(1 for a in answers if a.image)
    if all_pictures != len(images) + answer_pictures:
        raise ParseError(
            f"{table_id}: {all_pictures} pictures but only {len(images) + answer_pictures} assigned"
        )

    return ParsedQuestion(
        original_id=original_id,
        points=int(points_text),
        section_number=section_number,
        position=position,
        text=text,
        answers=tuple(answers),
        images=images,
        videos=tuple(videos),
    )


def parse_variant_file(html: str) -> ParsedVariantFile:
    soup = BeautifulSoup(html, "lxml")
    h1 = soup.select_one("h1.text-category")
    if h1 is None:
        raise ParseError("missing <h1 class='text-category'>")
    title = normalize_text(h1.get_text(" "))
    match = _H1.match(title)
    if not match:
        raise ParseError(f"unexpected title {title!r}")

    sections: list[ParsedSection] = []
    questions: list[ParsedQuestion] = []
    current: int | None = None
    for element in soup.select("p.sectionTitle, table.question"):
        if element.name == "p":
            section_title = normalize_text(element.get_text(" "))
            number = _SECTION.match(section_title)
            if not number:
                raise ParseError(f"unexpected section title {section_title!r}")
            current = int(number["number"])
            if any(s.number == current for s in sections):
                raise ParseError(f"section {current} appears twice")
            sections.append(ParsedSection(current, section_title, len(sections) + 1))
        else:
            if current is None:
                raise ParseError("question before the first section title")
            questions.append(_parse_question(element, current, len(questions) + 1))

    raw_questions = len(_RAW_QUESTION.findall(html))
    if raw_questions != len(questions):
        raise ParseError(
            f"parsed {len(questions)} questions but the file has {raw_questions} question blocks"
        )
    if len(_RAW_SECTION.findall(html)) != len(sections):
        raise ParseError("section count mismatch")
    ids = [q.original_id for q in questions]
    if len(ids) != len(set(ids)):
        raise ParseError("duplicate question id inside one file")

    warnings = []
    for q in questions:
        kinds = {("text" if a.text else "") + ("image" if a.image else "") for a in q.answers}
        if len(kinds) > 1:
            warnings.append(f"q{q.original_id}: answers mix text and pictures")
    return ParsedVariantFile(
        title=title,
        category_label=normalize_text(match["category"]),
        description=normalize_text(match["description"]),
        sections=tuple(sections),
        questions=tuple(questions),
        warnings=tuple(warnings),
    )

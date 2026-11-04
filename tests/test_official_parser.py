from __future__ import annotations

import pytest

from question_bank.extractor.parsers.official_html import ParseError, parse_variant_file


@pytest.fixture
def sample_html(fixtures_dir) -> str:
    """Real excerpt of the official B file (edition 2026-10-01): 2 sections, 6 questions, every format."""
    return (fixtures_dir / "official" / "variant-B-sample.html").read_text(encoding="utf-8")


def test_header_and_sections(sample_html):
    parsed = parse_variant_file(sample_html)
    assert parsed.category_label == "B"
    assert parsed.description == "без правоспособност или с правоспособност за категория АМ (След 12.12.24г.)"
    assert [(s.number, s.position) for s in parsed.sections] == [(1, 1), (2, 2)]
    assert parsed.sections[0].title == "Раздел 1. ОБЩИ СВЕДЕНИЯ ЗА АВТОМОБИЛА"
    assert parsed.warnings == ()


def test_text_question_with_single_correct_answer(sample_html):
    q = parse_variant_file(sample_html).questions[0]
    assert (q.original_id, q.points, q.section_number, q.position) == ("5300", 1, 1, 1)
    assert q.text == "Съединителят е предназначен:"
    assert [a.correct for a in q.answers] == [True, False, False, False]
    assert q.answers[0].text == "да прекъсва силовата връзка между двигателя и предавателната кутия"
    assert q.images == () and q.videos == ()


def test_multi_correct_question(sample_html):
    q = parse_variant_file(sample_html).questions[1]
    assert q.original_id == "5452"
    assert [a.correct for a in q.answers] == [False, True, True, False]


def test_question_picture_and_picture_answers(sample_html):
    questions = {q.original_id: q for q in parse_variant_file(sample_html).questions}
    assert questions["6164"].images == ("30115.png",)  # "qpictureWrp w-30 small" question picture
    assert questions["5244"].images == ("20243.png",)
    pictures = questions["5480"].answers
    assert [a.image for a in pictures] == ["334684.png", "29956.png", "334683.png", "29958.png"]
    assert all(a.text is None for a in pictures)
    assert [a.correct for a in pictures] == [True, False, False, False]
    assert questions["5480"].images == ()  # answer pictures are not question pictures


def test_video_question(sample_html):
    q = {q.original_id: q for q in parse_variant_file(sample_html).questions}["12004"]
    assert q.videos == ("5_video.mp4",)
    assert q.assets == ("5_video.mp4",)
    assert [a.correct for a in q.answers] == [False, False, True]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda h: h.replace('class="text-category"', 'class="other"'), "h1"),
        (lambda h: h.replace("<var>1</var>", "<var>5</var>", 1), "points"),
        (lambda h: h.replace("<b>Съединителят е предназначен:</b>", "<b></b>", 1), "question text"),
        (lambda h: h.replace('<var class="f-13">', '<img src="x.png"><var class="f-13">', 1), "img"),
        (lambda h: h.replace('id="q5300"', 'id="q9999"', 1), "does not match"),
        (lambda h: h.replace("Раздел 2.", "Глава 2.", 1), "section title"),
        (lambda h: h.replace("url(./assets/20243.png)", "url(/elsewhere/20243.png)", 1), "assets"),
    ],
)
def test_layout_changes_fail_loudly(sample_html, mutation, message):
    with pytest.raises(ParseError, match=message):
        parse_variant_file(mutation(sample_html))


def test_question_blocks_invisible_to_the_dom_are_detected(sample_html):
    # The raw-HTML count must agree with the DOM parse; a block the parser cannot see (here: inside a
    # comment) must fail the parse instead of being silently dropped.
    hidden = '<!-- <table class="tg question" id="q1"> --></body>'
    with pytest.raises(ParseError, match="question blocks"):
        parse_variant_file(sample_html.replace("</body>", hidden, 1))


def test_real_edition_counts_match_the_investigation(fixtures_dir):
    """Integration check on the full downloaded edition (skipped when `qb extract` has not been run)."""
    from question_bank.config import load_settings
    from question_bank.extractor.pipeline import load_extracted

    extracted = load_extracted(load_settings())
    if len(extracted) != 23:
        pytest.skip("full edition not extracted locally")
    rows = sum(len(e.parsed.questions) for e in extracted)
    unique = {q.original_id for e in extracted for q in e.parsed.questions}
    assert (rows, len(unique)) == (13_763, 2_476)

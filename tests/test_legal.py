"""The legal corpus: splitting acts into units and checking quotes against them."""

from __future__ import annotations

import zipfile

from question_bank.fsutil import read_json, write_json
from question_bank.legal.corpus import load, normalize, write_act
from question_bank.legal.extract import docx_text
from question_bank.legal.parse import parse

# The layout of the PDF exports: one article per line, earlier wordings after "Редакция към".
PDF_LAYOUT = """ЗАКОН ЗА ДВИЖЕНИЕТО ПО ПЪТИЩАТА
В сила от 01.09.1999 г.
Обн. ДВ. бр.20 от 5 Март 1999г., изм. ДВ. бр.43 от 26 Април 2002г., изм. и доп. ДВ. бр.64 от 5 Август 2025г.
Глава първа. ОБЩИ ПОЛОЖЕНИЯ
Чл. 1. (1) Този закон урежда правилата за движение по пътищата.
(2) (Изм. - ДВ, бр. 43 от 2002 г., в сила от 26.04.2002 г.) Всеки има право да се движи по пътищата.
Страница 1 от 3
Чл. 3. (1) (Доп. - ДВ, бр. 85 от 2004 г.) Лицата, които стопанисват пътищата:
1. ги поддържат изправни;
2. организират движението по тях;
3. (отм. - ДВ, бр. 64 от 2025 г.).
4. почистват пътното платно.
(2) (Отм. - ДВ, бр. 51 от 2007 г.)
Редакция към ДВ, бр. 23 от 19 Март 2021 г.
Чл. 3. (1) Лицата, които стопанисват пътищата, ги поддържат по стария начин.
(2) Стар текст.
Раздел II. Сигнали за регулиране на движението от упълномощените длъжностни лица. Пътни
сигнали
Чл. 50. (1) На кръстовище водачите са длъжни да пропуснат пътните превозни средства,
които се движат по пътя с предимство.
Източник: Правно-информационни системи "Сиела"
Допълнителни разпоредби
§ 6. По смисъла на този закон: 1. "Път" е всяка земна площ. 2. "Пътно превозно средство" е съоръжение.
Преходни и заключителни разпоредби
§ 7. Законът влиза в сила от 1 септември 1999 г.
Допълнителни разпоредби КЪМ ЗАКОНА ЗА ИЗМЕНЕНИЕ И ДОПЪЛНЕНИЕ НА ЗАКОНА
§ 1. Текст на изменящ закон.
"""

# The layout of the DOCX of the Ministry of Transport: indented lines, headings without a period, repeated
# final provisions of the amending acts, notes "(В сила от …)".
DOCX_LAYOUT = "\n".join(
    [
        "ЗАКОН за движението по пътищата",
        "Обн., ДВ, бр. 20 от 5.03.1999 г., изм., бр. 16 от 10.02.2026 г., бр. 55 от 16.06.2026 г.",
        "Глава втора",
        "ПРАВИЛА ЗА ДВИЖЕНИЕ ПО ПЪТИЩАТА",
        "Раздел I",
        "Общи правила",
        " Чл. 5. (1) Всеки участник в движението по пътищата: 1. с поведението си не трябва да създава"
        " опасности; 2. трябва да опазва околната среда.",
        " (2) Водачът е длъжен: 1. да бъде внимателен; 2.. 3. да не извършва маневри.",
        " Чл. 145. (1). (2) Приобретателят е длъжен да регистрира превозното средство.",
        " Чл. 157. (В сила от 1.01.2000 г.) (1) (Изм. - ДВ, бр. 43 от 2002 г.) Новият водач получава две"
        " трети от точките.",
        "ПРЕХОДНИ И ЗАКЛЮЧИТЕЛНИ РАЗПОРЕДБИ",
        " § 13. Законът влиза в сила от 1.09.1999 г.",
        "ПРЕХОДНИ И ЗАКЛЮЧИТЕЛНИ РАЗПОРЕДБИ",
        " § 1. Текст на изменящ закон.",
    ]
)

# Several articles on one line (some exports run them together).
INLINE = "\n".join(
    [
        "НАРЕДБА № РД-02-21-1 ОТ 23 НОЕМВРИ 2023 Г.",
        "Обн. ДВ. бр.101 от 5 Декември 2023г.",
        "Чл. 7. (1) Всички надписи са на български език. (2) Повтарянето е с латински букви."
        ' Чл. 8. Пътен знак Б2 "Спри!" има формата на осмоъгълник.',
        "Приложение № 1 към чл. 2",
        "А1 Опасен завой надясно",
    ]
)


def test_pdf_layout_keeps_only_the_current_text_of_the_act():
    act = parse(PDF_LAYOUT)
    assert act.title == "ЗАКОН ЗА ДВИЖЕНИЕТО ПО ПЪТИЩАТА"
    assert act.last_amendment == "ДВ, бр. 64 от 05.08.2025 г."
    assert act.units["чл. 1, ал. 2"] == "Всеки има право да се движи по пътищата."
    # The earlier wording after "Редакция към" is dropped; notes are removed; repealed parts are listed.
    assert act.units["чл. 3, ал. 1"].startswith(
        "Лицата, които стопанисват пътищата: 1. ги поддържат изправни;"
    )
    assert act.units["чл. 3, ал. 1, т. 2"] == "организират движението по тях;"
    assert act.units["чл. 3, ал. 1, т. 4"] == "почистват пътното платно."
    assert "чл. 3, ал. 1, т. 3" in act.repealed and "чл. 3, ал. 2" in act.repealed
    assert "стария начин" not in act.units["чл. 3"]
    # A heading that wraps onto the next line and the page furniture are not part of any article.
    assert act.units["чл. 50, ал. 1"] == (
        "На кръстовище водачите са длъжни да пропуснат пътните превозни средства, които се движат по пътя"
        " с предимство."
    )
    assert act.units["§ 6, т. 2"] == '"Пътно превозно средство" е съоръжение.'
    assert "§ 7" in act.units
    # The provisions of amending acts end the act.
    assert "§ 1" not in act.units
    assert "Текст на изменящ закон" not in " ".join(act.units.values())


def test_docx_layout_with_bare_headings_and_repealed_points():
    act = parse(DOCX_LAYOUT)
    assert act.last_amendment == "ДВ, бр. 55 от 16.06.2026 г."
    assert act.units["чл. 5, ал. 1, т. 2"] == "трябва да опазва околната среда."
    assert act.units["чл. 5, ал. 2, т. 3"] == "да не извършва маневри."
    assert "чл. 5, ал. 2, т. 2" in act.repealed
    assert act.units["чл. 145, ал. 2"] == "Приобретателят е длъжен да регистрира превозното средство."
    assert act.units["чл. 157, ал. 1"] == "Новият водач получава две трети от точките."
    assert "Общи правила" not in act.units["чл. 5"]
    assert "§ 13" in act.units and "§ 1" not in act.units


def test_articles_in_the_middle_of_a_line_and_annexes():
    act = parse(INLINE)
    assert act.units["чл. 7, ал. 2"] == "Повтарянето е с латински букви."
    assert act.units["чл. 8"] == 'Пътен знак Б2 "Спри!" има формата на осмоъгълник.'
    assert not any("Опасен завой" in text for text in act.units.values())


def test_docx_paragraphs_become_lines(tmp_path):
    document = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
        "<w:p><w:r><w:t>Чл. 1. (1) Текст</w:t></w:r><w:r><w:tab/><w:t>още.</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>(2) Втора алинея.</w:t></w:r></w:p></w:body></w:document>"
    )
    path = tmp_path / "act.docx"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)
    assert docx_text(path) == "Чл. 1. (1) Текст още.\n(2) Втора алинея."


def test_quotes_are_checked_word_for_word_in_the_cited_unit(tmp_path):
    write_json(
        tmp_path / "sources.json",
        {
            "acts": [
                {"id": "zdvp", "short": "ЗДвП", "title": "Закон за движението по пътищата", "source_url": "u"}
            ]
        },
    )
    source = tmp_path / "act.txt"
    source.write_text(PDF_LAYOUT, encoding="utf-8")
    entry = write_act(parse(PDF_LAYOUT), "zdvp", source, legal_dir=tmp_path)
    assert entry["consolidated_to"] == "ДВ, бр. 64 от 05.08.2025 г." and entry["units"] > 0
    assert read_json(tmp_path / "zdvp.json")["units"]["чл. 1, ал. 1"]

    corpus = load(tmp_path)
    ok = corpus.check(
        "zdvp", "чл. 50, ал. 1", "длъжни да пропуснат пътните превозни средства, които се движат"
    )
    assert ok.ok and ok.resolved == "чл. 50, ал. 1"
    # Typographic quotes and spacing do not matter; a point that is not split resolves to its paragraph.
    assert corpus.check("zdvp", "§ 6, т. 1", "„Път“ е всяка  земна площ").ok
    assert corpus.check("zdvp", "чл. 50, ал. 1, т. 4", "пътя с предимство").resolved == "чл. 50, ал. 1"
    # Made-up words, wrong units and unknown acts fail.
    assert not corpus.check("zdvp", "чл. 50, ал. 1", "длъжни да спрат винаги").ok
    assert not corpus.check("zdvp", "чл. 1, ал. 1", "длъжни да пропуснат").ok
    assert not corpus.check("zdvp", "чл. 999", "текст").ok
    assert not corpus.check("zdvp", "член 50", "текст").ok
    assert not corpus.check("other", "чл. 1", "текст").ok
    assert [u for u, _ in corpus.search("zdvp", ["предимство"])] == ["чл. 50", "чл. 50, ал. 1"]


def test_normalize_unifies_quotes_dashes_and_spaces():
    assert normalize("„Път“ – това­ е  «път»") == '"Път" - това е "път"'

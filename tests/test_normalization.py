from __future__ import annotations

import pytest

from question_bank.processor.normalization import ids
from question_bank.processor.normalization.text import match_key, normalize_text, split_effective_note


def test_normalize_text_only_touches_whitespace_and_unicode_form():
    assert normalize_text("  Линията, с която\n се очертава “ВUS”-лентата  ") == (
        "Линията, с която се очертава “ВUS”-лентата"
    )
    # NFC: "й" written as и + combining breve becomes the single code point
    assert normalize_text("й") == "й"


def test_split_effective_note():
    assert split_effective_note("без правоспособност (След 12.12.24г.)") == (
        "без правоспособност",
        "След 12.12.24г.",
    )
    assert split_effective_note("със стаж 2г.(След 07.02.26г.)") == ("със стаж 2г.", "След 07.02.26г.")
    assert split_effective_note("без бележка") == ("без бележка", None)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("B", "B"),
        ("В", "B"),
        ("AM", "AM"),
        ("C+E", "CE"),
        ("C1+E", "C1E"),
        ("D (103)", "D103"),
        ("Ттм", "TTM"),
    ],
)
def test_category_id(label, expected):
    assert ids.category_id(label) == expected


def test_transliteration_follows_streamlined_system():
    assert ids.transliterate_bg("Щастие") == "shtastie"
    assert ids.transliterate_bg("категория") == "kategoria"  # word-final "ия" → "ia"
    assert ids.transliterate_bg("Юлия Ямболска") == "yulia yambolska"


def test_variant_id_is_stable_and_ignores_effective_note():
    a = ids.variant_id("B", "без правоспособност или с правоспособност за категория АМ (След 12.12.24г.)")
    b = ids.variant_id("B", "без правоспособност или с правоспособност за категория АМ (След 01.01.27г.)")
    assert a == b == "B.bez-pravosposobnost-ili-s-pravosposobnost-za-kategoria-am"


def test_long_slugs_are_truncated_with_hash_suffix():
    long = "с правоспособност за кат. D и допълнително обучение за управление на тролейбус " * 2
    slug = ids.slugify(long)
    assert len(slug) <= ids.TRUNCATED_SLUG + 7
    assert slug == ids.slugify(long)  # deterministic


def test_topic_and_entity_ids():
    assert (
        ids.topic_id("Раздел 4. ПРАВИЛА ЗА ДВИЖЕНИЕТО ПО ПЪТИЩАТА") == "pravila-za-dvizhenieto-po-patishtata"
    )
    assert ids.section_id("B.x", 4) == "B.x#s4"
    assert ids.question_id("5300") == "iaaa-5300"
    assert ids.answer_id("iaaa-5300", 1) == "iaaa-5300-a1"
    assert ids.media_id("089e870fa3ce" + "0" * 52) == "m-089e870fa3ce0000"
    with pytest.raises(ValueError):
        ids.question_id("53a0")


def test_match_key_pairs_file_names_with_avtoizpit_descriptions():
    from_file = "загуба_на_правоспособност_по_реда_на_чл_157_ал_4_ЗДвП"
    from_avtoizpit = "загуба на правоспособност по реда на чл. 157, ал. 4 ЗДвП. (След 12.12.24г.)"
    assert match_key(from_file) == match_key(from_avtoizpit)
    assert match_key("с_правоспособност_за_категория_В_B78") == match_key(
        "с правоспособност за категория В/B(78)"
    )
    assert match_key("с правоспособност за категория А, А1 или А2") != match_key(
        "с правоспособност за категория А, А1 или А2 - държавна поръчка"
    )

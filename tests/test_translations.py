"""Translation work packages and the automatic translation checks (question_bank.translations)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from question_bank.translations import lint
from question_bank.translations.prepare import prepare

LANG = lint.LANGUAGES


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def source_part(questions: list[dict]) -> dict:
    return {"part": 1, "parts": 1, "picture_dir": "/x", "topics": {"T01": "ТЕМА"}, "questions": questions}


Q1 = {
    "id": "q-1",
    "topic": "T01",
    "text": "Водач на МПС от категория В при движение в населено място не трябва да превишава:",
    "answers": [
        {"id": "q-1-a1", "text": "50 km/h", "correct": True},
        {"id": "q-1-a2", "text": "60 km/h", "correct": False},
        {"id": "q-1-a3", "picture": "m-1", "correct": False},
    ],
}
Q2 = {
    "id": "q-2",
    "topic": "T01",
    "text": "Разрешено ли е престоят на 3,5 m от кръстовището?",
    "answers": [
        {"id": "q-2-a1", "text": "да", "correct": False},
        {"id": "q-2-a2", "text": "не", "correct": True},
    ],
}


@pytest.fixture
def work(tmp_path: Path) -> Path:
    write(tmp_path / "source" / "questions" / "part-01.json", source_part([Q1, Q2]))
    return tmp_path


def run_part(work: Path, lang: str, translated: dict) -> lint.Result:
    write(work / "out" / lang / "questions" / "part-01.json", translated)
    result = lint.lint_part(work, LANG[lang], 1)
    return lint.apply_exceptions(result, lint.load_exceptions(work / "out" / lang))


def checks(result: lint.Result, level: str = lint.ERROR) -> set[tuple[str, str]]:
    return {(f.item, f.check) for f in result.findings if f.level == level}


GOOD_EN = {
    "q-1": {
        "text": "When driving in a built-up area, the driver of a category B motor vehicle must not exceed:",
        "answers": {"q-1-a1": "50 km/h", "q-1-a2": "60 km/h"},
    },
    "q-2": {
        "text": "Is standing permitted 3.5 m from the intersection?",
        "answers": {"q-2-a1": "yes", "q-2-a2": "no"},
    },
}


def test_a_correct_translation_has_no_errors(work):
    result = run_part(work, "en", GOOD_EN)
    assert checks(result) == set()
    assert result.checked_strings == 6


def test_missing_extra_and_picture_answers_are_errors(work):
    bad = json.loads(json.dumps(GOOD_EN))
    del bad["q-2"]
    bad["q-1"]["answers"]["q-1-a3"] = "a picture"
    del bad["q-1"]["answers"]["q-1-a2"]
    found = checks(run_part(work, "en", bad))
    assert ("q-2", "missing") in found
    assert ("q-1-a2", "missing") in found
    assert ("q-1-a3", "extra") in found


def test_numbers_must_survive_with_local_separators(work):
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-2"]["text"] = "Is standing permitted 5 m from the intersection?"
    assert ("q-2", "numbers") in checks(run_part(work, "en", bad))
    de = {
        "q-1": {
            "text": "Der Führer eines Kraftfahrzeugs der Klasse B darf innerorts nicht schneller fahren als:",
            "answers": {"q-1-a1": "50 km/h", "q-1-a2": "60 km/h"},
        },
        "q-2": {
            "text": "Ist das Halten 3,5 m vor der Kreuzung erlaubt?",
            "answers": {"q-2-a1": "ja", "q-2-a2": "nein"},
        },
    }
    assert ("q-2", "numbers") not in checks(run_part(work, "de", de))


def test_thousands_separators_are_equivalent():
    assert lint.numbers("над 12 000 kg") == lint.numbers("over 12,000 kg") == lint.numbers("über 12.000 kg")
    assert lint.numbers("3,5 т") == lint.numbers("3.5 t")
    assert lint.numbers("22,00 ч.") == lint.numbers("22:00")


def test_colon_and_question_marks_are_kept(work):
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-1"]["text"] = bad["q-1"]["text"].rstrip(":")
    bad["q-2"]["text"] = bad["q-2"]["text"].rstrip("?")
    found = checks(run_part(work, "en", bad))
    assert {("q-1", "end_punct"), ("q-2", "end_punct")} <= found


def test_greek_question_mark_and_spanish_opening_mark(work):
    el = {
        "q-1": {
            "text": "Ο οδηγός μηχανοκίνητου οχήματος κατηγορίας B εντός κατοικημένης περιοχής "
            "δεν πρέπει να υπερβαίνει:",
            "answers": {"q-1-a1": "50 km/h", "q-1-a2": "60 km/h"},
        },
        "q-2": {
            "text": "Επιτρέπεται η στάση σε απόσταση 3,5 m από τη διασταύρωση;",
            "answers": {"q-2-a1": "ναι", "q-2-a2": "όχι"},
        },
    }
    assert checks(run_part(work, "el", el)) == set()
    el["q-2"]["text"] = el["q-2"]["text"][:-1] + "?"
    assert ("q-2", "end_punct") in checks(run_part(work, "el", el))
    es = {
        "q-1": {
            "text": "El conductor de un vehículo de motor de la categoría B en poblado no debe superar:",
            "answers": {"q-1-a1": "50 km/h", "q-1-a2": "60 km/h"},
        },
        "q-2": {
            "text": "Está permitido detenerse a 3,5 m de la intersección?",
            "answers": {"q-2-a1": "sí", "q-2-a2": "no"},
        },
    }
    assert ("q-2", "spanish_question") in checks(run_part(work, "es", es))


def test_category_letters_must_be_latin(work):
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-1"]["text"] = bad["q-1"]["text"].replace("category B", "category V")
    assert ("q-1", "category_code") in checks(run_part(work, "en", bad))
    bad["q-1"]["text"] = GOOD_EN["q-1"]["text"].replace("category B", "category В")  # Cyrillic Ve
    found = checks(run_part(work, "en", bad))
    assert ("q-1", "cyrillic") in found and ("q-1", "category_code") in found


def test_category_codes_are_folded_to_latin():
    assert lint.category_codes("с правоспособност за категория ВЕ и клас А") == ["BE", "A"]
    assert lint.category_codes("категория С1Е") == ["C1E"]
    assert lint.category_codes("категория Ттм") == ["Ttm"]
    assert lint.category_codes("категория МПС") == []
    assert lint.code_pattern("C1E").search("category C1+E")


def test_untranslated_mixed_script_and_identical_answers(work):
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-2"]["answers"] = {"q-2-a1": "no", "q-2-a2": "no"}
    bad["q-1"]["text"] = (
        "Тhe driver of a category B motor vehicle in a built-up area must not exceed:"  # Cyrillic Т
    )
    found = checks(run_part(work, "en", bad))
    assert ("q-2-a2", "same_answers") in found
    assert ("q-1", "mixed_script") in found
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-2"]["answers"]["q-2-a1"] = "да"
    assert ("q-2-a1", "untranslated") in checks(run_part(work, "en", bad))


def test_russian_and_romanian_spelling(work):
    ru = {
        "q-1": {
            "text": "Водитель механического транспортного средства категории B в населённом пункте "
            "не должен превышать:",
            "answers": {"q-1-a1": "50 км/ч", "q-1-a2": "60 км/ч"},
        },
        "q-2": {
            "text": "Разрешена ли стоянка в 3,5 м от перекрёстка, у подъезда?",
            "answers": {"q-2-a1": "да", "q-2-a2": "нет"},
        },
    }
    result = run_part(work, "ru", ru)
    assert checks(result) == set()
    ru["q-2"]["text"] = "Разрешен ли престой на 3,5 м от кръстовището?"
    assert ("q-2", "bulgarian") in checks(run_part(work, "ru", ru))
    ru["q-1"]["text"] = ru["q-1"]["text"].replace("категории B", "категории В")
    assert ("q-1", "category_code") in checks(run_part(work, "ru", ru))
    ro = {
        "q-1": {
            "text": "Conducătorul unui autovehicul din categoria B nu trebuie să depăşească în localitate:",
            "answers": {"q-1-a1": "50 km/h", "q-1-a2": "60 km/h"},
        },
        "q-2": {
            "text": "Este permisă staționarea la 3,5 m de intersecție?",
            "answers": {"q-2-a1": "da", "q-2-a2": "nu"},
        },
    }
    assert ("q-1", "romanian_comma") in checks(run_part(work, "ro", ro))


def test_justified_exceptions_are_accepted(work):
    bad = json.loads(json.dumps(GOOD_EN))
    bad["q-2"]["text"] = "Is standing permitted three and a half metres from the intersection?"
    write(work / "out" / "en" / "lint-exceptions.json", [{"id": "q-2", "check": "numbers", "reason": "test"}])
    result = run_part(work, "en", bad)
    assert ("q-2", "numbers") not in checks(result)
    assert [(f.item, f.check) for f in result.accepted] == [("q-2", "numbers")]
    write(work / "out" / "en" / "lint-exceptions.json", [{"id": "q-2", "check": "numbers", "reason": " "}])
    assert ("q-2", "numbers") in checks(run_part(work, "en", bad))  # an exception needs a reason


def test_consistency_reports_different_translations_of_the_same_text(tmp_path):
    q3 = dict(
        Q2,
        id="q-3",
        answers=[
            {"id": "q-3-a1", "text": "да", "correct": True},
            {"id": "q-3-a2", "text": "не", "correct": False},
        ],
    )
    write(tmp_path / "source" / "questions" / "part-01.json", source_part([Q2, q3]))
    write(
        tmp_path / "out" / "en" / "questions" / "part-01.json",
        {
            "q-2": {
                "text": "Is standing permitted 3.5 m from the intersection?",
                "answers": {"q-2-a1": "yes", "q-2-a2": "no"},
            },
            "q-3": {
                "text": "May you stand 3.5 m from the junction?",
                "answers": {"q-3-a1": "yes", "q-3-a2": "no"},
            },
        },
    )
    found = checks(lint.consistency(tmp_path, LANG["en"]), lint.WARNING)
    assert ("q-2", "consistency") in found


def test_ui_strings_placeholders_and_plurals(tmp_path):
    write(
        tmp_path / "source" / "ui-strings.bg.json",
        {
            "strings": {
                "a/title": {"text": "Въпрос %1$d от %2$d"},
                "a/answers": {"plurals": {"one": "%1$d отговор", "other": "%1$d отговора"}},
            }
        },
    )
    write(
        tmp_path / "out" / "ru" / "ui-strings.json",
        {
            "a/title": "Вопрос %1$d из %2$d",
            "a/answers": {
                "one": "%1$d ответ",
                "few": "%1$d ответа",
                "many": "%1$d ответов",
                "other": "%1$d ответа",
            },
        },
    )
    assert checks(lint.lint_ui(tmp_path, LANG["ru"])) == set()
    write(
        tmp_path / "out" / "ru" / "ui-strings.json",
        {
            "a/title": "Вопрос %1$d",
            "a/answers": {"one": "%1$d ответ", "other": "%1$d ответа"},
        },
    )
    found = checks(lint.lint_ui(tmp_path, LANG["ru"]))
    assert ("a/title", "placeholders") in found and ("a/answers", "plurals") in found


def test_labels_keep_official_category_codes(tmp_path):
    write(
        tmp_path / "source" / "labels.bg.json",
        {
            "categories": {"B": "B", "TTM": "Ттм"},
            "variants": {"B.x": {"description": "без правоспособност", "effective_note": "След 12.12.24г."}},
            "topics": {"t": "ПРАВИЛА ЗА ДВИЖЕНИЕТО ПО ПЪТИЩАТА"},
        },
    )
    write(
        tmp_path / "out" / "en" / "labels.json",
        {
            "categories": {"B": "B", "TTM": "Ttm"},
            "variants": {
                "B.x": {"description": "without a driving licence", "effective_note": "From 12.12.24."}
            },
            "topics": {"t": "Rules of the road"},
        },
    )
    assert checks(lint.lint_labels(tmp_path, LANG["en"])) == set()
    write(
        tmp_path / "out" / "en" / "labels.json",
        {
            "categories": {"B": "Cars", "TTM": "Ттм"},
            "variants": {
                "B.x": {"description": "without a driving licence", "effective_note": "From 12 December 2024"}
            },
            "topics": {"t": "RULES OF THE ROAD"},
        },
    )
    result = lint.lint_labels(tmp_path, LANG["en"])
    assert {
        ("categories:B", "category_code"),
        ("categories:TTM", "cyrillic"),
        ("variants:B.x.effective_note", "numbers"),
    } <= checks(result)
    assert ("topics:t", "all_caps") in checks(result, lint.WARNING)


def test_prepare_writes_parts_labels_and_index(tmp_path):
    exports = tmp_path / "exports"
    write(
        exports / "categories.json",
        {
            "topics": [{"id": "rules", "name": "ПРАВИЛА"}, {"id": "car", "name": "АВТОМОБИЛ"}],
            "categories": [
                {
                    "id": "B",
                    "name": "B",
                    "position": 1,
                    "variants": [
                        {
                            "id": "B.v",
                            "description": "без правоспособност",
                            "effective_note": None,
                            "position": 1,
                            "sections": [
                                {"id": "B.v#s1", "number": 1, "topic_id": "car"},
                                {"id": "B.v#s4", "number": 4, "topic_id": "rules"},
                            ],
                        }
                    ],
                }
            ],
        },
    )

    def question(qid: str, text: str, section: str, answers: list[dict], media=()) -> dict:
        return {
            "id": qid,
            "original_id": qid.split("-")[1],
            "text": text,
            "correct_count": 1,
            "media": list(media),
            "answers": answers,
            "assignments": [{"variant_id": "B.v", "section_id": section}],
        }

    write(
        exports / "questions.json",
        {
            "questions": [
                question(
                    "iaaa-3",
                    "Б?",
                    "B.v#s4",
                    [{"id": "iaaa-3-a1", "position": 1, "text": "да", "media_id": None, "is_correct": True}],
                ),
                question(
                    "iaaa-2",
                    "А?",
                    "B.v#s1",
                    [
                        {
                            "id": "iaaa-2-a1",
                            "position": 1,
                            "text": None,
                            "media_id": "m-1",
                            "is_correct": True,
                        },
                        {
                            "id": "iaaa-2-a2",
                            "position": 2,
                            "text": "не",
                            "media_id": None,
                            "is_correct": False,
                        },
                    ],
                    media=[{"media_id": "m-9", "role": "image", "position": 1}],
                ),
                question(
                    "iaaa-1",
                    "Б?",
                    "B.v#s4",
                    [{"id": "iaaa-1-a1", "position": 1, "text": "да", "media_id": None, "is_correct": True}],
                ),
            ]
        },
    )
    index = prepare(exports, tmp_path / "media", tmp_path / "work", parts=2)
    assert index["questions"] == 3 and index["text_answers"] == 3
    part1 = json.loads(
        (tmp_path / "work" / "source" / "questions" / "part-01.json").read_text(encoding="utf-8")
    )
    part2 = json.loads(
        (tmp_path / "work" / "source" / "questions" / "part-02.json").read_text(encoding="utf-8")
    )
    ids = [q["id"] for q in part1["questions"] + part2["questions"]]
    assert ids == ["iaaa-2", "iaaa-1", "iaaa-3"]  # section 1 topic first; same text together, by original id
    first = part1["questions"][0]
    assert first["pictures"] == ["m-9"]
    assert first["answers"][0] == {"id": "iaaa-2-a1", "picture": "m-1", "correct": True}
    assert part1["questions"][1]["same_text"] == ["iaaa-3"]
    labels = json.loads((tmp_path / "work" / "source" / "labels.bg.json").read_text(encoding="utf-8"))
    assert labels["variants"] == {"B.v": {"description": "без правоспособност", "effective_note": None}}
    assert list(labels["topics"]) == ["car", "rules"]

"""Explanations: lint against the bank and the legal corpus, work packages, merge and export."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from question_bank.explanations import curated
from question_bank.explanations.bank import load_bank
from question_bank.explanations.export import build_explanations, explanation_sets
from question_bank.explanations.lint import check_all
from question_bank.explanations.prepare import prepare
from question_bank.fsutil import read_json, write_json
from question_bank.legal.corpus import load, write_act
from question_bank.legal.parse import parse

ACT = "\n".join(
    [
        "ЗАКОН ЗА ДВИЖЕНИЕТО ПО ПЪТИЩАТА",
        "Обн. ДВ. бр.20 от 5 Март 1999г., изм. и доп. ДВ. бр.64 от 5 Август 2025г.",
        "Чл. 50. (1) На кръстовище, на което единият от пътищата е сигнализиран като път с предимство,"
        " водачите на пътни превозни средства от другите пътища са длъжни да пропуснат пътните превозни"
        " средства, които се движат по пътя с предимство.",
    ]
)
QUOTE = "водачите на пътни превозни средства от другите пътища са длъжни да пропуснат"
GOOD_TEXT = (
    "Пътят с предимство е обозначен със знак, затова водачите, които идват от другите пътища, трябва да"
    " пропуснат движещите се по него. Верният отговор е „пропускам“."
)


def _question(qid: str, number: str, content_hash: str, category: str, section: str) -> dict:
    return {
        "id": qid,
        "original_id": number,
        "text": f"Въпрос {number}",
        "answer_format": "text",
        "correct_count": 1,
        "content_hash": content_hash,
        "media": [{"media_id": "m-1", "role": "image", "position": 1}],
        "answers": [
            {"id": f"{qid}-a1", "position": 1, "text": "пропускам", "media_id": None, "is_correct": True},
            {"id": f"{qid}-a2", "position": 2, "text": "минавам", "media_id": None, "is_correct": False},
        ],
        "assignments": [
            {
                "variant_id": f"{category}.x",
                "category_id": category,
                "section_id": section,
                "points": 1,
                "position": 1,
            }
        ],
    }


@pytest.fixture
def setup(tmp_path):
    exports = tmp_path / "exports"
    exports.mkdir()
    write_json(
        exports / "questions.json",
        {
            "media": [{"id": "m-1", "kind": "image", "relative_path": "images/m-1.png"}],
            "questions": [
                _question("iaaa-1", "1", "h1", "B", "B.x#s1"),
                _question("iaaa-2", "2", "h2", "B", "B.x#s2"),
                _question("iaaa-3", "3", "h3", "C", "C.x#s1"),
            ],
        },
    )
    write_json(
        exports / "categories.json",
        {
            "topics": [{"id": "t1", "name": "ПРАВИЛА"}, {"id": "t2", "name": "ЗНАЦИ"}],
            "categories": [
                {
                    "id": "B",
                    "variants": [
                        {
                            "sections": [
                                {"id": "B.x#s2", "topic_id": "t2", "position": 1},
                                {"id": "B.x#s1", "topic_id": "t1", "position": 2},
                            ]
                        }
                    ],
                },
                {"id": "C", "variants": [{"sections": [{"id": "C.x#s1", "topic_id": "t1", "position": 1}]}]},
            ],
        },
    )
    legal = tmp_path / "legal"
    legal.mkdir()
    write_json(
        legal / "sources.json",
        {
            "acts": [
                {"id": "zdvp", "short": "ЗДвП", "title": "Закон за движението по пътищата", "source_url": "u"}
            ]
        },
    )
    source = legal / "act.txt"
    source.write_text(ACT, encoding="utf-8")
    write_act(parse(ACT), "zdvp", source, legal_dir=legal)
    bank, _, _ = load_bank(exports)
    return SimpleNamespace(exports=exports, legal=legal, corpus=load(legal), bank=bank, tmp=tmp_path)


def law(text: str = GOOD_TEXT, unit: str = "чл. 50, ал. 1", quote: str = QUOTE) -> dict:
    return {"kind": "law", "text": text, "references": [{"act": "zdvp", "unit": unit, "quote": quote}]}


def levels(findings) -> list[tuple[str, str]]:
    return [(f.level, f.question_id) for f in findings]


def test_a_law_explanation_needs_a_verbatim_quote_in_the_cited_unit(setup):
    assert check_all({"iaaa-1": law()}, setup.bank, setup.corpus) == []
    wrong_quote = check_all({"iaaa-1": law(quote="водачите винаги спират")}, setup.bank, setup.corpus)
    assert levels(wrong_quote) == [("error", "iaaa-1")]
    wrong_unit = check_all({"iaaa-1": law(unit="чл. 51")}, setup.bank, setup.corpus)
    assert "does not exist" in wrong_unit[0].message
    no_refs = check_all(
        {"iaaa-1": {"kind": "law", "text": GOOD_TEXT, "references": []}}, setup.bank, setup.corpus
    )
    assert levels(no_refs) == [("error", "iaaa-1")]


def test_general_explanations_short_texts_letters_and_conflicts(setup):
    general = {"kind": "general", "text": GOOD_TEXT, "references": []}
    assert check_all({"iaaa-1": general}, setup.bank, setup.corpus) == []
    with_refs = dict(law(), kind="general")
    assert levels(check_all({"iaaa-1": with_refs}, setup.bank, setup.corpus)) == [("error", "iaaa-1")]
    short = check_all({"iaaa-1": dict(general, text="Кратко.")}, setup.bank, setup.corpus)
    assert "characters" in short[0].message
    letter = check_all(
        {"iaaa-1": dict(general, text=GOOD_TEXT + " Затова отговор „а“ е верен.")}, setup.bank, setup.corpus
    )
    assert levels(letter) == [("warning", "iaaa-1")]
    # "отговора" is a word, not a letter reference.
    word = dict(general, text=GOOD_TEXT + " И трите отговора за свързаните превозни средства са верни.")
    assert check_all({"iaaa-1": word}, setup.bank, setup.corpus) == []
    conflict = check_all(
        {"iaaa-1": {"conflict": "чл. 50, ал. 1 казва друго от официалния отговор."}}, setup.bank, setup.corpus
    )
    assert levels(conflict) == [("warning", "iaaa-1")]
    missing = check_all({}, setup.bank, setup.corpus, expected=["iaaa-2"])
    assert levels(missing) == [("error", "iaaa-2")]
    unknown = check_all({"iaaa-9": general}, setup.bank, setup.corpus)
    assert levels(unknown) == [("error", "iaaa-9")]


def test_work_packages_follow_the_category_topics_and_skip_explained_questions(setup):
    work = setup.tmp / "work"
    curated_dir = setup.tmp / "curated"
    index = prepare(setup.exports, setup.tmp / "media", work, "B", part_size=1, curated_dir=curated_dir)
    assert index["questions"] == 2 and [p["topics"] for p in index["parts"]] == [["ЗНАЦИ"], ["ПРАВИЛА"]]
    part = read_json(work / "source" / "part-01.json")
    question = part["questions"][0]
    assert question["id"] == "iaaa-2" and question["content_hash"] == "h2"
    assert [a["correct"] for a in question["answers"]] == [True, False]
    assert question["answers"][0]["letter"] == "а" and question["pictures"][0].endswith("m-1.png")

    write_json(work / "out" / "part-01.json", {"explanations": {"iaaa-2": law()}})
    write_json(
        work / "out" / "part-02.json",
        {"explanations": {"iaaa-1": {"conflict": "чл. 50 казва друго, виж ал. 1."}}},
    )
    stats = curated.merge(work, setup.exports, setup.corpus, curated_dir=curated_dir)
    assert stats == {"parts": 2, "explanations": 1, "conflicts": 1, "total": 1}
    assert curated.load(curated_dir)["iaaa-2"]["source_hash"] == "h2"
    assert "iaaa-1" in curated.load_conflicts(curated_dir)

    again = prepare(setup.exports, setup.tmp / "media", setup.tmp / "work2", "B", curated_dir=curated_dir)
    assert again["questions"] == 0


def test_a_part_with_errors_or_gaps_is_not_merged(setup):
    work = setup.tmp / "work"
    curated_dir = setup.tmp / "curated"
    prepare(setup.exports, setup.tmp / "media", work, "B", curated_dir=curated_dir)
    write_json(work / "out" / "part-01.json", {"explanations": {"iaaa-1": law()}})  # iaaa-2 is missing
    with pytest.raises(curated.MergeRefused):
        curated.merge(work, setup.exports, setup.corpus, curated_dir=curated_dir)
    assert curated.load(curated_dir) == {}


def test_only_current_explanations_with_valid_quotes_are_exported(setup, monkeypatch):
    curated_dir = setup.tmp / "curated"
    curated._save(
        curated_dir,
        {
            "iaaa-1": {"source_hash": "h1", **law()},
            "iaaa-2": {"source_hash": "old", **law()},
            "iaaa-3": {"source_hash": "h3", **law(quote="текст, който го няма")},
        },
        {},
    )
    dataset = SimpleNamespace(
        dataset_version="1.2.0",
        questions=[SimpleNamespace(id=q.id, content_hash=q.content_hash) for q in setup.bank.values()],
    )
    export, issues, checked = build_explanations(dataset, curated_dir, setup.legal)
    assert checked == 3
    assert [q.id for q in export.questions] == ["iaaa-1"]
    assert export.acts[0].short == "ЗДвП" and export.acts[0].consolidated_to == "ДВ, бр. 64 от 05.08.2025 г."
    assert sorted(i.severity for i in issues) == ["error", "warning"]
    assert explanation_sets(dataset, export)[0].coverage == round(1 / 3, 4)
    assert build_explanations(dataset, setup.tmp / "nothing", setup.legal)[0] is None

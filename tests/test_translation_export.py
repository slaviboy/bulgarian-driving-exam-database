"""Work package → merge → curated files → export (JSON, SQLite, manifest languages), on the real excerpt."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from test_build_pipeline import built  # noqa: F401  (fixture)

from question_bank.build import write_schemas
from question_bank.database.sqlite_builder import write_sqlite
from question_bank.exporter.json_export import write_json_exports
from question_bank.fsutil import read_json, write_json
from question_bank.translations import curated, lint
from question_bank.translations.export import (
    build_translations,
    language_infos,
    validate_translation_exports,
    write_translation_exports,
)
from question_bank.translations.prepare import prepare


def fake(source: str, index: int) -> str:
    """A 'translation' that passes the lint: Latin letters, the same numbers, codes and final punctuation."""
    tag = chr(97 + index % 26) * (index // 26 + 1)
    numbers = " ".join(lint.numbers(source))
    codes = " ".join(lint.category_codes(source))
    end = lint.ending(source) if lint.ending(source) in {":", "?", "."} else ""
    return " ".join(x for x in (f"Text {tag}", numbers, codes) if x) + end


def translate_package(work: Path, code: str) -> None:
    source_labels = read_json(work / "source" / "labels.bg.json")
    labels = {
        "categories": dict(source_labels["categories"]),
        "variants": {
            vid: {key: (fake(value, i) if value else value) for key, value in entry.items()}
            for i, (vid, entry) in enumerate(source_labels["variants"].items())
        },
        "topics": {tid: f"Topic {chr(97 + i)}" for i, tid in enumerate(source_labels["topics"])},
    }
    write_json(work / "out" / code / "labels.json", labels)
    for part in lint.part_numbers(work):
        name = f"part-{part:02d}.json"
        out = {}
        for q in read_json(work / "source" / "questions" / name)["questions"]:
            answers = {a["id"]: fake(a["text"], i + 1) for i, a in enumerate(q["answers"]) if "text" in a}
            out[q["id"]] = {"text": fake(q["text"], 0), "answers": answers}
        write_json(work / "out" / code / "questions" / name, out)


@pytest.fixture
def merged(built, tmp_path):  # noqa: F811
    settings, _extracted, _prepared, dataset = built
    exports = tmp_path / "exports"
    write_json_exports(dataset, exports)
    work = tmp_path / "work"
    prepare(exports, settings.media_dir, work, parts=2)
    translate_package(work, "en")
    curated_dir = tmp_path / "curated"
    stats = curated.merge(work, "en", exports, curated_dir)
    return dataset, exports, curated_dir, stats


def test_merge_records_the_source_of_every_translation(merged):
    dataset, _exports, curated_dir, stats = merged
    assert stats["questions"] == 6
    store = curated.load("en", curated_dir)
    hashes = {q.id: q.content_hash for q in dataset.questions}
    assert {qid: e["source_hash"] for qid, e in store.questions.items()} == hashes
    picture_only = {a.id for q in dataset.questions for a in q.answers if not a.text}
    assert picture_only and not picture_only & {a for e in store.questions.values() for a in e["answers"]}
    variant = dataset.variants[0]
    assert store.labels["variants"][variant.id]["source"]["description"] == variant.description


def test_merge_refuses_a_package_with_lint_errors(built, tmp_path):  # noqa: F811
    settings, _extracted, _prepared, dataset = built
    exports = tmp_path / "exports"
    write_json_exports(dataset, exports)
    work = tmp_path / "work"
    prepare(exports, settings.media_dir, work, parts=1)
    translate_package(work, "de")
    part = work / "out" / "de" / "questions" / "part-01.json"
    data = read_json(part)
    first = next(iter(data))
    data[first]["text"] = data[first]["text"].rstrip(":?.")  # loses its final punctuation
    write_json(part, data)
    with pytest.raises(curated.MergeRefused):
        curated.merge(work, "de", exports, tmp_path / "curated")


def test_export_keeps_current_translations_and_drops_stale_ones(merged, tmp_path):
    dataset, _exports, curated_dir, _stats = merged
    path = curated_dir / "en" / "questions.json"
    data = read_json(path)
    stale_id = dataset.questions[0].id
    data["questions"][stale_id]["source_hash"] = "0" * 64
    write_json(path, data)

    exports, issues, checked = build_translations(dataset, curated_dir)
    assert checked == 6
    [english] = exports
    assert [q.id for q in english.file.questions] == [q.id for q in dataset.questions[1:]]
    assert english.stale == 1 and english.missing == 0
    assert any(i.severity == "warning" and stale_id in i.refs for i in issues)
    assert not [i for i in issues if i.severity == "error"]

    infos = language_infos(dataset, exports)
    assert [(i.code, i.kind, i.file, i.questions) for i in infos] == [
        ("bg", "source", None, 6),
        ("en", "translation", "translation-en.json", 5),
    ]
    out = tmp_path / "out"
    out.mkdir()
    (out / "translation-xx.json").write_text("{}", encoding="utf-8")  # a language that is gone
    paths = write_translation_exports(exports, out)
    assert [p.name for p in paths] == ["translation-en.json"] and not (out / "translation-xx.json").exists()
    schemas = tmp_path / "schemas"
    write_schemas(schemas)
    assert validate_translation_exports(paths, schemas) == []
    exported = json.loads(paths[0].read_text(encoding="utf-8"))
    assert exported["language_tag"] == "en" and exported["translation"]["status"] == "unofficial"


def test_sqlite_holds_the_translations(merged, tmp_path):
    dataset, _exports, curated_dir, _stats = merged
    exports, _issues, _checked = build_translations(dataset, curated_dir)
    db = tmp_path / "master.sqlite"
    write_sqlite(
        dataset,
        db,
        info={"schema_version": "1"},
        languages=language_infos(dataset, exports),
        translations=exports,
    )
    con = sqlite3.connect(db)
    try:
        assert con.execute("SELECT COUNT(*) FROM languages").fetchone()[0] == 2
        assert con.execute("SELECT COUNT(*) FROM question_translations").fetchone()[0] == 6
        text_answers = sum(1 for q in dataset.questions for a in q.answers if a.text)
        assert con.execute("SELECT COUNT(*) FROM answer_translations").fetchone()[0] == text_answers
        kinds = {r[0] for r in con.execute("SELECT DISTINCT kind FROM label_translations")}
        assert {"category", "variant_description", "topic"} <= kinds
        assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        con.close()

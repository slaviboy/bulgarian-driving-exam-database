"""Offline end-to-end test of the build on the real 6-question excerpt, with synthetic media files."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest
from PIL import Image

from question_bank.build import write_schemas
from question_bank.database.sqlite_builder import write_sqlite
from question_bank.exporter.json_export import write_json_exports
from question_bank.exporter.media import prepare_media
from question_bank.extractor.downloaders.state import FetchRecord
from question_bank.extractor.parsers.official_html import parse_variant_file
from question_bank.extractor.pipeline import ExtractedFile, SourceFileInfo
from question_bank.processor.builder import DeduplicationConflict, build_dataset
from question_bank.processor.validation.validators import validate_dataset, validate_exports

VARIANT = "B.bez-pravosposobnost-ili-s-pravosposobnost-za-kategoria-am"
RULES = {
    "rules_version": "2024-12-12",
    "documents": {
        k: {"document": f"doc {k}", "url": f"https://example.test/{k}"} for k in ("N38", "MET", "OBS")
    },
    "defaults": {"scoring": "all_or_nothing", "show_correct_count": True, "max_video_plays": 3},
    "variants": [
        {
            "official_order": 7,
            "variant_id": VARIANT,
            "question_count": 3,
            "max_points": 4,
            "pass_points": 3,
            "duration_minutes": 5,
            "video_questions": 1,
            "section_quotas": {"1": 2, "2": 1},
            "section_quotas_basis": "methodology",
            "points_mix": {"1": 2, "2": 1, "3": 0},
            "points_mix_basis": "observation",
            "law": "test",
            "methodology": "test",
            "observed": True,
            "pass_points_basis": "law",
        }
    ],
}


def _extracted(fixtures_dir: Path) -> ExtractedFile:
    html = (fixtures_dir / "official" / "variant-B-sample.html").read_text(encoding="utf-8")
    source = SourceFileInfo(
        order=7,
        url="https://public-eis.rta.government.bg/exam-questions/7_B/7_B.html",
        relative_path="7_B/7_B.html",
        directory="7_B",
        edition="2026-10-01",
        sha256=hashlib.sha256(html.encode()).hexdigest(),
        bytes=len(html.encode()),
        etag='"x"',
        last_modified=None,
        fetched_at="2026-11-04T00:00:00+00:00",
    )
    return ExtractedFile(source, parse_variant_file(html))


def _media_records(settings, extracted: ExtractedFile) -> dict[str, FetchRecord]:
    records = {}
    for index, name in enumerate(sorted({a for q in extracted.parsed.questions for a in q.assets})):
        path = settings.raw_dir / "7_B" / "assets" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if name.endswith(".mp4"):
            path.write_bytes(b"\x00\x00\x00\x18ftypisom" + bytes(64))
        else:
            Image.new("RGB", (40 + index, 30), (index * 30 % 255, 90, 160)).save(path, "PNG")
        data = path.read_bytes()
        records[name] = FetchRecord(
            url=f"https://example.test/assets/{name}",
            path=path.relative_to(settings.data_dir).as_posix(),
            sha256=hashlib.sha256(data).hexdigest(),
            bytes=len(data),
            etag=None,
            last_modified=None,
            fetched_at="2026-11-04T00:00:00+00:00",
            checked_at="2026-11-04T00:00:00+00:00",
        )
    return records


@pytest.fixture
def built(fast_settings, fixtures_dir):
    extracted = _extracted(fixtures_dir)
    prepared = prepare_media(fast_settings, _media_records(fast_settings, extracted))
    dataset = build_dataset([extracted], prepared, RULES, dataset_version="0.0.1-test")
    return fast_settings, extracted, prepared, dataset


def test_dataset_shape(built):
    _settings, _extracted_file, prepared, dataset = built
    assert [c.id for c in dataset.categories] == ["B"]
    assert [v.id for v in dataset.variants] == [VARIANT]
    assert [s.id for s in dataset.sections] == [f"{VARIANT}#s1", f"{VARIANT}#s2"]
    assert [q.id for q in dataset.questions] == [
        "iaaa-5244",
        "iaaa-5300",
        "iaaa-5452",
        "iaaa-5480",
        "iaaa-6164",
        "iaaa-12004",
    ]
    pictures = {q.id: q for q in dataset.questions}["iaaa-5480"]
    assert pictures.answer_format == "image" and all(a.media_id for a in pictures.answers)
    video = {q.id: q for q in dataset.questions}["iaaa-12004"]
    assert [m.role for m in video.media] == ["video"]
    assert len(dataset.media) == 7 and len(prepared.by_name) == 7
    assert all(m.derivatives for m in dataset.media if m.kind == "image")
    config = dataset.exam_configs[0]
    assert config.id == f"{VARIANT}@2024-12-12" and config.status == "official"


def test_exports_validate_cleanly(built, tmp_path):
    settings, _extracted_file, _prepared, dataset = built
    paths = write_json_exports(dataset, tmp_path / "exports")
    paths["sqlite"] = tmp_path / "exports" / "master.sqlite"
    write_sqlite(dataset, paths["sqlite"], info={"schema_version": "1", "dataset_version": "0.0.1-test"})
    schemas = tmp_path / "schemas"
    write_schemas(schemas)
    report = validate_dataset(dataset, settings.media_dir, expected_rows=6)
    validate_exports(report, paths, schemas)
    assert report.ok, [i.message for i in report.issues if i.severity == "error"]
    assert {c.name for c in report.checks} >= {
        "missing_questions",
        "missing_answers",
        "invalid_correct_answers",
        "broken_media_references",
        "missing_media_files",
        "duplicate_questions",
        "duplicate_answers",
        "invalid_references",
        "incorrect_ordering",
        "invalid_attribution",
        "exam_feasibility",
        "json_schema",
        "sqlite_integrity",
    }

    con = sqlite3.connect(paths["sqlite"])
    assert con.execute("PRAGMA user_version").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 6
    assert con.execute("SELECT COUNT(*) FROM variant_questions").fetchone()[0] == 6
    assert con.execute("SELECT COUNT(*) FROM answers WHERE is_correct = 1").fetchone()[0] == 7
    assert con.execute("PRAGMA foreign_key_check").fetchall() == []
    con.close()


def test_validation_catches_broken_data(built):
    settings, _extracted_file, _prepared, dataset = built
    broken = dataset.questions[0].model_copy(
        update={"answers": [a.model_copy(update={"is_correct": False}) for a in dataset.questions[0].answers]}
    )
    dataset.questions[0] = broken
    report = validate_dataset(dataset, settings.media_dir)
    assert not report.ok
    assert any(i.check == "invalid_correct_answers" and i.severity == "error" for i in report.issues)


def test_conflicting_duplicate_ids_fail_the_build(built, fixtures_dir):
    _settings, extracted, prepared, _dataset = built
    first = extracted.parsed.questions[0]
    altered = first.__class__(**{**first.__dict__, "text": first.text + " (променен)"})
    other = ExtractedFile(
        extracted.source.__class__(**{**extracted.source.__dict__, "order": 8}),
        extracted.parsed.__class__(
            **{**extracted.parsed.__dict__, "description": "друг вариант", "questions": (altered,)}
        ),
    )
    with pytest.raises(DeduplicationConflict):
        build_dataset([extracted, other], prepared, RULES, dataset_version="0.0.1-test")

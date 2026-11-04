"""Write the dataset into master.sqlite (schema_v1.sql) — atomically, in a deterministic row order."""

from __future__ import annotations

import json
import os
import sqlite3
from importlib import resources
from pathlib import Path

from question_bank.models import SCHEMA_VERSION
from question_bank.processor.builder import Dataset


def schema_sql() -> str:
    return (
        resources.files("question_bank.database")
        .joinpath("schema", "schema_v1.sql")
        .read_text(encoding="utf-8")
    )


def _j(value) -> str | None:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    elif isinstance(value, list):
        value = [v.model_dump(mode="json") if hasattr(v, "model_dump") else v for v in value]
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_sqlite(dataset: Dataset, dest: Path, *, info: dict[str, str]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(schema_sql())
        with con:
            con.executemany("INSERT INTO dataset_info VALUES (?, ?)", sorted(info.items()))
            con.executemany(
                "INSERT INTO sources VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        s.id,
                        s.name,
                        s.source_url,
                        s.attribution,
                        s.license,
                        s.redistribution_status,
                        s.retrieved_at,
                    )
                    for s in dataset.sources
                ],
            )
            con.executemany(
                "INSERT INTO categories VALUES (?, ?, ?, ?, ?)",
                [(c.id, c.name, c.description, c.source_id, c.position) for c in dataset.categories],
            )
            con.executemany(
                "INSERT INTO variants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        v.id,
                        v.category_id,
                        v.title,
                        v.description,
                        v.effective_note,
                        v.source_url,
                        v.source_sha256,
                        v.source_edition,
                        v.position,
                        v.question_count,
                    )
                    for v in dataset.variants
                ],
            )
            con.executemany("INSERT INTO topics VALUES (?, ?)", [(t.id, t.name) for t in dataset.topics])
            category_of = {v.id: v.category_id for v in dataset.variants}
            con.executemany(
                "INSERT INTO sections VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        s.id,
                        s.variant_id,
                        category_of[s.variant_id],
                        s.topic_id,
                        s.number,
                        s.name,
                        s.position,
                        s.question_count,
                    )
                    for s in dataset.sections
                ],
            )
            con.executemany(
                "INSERT INTO media VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        m.id,
                        m.kind,
                        m.original_name,
                        m.relative_path,
                        m.mime_type,
                        m.bytes,
                        m.width,
                        m.height,
                        m.sha256,
                        m.source_url,
                        m.source_id,
                    )
                    for m in dataset.media
                ],
            )
            con.executemany(
                "INSERT INTO media_derivatives VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (m.id, d.format, d.relative_path, d.mime_type, d.bytes, d.width, d.height, d.sha256)
                    for m in dataset.media
                    for d in m.derivatives
                ],
            )
            con.executemany(
                "INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        q.id,
                        q.original_id,
                        q.source_id,
                        q.text,
                        q.explanation,
                        q.answer_format,
                        q.correct_count,
                        q.content_hash,
                    )
                    for q in dataset.questions
                ],
            )
            con.executemany(
                "INSERT INTO answers VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (a.id, q.id, a.position, a.text, a.media_id, int(a.is_correct))
                    for q in dataset.questions
                    for a in q.answers
                ],
            )
            con.executemany(
                "INSERT INTO question_media VALUES (?, ?, ?, ?)",
                [(q.id, m.media_id, m.role, m.position) for q in dataset.questions for m in q.media],
            )
            con.executemany(
                "INSERT INTO variant_questions VALUES (?, ?, ?, ?, ?)",
                sorted(
                    (a.variant_id, q.id, a.section_id, a.points, a.position)
                    for q in dataset.questions
                    for a in q.assignments
                ),
            )
            con.executemany(
                "INSERT INTO exam_configs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        c.id,
                        c.variant_id,
                        c.status,
                        c.question_count,
                        c.max_points,
                        c.pass_points,
                        c.duration_minutes,
                        c.video_questions,
                        c.max_video_plays,
                        c.scoring,
                        int(c.show_correct_count),
                        _j(c.section_quotas),
                        _j(c.points_mix),
                        _j(c.verification),
                        _j(c.evidence),
                        _j(c.notes),
                    )
                    for c in dataset.exam_configs
                ],
            )
        problems = con.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise ValueError(f"foreign key violations: {problems[:5]}")
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity check failed")
        con.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        con.commit()
        con.execute("VACUUM")
    finally:
        con.close()
    os.replace(tmp, dest)

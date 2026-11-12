"""Data-quality validation (spec §2.7). Every check reports actual counts; errors fail the build."""

from __future__ import annotations

import random
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from question_bank.exam_rules.generator import (
    ExamSpec,
    GenerationError,
    PoolQuestion,
    generate_exam,
    verify_exam,
)
from question_bank.fsutil import read_json, sha256_file
from question_bank.models import SCHEMA_MODELS
from question_bank.processor.builder import Dataset

Severity = Literal["error", "warning"]
FEASIBILITY_SEEDS = 20


@dataclass
class Issue:
    check: str
    severity: Severity
    message: str
    refs: list[str] = field(default_factory=list)


@dataclass
class Check:
    name: str
    description: str
    passed: bool
    checked: int  # how many items were examined
    errors: int
    warnings: int


@dataclass
class ValidationReport:
    checks: list[Check] = field(default_factory=list)
    issues: list[Issue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def ok(self) -> bool:
        return self.error_count == 0

    def run(self, name: str, description: str, checked: int, issues: list[Issue]) -> None:
        errors = sum(1 for i in issues if i.severity == "error")
        warnings = sum(1 for i in issues if i.severity == "warning")
        self.checks.append(Check(name, description, errors == 0, checked, errors, warnings))
        self.issues.extend(issues)


def _contiguous(values: list[int]) -> bool:
    return sorted(values) == list(range(1, len(values) + 1))


def validate_dataset(
    dataset: Dataset, media_dir: Path, *, expected_rows: int | None = None
) -> ValidationReport:
    report = ValidationReport()
    questions = dataset.questions
    variants = {v.id: v for v in dataset.variants}
    sections = {s.id: s for s in dataset.sections}
    media = {m.id: m for m in dataset.media}

    # 1. missing questions
    issues: list[Issue] = []
    per_variant = Counter(a.variant_id for q in questions for a in q.assignments)
    for v in variants.values():
        if v.question_count == 0:
            issues.append(Issue("missing_questions", "error", f"variant {v.id} has no questions", [v.id]))
        if per_variant[v.id] != v.question_count:
            issues.append(
                Issue(
                    "missing_questions",
                    "error",
                    f"variant {v.id}: {per_variant[v.id]} assignments, expected {v.question_count}",
                    [v.id],
                )
            )
    rows = sum(per_variant.values())
    if expected_rows is not None and rows != expected_rows:
        issues.append(
            Issue("missing_questions", "error", f"{rows} question rows, source has {expected_rows}")
        )
    if len({q.id for q in questions}) != len(questions):
        issues.append(Issue("missing_questions", "error", "duplicate question IDs"))
    report.run("missing_questions", "every variant has all of its questions", len(variants), issues)

    # 2. missing answers
    issues = [
        Issue("missing_answers", "error", f"{q.id} has {len(q.answers)} answer(s)", [q.id])
        for q in questions
        if len(q.answers) < 2
    ]
    issues += [
        Issue("missing_answers", "error", f"{a.id} has neither text nor picture", [a.id])
        for q in questions
        for a in q.answers
        if not a.text and not a.media_id
    ]
    report.run(
        "missing_answers", "every question has ≥2 answers with text or picture", len(questions), issues
    )

    # 3. correct-answer mapping
    issues = []
    for q in questions:
        correct = sum(1 for a in q.answers if a.is_correct)
        if correct == 0:
            issues.append(Issue("invalid_correct_answers", "error", f"{q.id} has no correct answer", [q.id]))
        elif correct == len(q.answers):
            issues.append(
                Issue("invalid_correct_answers", "warning", f"{q.id}: every answer is correct", [q.id])
            )
        if correct != q.correct_count:
            issues.append(
                Issue("invalid_correct_answers", "error", f"{q.id}: correct_count mismatch", [q.id])
            )
    report.run(
        "invalid_correct_answers", "≥1 correct answer, correct_count consistent", len(questions), issues
    )

    # 4. missing images / broken media references
    issues = []
    referenced = set()
    for q in questions:
        for ref in q.media:
            referenced.add(ref.media_id)
            if ref.media_id not in media:
                issues.append(Issue("broken_media_references", "error", f"{q.id} → {ref.media_id}", [q.id]))
            elif media[ref.media_id].kind != ref.role:
                issues.append(
                    Issue("broken_media_references", "error", f"{q.id}: role/kind mismatch", [q.id])
                )
        for a in q.answers:
            if a.media_id:
                referenced.add(a.media_id)
                if a.media_id not in media:
                    issues.append(Issue("broken_media_references", "error", f"{a.id} → {a.media_id}", [a.id]))
    for m in media.values():
        if m.id not in referenced:
            issues.append(Issue("broken_media_references", "warning", f"{m.id} is not referenced", [m.id]))
    report.run("broken_media_references", "every media reference resolves", len(referenced), issues)

    issues = []
    files_checked = 0
    for m in media.values():
        for relative, sha, size in [(m.relative_path, m.sha256, m.bytes)] + [
            (d.relative_path, d.sha256, d.bytes) for d in m.derivatives
        ]:
            files_checked += 1
            path = media_dir / relative
            if not path.exists():
                issues.append(Issue("missing_media_files", "error", f"missing file {relative}", [m.id]))
            elif path.stat().st_size != size or sha256_file(path) != sha:
                issues.append(Issue("missing_media_files", "error", f"checksum mismatch {relative}", [m.id]))
    report.run("missing_media_files", "every media file exists with its SHA-256", files_checked, issues)

    # 5. duplicate questions / answers
    issues = [
        Issue("duplicate_questions", "warning", f"identical content under IDs {', '.join(ids)}", ids)
        for ids in dataset.duplicate_content
    ]
    report.run("duplicate_questions", "no identical content under different IDs", len(questions), issues)

    issues = []
    for q in questions:
        keys = [(a.text, a.media_id) for a in q.answers]
        if len(set(keys)) != len(keys):
            issues.append(Issue("duplicate_answers", "warning", f"{q.id} repeats an answer", [q.id]))
    report.run("duplicate_answers", "no repeated answer inside a question", len(questions), issues)

    # 6. category / section references
    issues = []
    for q in questions:
        for a in q.assignments:
            v = variants.get(a.variant_id)
            s = sections.get(a.section_id)
            if v is None or s is None or v.category_id != a.category_id or s.variant_id != a.variant_id:
                issues.append(
                    Issue("invalid_references", "error", f"{q.id}: bad assignment {a.section_id}", [q.id])
                )
    for s in sections.values():
        if s.variant_id not in variants:
            issues.append(Issue("invalid_references", "error", f"section {s.id} without variant", [s.id]))
    report.run("invalid_references", "assignments point at existing variant/category/section", rows, issues)

    # 7. ordering
    issues = []
    positions: dict[str, list[int]] = defaultdict(list)
    for q in questions:
        if not _contiguous([a.position for a in q.answers]):
            issues.append(Issue("incorrect_ordering", "error", f"{q.id}: answer positions not 1..n", [q.id]))
        for a in q.assignments:
            positions[a.variant_id].append(a.position)
    for vid, values in positions.items():
        if not _contiguous(values):
            issues.append(Issue("incorrect_ordering", "error", f"{vid}: question positions not 1..n", [vid]))
    for v in variants.values():
        if not _contiguous([s.position for s in v.sections]):
            issues.append(Issue("incorrect_ordering", "error", f"{v.id}: section positions not 1..n", [v.id]))
    variant_positions = [v.position for v in variants.values()]  # = official manifest order, may have gaps
    if len(set(variant_positions)) != len(variant_positions):
        issues.append(Issue("incorrect_ordering", "error", "duplicate variant positions"))
    report.run(
        "incorrect_ordering", "answers, questions, sections and variants keep source order", rows, issues
    )

    # 8. attribution
    issues = []
    source_ids = {s.id for s in dataset.sources}
    for s in dataset.sources:
        if not (s.attribution and s.license and s.redistribution_status and s.source_url):
            issues.append(
                Issue("invalid_attribution", "error", f"source {s.id} lacks attribution data", [s.id])
            )
    for q in questions:
        if q.source_id not in source_ids:
            issues.append(
                Issue("invalid_attribution", "error", f"{q.id}: unknown source {q.source_id}", [q.id])
            )
    for m in media.values():
        if m.source_id not in source_ids or not m.source_url:
            issues.append(Issue("invalid_attribution", "error", f"{m.id}: missing source", [m.id]))
    report.run("invalid_attribution", "every record has a known, attributed source", len(questions), issues)

    # 8b. enhanced pictures: a WebP for every picture, vector signs that AndroidSVG can draw, complete credits
    from question_bank.media_enhance.svg import sanitise

    issues = []
    images = [m for m in media.values() if m.kind == "image"]
    for m in images:
        if "webp" not in {d.format for d in m.derivatives}:
            issues.append(Issue("enhanced_media", "error", f"{m.id}: no WebP derivative", [m.id]))
        for d in m.derivatives:
            path = media_dir / d.relative_path
            if d.format == "svg" and path.exists() and sanitise(path.read_bytes()).issues:
                issues.append(Issue("enhanced_media", "error", f"{m.id}: SVG fails the lint", [m.id]))
            if "vector-commons" in d.process and not m.credits:
                issues.append(
                    Issue("enhanced_media", "error", f"{m.id}: Commons drawing without credit", [m.id])
                )
        for c in m.credits:
            if not (c.author and c.license and c.page.startswith("https://")):
                issues.append(
                    Issue("enhanced_media", "error", f"{m.id}: incomplete credit {c.title}", [m.id])
                )
    report.run(
        "enhanced_media",
        "every picture has a WebP; vector signs pass the AndroidSVG lint; Commons drawings are credited",
        len(images),
        issues,
    )

    # 9. exam configuration feasibility
    report.run(*_feasibility(dataset))
    return report


def exam_pool(dataset: Dataset, variant_id: str) -> list[PoolQuestion]:
    number_of = {s.id: s.number for s in dataset.sections}
    pool = []
    for q in dataset.questions:
        for a in q.assignments:
            if a.variant_id == variant_id:
                video = any(m.role == "video" for m in q.media)
                pool.append(PoolQuestion(q.id, number_of[a.section_id], a.points, video))
    return pool


def _feasibility(dataset: Dataset) -> tuple[str, str, int, list[Issue]]:
    issues: list[Issue] = []
    for config in dataset.exam_configs:
        spec = ExamSpec(
            question_count=config.question_count,
            max_points=config.max_points,
            video_questions=config.video_questions,
            section_quotas={q.section_number: q.count for q in config.section_quotas}
            if config.section_quotas
            else None,
            points_mix={int(k): v for k, v in config.points_mix.items()} if config.points_mix else None,
        )
        pool = exam_pool(dataset, config.variant_id)
        for seed in range(FEASIBILITY_SEEDS):
            try:
                selection = generate_exam(pool, spec, random.Random(seed))
            except GenerationError as exc:
                issues.append(Issue("exam_feasibility", "error", f"{config.id}: {exc}", [config.id]))
                break
            problem = verify_exam(selection, spec)
            if problem:
                issues.append(Issue("exam_feasibility", "error", f"{config.id}: {problem}", [config.id]))
                break
        if config.pass_points > config.max_points:
            issues.append(
                Issue("exam_feasibility", "error", f"{config.id}: pass mark above maximum", [config.id])
            )
    return (
        "exam_feasibility",
        f"every exam configuration can be generated ({FEASIBILITY_SEEDS} seeds each)",
        len(dataset.exam_configs),
        issues,
    )


def validate_exports(report: ValidationReport, paths: dict[str, Path], schemas_dir: Path) -> None:
    """JSON Schema conformance of the exported files and SQLite integrity."""
    import jsonschema

    issues: list[Issue] = []
    mapping = {"categories": "categories", "questions": "questions", "exam_configs": "exam-configs"}
    for key, schema_name in mapping.items():
        schema = read_json(schemas_dir / f"{schema_name}.schema.json")
        validator = jsonschema.Draft202012Validator(schema)
        for error in list(validator.iter_errors(read_json(paths[key])))[:20]:
            location = "/".join(map(str, error.absolute_path))
            issues.append(Issue("json_schema", "error", f"{paths[key].name}: {location}: {error.message}"))
    report.run("json_schema", "exports conform to contract/schemas", len(mapping), issues)

    issues = []
    con = sqlite3.connect(f"file:{paths['sqlite'].as_posix()}?mode=ro", uri=True)
    try:
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            issues.append(Issue("sqlite_integrity", "error", "integrity_check failed"))
        for row in con.execute("PRAGMA foreign_key_check").fetchall()[:20]:
            issues.append(Issue("sqlite_integrity", "error", f"foreign key violation {row}"))
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version != 1:
            issues.append(Issue("sqlite_integrity", "error", f"user_version {version} != 1"))
    finally:
        con.close()
    report.run("sqlite_integrity", "master.sqlite integrity, foreign keys, user_version", 1, issues)


def validate_manifest(manifest_path: Path, exports_dir: Path) -> list[Issue]:
    """Re-verify every checksum listed in a manifest (used by CI and before releases)."""
    manifest = read_json(manifest_path)
    issues = []
    for entry in manifest["files"]:
        path = exports_dir / entry["path"]
        if not path.exists():
            issues.append(Issue("manifest_checksums", "error", f"missing {entry['path']}"))
        elif path.stat().st_size != entry["bytes"] or sha256_file(path) != entry["sha256"]:
            issues.append(Issue("manifest_checksums", "error", f"checksum mismatch {entry['path']}"))
    SCHEMA_MODELS["manifest"].model_validate(manifest)
    return issues

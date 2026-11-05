"""manifest.json — the entry point of a dataset release (data contract §5.2)."""

from __future__ import annotations

import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from question_bank import __version__
from question_bank.config import REPO_ROOT
from question_bank.extractor.pipeline import ExtractedFile
from question_bank.fsutil import sha256_file
from question_bank.models import (
    Completeness,
    CompletenessCheck,
    Generator,
    LanguageInfo,
    Manifest,
    ManifestFile,
    MediaPack,
    SourceSnapshot,
)
from question_bank.processor.builder import LICENSING, Dataset
from question_bank.processor.hashing import content_fingerprint
from question_bank.processor.validation.validators import ValidationReport

MEDIA_TYPES = {".json": "application/json", ".sqlite": "application/vnd.sqlite3"}


def git_commit() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def dataset_fingerprint(dataset: Dataset) -> str:
    assignments = sorted(
        (a.variant_id, q.id, a.section_id, a.points, a.position)
        for q in dataset.questions
        for a in q.assignments
    )
    configs = [c.model_dump(mode="json") for c in dataset.exam_configs]
    return content_fingerprint({q.id: q.content_hash for q in dataset.questions}, assignments, configs)


def build_manifest(
    dataset: Dataset,
    extracted: list[ExtractedFile],
    export_paths: list[Path],
    exports_dir: Path,
    media_packs: list[MediaPack],
    *,
    dataset_base_url: str,
    media_base_url: str,
    report: ValidationReport,
    coverage_checks: list[CompletenessCheck],
    built_at: str | None = None,
    languages: list[LanguageInfo] | None = None,
) -> Manifest:
    files = [
        ManifestFile(
            path=p.relative_to(exports_dir).as_posix(),
            bytes=p.stat().st_size,
            sha256=sha256_file(p),
            media_type=MEDIA_TYPES.get(p.suffix, "application/octet-stream"),
        )
        for p in export_paths
    ]
    per_category: dict[str, dict[str, int]] = defaultdict(
        lambda: {"variants": 0, "questions": 0, "assignments": 0}
    )
    questions_per_category: dict[str, set[str]] = defaultdict(set)
    for v in dataset.variants:
        per_category[v.category_id]["variants"] += 1
    for q in dataset.questions:
        for a in q.assignments:
            per_category[a.category_id]["assignments"] += 1
            questions_per_category[a.category_id].add(q.id)
    for cid, ids in questions_per_category.items():
        per_category[cid]["questions"] = len(ids)

    checks = [
        CompletenessCheck(
            name=c.name,
            passed=c.passed,
            detail=f"{c.checked} checked, {c.errors} errors, {c.warnings} warnings — {c.description}",
        )
        for c in report.checks
    ] + coverage_checks
    return Manifest(
        dataset_version=dataset.dataset_version,
        source_edition=dataset.source_edition,
        rules_version=dataset.rules_version,
        built_at=built_at or datetime.now(UTC).isoformat(timespec="seconds"),
        generator=Generator(
            name="bulgarian-driving-exam-database", version=__version__, git_commit=git_commit()
        ),
        content_fingerprint=dataset_fingerprint(dataset),
        sources=dataset.sources,
        source_snapshot=[
            SourceSnapshot(
                url=e.source.url,
                etag=e.source.etag,
                last_modified=e.source.last_modified,
                sha256=e.source.sha256,
                bytes=e.source.bytes,
            )
            for e in sorted(extracted, key=lambda e: e.source.order)
        ],
        counts={
            "categories": len(dataset.categories),
            "variants": len(dataset.variants),
            "sections": len(dataset.sections),
            "topics": len(dataset.topics),
            "questions": len(dataset.questions),
            "answers": sum(len(q.answers) for q in dataset.questions),
            "assignments": sum(len(q.assignments) for q in dataset.questions),
            "media": len(dataset.media),
            "images": sum(1 for m in dataset.media if m.kind == "image"),
            "videos": sum(1 for m in dataset.media if m.kind == "video"),
            "exam_configs": len(dataset.exam_configs),
        },
        category_counts={k: dict(v) for k, v in sorted(per_category.items())},
        variant_counts={v.id: v.question_count for v in dataset.variants},
        dataset_base_url=dataset_base_url,
        files=files,
        media_base_url=media_base_url,
        media_packs=media_packs,
        licensing=LICENSING,
        completeness=Completeness(
            status="complete" if all(c.passed for c in checks) else "partial", checks=checks
        ),
        languages=languages or [],
    )

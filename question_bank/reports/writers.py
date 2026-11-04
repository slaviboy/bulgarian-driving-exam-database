"""Human- and machine-readable reports written to reports/ (committed with every dataset build)."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from question_bank.extractor.pipeline import ExtractedFile
from question_bank.fsutil import write_json, write_text
from question_bank.processor.builder import Dataset
from question_bank.processor.validation.validators import ValidationReport


def write_validation_report(report: ValidationReport, dataset: Dataset, out_dir: Path) -> None:
    payload = {
        "dataset_version": dataset.dataset_version,
        "source_edition": dataset.source_edition,
        "summary": {
            "checks": len(report.checks),
            "checks_passed": sum(1 for c in report.checks if c.passed),
            "errors": report.error_count,
            "warnings": report.warning_count,
        },
        "checks": [asdict(c) for c in report.checks],
        "issues": [asdict(i) for i in report.issues],
    }
    write_json(out_dir / "validation-report.json", payload)
    lines = [
        f"# Validation report — dataset {dataset.dataset_version} (edition {dataset.source_edition})",
        "",
        f"**{payload['summary']['checks_passed']}/{len(report.checks)} checks passed** · "
        f"{report.error_count} errors · {report.warning_count} warnings",
        "",
        "| Check | Result | Items checked | Errors | Warnings | Description |",
        "|---|---|---|---|---|---|",
    ]
    for c in report.checks:
        result = "✅ pass" if c.passed else "❌ fail"
        lines.append(f"| `{c.name}` | {result} | {c.checked} | {c.errors} | {c.warnings} | {c.description} |")
    if report.issues:
        lines += ["", "## Issues", "", "| Severity | Check | Message |", "|---|---|---|"]
        for i in report.issues[:500]:
            lines.append(f"| {i.severity} | `{i.check}` | {i.message} |")
        if len(report.issues) > 500:
            lines.append(f"| … | | {len(report.issues) - 500} more in validation-report.json |")
    write_text(out_dir / "validation-report.md", "\n".join(lines) + "\n")


def write_category_counts(dataset: Dataset, out_dir: Path) -> None:
    payload: dict[str, Any] = {"dataset_version": dataset.dataset_version, "categories": []}
    for c in dataset.categories:
        unique = {q.id for q in dataset.questions for a in q.assignments if a.category_id == c.id}
        payload["categories"].append(
            {
                "id": c.id,
                "name": c.name,
                "unique_questions": len(unique),
                "variants": [
                    {
                        "id": v.id,
                        "title": v.title,
                        "questions": v.question_count,
                        "sections": [
                            {"number": s.number, "name": s.name, "questions": s.question_count}
                            for s in v.sections
                        ],
                    }
                    for v in c.variants
                ],
            }
        )
    write_json(out_dir / "category-counts.json", payload)


def write_extraction_report(
    dataset: Dataset, extracted: list[ExtractedFile], copy_checks: dict[str, Any] | None, out_dir: Path
) -> None:
    images = [m for m in dataset.media if m.kind == "image"]
    videos = [m for m in dataset.media if m.kind == "video"]
    webp = [d for m in images for d in m.derivatives]
    points = Counter(a.points for q in dataset.questions for a in q.assignments)
    answers = Counter(len(q.answers) for q in dataset.questions)
    correct = Counter(q.correct_count for q in dataset.questions)
    formats = Counter(q.answer_format for q in dataset.questions)
    lines = [
        f"# Extraction report — edition {dataset.source_edition}",
        "",
        "Source: https://public-eis.rta.government.bg/exam-questions/ (ИААА). Every number below is counted "
        "from the downloaded files.",
        "",
        "## Variant files",
        "",
        "| # | Variant | Questions | Sections | Size | SHA-256 |",
        "|---|---|---|---|---|---|",
    ]
    for e in sorted(extracted, key=lambda e: e.source.order):
        lines.append(
            f"| {e.source.order} | {e.parsed.title} | {len(e.parsed.questions)} | {len(e.parsed.sections)} | "
            f"{e.source.bytes / 1e6:.2f} MB | `{e.source.sha256[:16]}…` |"
        )
    rows = sum(len(e.parsed.questions) for e in extracted)
    lines += [
        "",
        "## Totals",
        "",
        f"* Variant files: **{len(extracted)}** · question rows: **{rows}** · unique questions: "
        f"**{len(dataset.questions)}** · answers: **{sum(len(q.answers) for q in dataset.questions)}**",
        f"* Categories: **{len(dataset.categories)}** ({', '.join(c.name for c in dataset.categories)}) · "
        f"sections: **{len(dataset.sections)}** · topics: **{len(dataset.topics)}**",
        f"* Points per question row: {', '.join(f'{p} pt × {n}' for p, n in sorted(points.items()))}",
        f"* Answers per question: {', '.join(f'{k} × {v}' for k, v in sorted(answers.items()))} · "
        f"correct answers per question: {', '.join(f'{k} × {v}' for k, v in sorted(correct.items()))}",
        f"* Answer formats: {', '.join(f'{k} × {v}' for k, v in sorted(formats.items()))}",
        f"* Images: **{len(images)}** ({sum(m.bytes for m in images) / 1e6:.1f} MB original, "
        f"{sum(d.bytes for d in webp) / 1e6:.1f} MB as WebP) · videos: **{len(videos)}** "
        f"({sum(m.bytes for m in videos) / 1e6:.1f} MB)",
        f"* Asset names with byte-identical content (merged into one media record): "
        f"{sum(len(v) for v in dataset.duplicate_media_names.values())} names → "
        f"{len(dataset.duplicate_media_names)} records",
        f"* Questions with identical content under different IDs: {len(dataset.duplicate_content)} groups",
        "* Explanations: none — the source publishes none, so `explanation` is always null.",
    ]
    if copy_checks is not None:
        by_method = Counter(c["method"] for c in copy_checks["checks"])
        methods = ", ".join(f"{k}: {v}" for k, v in sorted(by_method.items()))
        lines += [
            "",
            "## Copies of assets in other variant directories",
            "",
            f"{copy_checks['checked']} copies verified ({methods}), "
            f"**{copy_checks['mismatches']} mismatches**. "
            "Every video copy and a seeded sample of picture copies are compared with the downloaded file "
            "(ETag and size, or SHA-256 after download).",
        ]
    write_text(out_dir / "extraction-report.md", "\n".join(lines) + "\n")


def write_dataset_diff(previous: dict[str, Any] | None, dataset: Dataset, out_dir: Path) -> dict[str, int]:
    current = {q.id: q.content_hash for q in dataset.questions}
    if previous is None:
        write_text(
            out_dir / "dataset-diff.md",
            f"# Dataset diff — {dataset.dataset_version}\n\n"
            f"First build: {len(current)} questions, no previous export.\n",
        )
        return {"added": len(current), "removed": 0, "changed": 0}
    before = {q["id"]: q["content_hash"] for q in previous.get("questions", [])}
    added = sorted(set(current) - set(before))
    removed = sorted(set(before) - set(current))
    changed = sorted(q for q in set(current) & set(before) if current[q] != before[q])
    lines = [
        f"# Dataset diff — {previous.get('dataset_version')} → {dataset.dataset_version}",
        "",
        f"* added: {len(added)} · removed: {len(removed)} · changed content: {len(changed)}",
    ]
    for title, ids in (("Added", added), ("Removed", removed), ("Changed", changed)):
        if ids:
            lines += ["", f"## {title}", "", ", ".join(ids[:400]) + (" …" if len(ids) > 400 else "")]
    write_text(out_dir / "dataset-diff.md", "\n".join(lines) + "\n")
    return {"added": len(added), "removed": len(removed), "changed": len(changed)}

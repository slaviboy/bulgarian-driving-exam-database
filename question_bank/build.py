"""`qb build`: turn the extracted edition into the published dataset.

Outputs: exports, media packs, manifest and reports."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from question_bank.config import REPO_ROOT, Settings
from question_bank.database.sqlite_builder import write_sqlite
from question_bank.explanations.export import (
    build_explanations,
    explanation_sets,
    validate_explanation_exports,
    write_explanation_export,
)
from question_bank.exporter.json_export import FILE_NAMES, write_json_exports
from question_bank.exporter.manifest import build_manifest, dataset_fingerprint
from question_bank.exporter.media import prepare_media
from question_bank.exporter.packages import build_core_package, build_media_release, release_download_base
from question_bank.extractor.downloaders.media import collect_asset_refs, records_from_journal
from question_bank.extractor.pipeline import load_extracted
from question_bank.fsutil import dumps_json, read_json, write_json
from question_bank.models import SCHEMA_MODELS, CompletenessCheck, Manifest
from question_bank.processor.builder import build_dataset
from question_bank.processor.validation.validators import ValidationReport, validate_dataset, validate_exports
from question_bank.reports.writers import (
    write_category_counts,
    write_dataset_diff,
    write_extraction_report,
    write_validation_report,
)
from question_bank.translations.export import (
    build_translations,
    language_infos,
    validate_translation_exports,
    write_translation_exports,
)

log = logging.getLogger(__name__)

SCHEMAS_DIR = REPO_ROOT / "contract" / "schemas"
EXAM_RULES = REPO_ROOT / "data" / "exam-rules" / "exam-configs.source.json"
EXPECTED_OFFICIAL_FILES = 23  # edition 2026-10-01; a different count must be reviewed, not silently accepted


def schema_documents() -> dict[str, str]:
    documents = {}
    for name, model in SCHEMA_MODELS.items():
        schema = model.model_json_schema(mode="serialization")
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": f"https://github.com/slaviboy/bulgarian-driving-exam-database/contract/schemas/{name}.schema.json",
            **schema,
        }
        documents[f"{name}.schema.json"] = dumps_json(schema)
    return documents


def write_schemas(directory: Path = SCHEMAS_DIR) -> list[Path]:
    paths = []
    for file_name, text in schema_documents().items():
        path = directory / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        paths.append(path)
    return paths


@dataclass
class BuildResult:
    manifest: Manifest
    report: ValidationReport
    diff: dict[str, int]
    release_dirs: list[Path]


def run_build(
    settings: Settings, dataset_version: str, *, webp: bool = True, translations_dir: Path | None = None
) -> BuildResult:
    extracted = load_extracted(settings)
    if not extracted:
        raise SystemExit("run `qb extract` first")
    refs = collect_asset_refs(extracted)
    records = records_from_journal(settings, refs)
    log.info("preparing media", extra={"assets": len(records)})
    prepared = prepare_media(settings, records, webp=webp)

    exports = settings.exports_dir
    previous_questions = exports / FILE_NAMES["questions"]
    previous = read_json(previous_questions) if previous_questions.exists() else None

    dataset = build_dataset(
        extracted,
        prepared,
        read_json(EXAM_RULES),
        dataset_version=dataset_version,
        retrieved_at=max(e.source.fetched_at for e in extracted),
    )
    paths = write_json_exports(dataset, exports)
    translations, translation_issues, translation_checked = (
        build_translations(dataset, translations_dir) if translations_dir else build_translations(dataset)
    )
    translation_paths = write_translation_exports(translations, exports)
    languages = language_infos(dataset, translations)
    explanations, explanation_issues, explanation_checked = build_explanations(dataset)
    explanation_paths = write_explanation_export(explanations, exports)
    sqlite_path = exports / FILE_NAMES["sqlite"]
    write_sqlite(
        dataset,
        sqlite_path,
        info={
            "schema_version": "1",
            "dataset_version": dataset.dataset_version,
            "source_edition": dataset.source_edition,
            "rules_version": dataset.rules_version,
            "content_fingerprint": dataset_fingerprint(dataset),
        },
        languages=languages,
        translations=translations,
        explanations=explanations,
    )
    paths["sqlite"] = sqlite_path

    write_schemas()
    rows = sum(len(e.parsed.questions) for e in extracted)
    report = validate_dataset(dataset, settings.media_dir, expected_rows=rows)
    report.run(
        "translations",
        "translations match the current Bulgarian text (stale or missing ones are left out)",
        translation_checked,
        translation_issues,
    )
    validate_exports(report, paths, SCHEMAS_DIR)
    report.run(
        "translation_schema",
        "translation files conform to contract/schemas",
        len(translation_paths),
        validate_translation_exports(translation_paths, SCHEMAS_DIR),
    )
    report.run(
        "explanations",
        "explanations match the current Bulgarian text and every quote is still in the cited act",
        explanation_checked,
        explanation_issues,
    )
    report.run(
        "explanation_schema",
        "explanation files conform to contract/schemas",
        len(explanation_paths),
        validate_explanation_exports(explanation_paths, SCHEMAS_DIR),
    )

    release_root = settings.data_dir.parent / "release"
    media_release = build_media_release(
        dataset.media, settings.media_dir, release_root, dataset.source_edition
    )

    copy_checks_path = settings.cache_dir / "media-copy-checks.json"
    copy_checks = read_json(copy_checks_path) if copy_checks_path.exists() else None
    coverage = [
        CompletenessCheck(
            name="all_official_files_extracted",
            passed=len(extracted) == EXPECTED_OFFICIAL_FILES,
            detail=f"{len(extracted)} of {EXPECTED_OFFICIAL_FILES} files listed in manifest.txt",
        ),
        CompletenessCheck(
            name="all_referenced_media_downloaded",
            passed=len(records) == len(refs),
            detail=f"{len(records)} of {len(refs)} referenced assets downloaded and checksummed",
        ),
        CompletenessCheck(
            name="asset_copies_identical",
            passed=bool(copy_checks) and copy_checks["mismatches"] == 0,
            detail=(
                f"{copy_checks['checked']} copies in other variant directories compared, "
                f"{copy_checks['mismatches']} mismatches"
                if copy_checks
                else "copy verification has not been run"
            ),
        ),
    ]
    manifest = build_manifest(
        dataset,
        extracted,
        [
            paths["categories"],
            paths["questions"],
            paths["exam_configs"],
            *translation_paths,
            *explanation_paths,
            paths["sqlite"],
        ],
        exports,
        media_release.packs,
        dataset_base_url=release_download_base(f"v{dataset_version}"),
        media_base_url=release_download_base(media_release.tag),
        report=report,
        coverage_checks=coverage,
        languages=languages,
        explanations=explanation_sets(dataset, explanations),
    )
    write_json(exports / FILE_NAMES["manifest"], manifest.model_dump(mode="json"))

    reports = settings.reports_dir
    write_validation_report(report, dataset, reports)
    write_category_counts(dataset, reports)
    write_extraction_report(dataset, extracted, copy_checks, reports)
    diff = write_dataset_diff(previous, dataset, reports)
    core = build_core_package(
        exports,
        release_root,
        dataset_version,
        extra=[REPO_ROOT / "DATA_NOTICE.md", reports / "validation-report.md"],
        translations=[p.name for p in translation_paths],
        explanations=[p.name for p in explanation_paths],
    )
    return BuildResult(manifest, report, diff, [media_release.directory, core.parent])

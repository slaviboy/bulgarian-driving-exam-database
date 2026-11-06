"""The exported explanations: ``explanation-bg.json``, explanations of the current Bulgarian content."""

from __future__ import annotations

from pathlib import Path

from question_bank.explanations import curated
from question_bank.fsutil import read_json, write_json
from question_bank.legal.corpus import LEGAL_DIR, load
from question_bank.models import (
    ExplainedQuestion,
    ExplanationFile,
    ExplanationInfo,
    ExplanationReference,
    ExplanationSet,
    LegalAct,
)
from question_bank.processor.builder import Dataset
from question_bank.processor.validation.validators import Issue

FILE_NAME = "explanation-bg.json"
METHOD = (
    "Written for this dataset with AI from the current text of the cited acts, then reviewed independently. "
    "Every quote is checked word for word against the act's published text when the dataset is built. "
    "Questions on technical or safety knowledge that no provision states are explained without a citation."
)
AUTHORITATIVE = "The official question bank of ИААА and the text of the law prevail."


def build_explanations(
    dataset: Dataset, curated_dir: Path = curated.CURATED_DIR, legal_dir: Path = LEGAL_DIR
) -> tuple[ExplanationFile | None, list[Issue], int]:
    """Explanations that match the current Bulgarian text and whose quotes are still in the acts.

    Errors: a quote that is no longer in the cited unit (the law changed; the explanation must be revised).
    Warnings: stale (the question changed) and obsolete entries — they are left out.
    Returns the export (None without explanations), the issues and the number of checked entries."""
    entries = curated.load(curated_dir)
    if not entries:
        return None, [], 0
    corpus = load(legal_dir)
    current = {q.id: q.content_hash for q in dataset.questions}
    issues: list[Issue] = []
    out: list[ExplainedQuestion] = []
    used_acts: set[str] = set()
    for question_id, entry in sorted(entries.items()):
        if question_id not in current:
            issues.append(Issue("explanations", "warning", f"{question_id}: no longer in the bank"))
            continue
        if entry["source_hash"] != current[question_id]:
            issues.append(Issue("explanations", "warning", f"{question_id}: stale (the question changed)"))
            continue
        broken = False
        for ref in entry["references"]:
            result = corpus.check(ref["act"], ref["unit"], ref["quote"])
            if not result.ok:
                issues.append(
                    Issue("explanations", "error", f"{question_id}: {result.message}", [question_id])
                )
                broken = True
            used_acts.add(ref["act"])
        if broken:
            continue
        out.append(
            ExplainedQuestion(
                id=question_id,
                source_hash=entry["source_hash"],
                kind=entry["kind"],
                text=entry["text"],
                references=[ExplanationReference(**ref) for ref in entry["references"]],
            )
        )
    acts = [
        LegalAct(
            id=act.id,
            short=act.short,
            title=act.title,
            consolidated_to=act.consolidated_to,
            source_url=act.source_url,
        )
        for act_id, act in corpus.acts.items()
        if act_id in used_acts
    ]
    export = ExplanationFile(
        dataset_version=dataset.dataset_version,
        explanation=ExplanationInfo(method=METHOD, authoritative=AUTHORITATIVE),
        acts=acts,
        questions=out,
    )
    return export, issues, len(entries)


def write_explanation_export(export: ExplanationFile | None, exports_dir: Path) -> list[Path]:
    path = exports_dir / FILE_NAME
    if export is None:
        path.unlink(missing_ok=True)
        return []
    write_json(path, export.model_dump(mode="json"))
    return [path]


def explanation_sets(dataset: Dataset, export: ExplanationFile | None) -> list[ExplanationSet]:
    if export is None:
        return []
    total = len(dataset.questions)
    count = len(export.questions)
    return [
        ExplanationSet(
            language="bg", file=FILE_NAME, questions=count, coverage=round(count / total, 4) if total else 0.0
        )
    ]


def validate_explanation_exports(paths: list[Path], schemas_dir: Path) -> list[Issue]:
    import jsonschema

    schema = read_json(schemas_dir / "explanation.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    issues = []
    for path in paths:
        for error in list(validator.iter_errors(read_json(path)))[:20]:
            location = "/".join(map(str, error.absolute_path))
            issues.append(Issue("json_schema", "error", f"{path.name}: {location}: {error.message}"))
    return issues

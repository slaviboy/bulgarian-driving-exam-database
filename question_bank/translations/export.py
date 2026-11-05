"""Translations of the current dataset: what is exported, what is stale, and the manifest's language list."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from question_bank.fsutil import read_json, write_json
from question_bank.models import (
    LanguageInfo,
    TranslatedAnswer,
    TranslatedLabel,
    TranslatedQuestion,
    TranslatedVariant,
    TranslationFile,
    TranslationInfo,
)
from question_bank.processor.builder import Dataset
from question_bank.processor.validation.validators import Issue
from question_bank.translations import curated, lint


@dataclass
class LanguageExport:
    language: lint.Language
    file: TranslationFile
    stale: int
    missing: int

    @property
    def path_name(self) -> str:
        return file_name(self.language.code)


def file_name(code: str) -> str:
    return f"translation-{code}.json"


def _label(
    store: curated.Curated, issues: list[Issue], group: str, item_id: str, source: object
) -> object | None:
    """The translated label, or None (with a warning) when it is missing or was made from another text."""
    entry = store.labels.get(group, {}).get(item_id)
    if entry is None:
        issues.append(Issue("translations", "warning", f"{store.language}: {group} {item_id} not translated"))
        return None
    if entry.get("source") != source:
        issues.append(Issue("translations", "warning", f"{store.language}: {group} {item_id} is stale"))
        return None
    return entry["text"]


def build_translations(
    dataset: Dataset, curated_dir: Path = curated.CURATED_DIR
) -> tuple[list[LanguageExport], list[Issue], int]:
    """Per curated language, the translations that match the current Bulgarian text.

    Errors: broken entries (empty text, wrong answer set). Warnings: stale (the Bulgarian changed), missing
    and obsolete entries — they are left out and consumers show the Bulgarian text instead.
    Returns the exports, the issues and the number of checked entries."""
    issues: list[Issue] = []
    exports: list[LanguageExport] = []
    checked = 0
    questions = {q.id: q for q in dataset.questions}
    for code in curated.languages(curated_dir):
        language = lint.LANGUAGES[code]
        store = curated.load(code, curated_dir)
        out_questions: list[TranslatedQuestion] = []
        stale = missing = 0
        for q in dataset.questions:
            checked += 1
            entry = store.questions.get(q.id)
            if entry is None:
                missing += 1
                continue
            if entry.get("source_hash") != q.content_hash:
                stale += 1
                issues.append(
                    Issue(
                        "translations", "warning", f"{code}: {q.id} is stale (the Bulgarian changed)", [q.id]
                    )
                )
                continue
            text_answers = [a for a in sorted(q.answers, key=lambda a: a.position) if a.text]
            answers = entry.get("answers") or {}
            if set(answers) != {a.id for a in text_answers}:
                issues.append(
                    Issue(
                        "translations", "error", f"{code}: {q.id} answers do not match the question", [q.id]
                    )
                )
                continue
            texts = [entry.get("text", ""), *answers.values()]
            if any(not isinstance(t, str) or not t.strip() for t in texts):
                issues.append(Issue("translations", "error", f"{code}: {q.id} has an empty text", [q.id]))
                continue
            out_questions.append(
                TranslatedQuestion(
                    id=q.id,
                    source_hash=q.content_hash,
                    text=curated.nfc(entry["text"]).strip(),
                    answers=[
                        TranslatedAnswer(id=a.id, text=curated.nfc(answers[a.id]).strip())
                        for a in text_answers
                    ],
                )
            )
        obsolete = sorted(set(store.questions) - set(questions))
        if obsolete:
            issues.append(
                Issue(
                    "translations",
                    "warning",
                    f"{code}: {len(obsolete)} translations of removed questions",
                    obsolete[:20],
                )
            )
        if missing:
            issues.append(Issue("translations", "warning", f"{code}: {missing} questions not translated yet"))

        categories = [
            TranslatedLabel(id=c.id, text=text)
            for c in dataset.categories
            if (text := _label(store, issues, "categories", c.id, c.name)) is not None
        ]
        variants = []
        for v in dataset.variants:
            source = {"description": v.description, "effective_note": v.effective_note}
            text = _label(store, issues, "variants", v.id, source)
            if text is not None:
                variants.append(
                    TranslatedVariant(
                        id=v.id, description=text["description"], effective_note=text["effective_note"]
                    )
                )
        topics = [
            TranslatedLabel(id=t.id, text=text)
            for t in dataset.topics
            if (text := _label(store, issues, "topics", t.id, t.name)) is not None
        ]
        exports.append(
            LanguageExport(
                language=language,
                file=TranslationFile(
                    dataset_version=dataset.dataset_version,
                    language=code,
                    language_tag=language.tag,
                    translation=TranslationInfo(method=curated.METHOD, authoritative=curated.AUTHORITATIVE),
                    categories=categories,
                    variants=variants,
                    topics=topics,
                    questions=out_questions,
                ),
                stale=stale,
                missing=missing,
            )
        )
    return exports, issues, checked


def write_translation_exports(exports: list[LanguageExport], exports_dir: Path) -> list[Path]:
    """Write ``translation-<code>.json`` per language and remove files of languages that are gone."""
    wanted = {e.path_name for e in exports}
    for old in exports_dir.glob("translation-*.json"):
        if old.name not in wanted:
            old.unlink()
    paths = []
    for e in exports:
        path = exports_dir / e.path_name
        write_json(path, e.file.model_dump(mode="json"))
        paths.append(path)
    return paths


def language_infos(dataset: Dataset, exports: list[LanguageExport]) -> list[LanguageInfo]:
    total = len(dataset.questions)
    bg = lint.LANGUAGES[lint.SOURCE_LANGUAGE]
    infos = [
        LanguageInfo(
            code=bg.code,
            tag=bg.tag,
            native_name=bg.native_name,
            english_name=bg.english_name,
            kind="source",
            status="official",
            file=None,
            questions=total,
            coverage=1.0,
        )
    ]
    for e in exports:
        count = len(e.file.questions)
        infos.append(
            LanguageInfo(
                code=e.language.code,
                tag=e.language.tag,
                native_name=e.language.native_name,
                english_name=e.language.english_name,
                kind="translation",
                status="unofficial",
                file=e.path_name,
                questions=count,
                coverage=round(count / total, 4) if total else 0.0,
            )
        )
    return infos


def validate_translation_exports(paths: list[Path], schemas_dir: Path) -> list[Issue]:
    import jsonschema

    schema = read_json(schemas_dir / "translation.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    issues = []
    for path in paths:
        for error in list(validator.iter_errors(read_json(path)))[:20]:
            location = "/".join(map(str, error.absolute_path))
            issues.append(Issue("json_schema", "error", f"{path.name}: {location}: {error.message}"))
    return issues

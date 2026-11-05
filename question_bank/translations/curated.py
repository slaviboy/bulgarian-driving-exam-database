"""The curated translations in ``data/translations/<lang>/`` and the merge of reviewed work packages.

Each language folder holds::

    questions.json   {"language", "questions": {question_id: {"source_hash", "text",
                                                               "answers": {answer_id: text}}}}
    labels.json      {"language", "categories"|"topics": {id: {"source", "text"}},
                      "variants": {id: {"source": {description, effective_note}, "text": {…}}}}
    glossary.json    the translator's terminology decisions
    notes.md         open questions and decisions; review.json — the reviewer's change log (when present)

``source_hash`` (questions) and ``source`` (labels) record which Bulgarian text was translated, so a new
official edition that changes a question makes its translation stale instead of silently wrong.
"""

from __future__ import annotations

import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from question_bank.config import REPO_ROOT
from question_bank.fsutil import read_json, write_json
from question_bank.translations import lint

CURATED_DIR = REPO_ROOT / "data" / "translations"
METHOD = (
    "AI translation (Claude) from the Bulgarian original with a shared style guide and terminology, "
    "automatic checks, and a second, independent AI review against the Bulgarian"
)
AUTHORITATIVE = "The Bulgarian original published by ИААА prevails; the translations are unofficial."
COPIED = ("glossary.json", "notes.md")


class MergeRefused(RuntimeError):
    """The work package still has lint errors or is incomplete."""


@dataclass
class Curated:
    language: str
    questions: dict[str, dict]
    labels: dict[str, dict]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def languages(curated_dir: Path = CURATED_DIR) -> list[str]:
    """Target languages that have curated question translations, in the contract's language order."""
    return [code for code in lint.TARGET_LANGUAGES if (curated_dir / code / "questions.json").exists()]


def load(code: str, curated_dir: Path = CURATED_DIR) -> Curated:
    folder = curated_dir / code
    questions = read_json(folder / "questions.json")
    labels_path = folder / "labels.json"
    labels = (
        read_json(labels_path) if labels_path.exists() else {"categories": {}, "variants": {}, "topics": {}}
    )
    return Curated(code, questions["questions"], labels)


def _numeric_id(question_id: str) -> tuple[int, str]:
    match = re.search(r"(\d+)$", question_id)
    return (int(match.group(1)) if match else 0, question_id)


def merge(work: Path, code: str, exports_dir: Path, curated_dir: Path = CURATED_DIR) -> dict:
    """Write the curated files of one language from a finished work package (``out/<code>/``)."""
    language = lint.LANGUAGES[code]
    out = work / "out" / code
    result = lint.Result()
    result.extend(lint.lint_labels(work, language))
    for part in lint.part_numbers(work):
        result.extend(lint.lint_part(work, language, part))
    lint.apply_exceptions(result, lint.load_exceptions(out))
    if result.errors:
        first = "; ".join(f.line() for f in result.errors[:5])
        raise MergeRefused(f"{code}: {len(result.errors)} lint errors, e.g. {first}")

    bank = {q["id"]: q for q in read_json(exports_dir / "questions.json")["questions"]}
    catalogue = read_json(exports_dir / "categories.json")
    questions: dict[str, dict] = {}
    for part in lint.part_numbers(work):
        translated = read_json(out / "questions" / f"part-{part:02d}.json")
        for qid, entry in translated.items():
            q = bank[qid]
            order = {a["id"]: a["position"] for a in q["answers"]}
            questions[qid] = {
                "source_hash": q["content_hash"],
                "text": nfc(entry["text"]),
                "answers": {
                    aid: nfc(entry["answers"][aid]) for aid in sorted(entry["answers"], key=order.get)
                },
            }
    if set(questions) != set(bank):
        raise MergeRefused(f"{code}: {len(set(bank) - set(questions))} questions are not translated")

    translated_labels = read_json(out / "labels.json")
    variants = [v for c in catalogue["categories"] for v in c["variants"]]
    labels = {
        "language": code,
        "categories": {
            c["id"]: {"source": c["name"], "text": nfc(translated_labels["categories"][c["id"]])}
            for c in catalogue["categories"]
        },
        "variants": {
            v["id"]: {
                "source": {"description": v["description"], "effective_note": v["effective_note"]},
                "text": {
                    "description": nfc(translated_labels["variants"][v["id"]]["description"]),
                    "effective_note": (
                        nfc(translated_labels["variants"][v["id"]]["effective_note"])
                        if v["effective_note"] is not None
                        else None
                    ),
                },
            }
            for v in variants
        },
        "topics": {
            t["id"]: {"source": t["name"], "text": nfc(translated_labels["topics"][t["id"]])}
            for t in catalogue["topics"]
        },
    }

    folder = curated_dir / code
    write_json(
        folder / "questions.json",
        {"language": code, "questions": {qid: questions[qid] for qid in sorted(questions, key=_numeric_id)}},
    )
    write_json(folder / "labels.json", labels)
    for name in COPIED:
        if (out / name).exists():
            shutil.copyfile(out / name, folder / name)
    review = work / "review" / code / "changes.json"
    if review.exists():
        shutil.copyfile(review, folder / "review.json")
    return {
        "language": code,
        "questions": len(questions),
        "answers": sum(len(q["answers"]) for q in questions.values()),
        "warnings": len(result.warnings),
        "accepted_exceptions": len(result.accepted),
    }

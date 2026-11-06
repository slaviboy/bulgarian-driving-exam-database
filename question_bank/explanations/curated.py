"""The curated explanations (data/explanations/bg/): merged from finished work packages, never edited by
hand.

``explanations.json`` maps question IDs to their explanation and the ``source_hash`` (content_hash of the
question that was explained); ``conflicts.json`` lists questions whose official answer seemed to contradict
the cited law (they are not explained until the maintainer decides); ``review.json`` keeps the reviewers'
logs.
"""

from __future__ import annotations

from pathlib import Path

from question_bank.config import REPO_ROOT
from question_bank.explanations.bank import load_bank
from question_bank.explanations.lint import check_all
from question_bank.fsutil import read_json, write_json
from question_bank.legal.corpus import Corpus

CURATED_DIR = REPO_ROOT / "data" / "explanations" / "bg"


class MergeRefused(Exception):
    pass


def _path(curated_dir: Path, name: str) -> Path:
    return curated_dir / name


def load(curated_dir: Path = CURATED_DIR) -> dict[str, dict]:
    path = _path(curated_dir, "explanations.json")
    return read_json(path)["explanations"] if path.exists() else {}


def load_conflicts(curated_dir: Path = CURATED_DIR) -> dict[str, dict]:
    path = _path(curated_dir, "conflicts.json")
    return read_json(path)["conflicts"] if path.exists() else {}


def _save(curated_dir: Path, explanations: dict[str, dict], conflicts: dict[str, dict]) -> None:
    curated_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        _path(curated_dir, "explanations.json"),
        {"language": "bg", "explanations": dict(sorted(explanations.items()))},
    )
    write_json(
        _path(curated_dir, "conflicts.json"), {"language": "bg", "conflicts": dict(sorted(conflicts.items()))}
    )


def merge(
    work: Path,
    exports_dir: Path,
    corpus: Corpus,
    parts: list[int] | None = None,
    curated_dir: Path = CURATED_DIR,
) -> dict[str, int]:
    """Merge finished parts of a work package. A part with lint errors or missing questions is refused."""
    bank, _, _ = load_bank(exports_dir)
    index = read_json(work / "source" / "index.json")
    wanted = parts or [p["part"] for p in index["parts"]]
    explanations, conflicts = load(curated_dir), load_conflicts(curated_dir)
    merged = new_conflicts = 0
    for part in wanted:
        source = read_json(work / "source" / f"part-{part:02d}.json")
        out_path = work / "out" / f"part-{part:02d}.json"
        if not out_path.exists():
            raise MergeRefused(f"part {part}: {out_path} does not exist")
        entries = read_json(out_path)["explanations"]
        expected = [q["id"] for q in source["questions"]]
        errors = [f for f in check_all(entries, bank, corpus, expected) if f.level == "error"]
        if errors:
            raise MergeRefused(f"part {part}: {len(errors)} errors, first: {errors[0]}")
        for question_id, entry in entries.items():
            source_hash = bank[question_id].content_hash
            if "conflict" in entry:
                conflicts[question_id] = {"source_hash": source_hash, "conflict": entry["conflict"].strip()}
                explanations.pop(question_id, None)
                new_conflicts += 1
                continue
            explanations[question_id] = {
                "source_hash": source_hash,
                "kind": entry["kind"],
                "text": entry["text"].strip(),
                "references": entry.get("references", []),
            }
            conflicts.pop(question_id, None)
            merged += 1
    _save(curated_dir, explanations, conflicts)
    return {
        "parts": len(wanted),
        "explanations": merged,
        "conflicts": new_conflicts,
        "total": len(explanations),
    }

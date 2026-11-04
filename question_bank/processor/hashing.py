"""`content_hash` and `content_fingerprint` exactly as specified in docs/data-contract.md §5.3."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from question_bank.processor.normalization.text import normalize_text


@dataclass(frozen=True)
class HashAnswer:
    position: int
    text: str | None
    media_sha256: str | None
    correct: bool


@dataclass(frozen=True)
class HashMedia:
    role: str
    position: int
    sha256: str


def canonical_json(value: Any) -> str:
    """Sorted keys, no whitespace, non-ASCII written as-is."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _norm(value: str | None) -> str | None:
    return normalize_text(value) if value is not None else None


def content_hash(text: str, answers: Iterable[HashAnswer], media: Iterable[HashMedia]) -> str:
    payload = {
        "text": _norm(text),
        "answers": [
            {"position": a.position, "text": _norm(a.text), "media": a.media_sha256, "correct": a.correct}
            for a in sorted(answers, key=lambda a: a.position)
        ],
        "media": [
            {"role": m.role, "sha256": m.sha256} for m in sorted(media, key=lambda m: (m.role, m.position))
        ],
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def content_fingerprint(
    question_hashes: dict[str, str], assignments: list[Any], exam_configs: list[Any]
) -> str:
    """Build-time independent fingerprint of the whole dataset content."""
    digest = hashlib.sha256()
    for question_id in sorted(question_hashes):
        digest.update(f"{question_id}:{question_hashes[question_id]}\n".encode())
    digest.update(canonical_json(assignments).encode("utf-8"))
    digest.update(canonical_json(exam_configs).encode("utf-8"))
    return digest.hexdigest()

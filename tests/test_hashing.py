from __future__ import annotations

import json
from pathlib import Path

import pytest

from question_bank.processor.hashing import HashAnswer, HashMedia, canonical_json, content_hash

VECTORS = json.loads(
    (Path(__file__).parent / "data" / "content_hash_vectors.json").read_text(encoding="utf-8")
)


def _hash(vector: dict) -> str:
    return content_hash(
        vector["text"],
        [HashAnswer(a["position"], a["text"], a["media_sha256"], a["correct"]) for a in vector["answers"]],
        [HashMedia(m["role"], m["position"], m["sha256"]) for m in vector["media"]],
    )


@pytest.mark.parametrize("vector", VECTORS["vectors"], ids=lambda v: v["name"])
def test_published_vectors(vector):
    assert _hash(vector) == vector["expected_content_hash"]


def test_hash_ignores_whitespace_and_input_order_but_not_content():
    base = VECTORS["vectors"][0]
    spaced = {**base, "text": "  Съединителят   е\nпредназначен: "}
    assert _hash(spaced) == base["expected_content_hash"]
    reordered = {**base, "answers": list(reversed(base["answers"]))}
    assert _hash(reordered) == base["expected_content_hash"]
    flipped = {**base, "answers": [{**a, "correct": not a["correct"]} for a in base["answers"]]}
    assert _hash(flipped) != base["expected_content_hash"]


def test_canonical_json_is_compact_sorted_and_keeps_cyrillic():
    assert canonical_json({"b": 1, "a": "ж"}) == '{"a":"ж","b":1}'

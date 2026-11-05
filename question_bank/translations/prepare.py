"""Work packages for translators (``qb translations prepare``).

The question bank is split into parts of about 100 questions, grouped by subject (section number, then
topic) and, inside a topic, by text, so that related and identical questions are translated next to each
other. Each question carries what a translator needs to keep the meaning exact: its correct answers, whether
it has pictures (with their file names, to look at when the text alone is ambiguous) or a video, and the
other questions with the same text.
"""

from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from pathlib import Path

from question_bank.fsutil import read_json, write_json, write_text

DEFAULT_PARTS = 25


def _nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def _split(items: list, parts: int) -> list[list]:
    size, extra = divmod(len(items), parts)
    out, start = [], 0
    for i in range(parts):
        end = start + size + (1 if i < extra else 0)
        out.append(items[start:end])
        start = end
    return out


def _write_part(path: Path, header: dict, questions: list[dict]) -> None:
    """Valid JSON with one question per line: compact for the translators, still easy to read and diff."""
    lines = ["{"]
    for key, value in header.items():
        lines.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)},")
    lines.append('  "questions": [')
    for i, q in enumerate(questions):
        comma = "," if i < len(questions) - 1 else ""
        lines.append("    " + json.dumps(q, ensure_ascii=False) + comma)
    lines.append("  ]")
    lines.append("}")
    write_text(path, "\n".join(lines) + "\n")


def prepare(exports_dir: Path, media_dir: Path, out: Path, *, parts: int = DEFAULT_PARTS) -> dict:
    questions = read_json(exports_dir / "questions.json")["questions"]
    catalogue = read_json(exports_dir / "categories.json")
    topics = {t["id"]: t["name"] for t in catalogue["topics"]}
    variants = [v for c in catalogue["categories"] for v in c["variants"]]
    variant_position = {v["id"]: v["position"] for v in variants}
    sections = {s["id"]: s for v in variants for s in v["sections"]}

    # A topic's place: the lowest section number it is used with, so subjects stay together.
    topic_rank: dict[str, tuple[int, str]] = {}
    for s in sections.values():
        rank = (s["number"], s["topic_id"])
        topic_rank[s["topic_id"]] = min(topic_rank.get(s["topic_id"], rank), rank)

    def primary_topic(q: dict) -> str:
        first = min(
            q["assignments"],
            key=lambda a: (sections[a["section_id"]]["number"], variant_position[a["variant_id"]]),
        )
        return sections[first["section_id"]]["topic_id"]

    same_text: dict[str, list[str]] = defaultdict(list)
    for q in questions:
        same_text[_nfc(q["text"])].append(q["id"])

    ordered = sorted(
        questions,
        key=lambda q: (topic_rank[primary_topic(q)], _nfc(q["text"]).casefold(), int(q["original_id"])),
    )
    picture_dir = (media_dir / "images").resolve()
    ranked_topics = sorted(topic_rank, key=lambda t: topic_rank[t])
    code = {t: f"T{i:02d}" for i, t in enumerate(ranked_topics, start=1)}
    index = {
        "parts": [],
        "questions": len(questions),
        "text_answers": 0,
        "picture_dir": str(picture_dir),
        "topics": {code[t]: {"id": t, "title": topics[t]} for t in ranked_topics},
    }
    for number, chunk in enumerate(_split(ordered, parts), start=1):
        entries = []
        for q in chunk:
            topic = primary_topic(q)
            entry: dict = {"id": q["id"], "topic": code[topic], "text": q["text"]}
            pictures = [
                m["media_id"] for m in sorted(q["media"], key=lambda m: m["position"]) if m["role"] == "image"
            ]
            if pictures:
                entry["pictures"] = pictures
            if any(m["role"] == "video" for m in q["media"]):
                entry["video"] = True
            answers = []
            for a in sorted(q["answers"], key=lambda a: a["position"]):
                if a["text"]:
                    answers.append({"id": a["id"], "text": a["text"], "correct": a["is_correct"]})
                else:
                    answers.append({"id": a["id"], "picture": a["media_id"], "correct": a["is_correct"]})
            entry["answers"] = answers
            others = [i for i in same_text[_nfc(q["text"])] if i != q["id"]]
            if others:
                entry["same_text"] = others[:5]
            entries.append(entry)
        part_topics = [t for t in ranked_topics if code[t] in {e["topic"] for e in entries}]
        _write_part(
            out / "source" / "questions" / f"part-{number:02d}.json",
            {
                "part": number,
                "parts": parts,
                "picture_dir": str(picture_dir),
                "topics": {code[t]: topics[t] for t in part_topics},
            },
            entries,
        )
        text_answers = sum(1 for e in entries for a in e["answers"] if "text" in a)
        index["text_answers"] += text_answers
        index["parts"].append(
            {
                "part": number,
                "questions": len(entries),
                "text_answers": text_answers,
                "topics": [code[t] for t in part_topics],
            }
        )

    labels = {
        "categories": {
            c["id"]: c["name"] for c in sorted(catalogue["categories"], key=lambda c: c["position"])
        },
        "variants": {
            v["id"]: {"description": v["description"], "effective_note": v["effective_note"]}
            for v in sorted(variants, key=lambda v: v["position"])
        },
        "topics": {t: topics[t] for t in sorted(topics, key=lambda t: topic_rank.get(t, (99, t)))},
    }
    write_json(out / "source" / "labels.bg.json", labels)
    write_json(out / "source" / "index.json", index)
    return index

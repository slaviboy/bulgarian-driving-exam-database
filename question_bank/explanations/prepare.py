"""Work packages for the explanation writers: the questions of a category in parts of about 100.

``<work>/source/part-NN.json`` holds, per question, the text, the answers with their letters and correct
markers, and absolute paths of the pictures (writers must look at them). ``<work>/source/index.json`` lists
the parts. Writers put their result in ``<work>/out/part-NN.json`` as ``{"explanations": {id: entry}}`` (see
``question_bank.explanations.lint``) and check it with ``qb explanations lint --work <work> --part N``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from question_bank.explanations import curated
from question_bank.explanations.bank import BankQuestion, load_bank
from question_bank.fsutil import read_json, write_json


def _topic_order(exports_dir: Path, category: str) -> list[str]:
    """Topics in the order of the category's sections (the first variant that has them)."""
    order: list[str] = []
    for c in read_json(exports_dir / "categories.json")["categories"]:
        if c["id"] != category:
            continue
        for v in c["variants"]:
            for s in sorted(v["sections"], key=lambda s: s["position"]):
                if s["topic_id"] not in order:
                    order.append(s["topic_id"])
    return order


def _question_json(q: BankQuestion, media_dir: Path, media: dict[str, str], topic: str) -> dict:
    def picture(media_id: str | None) -> str | None:
        return str((media_dir / media[media_id]).resolve()) if media_id else None

    return {
        "id": q.id,
        "original_id": q.original_id,
        "content_hash": q.content_hash,
        "topic": topic,
        "text": q.text,
        "correct_count": q.correct_count,
        "answers": [
            {"letter": a.letter, "text": a.text, "picture": picture(a.media_id), "correct": a.correct}
            for a in q.answers
        ],
        "pictures": [picture(m) for m in q.image_ids],
        "video": q.has_video,
    }


def prepare(
    exports_dir: Path,
    media_dir: Path,
    out: Path,
    category: str,
    part_size: int = 100,
    redo: bool = False,
    curated_dir: Path = curated.CURATED_DIR,
    only: list[str] | None = None,
) -> dict:
    bank, topic_names, media = load_bank(exports_dir)
    done = {qid: e["source_hash"] for qid, e in curated.load(curated_dir).items()}
    done.update({qid: e["source_hash"] for qid, e in curated.load_conflicts(curated_dir).items()})
    order = {topic: i for i, topic in enumerate(_topic_order(exports_dir, category))}
    selected = [
        q
        for q in bank.values()
        if category in q.categories
        and (only is None or q.original_id in only or q.id in only)
        and (redo or done.get(q.id) != q.content_hash)
    ]
    selected.sort(key=lambda q: (order.get(q.topic_by_category[category], 999), int(q.original_id)))

    source = out / "source"
    source.mkdir(parents=True, exist_ok=True)
    (out / "out").mkdir(exist_ok=True)
    parts = []
    for start in range(0, len(selected), part_size):
        chunk = selected[start : start + part_size]
        number = len(parts) + 1
        topics = []
        questions = []
        for q in chunk:
            topic = topic_names[q.topic_by_category[category]]
            if topic not in topics:
                topics.append(topic)
            questions.append(_question_json(q, media_dir, media, topic))
        write_json(
            source / f"part-{number:02d}.json", {"part": number, "category": category, "questions": questions}
        )
        parts.append({"part": number, "questions": len(chunk), "topics": topics})
    index = {
        "category": category,
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "questions": len(selected),
        "parts": parts,
    }
    write_json(source / "index.json", index)
    return index

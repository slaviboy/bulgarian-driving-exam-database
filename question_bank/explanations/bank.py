"""The exported question bank as the explanation tools need it: text, answers, pictures, topics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from question_bank.fsutil import read_json

LETTERS = "абвгде"


@dataclass(frozen=True)
class BankAnswer:
    id: str
    letter: str
    text: str | None
    media_id: str | None
    correct: bool


@dataclass(frozen=True)
class BankQuestion:
    id: str
    original_id: str
    text: str
    content_hash: str
    correct_count: int
    answers: list[BankAnswer]
    image_ids: list[str]
    has_video: bool
    categories: list[str]
    topics: list[str]
    # The topic of the question's first section in each category (sections differ between variants).
    topic_by_category: dict[str, str]

    @property
    def correct_answers(self) -> list[BankAnswer]:
        return [a for a in self.answers if a.correct]


def load_bank(exports_dir: Path) -> tuple[dict[str, BankQuestion], dict[str, str], dict[str, str]]:
    """Questions by ID, topic names by ID and media paths (relative to the media folder) by media ID."""
    questions_file = read_json(exports_dir / "questions.json")
    categories_file = read_json(exports_dir / "categories.json")
    topic_names = {t["id"]: t["name"] for t in categories_file["topics"]}
    section_topic = {
        s["id"]: s["topic_id"]
        for c in categories_file["categories"]
        for v in c["variants"]
        for s in v["sections"]
    }
    media = {m["id"]: m["relative_path"] for m in questions_file["media"]}
    bank = {}
    for q in questions_file["questions"]:
        answers = [
            BankAnswer(a["id"], LETTERS[a["position"] - 1], a.get("text"), a.get("media_id"), a["is_correct"])
            for a in sorted(q["answers"], key=lambda a: a["position"])
        ]
        images = [
            m["media_id"] for m in sorted(q["media"], key=lambda m: m["position"]) if m["role"] != "video"
        ]
        topics: list[str] = []
        topic_by_category: dict[str, str] = {}
        for assignment in q["assignments"]:
            topic = section_topic[assignment["section_id"]]
            if topic not in topics:
                topics.append(topic)
            topic_by_category.setdefault(assignment["category_id"], topic)
        bank[q["id"]] = BankQuestion(
            id=q["id"],
            original_id=q["original_id"],
            text=q["text"],
            content_hash=q["content_hash"],
            correct_count=q["correct_count"],
            answers=answers,
            image_ids=images,
            has_video=any(m["role"] == "video" for m in q["media"]),
            categories=sorted({a["category_id"] for a in q["assignments"]}),
            topics=topics,
            topic_by_category=topic_by_category,
        )
    return bank, topic_names, media

"""Build the canonical dataset (data contract v1) from the parsed official files, the prepared media and
the curated exam rules. Pure transformation — no network, no files written."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from question_bank.exporter.media import PreparedMedia
from question_bank.extractor.parsers.official_html import ParsedQuestion
from question_bank.extractor.pipeline import ExtractedFile
from question_bank.models import (
    Answer,
    Assignment,
    Category,
    Evidence,
    ExamConfig,
    Licensing,
    Media,
    Question,
    QuestionMediaRef,
    Section,
    SectionQuota,
    Source,
    Topic,
    Variant,
)
from question_bank.processor.hashing import HashAnswer, HashMedia, content_hash
from question_bank.processor.normalization import ids
from question_bank.processor.normalization.text import split_effective_note

OBSERVED_PARAMETERS = "брой въпроси, общ брой точки, продължителност, разпределение по точки, видео"
ATTRIBUTION = (
    "Източник: Изпълнителна агенция „Автомобилна администрация“ — "
    "https://public-eis.rta.government.bg/exam-questions/"
)
LICENSING = Licensing(
    attribution=ATTRIBUTION,
    license="none granted by source",
    redistribution_status="published_by_maintainer_decision",
    notice_url="https://github.com/slaviboy/bulgarian-driving-exam-database/blob/main/DATA_NOTICE.md",
)


class DeduplicationConflict(ValueError):
    """The same ИААА question ID has different content in two variant files."""


@dataclass
class Dataset:
    dataset_version: str
    source_edition: str
    rules_version: str
    sources: list[Source]
    categories: list[Category]
    topics: list[Topic]
    media: list[Media]
    questions: list[Question]
    exam_configs: list[ExamConfig]
    duplicate_content: list[list[str]] = field(default_factory=list)  # question IDs sharing one content_hash
    duplicate_media_names: dict[str, list[str]] = field(default_factory=dict)

    @property
    def variants(self) -> list[Variant]:
        return [v for c in self.categories for v in c.variants]

    @property
    def sections(self) -> list[Section]:
        return [s for v in self.variants for s in v.sections]


def _content_signature(q: ParsedQuestion) -> tuple:
    return (
        q.text,
        tuple((a.position, a.text, a.image, a.correct) for a in q.answers),
        q.images,
        q.videos,
    )


def _exam_config(
    rule: dict[str, Any],
    defaults: dict[str, Any],
    documents: dict[str, Any],
    rules_version: str,
    variant_sections: set[int],
) -> ExamConfig:
    quotas = rule.get("section_quotas")
    observed = bool(rule.get("observed"))
    evidence = [
        Evidence(
            kind="law",
            document=documents["N38"]["document"],
            reference=rule["law"],
            url=documents["N38"]["url"],
        ),
        Evidence(
            kind="methodology",
            document=documents["MET"]["document"],
            reference=rule["methodology"],
            url=documents["MET"]["url"],
        ),
    ]
    if observed:
        evidence.append(
            Evidence(
                kind="observation",
                document=documents["OBS"]["document"],
                reference=OBSERVED_PARAMETERS,
                url=documents["OBS"]["url"],
            )
        )
    verification = {
        "question_count": "law+observation" if observed else "law",
        "max_points": "law+observation" if observed else "law",
        "pass_points": "law" if rule["pass_points_basis"] == "law" else "category-rule",
        "duration_minutes": "law+observation" if observed else "law",
        "section_quotas": rule["section_quotas_basis"] if quotas else "unverified",
        "points_mix": rule["points_mix_basis"],
        "video_questions": "methodology+observation" if observed else "methodology",
        "scoring": "methodology",
        "max_video_plays": "observation",
    }
    if quotas and not set(int(k) for k in quotas) <= variant_sections:
        raise ValueError(f"{rule['variant_id']}: quotas reference sections the variant does not have")
    return ExamConfig(
        id=ids.exam_config_id(rule["variant_id"], rules_version),
        variant_id=rule["variant_id"],
        status="official",
        question_count=rule["question_count"],
        max_points=rule["max_points"],
        pass_points=rule["pass_points"],
        duration_minutes=rule["duration_minutes"],
        video_questions=rule["video_questions"],
        max_video_plays=defaults["max_video_plays"],
        scoring=defaults["scoring"],
        show_correct_count=defaults["show_correct_count"],
        section_quotas=(
            [
                SectionQuota(section_number=int(k), count=v)
                for k, v in sorted(quotas.items(), key=lambda kv: int(kv[0]))
            ]
            if quotas
            else None
        ),
        points_mix=rule.get("points_mix"),
        verification=verification,
        evidence=evidence,
        notes=list(rule.get("notes", [])),
    )


def build_dataset(
    extracted: list[ExtractedFile],
    prepared: PreparedMedia,
    exam_rules: dict[str, Any],
    *,
    dataset_version: str,
    retrieved_at: str | None = None,
) -> Dataset:
    if not extracted:
        raise ValueError("nothing extracted")
    editions = {e.source.edition for e in extracted}
    if len(editions) != 1:
        raise ValueError(f"mixed editions in one build: {sorted(editions)}")
    source_edition = editions.pop()

    source = Source(
        id=ids.SOURCE_ID,
        name="ИААА — Масив от изпитни въпроси за теоретичните изпити",
        source_url="https://public-eis.rta.government.bg/exam-questions/",
        attribution=ATTRIBUTION,
        license=LICENSING.license,
        redistribution_status=LICENSING.redistribution_status,
        retrieved_at=retrieved_at,
    )

    # ------------------------------------------------------------------ questions (canonical)
    canonical: dict[str, ParsedQuestion] = {}
    first_seen: dict[str, int] = {}
    for item in sorted(extracted, key=lambda e: e.source.order):
        for q in item.parsed.questions:
            if q.original_id not in canonical:
                canonical[q.original_id] = q
                first_seen[q.original_id] = item.source.order
            elif _content_signature(canonical[q.original_id]) != _content_signature(q):
                first = first_seen[q.original_id]
                raise DeduplicationConflict(
                    f"question {q.original_id}: file #{first} and #{item.source.order} differ"
                )

    # ------------------------------------------------------------------ categories, variants, sections
    topics: dict[str, Topic] = {}
    categories: dict[str, dict[str, Any]] = {}
    assignments: dict[str, list[Assignment]] = defaultdict(list)
    variant_sections: dict[str, set[int]] = {}
    for item in sorted(extracted, key=lambda e: e.source.order):
        parsed = item.parsed
        category = ids.category_id(parsed.category_label)
        variant = ids.variant_id(category, parsed.description)
        description, note = split_effective_note(parsed.description)
        per_section = defaultdict(int)
        for q in parsed.questions:
            per_section[q.section_number] += 1
        sections = []
        for s in parsed.sections:
            title = ids.section_title_without_number(s.title)
            topic = ids.topic_id(s.title)
            topics.setdefault(topic, Topic(id=topic, name=title))
            sections.append(
                Section(
                    id=ids.section_id(variant, s.number),
                    variant_id=variant,
                    number=s.number,
                    name=s.title,
                    topic_id=topic,
                    position=s.position,
                    question_count=per_section[s.number],
                )
            )
        variant_sections[variant] = {s.number for s in parsed.sections}
        entry = categories.setdefault(
            category, {"name": parsed.category_label, "position": len(categories) + 1, "variants": []}
        )
        if any(v.id == variant for v in entry["variants"]):
            raise ValueError(f"duplicate variant id {variant}")
        entry["variants"].append(
            Variant(
                id=variant,
                category_id=category,
                title=parsed.title,
                description=description,
                effective_note=note,
                source_url=item.source.url,
                source_sha256=item.source.sha256,
                source_edition=item.source.edition,
                position=item.source.order,
                question_count=len(parsed.questions),
                sections=sections,
            )
        )
        for q in parsed.questions:
            assignments[ids.question_id(q.original_id)].append(
                Assignment(
                    variant_id=variant,
                    category_id=category,
                    section_id=ids.section_id(variant, q.section_number),
                    points=q.points,
                    position=q.position,
                )
            )

    # ------------------------------------------------------------------ question records
    questions: list[Question] = []
    by_hash: dict[str, list[str]] = defaultdict(list)
    for original_id in sorted(canonical, key=int):
        q = canonical[original_id]
        qid = ids.question_id(original_id)
        media_refs = [
            QuestionMediaRef(media_id=prepared.by_name[name], role="image", position=i)
            for i, name in enumerate(q.images, start=1)
        ] + [
            QuestionMediaRef(media_id=prepared.by_name[name], role="video", position=i)
            for i, name in enumerate(q.videos, start=1)
        ]
        answers = [
            Answer(
                id=ids.answer_id(qid, a.position),
                position=a.position,
                text=a.text,
                media_id=prepared.by_name[a.image] if a.image else None,
                is_correct=a.correct,
            )
            for a in q.answers
        ]
        has_text = [a.text is not None for a in answers]
        answer_format = "text" if all(has_text) else ("image" if not any(has_text) else "mixed")
        digest = content_hash(
            q.text,
            [
                HashAnswer(
                    a.position,
                    a.text,
                    prepared.media[a.media_id].sha256 if a.media_id else None,
                    a.is_correct,
                )
                for a in answers
            ],
            [HashMedia(m.role, m.position, prepared.media[m.media_id].sha256) for m in media_refs],
        )
        by_hash[digest].append(qid)
        questions.append(
            Question(
                id=qid,
                original_id=original_id,
                source_id=ids.SOURCE_ID,
                text=q.text,
                explanation=None,
                answer_format=answer_format,
                correct_count=sum(1 for a in answers if a.is_correct),
                content_hash=digest,
                media=media_refs,
                answers=answers,
                assignments=sorted(assignments[qid], key=lambda a: (a.variant_id, a.position)),
            )
        )

    # ------------------------------------------------------------------ exam configs
    rules_version = exam_rules["rules_version"]
    known_variants = {v.id for c in categories.values() for v in c["variants"]}
    configs = []
    for rule in exam_rules["variants"]:
        if rule["variant_id"] not in known_variants:
            raise ValueError(f"exam rule for unknown variant {rule['variant_id']}")
        configs.append(
            _exam_config(
                rule,
                exam_rules["defaults"],
                exam_rules["documents"],
                rules_version,
                variant_sections[rule["variant_id"]],
            )
        )

    used_media = {m.media_id for q in questions for m in q.media} | {
        a.media_id for q in questions for a in q.answers if a.media_id
    }
    return Dataset(
        dataset_version=dataset_version,
        source_edition=source_edition,
        rules_version=rules_version,
        sources=[source],
        categories=[
            Category(
                id=cid,
                name=c["name"],
                description=None,
                source_id=ids.SOURCE_ID,
                position=c["position"],
                variants=c["variants"],
            )
            for cid, c in categories.items()
        ],
        topics=sorted(topics.values(), key=lambda t: t.id),
        media=[prepared.media[m] for m in sorted(used_media)],
        questions=questions,
        exam_configs=configs,
        duplicate_content=[sorted(v) for v in by_hash.values() if len(v) > 1],
        duplicate_media_names=prepared.duplicate_names,
    )

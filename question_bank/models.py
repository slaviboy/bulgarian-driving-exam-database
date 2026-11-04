"""Pydantic models of the data contract (docs/data-contract.md). The JSON Schemas in contract/schemas are
generated from these models (`qb schemas`), so the models are the single source of truth."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1

Id = str
Sha256 = str


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


# ---------------------------------------------------------------------------------------- sources


class Licensing(_Model):
    attribution: str
    license: str
    redistribution_status: Literal["published_by_maintainer_decision", "permitted", "restricted", "unknown"]
    notice_url: str


class Source(_Model):
    id: Id
    name: str
    source_url: str
    attribution: str
    license: str
    redistribution_status: str
    retrieved_at: str | None = None


# ------------------------------------------------------------------------------- categories.json


class Topic(_Model):
    id: Id
    name: str


class Section(_Model):
    id: Id
    variant_id: Id
    number: int = Field(ge=1)
    name: str = Field(description="Full official title, e.g. 'Раздел 1. ОБЩИ СВЕДЕНИЯ ЗА АВТОМОБИЛА'")
    topic_id: Id
    position: int = Field(ge=1)
    question_count: int = Field(ge=0)


class Variant(_Model):
    id: Id
    category_id: Id
    title: str = Field(description="Official <h1> of the variant file")
    description: str
    effective_note: str | None
    source_url: str
    source_sha256: Sha256
    source_edition: str
    position: int = Field(ge=1)
    question_count: int = Field(ge=0)
    sections: list[Section]


class Category(_Model):
    id: Id
    name: str = Field(description="Official label, e.g. 'C+E', 'D (103)', 'Ттм'")
    description: str | None = None
    source_id: Id
    position: int = Field(ge=1)
    variants: list[Variant]


class CategoriesFile(_Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    sources: list[Source]
    categories: list[Category]
    topics: list[Topic]


# -------------------------------------------------------------------------------- questions.json


class MediaDerivative(_Model):
    format: Literal["webp"]
    relative_path: str
    mime_type: str
    bytes: int
    width: int | None
    height: int | None
    sha256: Sha256


class Media(_Model):
    id: Id
    kind: Literal["image", "video"]
    original_name: str
    relative_path: str
    mime_type: str
    bytes: int
    width: int | None
    height: int | None
    sha256: Sha256
    source_url: str
    source_id: Id
    derivatives: list[MediaDerivative] = Field(default_factory=list)


class QuestionMediaRef(_Model):
    media_id: Id
    role: Literal["image", "video"]
    position: int = Field(ge=1)


class Answer(_Model):
    id: Id
    position: int = Field(ge=1)
    text: str | None
    media_id: Id | None
    is_correct: bool


class Assignment(_Model):
    variant_id: Id
    category_id: Id
    section_id: Id
    points: int = Field(ge=1, le=3)
    position: int = Field(ge=1)


class Question(_Model):
    id: Id
    original_id: str
    source_id: Id
    text: str
    explanation: str | None = None
    answer_format: Literal["text", "image", "mixed"]
    correct_count: int = Field(ge=0)
    content_hash: Sha256
    media: list[QuestionMediaRef]
    answers: list[Answer]
    assignments: list[Assignment]


class QuestionsFile(_Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    media: list[Media]
    questions: list[Question]


# ----------------------------------------------------------------------------- exam-configs.json


class SectionQuota(_Model):
    section_number: int = Field(ge=1)
    count: int = Field(ge=0)


class Evidence(_Model):
    kind: Literal["law", "methodology", "observation"]
    document: str
    reference: str
    url: str | None = None


class ExamConfig(_Model):
    id: Id
    variant_id: Id
    status: Literal["official", "unofficial"]
    question_count: int = Field(ge=1)
    max_points: int = Field(ge=1)
    pass_points: int = Field(ge=1)
    duration_minutes: int = Field(ge=1)
    video_questions: int = Field(ge=0)
    max_video_plays: int | None
    scoring: Literal["all_or_nothing"]
    show_correct_count: bool
    section_quotas: list[SectionQuota] | None
    points_mix: dict[str, int] | None = Field(description="number of questions worth '1', '2', '3' points")
    verification: dict[str, str] = Field(description="parameter → basis (law, methodology, observation, …)")
    evidence: list[Evidence]
    notes: list[str] = Field(default_factory=list)


class ExamConfigsFile(_Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    rules_version: str
    configs: list[ExamConfig]


# ---------------------------------------------------------------------------------- manifest.json


class Generator(_Model):
    name: str
    version: str
    git_commit: str | None


class SourceSnapshot(_Model):
    url: str
    etag: str | None
    last_modified: str | None
    sha256: Sha256
    bytes: int


class ManifestFile(_Model):
    path: str
    bytes: int
    sha256: Sha256
    media_type: str


class MediaPack(_Model):
    id: str
    kind: Literal["images-webp", "images-original", "videos"]
    url: str
    bytes: int
    sha256: Sha256
    file_count: int


class CompletenessCheck(_Model):
    name: str
    passed: bool
    detail: str


class Completeness(_Model):
    status: Literal["complete", "partial"]
    checks: list[CompletenessCheck]


class Manifest(_Model):
    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    source_edition: str
    rules_version: str
    built_at: str
    generator: Generator
    content_fingerprint: Sha256
    sources: list[Source]
    source_snapshot: list[SourceSnapshot]
    counts: dict[str, int]
    category_counts: dict[str, dict[str, int]]
    variant_counts: dict[str, int]
    dataset_base_url: str = Field(description="release download URL that `files[].path` is relative to")
    files: list[ManifestFile]
    media_base_url: str = Field(description="media release download URL; single videos are '<media id>.mp4'")
    media_packs: list[MediaPack]
    licensing: Licensing
    completeness: Completeness


SCHEMA_MODELS = {
    "categories": CategoriesFile,
    "questions": QuestionsFile,
    "exam-configs": ExamConfigsFile,
    "manifest": Manifest,
}

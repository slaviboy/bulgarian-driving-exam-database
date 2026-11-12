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
    format: Literal["webp", "svg"]
    relative_path: str
    mime_type: str
    bytes: int
    width: int | None
    height: int | None
    sha256: Sha256
    process: list[str] = Field(
        default_factory=list,
        description="how the file was made from the original: stamp-removed, enlarged-2x, vector-commons, "
        "vector-traced, vector-drawn (empty: format conversion only)",
    )


class MediaCredit(_Model):
    """A third-party drawing used in a derivative (Wikimedia Commons), with what its licence requires."""

    title: str
    author: str
    license: str
    license_url: str | None = None
    page: str
    sha1: str


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
    aliases: list[str] = Field(
        default_factory=list, description="other official file names with byte-identical content"
    )
    derivatives: list[MediaDerivative] = Field(default_factory=list)
    credits: list[MediaCredit] = Field(
        default_factory=list, description="third-party drawings in the derivatives (attribution required)"
    )


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


# --------------------------------------------------------------------- translation-<language>.json


class TranslatedAnswer(_Model):
    id: Id
    text: str


class TranslatedQuestion(_Model):
    id: Id
    source_hash: Sha256 = Field(description="content_hash of the Bulgarian question that was translated")
    text: str
    answers: list[TranslatedAnswer] = Field(description="every answer that has text, in position order")


class TranslatedLabel(_Model):
    id: Id
    text: str


class TranslatedVariant(_Model):
    id: Id
    description: str
    effective_note: str | None


class TranslationInfo(_Model):
    status: Literal["unofficial"] = "unofficial"
    method: str = Field(description="how the translation was made and reviewed")
    authoritative: str = Field(description="which text prevails when they differ")


class TranslationFile(_Model):
    """One language. Only translations of the current Bulgarian content are exported: a question whose
    content_hash changed is left out until it is translated again, and consumers show the Bulgarian text."""

    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    language: str = Field(description="ISO 639-1 code, e.g. 'en'")
    language_tag: str = Field(description="BCP 47 tag of the wording, e.g. 'pt-PT'")
    source_language: Literal["bg"] = "bg"
    translation: TranslationInfo
    categories: list[TranslatedLabel]
    variants: list[TranslatedVariant]
    topics: list[TranslatedLabel]
    questions: list[TranslatedQuestion]


# ------------------------------------------------------------------------- explanation-bg.json


class ExplanationReference(_Model):
    act: str = Field(description="id of an act in `acts[]`")
    unit: str = Field(description="article, paragraph and point, e.g. 'чл. 50, ал. 1' or '§ 6, т. 21'")
    quote: str = Field(description="the words of the act the explanation rests on, word for word")


class ExplainedQuestion(_Model):
    id: Id
    source_hash: Sha256 = Field(description="content_hash of the Bulgarian question that was explained")
    kind: Literal["law", "general"] = Field(
        description="law: rests on the cited provisions; general: technical or safety knowledge that no "
        "provision of the cited acts states"
    )
    text: str = Field(description="why the correct answers are correct, in Bulgarian")
    references: list[ExplanationReference] = Field(description="empty for kind 'general'")


class LegalAct(_Model):
    id: str
    short: str = Field(description="short name, e.g. 'ЗДвП'")
    title: str
    consolidated_to: str | None = Field(description="the last State Gazette issue in the quoted text")
    source_url: str = Field(description="the government file the text was taken from")


class ExplanationInfo(_Model):
    status: Literal["unofficial"] = "unofficial"
    method: str = Field(description="how the explanations were written and checked")
    authoritative: str = Field(description="what prevails when an explanation differs")


class ExplanationFile(_Model):
    """Explanations of why the correct answers are correct, in Bulgarian only. Only explanations of the
    current Bulgarian content are exported: a question whose content_hash changed is left out until it is
    explained again."""

    schema_version: Literal[1] = SCHEMA_VERSION
    dataset_version: str
    language: Literal["bg"] = "bg"
    language_tag: Literal["bg-BG"] = "bg-BG"
    explanation: ExplanationInfo
    acts: list[LegalAct]
    questions: list[ExplainedQuestion]


class ExplanationSet(_Model):
    language: str = Field(description="ISO 639-1 code of the explanations' language")
    file: str = Field(description="explanation file (a `files[].path`)")
    questions: int = Field(ge=0, description="questions with an explanation")
    coverage: float = Field(ge=0, le=1, description="questions / all questions")


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
    kind: Literal["images-webp", "images-original", "images-svg"]
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


class LanguageInfo(_Model):
    code: str = Field(description="ISO 639-1 code")
    tag: str = Field(description="BCP 47 tag of the wording, e.g. 'pt-PT'")
    native_name: str
    english_name: str
    kind: Literal["source", "translation"]
    status: Literal["official", "unofficial"]
    file: str | None = Field(description="translation file (a `files[].path`); null for the source language")
    questions: int = Field(ge=0, description="questions available in this language")
    coverage: float = Field(ge=0, le=1, description="questions / all questions")


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
    languages: list[LanguageInfo] = Field(
        default_factory=list, description="Bulgarian (the source) and the available translations"
    )
    explanations: list[ExplanationSet] = Field(
        default_factory=list, description="unofficial explanations of the correct answers (Bulgarian only)"
    )


SCHEMA_MODELS = {
    "categories": CategoriesFile,
    "questions": QuestionsFile,
    "exam-configs": ExamConfigsFile,
    "translation": TranslationFile,
    "explanation": ExplanationFile,
    "manifest": Manifest,
}

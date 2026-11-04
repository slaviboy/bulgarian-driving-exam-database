"""JSON exports of the dataset (categories.json, questions.json, exam-configs.json)."""

from __future__ import annotations

from pathlib import Path

from question_bank.fsutil import write_json
from question_bank.models import CategoriesFile, ExamConfigsFile, QuestionsFile
from question_bank.processor.builder import Dataset

FILE_NAMES = {
    "categories": "categories.json",
    "questions": "questions.json",
    "exam_configs": "exam-configs.json",
    "sqlite": "master.sqlite",
    "manifest": "manifest.json",
}


def categories_file(dataset: Dataset) -> CategoriesFile:
    return CategoriesFile(
        dataset_version=dataset.dataset_version,
        sources=dataset.sources,
        categories=dataset.categories,
        topics=dataset.topics,
    )


def questions_file(dataset: Dataset) -> QuestionsFile:
    return QuestionsFile(
        dataset_version=dataset.dataset_version, media=dataset.media, questions=dataset.questions
    )


def exam_configs_file(dataset: Dataset) -> ExamConfigsFile:
    return ExamConfigsFile(
        dataset_version=dataset.dataset_version,
        rules_version=dataset.rules_version,
        configs=dataset.exam_configs,
    )


def write_json_exports(dataset: Dataset, exports_dir: Path) -> dict[str, Path]:
    """Write the three JSON files. Every payload passes through its Pydantic model first."""
    paths = {
        "categories": exports_dir / FILE_NAMES["categories"],
        "questions": exports_dir / FILE_NAMES["questions"],
        "exam_configs": exports_dir / FILE_NAMES["exam_configs"],
    }
    write_json(paths["categories"], categories_file(dataset).model_dump(mode="json"))
    write_json(paths["questions"], questions_file(dataset).model_dump(mode="json"))
    write_json(paths["exam_configs"], exam_configs_file(dataset).model_dump(mode="json"))
    return paths

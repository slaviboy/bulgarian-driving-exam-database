"""AvtoIzpit (avtoizpit.com, ИААА's online exam simulator): public metadata and opt-in test-set sampling.

Only unauthenticated endpoints that the public web page itself calls are used. The voucher endpoints
(`api/vouchers/*`, a candidate's personal exam review) are deliberately never called.
AvtoIzpit data is used for comparison reports and exam-rule evidence only; it never enters the dataset.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from question_bank.config import AVTOIZPIT_BASE_URL
from question_bank.extractor.clients.http import HttpClient
from question_bank.processor.normalization.ids import category_id
from question_bank.processor.normalization.text import match_key

log = logging.getLogger(__name__)

SUB_CATEGORIES = "api/sub-categories"
TEST_SETS = "api/test-sets"
ASSESSMENT = "api/test-sets/{id}/assessment"
LANGUAGE_BG = 1


@dataclass(frozen=True)
class LearningPlan:
    id: int
    description: str


@dataclass(frozen=True)
class SubCategory:
    id: int
    category_id: int
    name: str
    learning_plans: tuple[LearningPlan, ...]


def parse_sub_categories(payload: list[dict[str, Any]]) -> tuple[SubCategory, ...]:
    result = []
    for item in payload:
        plans = tuple(
            LearningPlan(int(p["id"]), str(p["description"])) for p in item.get("learningPlans", [])
        )
        result.append(SubCategory(int(item["id"]), int(item["categoryId"]), str(item["name"]), plans))
    return tuple(result)


def fetch_sub_categories(client: HttpClient) -> tuple[list[dict[str, Any]], tuple[SubCategory, ...]]:
    """GET the public category / learning-plan list. Returns the raw payload and its parsed form."""
    payload = client.get_json(AVTOIZPIT_BASE_URL + SUB_CATEGORIES)
    if not isinstance(payload, list):
        raise ValueError("unexpected sub-categories payload")
    return payload, parse_sub_categories(payload)


@dataclass(frozen=True)
class PlanMatch:
    official_order: int
    official_file: str
    sub_category: SubCategory | None
    learning_plan: LearningPlan | None
    candidates: int  # 0 = unmatched, 1 = matched, >1 = ambiguous (not used)


def _official_keys(category_token: str, description_words: str) -> tuple[str, str]:
    # "19_D_103_с_…" carries the trolleybus code 103 in the description words; AvtoIzpit names it "D (103)".
    head = re.match(r"^(\d+)_(.*)$", description_words)
    if head:
        return category_id(category_token + head.group(1)), match_key(head.group(2))
    return category_id(category_token), match_key(description_words)


def match_learning_plans(
    official_files: Iterable[Any], sub_categories: Iterable[SubCategory]
) -> list[PlanMatch]:
    """Pair each official variant file with the AvtoIzpit plan of the same category and description."""
    subs = list(sub_categories)
    matches = []
    for f in official_files:
        cat_key, desc_key = _official_keys(f.category_token, f.description_words)
        found = [
            (sub, plan)
            for sub in subs
            if category_id(sub.name) == cat_key
            for plan in sub.learning_plans
            if match_key(plan.description) == desc_key
        ]
        sub, plan = found[0] if len(found) == 1 else (None, None)
        matches.append(PlanMatch(f.order, f.file_name, sub, plan, len(found)))
    return matches


def generate_test_set(client: HttpClient, sub_category_id: int, learning_plan_id: int) -> dict[str, Any]:
    """POST a request for a new random test set, exactly as the public page does when a test starts."""
    body = {"subCategoryId": sub_category_id, "learningPlanId": learning_plan_id, "languageId": LANGUAGE_BG}
    log.info("avtoizpit: generating test set", extra=body)
    return client.post_json(AVTOIZPIT_BASE_URL + TEST_SETS, body)


def assess_without_answers(client: HttpClient, test_set: dict[str, Any]) -> dict[str, Any]:
    """Submit the test set with nothing ticked so the simulator reveals its result and correct answers.

    The body mirrors `TestSet.toAssessmentDto()` of the public page:
    `{questions: [{id, answers: [{id, checked}]}]}`.
    """
    questions = test_set.get("questions", [])
    dto = {
        "questions": [
            {"id": q["id"], "answers": [{"id": a["id"], "checked": False} for a in q.get("answers", [])]}
            for q in questions
        ],
    }
    log.info("avtoizpit: assessing test set", extra={"test_set_id": test_set["id"]})
    return client.post_json(AVTOIZPIT_BASE_URL + ASSESSMENT.format(id=test_set["id"]), dto)

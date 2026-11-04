from __future__ import annotations

import random

import pytest

from question_bank.exam_rules.generator import (
    ExamSpec,
    GenerationError,
    PoolQuestion,
    generate_exam,
    verify_exam,
)


def pool(
    seed: int = 1, per_section: int = 60, sections: tuple[int, ...] = (1, 2, 3, 4)
) -> list[PoolQuestion]:
    rng = random.Random(seed)
    questions = []
    for s in sections:
        for i in range(per_section):
            questions.append(PoolQuestion(f"s{s}q{i}", s, rng.choice([1, 2, 3]), video=(s == 4 and i < 6)))
    return questions


B_LIKE = ExamSpec(
    question_count=20,
    max_points=43,
    video_questions=2,
    section_quotas={1: 2, 2: 4, 3: 6, 4: 8},
    points_mix={1: 5, 2: 7, 3: 8},
)


@pytest.mark.parametrize("seed", range(30))
def test_quotas_mix_and_videos_are_all_satisfied(seed):
    selection = generate_exam(pool(), B_LIKE, random.Random(seed))
    assert verify_exam(selection, B_LIKE) is None
    assert [q.section for q in selection] == sorted(q.section for q in selection)  # grouped by section


@pytest.mark.parametrize("seed", range(10))
def test_total_points_only_when_mix_unknown(seed):
    spec = ExamSpec(15, 29, 0, {1: 6, 2: 9}, None)
    selection = generate_exam(pool(sections=(1, 2)), spec, random.Random(seed))
    assert verify_exam(selection, spec) is None


def test_without_section_quotas():
    spec = ExamSpec(15, 35, 0, None, {1: 2, 2: 6, 3: 7})
    selection = generate_exam(pool(), spec, random.Random(3))
    assert verify_exam(selection, spec) is None


def test_different_seeds_give_different_exams():
    a = {q.id for q in generate_exam(pool(), B_LIKE, random.Random(1))}
    b = {q.id for q in generate_exam(pool(), B_LIKE, random.Random(2))}
    assert a != b


def test_impossible_specs_are_reported():
    with pytest.raises(GenerationError):  # more 3-point questions than the pool can offer in one section
        generate_exam(
            pool(per_section=3), ExamSpec(12, 36, 0, {1: 3, 2: 3, 3: 3, 4: 3}, {3: 12}), random.Random(1)
        )
    with pytest.raises(GenerationError):  # mix inconsistent with max points
        generate_exam(pool(), ExamSpec(20, 40, 2, B_LIKE.section_quotas, B_LIKE.points_mix), random.Random(1))
    with pytest.raises(GenerationError):  # more videos than exist
        generate_exam(pool(), ExamSpec(20, 43, 9, B_LIKE.section_quotas, B_LIKE.points_mix), random.Random(1))


def test_verify_exam_explains_violations():
    selection = generate_exam(pool(), B_LIKE, random.Random(5))
    assert "questions" in verify_exam(selection[:-1], B_LIKE)
    assert verify_exam(selection + selection[:1], B_LIKE) is not None

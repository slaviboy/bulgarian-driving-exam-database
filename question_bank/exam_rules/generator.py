"""Reference exam generator. Used by validation as a constructive proof that every exam configuration can
be satisfied with the published questions, and as the specification of the Android exam engine.

Constraints of one test (docs/exam-rules.md):
  * exactly `question_count` questions, at most one per question ID;
  * per-section quotas (when known) — the selection per section equals the quota;
  * exactly `video_questions` questions with a video (they count towards their section quota);
  * the points mix (number of 1-, 2- and 3-point questions) when known, otherwise only the total
    `max_points`.

Algorithm: choose the video questions first (random, within quotas), then distribute the remaining
non-video questions over (section × points) cells. With a known points mix this is a transportation
problem solved by max-flow (augmenting paths explored in random order for variety); without one,
a random quota-respecting selection is repaired by swapping questions inside a section until the
total equals `max_points`. Questions are finally sampled uniformly from each cell.
"""

from __future__ import annotations

import random
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class PoolQuestion:
    id: str
    section: int
    points: int
    video: bool


@dataclass(frozen=True)
class ExamSpec:
    question_count: int
    max_points: int
    video_questions: int
    section_quotas: dict[int, int] | None
    points_mix: dict[int, int] | None


class GenerationError(RuntimeError):
    pass


def _max_flow_assignment(
    supply: dict[int, int], demand: dict[int, int], capacity: dict[tuple[int, int], int], rng: random.Random
) -> dict[tuple[int, int], int] | None:
    """Integral flow sections → points meeting every supply and demand exactly, or None if impossible.

    Edmonds–Karp on the graph S → section (supply) → points (cell capacity) → T (demand), augmenting one
    unit at a time with neighbours visited in random order, so different feasible splits come out.
    """
    if sum(supply.values()) != sum(demand.values()):
        return None
    source, sink = ("S", 0), ("T", 0)
    residual: dict[tuple, int] = defaultdict(int)
    neighbours: dict[tuple, set] = defaultdict(set)

    def edge(u: tuple, v: tuple, c: int) -> None:
        residual[(u, v)] += c
        neighbours[u].add(v)
        neighbours[v].add(u)

    for s, n in supply.items():
        edge(source, ("s", s), n)
    for p, n in demand.items():
        edge(("p", p), sink, n)
    cells = {(s, p): c for (s, p), c in capacity.items() if c > 0 and s in supply and p in demand}
    for (s, p), c in cells.items():
        edge(("s", s), ("p", p), c)

    pushed = 0
    while True:
        parent: dict[tuple, tuple | None] = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            options = sorted(neighbours[u])
            rng.shuffle(options)
            for v in options:
                if v not in parent and residual[(u, v)] > 0:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            break
        v = sink
        while parent[v] is not None:
            u = parent[v]
            residual[(u, v)] -= 1
            residual[(v, u)] += 1
            v = u
        pushed += 1
    if pushed != sum(supply.values()):
        return None
    return {
        k: c - residual[(("s", k[0]), ("p", k[1]))]
        for k, c in cells.items()
        if c - residual[(("s", k[0]), ("p", k[1]))] > 0
    }


def generate_exam(
    pool: list[PoolQuestion], spec: ExamSpec, rng: random.Random, attempts: int = 200
) -> list[PoolQuestion]:
    sections = sorted({q.section for q in pool})
    quotas = dict(spec.section_quotas) if spec.section_quotas else None
    section_of = (lambda q: q.section) if quotas else (lambda q: 0)
    if quotas is None:
        quotas = {0: spec.question_count}
    if sum(quotas.values()) != spec.question_count:
        raise GenerationError("section quotas do not add up to the question count")
    if spec.points_mix is not None:
        mix = {int(p): n for p, n in spec.points_mix.items()}
        if sum(mix.values()) != spec.question_count or sum(p * n for p, n in mix.items()) != spec.max_points:
            raise GenerationError("points mix inconsistent with question count / max points")
    else:
        mix = None
    del sections

    buckets: dict[tuple[int, int, bool], list[PoolQuestion]] = defaultdict(list)
    for q in pool:
        buckets[(section_of(q), q.points, q.video)].append(q)
    videos = [q for q in pool if q.video and quotas.get(section_of(q), 0) > 0]

    for _attempt in range(attempts):
        # 1) video questions
        chosen: list[PoolQuestion] = []
        remaining = dict(quotas)
        candidates = videos[:]
        rng.shuffle(candidates)
        for q in candidates:
            if len(chosen) == spec.video_questions:
                break
            if remaining[section_of(q)] > 0:
                chosen.append(q)
                remaining[section_of(q)] -= 1
        if len(chosen) != spec.video_questions:
            raise GenerationError("not enough video questions within the section quotas")

        # 2) non-video questions
        if mix is not None:
            need = dict(mix)
            for q in chosen:
                need[q.points] = need.get(q.points, 0) - 1
            if any(v < 0 for v in need.values()):
                continue
            capacity = {(s, p): len(buckets.get((s, p, False), [])) for s in remaining for p in (1, 2, 3)}
            assignment = _max_flow_assignment(remaining, {p: n for p, n in need.items()}, capacity, rng)
            if assignment is None:
                continue
            for (s, p), n in sorted(assignment.items()):
                chosen.extend(rng.sample(buckets[(s, p, False)], n))
        else:
            picked: dict[int, list[PoolQuestion]] = {}
            ok = True
            for s, n in remaining.items():
                options = [q for (bs, _p, video), qs in buckets.items() if bs == s and not video for q in qs]
                if len(options) < n:
                    ok = False
                    break
                picked[s] = rng.sample(options, n)
            if not ok:
                raise GenerationError("not enough questions in a section")
            total = sum(q.points for q in chosen) + sum(q.points for qs in picked.values() for q in qs)
            for _ in range(5000):
                if total == spec.max_points:
                    break
                diff = spec.max_points - total
                s = rng.choice([s for s in picked if picked[s]])
                current = rng.choice(picked[s])
                ids = {q.id for q in picked[s]}
                swaps = [
                    q
                    for (bs, _p, video), qs in buckets.items()
                    if bs == s and not video
                    for q in qs
                    if q.id not in ids
                    and 0 < (q.points - current.points) * (1 if diff > 0 else -1) <= abs(diff)
                ]
                if swaps:
                    new = rng.choice(swaps)
                    picked[s][picked[s].index(current)] = new
                    total += new.points - current.points
            if total != spec.max_points:
                continue
            for qs in picked.values():
                chosen.extend(qs)

        if verify_exam(chosen, spec, section_of) is None:
            return sorted(chosen, key=lambda q: (q.section, rng.random()))
    raise GenerationError(f"no valid exam found in {attempts} attempts")


def verify_exam(selection: list[PoolQuestion], spec: ExamSpec, section_of=None) -> str | None:
    """Return None when `selection` satisfies `spec`, otherwise a description of the first violation."""
    section_of = section_of or (lambda q: q.section)
    if len(selection) != spec.question_count:
        return f"{len(selection)} questions instead of {spec.question_count}"
    if len({q.id for q in selection}) != len(selection):
        return "duplicate question"
    if sum(q.points for q in selection) != spec.max_points:
        return f"{sum(q.points for q in selection)} points instead of {spec.max_points}"
    if sum(1 for q in selection if q.video) != spec.video_questions:
        return "wrong number of video questions"
    if spec.points_mix is not None:
        for p, n in spec.points_mix.items():
            if sum(1 for q in selection if q.points == int(p)) != n:
                return f"wrong number of {p}-point questions"
    if spec.section_quotas:
        for s, n in spec.section_quotas.items():
            if sum(1 for q in selection if q.section == s) != n:
                return f"section {s}: quota {n} not met"
    return None

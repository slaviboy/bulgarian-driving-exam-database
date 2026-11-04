"""Compare the AvtoIzpit samples with the official array (spec §2.8) and derive exam-rule evidence.

Nothing is merged: the official array stays the only source of the dataset. AvtoIzpit shuffles answer
order, so answers are compared as sets. Pictures are compared by identifier (official asset names are
`<pictureId>.png`); no AvtoIzpit media is downloaded.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from question_bank.extractor.parsers.official_html import ParsedQuestion
from question_bank.extractor.pipeline import ExtractedFile
from question_bank.fsutil import read_json, write_json, write_text
from question_bank.processor.normalization.text import normalize_text


def _stem(name: str | None) -> str | None:
    return name.rsplit(".", 1)[0] if name else None


def _norm(text: str | None) -> str:
    return normalize_text(text or "")


def _answer_key(text: str | None, picture: Any) -> str:
    return f"text:{_norm(text)}" if _norm(text) else f"picture:{picture}"


def _compare_question(official: ParsedQuestion, points: int, aq: dict[str, Any]) -> list[dict[str, Any]]:
    diffs = []

    def diff(kind: str, official_value: Any, avtoizpit_value: Any) -> None:
        diffs.append(
            {
                "question": official.original_id,
                "kind": kind,
                "official": official_value,
                "avtoizpit": avtoizpit_value,
            }
        )

    if _norm(official.text) != _norm(aq["text"]):
        diff("wording", official.text, aq["text"])
    if points != int(aq["points"]):
        diff("points", points, aq["points"])
    official_answers = Counter(_answer_key(a.text, _stem(a.image)) for a in official.answers)
    avto_answers = Counter(_answer_key(a.get("text"), a.get("pictureId")) for a in aq["answers"])
    if official_answers != avto_answers:
        diff("answer_options", sorted(official_answers), sorted(avto_answers))
    official_correct = sum(1 for a in official.answers if a.correct)
    if official_correct != int(aq["correctAnswersCount"]):
        diff("correct_answer_count", official_correct, aq["correctAnswersCount"])
    if "assessed" in aq:
        mine = sorted(_answer_key(a.text, _stem(a.image)) for a in official.answers if a.correct)
        theirs = sorted(
            _answer_key(a.get("text"), a.get("pictureId")) for a in aq["assessed"] if a.get("correct")
        )
        if mine != theirs:
            diff("correct_answers", mine, theirs)
    picture = _stem(official.images[0]) if official.images else None
    if str(picture) != str(aq.get("pictureId")) and (picture or aq.get("pictureId")):
        diff("illustration", picture, aq.get("pictureId"))
    if bool(official.videos) != bool(aq.get("videoFileId")):
        diff("video", list(official.videos), aq.get("videoFileId"))
    return diffs


def _methodology_quotas(
    rules: dict[str, Any], tables: dict[str, Any] | None
) -> dict[int, dict[str, int] | None]:
    """Quotas as printed in the methodology table each rule cites ("…, Таблица N")."""
    by_number = {t["table"]: t for t in (tables or {}).get("tables", [])}
    result: dict[int, dict[str, int] | None] = {}
    for rule in rules["variants"]:
        match = re.search(r"Таблица\s+(\d+)", rule.get("methodology", ""))
        table = by_number.get(int(match.group(1))) if match else None
        result[rule["official_order"]] = (
            {str(s["number"]): s["count"] for s in table["sections"]} if table else None
        )
    return result


def compare_samples(
    extracted: list[ExtractedFile],
    samples_dir: Path,
    rules: dict[str, Any],
    methodology_tables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    files = {e.source.order: e for e in extracted}
    configured = {r["official_order"]: r.get("section_quotas") for r in rules["variants"]}
    methodology = _methodology_quotas(rules, methodology_tables)
    samples = []
    all_diffs: list[dict[str, Any]] = []
    evidence: dict[int, dict[str, Any]] = defaultdict(lambda: {"samples": []})
    for path in sorted(samples_dir.glob("*.json")):
        record = read_json(path)
        order = record["official_order"]
        variant = files[order]
        official = {q.original_id: q for q in variant.parsed.questions}
        assessed = {
            q["id"]: q["answers"]
            for q in ((record.get("assessment") or {}).get("testSet") or {}).get("questions", [])
        }
        matched, unmatched, sections = 0, [], []
        diffs = []
        for aq in record["test_set"]["questions"]:
            oq = official.get(str(aq["id"]))
            if oq is None:
                unmatched.append(aq["id"])
                continue
            matched += 1
            sections.append(oq.section_number)
            if aq["id"] in assessed:
                aq = {**aq, "assessed": assessed[aq["id"]]}
            diffs += _compare_question(oq, oq.points, aq)
        for d in diffs:
            d["sample"] = path.stem
        all_diffs += diffs
        per_section = dict(sorted(Counter(sections).items()))
        observed_quotas = {str(k): v for k, v in per_section.items()}
        samples.append(
            {
                "sample": path.stem,
                "official_order": order,
                "variant": variant.parsed.title,
                "questions": len(record["test_set"]["questions"]),
                "matched_by_id": matched,
                "unmatched_ids": unmatched,
                "differences": len(diffs),
                "per_section": {str(k): v for k, v in per_section.items()},
                "ordered_by_section": sections == sorted(sections),
            }
        )
        evidence[order]["variant"] = variant.parsed.title
        evidence[order]["methodology_quotas"] = methodology.get(order)
        evidence[order]["configured_quotas"] = configured.get(order)
        evidence[order]["samples"].append(
            {
                "sample": path.stem,
                "per_section": observed_quotas,
                "matches_methodology": observed_quotas == methodology.get(order),
                "matches_configuration": observed_quotas == configured.get(order),
                "ordered_by_section": sections == sorted(sections),
            }
        )
    for item in evidence.values():
        observed = [s["per_section"] for s in item["samples"]]
        item["observed_quotas_identical"] = all(o == observed[0] for o in observed)
        item["observed_quotas"] = observed[0] if item["observed_quotas_identical"] else None
    kinds = Counter(d["kind"] for d in all_diffs)
    return {
        "summary": {
            "samples": len(samples),
            "questions_compared": sum(s["matched_by_id"] for s in samples),
            "unmatched": sum(len(s["unmatched_ids"]) for s in samples),
            "questions_with_differences": len({(d["sample"], d["question"]) for d in all_diffs}),
            "differences_by_kind": dict(sorted(kinds.items())),
        },
        "samples": samples,
        "differences": all_diffs,
        "evidence": {str(k): v for k, v in sorted(evidence.items())},
    }


def write_comparison(result: dict[str, Any], reports_dir: Path) -> None:
    write_json(
        reports_dir / "source-comparison.json", {k: result[k] for k in ("summary", "samples", "differences")}
    )
    write_json(reports_dir / "exam-rules-evidence.json", result["evidence"])
    s = result["summary"]
    lines = [
        "# Source comparison — official array vs AvtoIzpit samples",
        "",
        f"{s['samples']} AvtoIzpit test sets, {s['questions_compared']} questions compared by ИААА "
        f"question ID ({s['unmatched']} without an official match). Answers are compared as sets because "
        "AvtoIzpit shuffles them; correct answers come from the simulator's assessment response; "
        "pictures are compared by identifier. Nothing from AvtoIzpit is merged into the dataset.",
        "",
        f"* Questions with at least one difference: **{s['questions_with_differences']}**",
    ]
    for kind, n in s["differences_by_kind"].items():
        lines.append(f"* `{kind}`: {n}")
    if not s["differences_by_kind"]:
        lines.append("* No differences in wording, answer options, correct answers, points or illustrations.")
    lines += [
        "",
        "## Section composition of the sampled tests",
        "",
        "| # | Variant | Methodology | Observed |",
        "|---|---|---|---|",
    ]

    def fmt(quotas: dict[str, int] | None) -> str:
        return " · ".join(f"{k}:{v}" for k, v in quotas.items()) if quotas else "—"

    for order, item in result["evidence"].items():
        observed = fmt(item["observed_quotas"]) if item["observed_quotas"] else "differs between samples"
        lines.append(
            f"| {order} | {item['variant']} | {fmt(item['methodology_quotas'])} | "
            f"{fmt(item['configured_quotas'])} | {observed} |"
        )
    if result["differences"]:
        lines += [
            "",
            "## Differences",
            "",
            "| Sample | Question | Kind | Official | AvtoIzpit |",
            "|---|---|---|---|---|",
        ]
        for d in result["differences"][:300]:
            lines.append(
                f"| {d['sample']} | {d['question']} | {d['kind']} | {d['official']} | {d['avtoizpit']} |"
            )
    write_text(reports_dir / "source-comparison.md", "\n".join(lines) + "\n")

"""Checks of explanations against the question bank and the legal corpus.

Errors block a merge and a release; warnings are shown for the reviewer. An explanation entry is::

    {"kind": "law" | "general", "text": "…", "references": [{"act": "zdvp", "unit": "чл. 50, ал. 1",
     "quote": "…"}]}

or, when the cited law seems to contradict the official answer, ``{"conflict": "<what and where>"}`` — such
questions are reported to the maintainer and never exported.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from question_bank.explanations.bank import BankQuestion
from question_bank.legal.corpus import Corpus, normalize

MIN_TEXT = 80
MAX_TEXT = 900
MIN_QUOTE_WORDS = 3
MAX_QUOTE_WORDS = 70
MAX_REFERENCES = 4
# Latin words that are normal in Bulgarian traffic texts.
LATIN_ALLOWED = {
    "km",
    "h",
    "m",
    "kg",
    "t",
    "cm",
    "mm",
    "kw",
    "abs",
    "esp",
    "asr",
    "ebd",
    "adr",
    "vin",
    "led",
    "lpg",
    "cng",
    "stop",
    "gps",
    "co",
    "co2",
    "nox",
    "ii",
    "iii",
    "iv",
    "kmh",
    "ml",
    "l",
    "s",
    "hz",
    "eu",
    "ece",
    "un",
    "isofix",
    "e",
    "ev",
    "dpf",
    "egr",
    "tsi",
    "srs",
    "tcs",
    "tpms",
    "m1",
    "n1",
    "o1",
    "o2",
    "o3",
    "o4",
}
_LETTER_REFERENCE = re.compile(r"(?i)отговор(?:и)?\s*[„\"(]?\s*[абвг]\s*[“\")]?(?:[\s,.;:]|$)")
_LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]*")
_CYRILLIC = re.compile(r"[А-Яа-яЁёЪъЬьЮюЯя]")


@dataclass(frozen=True)
class Finding:
    question_id: str
    level: str  # "error" | "warning"
    message: str

    def __str__(self) -> str:
        return f"{self.level.upper():7} {self.question_id}: {self.message}"


def check(question: BankQuestion | None, question_id: str, entry: object, corpus: Corpus) -> list[Finding]:
    found: list[Finding] = []

    def error(message: str) -> None:
        found.append(Finding(question_id, "error", message))

    def warning(message: str) -> None:
        found.append(Finding(question_id, "warning", message))

    if question is None:
        error("no such question in the bank")
        return found
    if not isinstance(entry, dict):
        error("the entry must be an object")
        return found
    if "conflict" in entry:
        if not isinstance(entry["conflict"], str) or len(entry["conflict"].strip()) < 20:
            error("a conflict needs a description: which provision says what")
        else:
            warning(f"conflict reported: {entry['conflict'].strip()}")
        return found

    unknown = set(entry) - {"kind", "text", "references", "source_hash", "note"}
    if unknown:
        error(f"unknown fields {sorted(unknown)}")
    kind = entry.get("kind")
    if kind not in ("law", "general"):
        error("kind must be 'law' or 'general'")
    text = entry.get("text")
    if not isinstance(text, str) or not text.strip():
        error("empty text")
        return found
    text = text.strip()
    if not MIN_TEXT <= len(text) <= MAX_TEXT:
        error(f"text has {len(text)} characters (allowed {MIN_TEXT}–{MAX_TEXT})")
    if not _CYRILLIC.search(text):
        error("the text is not in Bulgarian")
    latin = sorted({w for w in _LATIN_WORD.findall(text) if w.lower() not in LATIN_ALLOWED})
    if latin:
        warning(f"Latin words in the text: {', '.join(latin)} (Bulgarian only, apart from units and codes)")
    if _LETTER_REFERENCE.search(text):
        warning("refers to an answer by its letter; quote the answer's words instead")
    if "source_hash" in entry and entry["source_hash"] != question.content_hash:
        error("source_hash differs from the question's content_hash (the question changed)")

    references = entry.get("references", [])
    if not isinstance(references, list):
        error("references must be a list")
        return found
    if kind == "general" and references:
        error("kind 'general' takes no references; use kind 'law' to cite the acts")
    if kind == "law" and not references:
        error("kind 'law' needs at least one reference with a quote")
    if len(references) > MAX_REFERENCES:
        error(f"{len(references)} references (at most {MAX_REFERENCES})")
    seen = set()
    for i, ref in enumerate(references, 1):
        if not isinstance(ref, dict) or set(ref) != {"act", "unit", "quote"}:
            error(f"reference {i} must have exactly act, unit and quote")
            continue
        key = (ref["act"], ref["unit"], normalize(ref["quote"]))
        if key in seen:
            error(f"reference {i} repeats an earlier one")
        seen.add(key)
        words = len(ref["quote"].split())
        if not MIN_QUOTE_WORDS <= words <= MAX_QUOTE_WORDS:
            error(f"reference {i}: the quote has {words} words (allowed {MIN_QUOTE_WORDS}–{MAX_QUOTE_WORDS})")
        result = corpus.check(ref["act"], ref["unit"], ref["quote"])
        if not result.ok:
            error(f"reference {i}: {result.message}")
        elif result.resolved != ref["unit"]:
            warning(f"reference {i}: {ref['unit']} is not split in the text; quote is in {result.resolved}")
    return found


def check_all(
    entries: dict[str, object],
    bank: dict[str, BankQuestion],
    corpus: Corpus,
    expected: list[str] | None = None,
) -> list[Finding]:
    """Every entry, plus coverage: each expected question needs an entry."""
    findings = []
    for question_id, entry in entries.items():
        findings.extend(check(bank.get(question_id), question_id, entry, corpus))
    for question_id in expected or []:
        if question_id not in entries:
            findings.append(Finding(question_id, "error", "no explanation (or conflict) for this question"))
    return findings

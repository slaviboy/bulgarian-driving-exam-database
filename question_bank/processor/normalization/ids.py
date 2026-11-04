"""Deterministic, stable identifiers (data contract §2)."""

from __future__ import annotations

import hashlib
import re

from question_bank.processor.normalization.text import (
    CYRILLIC_TO_LATIN_LOOKALIKE,
    normalize_text,
    split_effective_note,
)

SOURCE_ID = "iaaa-eis"
MAX_SLUG = 80
TRUNCATED_SLUG = 64

# Bulgarian Streamlined System (Закон за транслитерацията, 2009). Word-final "ия" becomes "ia".
_BG_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "zh", "з": "z", "и": "i",
    "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s",
    "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sht", "ъ": "a",
    "ь": "y", "ю": "yu", "я": "ya",
}  # fmt: skip
_WORD_FINAL_IA = re.compile(r"ия\b")
_SECTION_PREFIX = re.compile(r"^\s*Раздел\s+\d+\s*\.\s*", re.IGNORECASE)


def transliterate_bg(value: str) -> str:
    """Transliterate Bulgarian Cyrillic to Latin (lower-case output for Cyrillic letters)."""
    lowered = _WORD_FINAL_IA.sub("ia", value.lower())
    return "".join(_BG_TRANSLIT.get(ch, ch) for ch in lowered)


def slugify(value: str) -> str:
    """Transliterate, lower-case and join alphanumeric runs with '-'. Long slugs get a stable hash suffix."""
    words = re.findall(r"[a-z0-9]+", transliterate_bg(normalize_text(value)))
    slug = "-".join(words)
    if len(slug) <= MAX_SLUG:
        return slug
    digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:6]
    cut = slug[:TRUNCATED_SLUG]
    if "-" in cut:
        cut = cut[: cut.rfind("-")]
    return f"{cut}-{digest}"


def category_id(label: str) -> str:
    """'C+E' → 'CE', 'D (103)' → 'D103', 'Ттм' → 'TTM', Cyrillic 'В' → 'B'."""
    folded = normalize_text(label).upper().translate(CYRILLIC_TO_LATIN_LOOKALIKE)
    latin = transliterate_bg(folded).upper()
    result = "".join(ch for ch in latin if ch.isascii() and ch.isalnum())
    if not result:
        raise ValueError(f"cannot derive a category id from {label!r}")
    return result


def variant_id(category: str, description: str) -> str:
    base, _note = split_effective_note(description)
    slug = slugify(base)
    if not slug:
        raise ValueError(f"cannot derive a variant slug from {description!r}")
    return f"{category}.{slug}"


def section_title_without_number(title: str) -> str:
    return normalize_text(_SECTION_PREFIX.sub("", title))


def topic_id(section_title: str) -> str:
    return slugify(section_title_without_number(section_title))


def section_id(variant: str, number: int) -> str:
    return f"{variant}#s{number}"


def question_id(original_id: str) -> str:
    if not original_id.isdigit():
        raise ValueError(f"unexpected original question id {original_id!r}")
    return f"iaaa-{original_id}"


def answer_id(question: str, position: int) -> str:
    return f"{question}-a{position}"


def media_id(sha256_hex: str) -> str:
    return f"m-{sha256_hex[:16]}"


def exam_config_id(variant: str, rules_version: str) -> str:
    return f"{variant}@{rules_version}"

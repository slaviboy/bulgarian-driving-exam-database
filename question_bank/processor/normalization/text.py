"""Text normalisation. Deliberately minimal: the official wording is never "corrected".

Only Unicode NFC normalisation, HTML-entity decoding (done by the parser) and whitespace collapsing
are applied. Mixed Cyrillic/Latin spellings that occur in the source (e.g. "ВUS") are preserved.
"""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_EFFECTIVE_NOTE = re.compile(r"\(\s*след\s+[^)]*\)", re.IGNORECASE)

# Cyrillic letters that look like Latin ones. Folding is used only for identifiers and matching keys,
# never for stored text.
CYRILLIC_TO_LATIN_LOOKALIKE = str.maketrans(
    {
        "А": "A", "В": "B", "С": "C", "Е": "E", "Н": "H", "К": "K", "М": "M",
        "О": "O", "Р": "P", "Т": "T", "Х": "X", "У": "Y",
        "а": "a", "с": "c", "е": "e", "о": "o", "р": "p", "х": "x", "у": "y",
    }
)  # fmt: skip


def normalize_text(value: str) -> str:
    """NFC + collapse every run of whitespace (incl. NBSP and newlines) to one space + trim."""
    return _WS.sub(" ", unicodedata.normalize("NFC", value)).strip()


def split_effective_note(description: str) -> tuple[str, str | None]:
    """Split "… (След 12.12.24г.)" into ("…", "След 12.12.24г.")."""
    match = _EFFECTIVE_NOTE.search(description)
    if not match:
        return normalize_text(description), None
    note = normalize_text(match.group(0)[1:-1])
    rest = normalize_text(description[: match.start()] + " " + description[match.end() :])
    return rest, note


def match_key(value: str) -> str:
    """Aggressive key for comparing descriptions written in different places (file names, AvtoIzpit, <h1>).

    Drops the "(След …)" note, folds look-alike letters, lower-cases and removes everything that is not a
    letter or digit. Only for matching — never stored as content.
    """
    without_note, _ = split_effective_note(value.replace("_", " "))
    folded = without_note.translate(CYRILLIC_TO_LATIN_LOOKALIKE).lower()
    return "".join(ch for ch in folded if ch.isalnum())

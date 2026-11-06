"""The legal corpus: the current text of the acts the explanations quote (``data/legal/``).

``data/legal/sources.json`` describes every act (title, short name, the government page its text was taken
from, the SHA-256 of that file, the last amendment it contains and the amendments known to be missing).
``data/legal/<act>.json`` holds the act's units as parsed by :mod:`question_bank.legal.parse`.

Legal acts are not subject to copyright (ЗАПСП, чл. 4, т. 1); see docs/licensing.md.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from question_bank.config import REPO_ROOT
from question_bank.fsutil import read_json, write_json
from question_bank.legal.parse import ParsedAct

LEGAL_DIR = REPO_ROOT / "data" / "legal"
SOURCES = "sources.json"

_QUOTES = str.maketrans(
    {"„": '"', "“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "–": "-", "—": "-"}
)
_SPACES = re.compile(r"\s+")
_UNIT = re.compile(r"^(?:чл\. \d+[а-я]?|§ \d+[а-я]?)(?:, ал\. \d+[а-я]?)?(?:, т\. \d+[а-я]?)?$")


def normalize(text: str) -> str:
    """Comparable text: one kind of quotes and dashes, single spaces, no soft hyphens."""
    return _SPACES.sub(" ", text.replace("­", "").translate(_QUOTES)).strip()


def is_unit_id(unit: str) -> bool:
    return bool(_UNIT.match(unit))


def parent(unit: str) -> str | None:
    return unit.rsplit(", ", 1)[0] if ", " in unit else None


@dataclass(frozen=True)
class Act:
    id: str
    short: str
    title: str
    source_url: str
    consolidated_to: str | None
    units: dict[str, str]

    def resolve(self, unit: str) -> tuple[str, str] | None:
        """The unit itself, or the closest enclosing unit when the act's text does not split it further."""
        current: str | None = unit
        while current is not None:
            if current in self.units:
                return current, self.units[current]
            current = parent(current)
        return None


@dataclass(frozen=True)
class QuoteCheck:
    ok: bool
    resolved: str | None
    message: str = ""


class Corpus:
    def __init__(self, acts: dict[str, Act], meta: dict):
        self.acts = acts
        self.meta = meta

    def check(self, act_id: str, unit: str, quote: str) -> QuoteCheck:
        """The quote must be word for word in the cited unit (or the unit enclosing it)."""
        act = self.acts.get(act_id)
        if act is None:
            return QuoteCheck(False, None, f"unknown act {act_id!r}")
        if not is_unit_id(unit):
            return QuoteCheck(
                False, None, f"malformed unit {unit!r} (e.g. 'чл. 50, ал. 1, т. 2' or '§ 6, т. 21')"
            )
        found = act.resolve(unit)
        if found is None:
            return QuoteCheck(False, None, f"{act.short}: {unit} does not exist in the corpus")
        resolved, text = found
        if not quote.strip():
            return QuoteCheck(False, resolved, "empty quote")
        if normalize(quote) not in normalize(text):
            return QuoteCheck(
                False, resolved, f"{act.short}, {resolved}: the quote is not in the text of the unit"
            )
        return QuoteCheck(True, resolved)

    def search(self, act_id: str, words: list[str], limit: int = 30) -> list[tuple[str, str]]:
        """Units containing every word (case-insensitive), in the order of the act."""
        act = self.acts[act_id]
        needles = [normalize(w).lower() for w in words]
        hits = [(u, t) for u, t in act.units.items() if all(n in normalize(t).lower() for n in needles)]
        return hits[:limit]


def load(legal_dir: Path = LEGAL_DIR) -> Corpus:
    meta = read_json(legal_dir / SOURCES)
    acts = {}
    for entry in meta["acts"]:
        path = legal_dir / f"{entry['id']}.json"
        if not path.exists():
            continue
        data = read_json(path)
        acts[entry["id"]] = Act(
            id=entry["id"],
            short=entry["short"],
            title=entry["title"],
            source_url=entry["source_url"],
            consolidated_to=data.get("consolidated_to"),
            units=data["units"],
        )
    return Corpus(acts, meta)


def write_act(
    parsed: ParsedAct, act_id: str, source: Path, legal_dir: Path = LEGAL_DIR, retrieved: date | None = None
) -> dict:
    """Write ``<act>.json``; record the source file's checksum and consolidation date in sources.json."""
    meta = read_json(legal_dir / SOURCES)
    entry = next((a for a in meta["acts"] if a["id"] == act_id), None)
    if entry is None:
        raise KeyError(f"{act_id} is not described in {legal_dir / SOURCES}")
    sha256 = hashlib.sha256(source.read_bytes()).hexdigest()
    write_json(
        legal_dir / f"{act_id}.json",
        {
            "act": act_id,
            "title": parsed.title,
            "consolidated_to": parsed.last_amendment,
            "repealed": parsed.repealed,
            "units": {unit: parsed.units[unit] for unit in parsed.order},
        },
    )
    entry["source_sha256"] = sha256
    entry["consolidated_to"] = parsed.last_amendment
    entry["units"] = len(parsed.units)
    entry["retrieved"] = (retrieved or date.today()).isoformat()
    write_json(legal_dir / SOURCES, meta)
    return entry

#!/usr/bin/env python3
"""Automatic checks for translations of the question bank (standard library only).

The same module is used by the translation work packages (copied as ``tools/lint.py``) and by
``qb build`` through :mod:`question_bank.translations`. It cannot judge meaning; it catches the
mechanical mistakes that change meaning or break the app: missing entries, numbers that differ,
untranslated or wrong-script text, lost question marks and colons, wrong licence-category letters,
two answers that became identical, and inconsistent translations of identical Bulgarian text.

Work-package layout (``--work``, default: the folder above this file)::

    source/questions/part-NN.json    Bulgarian input, one part of the questions
    source/labels.bg.json            categories, variant descriptions/notes, topic titles
    source/ui-strings.bg.json        app UI strings
    out/<lang>/questions/part-NN.json   translation of a part: {question_id: {text, answers: {id: text}}}
    out/<lang>/labels.json           translation of the labels (same shape as the source)
    out/<lang>/ui-strings.json       translation of the UI strings: {key: text | {plural form: text}}
    out/<lang>/lint-exceptions.json  [{"id": …, "check": …, "reason": …}] — accepted, justified findings

Usage::

    python -I lint.py --lang en --part 7    # one part
    python -I lint.py --lang en --labels
    python -I lint.py --lang en --ui
    python -I lint.py --lang en --all       # everything, coverage and consistency

Exit code 1 when there are errors (warnings do not fail).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Language:
    code: str
    tag: str  # wording variant (BCP 47)
    native_name: str
    english_name: str
    script: str  # latin | cyrillic | greek | devanagari
    decimal: str
    plurals: tuple[str, ...]  # CLDR plural categories that Android resources need


LANGUAGES: dict[str, Language] = {
    "bg": Language("bg", "bg-BG", "Български", "Bulgarian", "cyrillic", ",", ("one", "other")),
    "en": Language("en", "en", "English", "English", "latin", ".", ("one", "other")),
    "ru": Language("ru", "ru-RU", "Русский", "Russian", "cyrillic", ",", ("one", "few", "many", "other")),
    "es": Language("es", "es-ES", "Español", "Spanish", "latin", ",", ("one", "many", "other")),
    "de": Language("de", "de-DE", "Deutsch", "German", "latin", ",", ("one", "other")),
    "fr": Language("fr", "fr-FR", "Français", "French", "latin", ",", ("one", "many", "other")),
    "hi": Language("hi", "hi-IN", "हिन्दी", "Hindi", "devanagari", ".", ("one", "other")),
    "pt": Language("pt", "pt-PT", "Português", "Portuguese", "latin", ",", ("one", "many", "other")),
    "el": Language("el", "el-GR", "Ελληνικά", "Greek", "greek", ",", ("one", "other")),
    "tr": Language("tr", "tr-TR", "Türkçe", "Turkish", "latin", ",", ("one", "other")),
    "ro": Language("ro", "ro-RO", "Română", "Romanian", "latin", ",", ("one", "few", "other")),
}
SOURCE_LANGUAGE = "bg"
TARGET_LANGUAGES = [code for code in LANGUAGES if code != SOURCE_LANGUAGE]

ERROR, WARNING = "ERROR", "WARN"


@dataclass
class Finding:
    level: str
    item: str  # question/answer id or label/ui key
    check: str
    message: str

    def line(self) -> str:
        return f"{self.level:<5}  {self.item}  [{self.check}] {self.message}"


@dataclass
class Result:
    findings: list[Finding] = field(default_factory=list)
    accepted: list[Finding] = field(default_factory=list)
    checked_strings: int = 0

    def add(self, level: str, item: str, check: str, message: str) -> None:
        self.findings.append(Finding(level, item, check, message))

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.level == ERROR]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.level == WARNING]

    def extend(self, other: Result) -> None:
        self.findings += other.findings
        self.accepted += other.accepted
        self.checked_strings += other.checked_strings


# ----------------------------------------------------------------------------- text helpers

INVISIBLE = {"\u00ad", "\u200b", "\u200c", "\u200d", "\u2060", "\ufeff", "\ufffd"}
SPACES_OK = {" ", "\u00a0", "\u202f"}
MARKUP = re.compile(r"\*\*|__|`|</?[a-zA-Z][^>]*>|\\n|\\\"")
WORD = re.compile(r"[^\W\d_]+")
THOUSANDS = re.compile(r"(?<=\d)[ \u00a0\u202f\u2009.,'](?=\d{3}(?!\d))")
DIGITS = re.compile(r"\d+")
LATIN_ACRONYM = re.compile(r"(?<![A-Za-z])[A-Z]{2,}(?![A-Za-z])")
# Cyrillic letters that Bulgarian uses for the Latin licence-category and bus-class letters.
LOOKALIKE = str.maketrans("АВСЕМТКНОРХ", "ABCEMTKHOPX")
TRANSLIT = str.maketrans({"т": "t", "м": "m", "к": "k", "б": "b"})
# "категория В", "категории С1Е", "клас А", "категория “А”", "категория Ттм" (licence codes: AM, A1, A2, A,
# B1, B, BE, C1, C1E, C, CE, D1, D1E, D, DE and the national Ттм/Ттб/Ткт).
CATEGORY_REF = re.compile(
    r"(?:категори[яиите]*|клас)\s+(?:от\s+)?[„“\"«]?"
    r"(Т[тк][мтб]|[ABCDАВС](?:[MМ]|[12])?(?:\s*\+?\s*[EЕ])?)"
    r"(?![A-Za-zА-Яа-я0-9])"
)
# A final "." that belongs to a Bulgarian abbreviation ("След 12.12.24г.", "стаж 2г.", "над 3,5 т.") is not
# sentence punctuation the translation has to keep.
BG_ABBREVIATION_END = re.compile(r"(?<![^\W\d_])(?:г|гр|чл|ал|т|м|км|мин|ч|напр|др|вкл|ок)\.\s*$|\dг\.\s*$")
RU_BULGARIAN_WORDS = {
    "е",
    "са",
    "ще",
    "със",
    "във",
    "към",
    "това",
    "които",
    "който",
    "която",
    "когато",
    "ако",
    "трябва",
    "път",
    "пътя",
    "пътното",
    "превозно",
    "превозни",
    "водачът",
    "водачите",
    "МПС",
    "ППС",
    "ПТП",
    "ЗДвП",
}


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def script_of(ch: str) -> str | None:
    if not ch.isalpha():
        return None
    o = ord(ch)
    if 0x0400 <= o <= 0x052F:
        return "cyrillic"
    if 0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF:
        return "greek"
    if 0x0900 <= o <= 0x097F or 0xA8E0 <= o <= 0xA8FF:
        return "devanagari"
    if o < 0x0250 or 0x1E00 <= o <= 0x1EFF or 0x2C60 <= o <= 0x2C7F or 0xA720 <= o <= 0xA7FF:
        return "latin"
    return "other"


def letter_scripts(text: str) -> Counter:
    return Counter(s for s in map(script_of, text) if s)


def numbers(text: str) -> list[str]:
    """Digit groups, with thousands separators removed the same way on both sides."""
    return sorted(DIGITS.findall(THOUSANDS.sub("", text)))


def ending(text: str) -> str:
    stripped = text.rstrip()
    return stripped[-1:] if stripped else ""


def category_codes(source: str) -> list[str]:
    """Licence categories and bus classes named in Bulgarian text, as their official Latin codes."""
    codes = []
    for raw in CATEGORY_REF.findall(source):
        code = re.sub(r"\s*\+\s*", "", raw).translate(LOOKALIKE).translate(TRANSLIT)
        codes.append(code)
    return codes


def code_pattern(code: str) -> re.Pattern:
    trailer = len(code) > 1 and code.endswith("E")
    body = re.escape(code[:-1]) + r"\s*\+?\s*E" if trailer else re.escape(code)
    return re.compile(r"(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])")


# ----------------------------------------------------------------------------- string checks


def check_string(
    result: Result, lang: Language, item: str, source: str, target: object, *, kind: str
) -> None:
    """kind: question | answer | label | ui."""
    result.checked_strings += 1
    if not isinstance(target, str):
        result.add(ERROR, item, "type", f"expected a string, got {type(target).__name__}")
        return
    if not target.strip():
        result.add(ERROR, item, "empty", "the translation is empty")
        return
    if target != nfc(target):
        result.add(WARNING, item, "nfc", "not NFC-normalised (it will be normalised on merge)")
    t = nfc(target)
    s = nfc(source)

    # Whitespace and invisible characters.
    if t != t.strip():
        result.add(ERROR, item, "whitespace", "leading or trailing space")
    if ("\n" in t or "\t" in t or "\r" in t) and not ("\n" in s and kind == "ui"):
        result.add(ERROR, item, "whitespace", "line break or tab inside the text")
    if re.search(r"[ \u00a0\u202f]{2,}", t):
        result.add(ERROR, item, "whitespace", "two spaces in a row")
    odd_spaces = {c for c in t if c.isspace() and c not in SPACES_OK and c not in "\n\t\r"}
    if odd_spaces:
        result.add(
            ERROR, item, "whitespace", f"unusual space characters {sorted(map(hex, map(ord, odd_spaces)))}"
        )
    bad = {c for c in t if c in INVISIBLE or (unicodedata.category(c) == "Cc" and c not in "\n\t\r")}
    if bad:
        result.add(
            ERROR, item, "invisible", f"invisible/control characters {sorted(map(hex, map(ord, bad)))}"
        )
    if kind != "ui" and MARKUP.search(t) and not MARKUP.search(s):
        result.add(ERROR, item, "markup", "markdown, HTML or escape sequences are not allowed")

    # Script.
    scripts = letter_scripts(t)
    source_scripts = letter_scripts(s)
    for word in WORD.findall(t):
        ws = {x for x in map(script_of, word) if x}
        if len(ws) > 1:
            result.add(
                ERROR, item, "mixed_script", f"word '{word}' mixes {sorted(ws)} letters (look-alike letters?)"
            )
    if source_scripts["cyrillic"] >= 2 and scripts[lang.script] == 0:
        result.add(ERROR, item, "wrong_script", f"no {lang.script} letters — not translated?")
    if lang.script != "cyrillic" and scripts["cyrillic"]:
        cyr = sorted({w for w in WORD.findall(t) if any(script_of(c) == "cyrillic" for c in w)})
        result.add(ERROR, item, "cyrillic", f"Cyrillic left in the translation: {cyr[:6]}")
    if lang.script == "devanagari" and re.search(r"[\u0966-\u096f]", t):
        result.add(ERROR, item, "digits", "use the digits 0–9, not Devanagari digits")
    if s == t and source_scripts["cyrillic"] >= 2:
        level = WARNING if lang.code == "ru" else ERROR
        result.add(level, item, "untranslated", "identical to the Bulgarian text")

    # Language-specific characters.
    if lang.code == "ru":
        if "ѝ" in t or "Ѝ" in t:
            result.add(ERROR, item, "bulgarian", "'ѝ' is Bulgarian, not Russian")
        if re.search(r"ъ(?![еёюяЕЁЮЯ])", t, flags=re.IGNORECASE):
            result.add(ERROR, item, "bulgarian", "'ъ' used as a vowel (Bulgarian spelling)")
        bg_words = sorted({w for w in WORD.findall(t) if w in RU_BULGARIAN_WORDS})
        if bg_words:
            result.add(WARNING, item, "bulgarian", f"Bulgarian words or abbreviations: {bg_words}")
    if lang.code == "ro" and re.search("[şŞţŢ]", t):
        result.add(ERROR, item, "romanian_comma", "use ș/ț (comma below), not ş/ţ (cedilla)")
    if lang.code == "fr" and re.search(r" [:;?!»]|« ", t):
        result.add(
            WARNING, item, "french_space", "use a no-break space (U+00A0) before : ; ? ! » and after «"
        )

    # Numbers and codes.
    if kind != "ui":
        ns, nt = numbers(s), numbers(t)
        if ns != nt:
            result.add(
                ERROR, item, "numbers", f"Bulgarian has {ns or 'no numbers'}, translation has {nt or 'none'}"
            )
        for code in category_codes(s):
            if lang.code == "ru":
                if re.search(r"категори\w*\s+[«„“\"]?[АВСЕМ]+\d?(?![а-яА-Я])", t):
                    result.add(
                        ERROR, item, "category_code", "write licence categories with Latin letters (B, C1E…)"
                    )
            elif not code_pattern(code).search(t):
                result.add(
                    ERROR,
                    item,
                    "category_code",
                    f"Bulgarian names category/class '{code}' (Latin letters); "
                    "it must appear in the translation in Latin letters",
                )
        missing = [a for a in LATIN_ACRONYM.findall(s) if a not in t]
        if missing:
            result.add(WARNING, item, "acronym", f"acronyms from the Bulgarian text not found: {missing}")

    # Punctuation at the end.
    se, te = ending(s), ending(t)
    question_marks = {";", "\u037e"} if lang.code == "el" else {"?"}
    if se == ":" and te != ":":
        result.add(
            ERROR, item, "end_punct", "the Bulgarian ends with ':' (the answers continue it); keep ':'"
        )
    elif se == "?" and te not in question_marks:
        result.add(
            ERROR,
            item,
            "end_punct",
            f"the Bulgarian is a question; end with {' or '.join(sorted(question_marks))}",
        )
    elif se == "." and te not in {".", "।", "…"} and kind != "ui" and not BG_ABBREVIATION_END.search(s):
        result.add(WARNING, item, "end_punct", "the Bulgarian ends with '.'")
    elif se not in {".", ":", "?", "!", "…", ";", ")", "»", "”", '"'} and te in {".", ":"} and kind != "ui":
        result.add(WARNING, item, "end_punct", f"punctuation '{te}' added at the end")
    if lang.code == "es" and se == "?" and "¿" not in t:
        result.add(ERROR, item, "spanish_question", "Spanish questions need the opening '¿'")
    if lang.code == "el" and te == "?":
        result.add(ERROR, item, "end_punct", "Greek uses ';' as the question mark")

    # Case of the first letter (answers continuing a stem start in lower case).
    first_s = next((c for c in s if c.isalpha()), "")
    first_t = next((c for c in t if c.isalpha()), "")
    first_word = (WORD.findall(s) or [""])[0]
    starts_with_abbreviation = len(first_word) >= 2 and first_word.isupper()
    if (
        kind in {"answer", "question"}
        and lang.code not in {"de", "hi"}
        and first_s
        and first_t
        and not starts_with_abbreviation
    ):
        if first_s.islower() and first_t.isupper() and not LATIN_ACRONYM.match(t.lstrip()):
            result.add(
                WARNING, item, "case", "the Bulgarian starts in lower case (it continues the question)"
            )
        elif first_s.isupper() and first_t.islower():
            result.add(WARNING, item, "case", "the Bulgarian starts with a capital letter")

    # Length.
    if len(s) >= 20 and kind != "ui":
        ratio = len(t) / len(s)
        if ratio < 0.45 or ratio > 2.3:
            result.add(
                WARNING,
                item,
                "length",
                f"{ratio:.2f}× the Bulgarian length — check nothing was added or lost",
            )
    if kind == "ui" and len(s) <= 16 and len(t) > max(24, 1.9 * len(s)):
        result.add(
            WARNING,
            item,
            "length",
            f"short UI label became {len(t)} characters — may not fit a button or tab",
        )
    if (
        kind == "label"
        and len(t) >= 6
        and t.upper() == t
        and any(c.isalpha() for c in t)
        and lang.script != "devanagari"
    ):
        result.add(WARNING, item, "all_caps", "write titles in sentence case, not ALL CAPS")


# ----------------------------------------------------------------------------- files


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_exceptions(out_dir: Path) -> set[tuple[str, str]]:
    path = out_dir / "lint-exceptions.json"
    if not path.exists():
        return set()
    accepted = set()
    for entry in read_json(path):
        if (
            isinstance(entry, dict)
            and entry.get("id")
            and entry.get("check")
            and str(entry.get("reason", "")).strip()
        ):
            accepted.add((entry["id"], entry["check"]))
    return accepted


def apply_exceptions(result: Result, accepted: set[tuple[str, str]]) -> Result:
    keep = []
    for f in result.findings:
        (result.accepted if (f.item, f.check) in accepted else keep).append(f)
    result.findings = keep
    return result


def text_answers(question: dict) -> list[dict]:
    return [a for a in question["answers"] if a.get("text")]


def lint_part(work: Path, lang: Language, part: int) -> Result:
    result = Result()
    name = f"part-{part:02d}.json"
    source = read_json(work / "source" / "questions" / name)
    out_path = work / "out" / lang.code / "questions" / name
    if not out_path.exists():
        result.add(ERROR, name, "missing", f"{out_path} does not exist")
        return result
    try:
        translated = read_json(out_path)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        result.add(ERROR, name, "json", f"not valid UTF-8 JSON: {e}")
        return result
    if not isinstance(translated, dict):
        result.add(ERROR, name, "json", "the file must be one object keyed by question id")
        return result
    wanted = {q["id"]: q for q in source["questions"]}
    for qid in sorted(set(wanted) - set(translated)):
        result.add(ERROR, qid, "missing", "question not translated")
    for qid in sorted(set(translated) - set(wanted)):
        result.add(ERROR, qid, "extra", f"not a question of {name}")
    for qid, q in wanted.items():
        entry = translated.get(qid)
        if entry is None:
            continue
        if (
            not isinstance(entry, dict)
            or set(entry) != {"text", "answers"}
            or not isinstance(entry.get("answers"), dict)
        ):
            result.add(ERROR, qid, "shape", 'expected {"text": "…", "answers": {"<answer id>": "…"}}')
            continue
        check_string(result, lang, qid, q["text"], entry["text"], kind="question")
        expected = {a["id"]: a for a in text_answers(q)}
        got = entry["answers"]
        for aid in sorted(set(expected) - set(got)):
            result.add(ERROR, aid, "missing", "answer not translated")
        for aid in sorted(set(got) - set(expected)):
            pic = any(a["id"] == aid for a in q["answers"])
            result.add(
                ERROR,
                aid,
                "extra",
                "picture-only answer — it has no text to translate" if pic else "unknown answer id",
            )
        for aid, a in expected.items():
            if aid in got:
                check_string(result, lang, aid, a["text"], got[aid], kind="answer")
        # Two different Bulgarian answers must not become the same translation.
        seen: dict[str, str] = {}
        for aid, a in expected.items():
            value = got.get(aid)
            if not isinstance(value, str):
                continue
            key = nfc(value).strip().casefold()
            if key in seen and nfc(expected[seen[key]]["text"]).casefold() != nfc(a["text"]).casefold():
                result.add(
                    ERROR,
                    aid,
                    "same_answers",
                    f"same translation as {seen[key]} although the Bulgarian differs",
                )
            seen.setdefault(key, aid)
        # A correct answer must not become clearer or longer than the wrong ones.
        ratios = {True: [], False: []}
        for aid, a in expected.items():
            value = got.get(aid)
            if isinstance(value, str) and len(a["text"]) >= 3:
                ratios[bool(a.get("correct"))].append(len(value) / len(a["text"]))
        if ratios[True] and ratios[False]:
            right = sum(ratios[True]) / len(ratios[True])
            wrong = sum(ratios[False]) / len(ratios[False])
            if right > 1.3 * wrong and right > 1.25:
                result.add(
                    WARNING,
                    qid,
                    "hint",
                    "the correct answer(s) grew much more than the wrong ones — "
                    "make sure the translation does not give the answer away",
                )
    return result


def lint_labels(work: Path, lang: Language) -> Result:
    result = Result()
    source = read_json(work / "source" / "labels.bg.json")
    path = work / "out" / lang.code / "labels.json"
    if not path.exists():
        result.add(ERROR, "labels", "missing", f"{path} does not exist")
        return result
    translated = read_json(path)
    for group in ("categories", "variants", "topics"):
        src = source[group]
        got = translated.get(group) if isinstance(translated, dict) else None
        if not isinstance(got, dict):
            result.add(ERROR, group, "shape", f"'{group}' must be an object")
            continue
        for key in sorted(set(src) - set(got)):
            result.add(ERROR, f"{group}:{key}", "missing", "not translated")
        for key in sorted(set(got) - set(src)):
            result.add(ERROR, f"{group}:{key}", "extra", "unknown key")
        for key, value in src.items():
            if key not in got:
                continue
            item = f"{group}:{key}"
            if group == "variants":
                if not isinstance(got[key], dict) or set(got[key]) != set(value):
                    result.add(ERROR, item, "shape", f"expected keys {sorted(value)}")
                    continue
                for field_name, text in value.items():
                    if text is None:
                        if got[key][field_name] is not None:
                            result.add(ERROR, f"{item}.{field_name}", "extra", "must stay null")
                        continue
                    check_string(
                        result, lang, f"{item}.{field_name}", text, got[key][field_name], kind="label"
                    )
            elif group == "categories":
                target = got[key]
                if not isinstance(target, str) or not target.strip():
                    result.add(ERROR, item, "empty", "the category label is empty")
                elif key != "TTM" and target != value:
                    result.add(ERROR, item, "category_code", f"keep the official label '{value}' unchanged")
                elif key == "TTM" and lang.script != "cyrillic" and letter_scripts(target)["cyrillic"]:
                    result.add(ERROR, item, "cyrillic", "write 'Ttm' (no Cyrillic letters)")
            else:
                check_string(result, lang, item, value, got[key], kind="label")
    return result


PLACEHOLDER = re.compile(r"%(?:\d+\$)?[-#+ 0,(]*\d*(?:\.\d+)?[sdfx]|%%")


def lint_ui(work: Path, lang: Language) -> Result:
    result = Result()
    source_path = work / "source" / "ui-strings.bg.json"
    if not source_path.exists():
        result.add(ERROR, "ui", "missing", f"{source_path} does not exist yet")
        return result
    source = read_json(source_path)["strings"]
    path = work / "out" / lang.code / "ui-strings.json"
    if not path.exists():
        result.add(ERROR, "ui", "missing", f"{path} does not exist")
        return result
    translated = read_json(path)
    if not isinstance(translated, dict):
        result.add(ERROR, "ui", "shape", "the file must be one object keyed by string key")
        return result
    for key in sorted(set(source) - set(translated)):
        result.add(ERROR, key, "missing", "not translated")
    for key in sorted(set(translated) - set(source)):
        result.add(ERROR, key, "extra", "unknown key")
    for key, entry in source.items():
        if key not in translated:
            continue
        target = translated[key]
        if "plurals" in entry:
            forms = entry["plurals"]
            if not isinstance(target, dict):
                result.add(
                    ERROR, key, "plurals", f"expected an object with the plural forms {list(lang.plurals)}"
                )
                continue
            if set(target) != set(lang.plurals):
                result.add(
                    ERROR,
                    key,
                    "plurals",
                    f"{lang.english_name} needs exactly the forms {list(lang.plurals)}, got {sorted(target)}",
                )
            reference = Counter(PLACEHOLDER.findall(forms["other"]))
            for form, text in target.items():
                check_string(result, lang, f"{key}#{form}", forms["other"], text, kind="ui")
                if isinstance(text, str) and Counter(PLACEHOLDER.findall(text)) != reference:
                    result.add(
                        ERROR,
                        f"{key}#{form}",
                        "placeholders",
                        f"placeholders must be {sorted(reference.elements())}",
                    )
        else:
            check_string(result, lang, key, entry["text"], target, kind="ui")
            if isinstance(target, str):
                want = Counter(PLACEHOLDER.findall(entry["text"]))
                got = Counter(PLACEHOLDER.findall(target))
                if want != got:
                    result.add(
                        ERROR,
                        key,
                        "placeholders",
                        f"placeholders must be {sorted(want.elements())}, got {sorted(got.elements())}",
                    )
    return result


def part_numbers(work: Path) -> list[int]:
    return sorted(int(p.stem.split("-")[1]) for p in (work / "source" / "questions").glob("part-*.json"))


def consistency(work: Path, lang: Language) -> Result:
    """Identical Bulgarian questions (and their answers) should read identically."""
    result = Result()
    by_text: dict[str, list[tuple[str, str]]] = defaultdict(list)
    answers_by_text: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for part in part_numbers(work):
        name = f"part-{part:02d}.json"
        out = work / "out" / lang.code / "questions" / name
        if not out.exists():
            continue
        try:
            translated = read_json(out)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for q in read_json(work / "source" / "questions" / name)["questions"]:
            entry = translated.get(q["id"]) if isinstance(translated, dict) else None
            if not isinstance(entry, dict) or not isinstance(entry.get("text"), str):
                continue
            by_text[nfc(q["text"])].append((q["id"], nfc(entry["text"])))
            for a in text_answers(q):
                value = (
                    entry.get("answers", {}).get(a["id"]) if isinstance(entry.get("answers"), dict) else None
                )
                if isinstance(value, str):
                    answers_by_text[(nfc(q["text"]), nfc(a["text"]))].append((a["id"], nfc(value)))
    for items in by_text.values():
        variants = {t for _, t in items}
        if len(variants) > 1:
            ids = ", ".join(i for i, _ in items[:8])
            result.add(
                WARNING,
                items[0][0],
                "consistency",
                f"{len(items)} questions with the same Bulgarian text "
                f"have {len(variants)} different translations ({ids})",
            )
    for (_, bg_answer), items in answers_by_text.items():
        variants = {t for _, t in items}
        if len(variants) > 1:
            ids = ", ".join(i for i, _ in items[:8])
            result.add(
                WARNING,
                items[0][0],
                "consistency",
                f"answer '{bg_answer[:40]}' under the same question text "
                f"has {len(variants)} different translations ({ids})",
            )
    return result


def coverage(work: Path, lang: Language) -> dict:
    parts = part_numbers(work)
    done = questions = answers = total_q = total_a = 0
    for part in parts:
        name = f"part-{part:02d}.json"
        src = read_json(work / "source" / "questions" / name)["questions"]
        total_q += len(src)
        total_a += sum(len(text_answers(q)) for q in src)
        out = work / "out" / lang.code / "questions" / name
        if not out.exists():
            continue
        done += 1
        try:
            translated = read_json(out)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        for q in src:
            entry = translated.get(q["id"]) if isinstance(translated, dict) else None
            if isinstance(entry, dict) and isinstance(entry.get("text"), str) and entry["text"].strip():
                questions += 1
                got = entry.get("answers") if isinstance(entry.get("answers"), dict) else {}
                answers += sum(
                    1 for a in text_answers(q) if isinstance(got.get(a["id"]), str) and got[a["id"]].strip()
                )
    return {
        "parts": f"{done}/{len(parts)}",
        "questions": f"{questions}/{total_q}",
        "answers": f"{answers}/{total_a}",
        "labels": (work / "out" / lang.code / "labels.json").exists(),
        "ui": (work / "out" / lang.code / "ui-strings.json").exists(),
    }


def print_result(result: Result, *, limit: int) -> None:
    ordered = result.errors + result.warnings
    for f in ordered[:limit]:
        print(f.line())
    if len(ordered) > limit:
        print(f"… {len(ordered) - limit} more (use --limit)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--work", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--lang", required=True, choices=TARGET_LANGUAGES)
    what = parser.add_mutually_exclusive_group(required=True)
    what.add_argument("--part", type=int)
    what.add_argument("--labels", action="store_true")
    what.add_argument("--ui", action="store_true")
    what.add_argument("--all", action="store_true")
    what.add_argument("--coverage", action="store_true")
    parser.add_argument("--limit", type=int, default=200, help="maximum findings printed")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    lang = LANGUAGES[args.lang]
    work: Path = args.work
    accepted = load_exceptions(work / "out" / lang.code)

    if args.coverage:
        print(json.dumps({lang.code: coverage(work, lang)}, ensure_ascii=False))
        return 0
    result = Result()
    if args.part is not None:
        result.extend(lint_part(work, lang, args.part))
    elif args.labels:
        result.extend(lint_labels(work, lang))
    elif args.ui:
        result.extend(lint_ui(work, lang))
    else:
        result.extend(lint_labels(work, lang))
        result.extend(lint_ui(work, lang))
        for part in part_numbers(work):
            result.extend(lint_part(work, lang, part))
        result.extend(consistency(work, lang))
    apply_exceptions(result, accepted)
    print_result(result, limit=args.limit)
    summary = (
        f"{lang.code}: {result.checked_strings} strings checked · {len(result.errors)} errors · "
        f"{len(result.warnings)} warnings · {len(result.accepted)} accepted exceptions"
    )
    if args.all:
        summary += " · coverage " + json.dumps(coverage(work, lang), ensure_ascii=False)
    print(summary)
    return 1 if result.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

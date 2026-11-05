"""Translations of the question bank into other languages (docs/translations.md).

Bulgarian is the source and stays authoritative; translations are unofficial. The curated translations live in
``data/translations/<lang>/`` and are exported with every dataset release.
"""

from question_bank.translations.lint import LANGUAGES, SOURCE_LANGUAGE, TARGET_LANGUAGES, Language

__all__ = ["LANGUAGES", "SOURCE_LANGUAGE", "TARGET_LANGUAGES", "Language"]

# Translations

The question bank is published in Bulgarian by ИААА. This repository adds **unofficial translations** for learners
who prepare for the Bulgarian theory exam but do not read Bulgarian well:

| Code | Language (wording) |
|---|---|
| en | English (British spelling, EU/UK terms) |
| ru | Russian |
| es | Spanish of Spain |
| de | German |
| fr | French |
| hi | Hindi |
| pt | European Portuguese |
| el | Greek |
| tr | Turkish |
| ro | Romanian |

**The Bulgarian original prevails.** The translations are a learning aid, made with AI and checked as described
below; they are not approved by ИААА. Pictures that contain Bulgarian text are not translated.

## What is translated

* Every question and every answer that has text (answers that are only a picture have nothing to translate).
* The names shown around the questions: licence categories (only "Ттм" changes, to "Ttm", outside Russian), the
  candidate's situation of each variant and its "След …" note, and the topic (section) titles.

## How the translations are made

1. **Work packages.** `qb translations prepare --out <work>` splits the question bank into 25 parts of about 100
   questions, grouped by subject. Identical texts sit together, and every question carries:
   * its correct answers, so the translator can check that right stays right and wrong stays wrong;
   * its pictures;
   * the other questions with the same text.
2. **Rules.** `data/translations/style-guide.md` is binding: meaning first, official legal terms of each language,
   the legal distinctions of the Bulgarian law, no hints, codes and numbers kept. `glossary-pivot.md` defines the
   Bulgarian terms.
3. **Translation.** One translator per language builds a glossary first, then translates the labels and the parts
   in order.
4. **Checks.** `qb translations lint` (or the work package's `tools/lint.py`) runs after every part. It checks:
   * coverage;
   * identical numbers, kept colons and question marks (Greek ";", Spanish "¿…?");
   * licence categories in Latin letters ("категория В" is B);
   * no Bulgarian left and no mixed-script words;
   * two different answers never becoming the same text;
   * consistency of identical Bulgarian texts.
   A part is only finished with 0 errors.
5. **Independent review.** A second reviewer per language rereads everything against the Bulgarian and fixes
   errors. The changes are logged in `data/translations/<lang>/review.json`.
6. **Merge.** `qb translations merge --work <work> --lang <code>` refuses a package with lint errors or missing
   questions. It writes `data/translations/<lang>/`:
   * `questions.json`, `labels.json`;
   * the translator's `glossary.json` and `notes.md`.

## Files

**Curated** (`data/translations/<lang>/questions.json`, committed):

```json
{"language": "en", "questions": {"iaaa-5145": {
    "source_hash": "aa54c528…",
    "text": "Road users are:",
    "answers": {"iaaa-5145-a1": "drivers", "iaaa-5145-a2": "pedestrians", …}}}}
```

`source_hash` is the `content_hash` of the Bulgarian question that was translated. `labels.json` stores the
Bulgarian `source` next to every translated label for the same reason.

**Exported** with every dataset release: `translation-<lang>.json` (schema `contract/schemas/translation.schema.json`).
It is listed in the manifest's `files[]` and `languages[]`, and its tables are in `master.sqlite`; see
`data-contract.md` §5.4.

## When the Bulgarian changes

A new official edition can change questions. `qb build` exports only translations whose `source_hash` equals the
current `content_hash`:
* a changed question is reported as **stale** and left out;
* a new question is reported as **missing**.

Consumers show the Bulgarian text for both until a new translation is merged. `qb translations status` lists
current, stale and missing translations per language. To update, prepare a work package, translate and review the
stale and missing questions, and merge them.

## Reporting a translation error

Open an issue with the "Data issue" template. Include:
* the question number (e.g. 5145);
* the language;
* what is wrong and the Bulgarian text.

The fix goes through the same checks and is released as a patch version.

# Changelog

All notable changes to the tooling, the data contract and the published datasets. Versions follow
[Semantic Versioning](https://semver.org/): dataset MAJOR = contract `schema_version` change, MINOR =
new official edition, questions added/removed or translations added, PATCH = corrections and metadata.

## [Unreleased]

### Dataset

* **Unofficial translations** of all 2,476 questions, the 7,465 answers that have text and the labels
  (categories, the candidate's situation of each variant and its "След …" note, topic titles) into nine
  languages:
  * English (British), Russian, Spanish (Spain), German, French, Portuguese (Portugal), Greek, Turkish and
    Romanian.
  * Each was translated from the Bulgarian with AI under `data/translations/style-guide.md`, linted, and
    checked by an independent review (changes in `data/translations/<lang>/review.json`).
  * They are labelled unofficial; the Bulgarian text prevails.
* The Bulgarian content is unchanged from 1.0.0 (edition 2026-10-01).

### Contract

* `schema_version` stays 1; the additions are optional for consumers:
  * `translation-<lang>.json` in the core package and the manifest's `files[]`;
  * the manifest's `languages[]` (the source and each translation, with coverage);
  * the `master.sqlite` tables `languages`, `question_translations`, `answer_translations` and
    `label_translations`.
* Only translations whose `source_hash` equals the current `content_hash` are exported; stale and missing
  ones are reported and left out, so consumers show the Bulgarian text for them.

### Tooling

* `qb translations prepare | lint | merge | status`, translation checks in the build, and the release
  notes list the translated languages.

## [1.0.0] — 2026-11-04

### Dataset

* First dataset release, built from the ИААА array edition **2026-10-01** (23 exam-variant files).
* Exam rules version **2024-12-12** (Наредба № 38 as amended by ДВ бр. 77/2024) for all 23 variants,
  cross-checked against 44 AvtoIzpit test sets.

### Contract

* Data contract `schema_version` 1: stable string IDs, questions separated from per-variant
  assignments (points and sections vary per variant), content-addressed media, `content_hash`,
  manifest with checksums, completeness and licensing.

### Tooling

* Polite HTTP client (rate limits, retries, conditional and resumable downloads), strict official
  HTML parser, media download with copy verification, builder, validators, reports, source
  comparison, release workflow.

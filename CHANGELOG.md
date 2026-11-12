# Changelog

All notable changes to the tooling, the data contract and the published datasets. Versions follow
[Semantic Versioning](https://semver.org/): dataset MAJOR = contract `schema_version` change, MINOR =
new official edition, questions added/removed or translations added, PATCH = corrections and metadata.

## [1.3.0] — 2026-11-12

### Dataset

* **Clean, sharp pictures** for apps (`images-webp`, media revision `media-2026.10.01-r2`):
  * the tiled "ИААА" stamp is removed: measured exactly from the pictures and its compositing inverted; pixels it
    does not touch are unchanged;
  * scenes and photos are enlarged 2–4× with Real-ESRGAN; a content check rejects any change of structure
    (labels, arrows, numbers), and the flagged ones were reviewed;
  * the 303 road signs and vehicle markings are also **vector drawings** (`images-svg`): 267 use drawings of
    Wikimedia Commons (130 files, CC BY-SA 4.0 or CC0, credited per picture), the others were traced from the
    picture or drawn for the project.
* The original pictures stay published unchanged (`images-original.zip` of `media-2026.10.01`).
* The questions, answers, translations and explanations are unchanged from 1.2.0.

### Tooling

* `qb enhance stamp-fit|clean|review|upscale|commons-import|signs-build|pack` (`question_bank/media_enhance/`,
  docs/media-enhance.md) and the optional extra `media` (NumPy, OpenCV, fontTools).
* `tools/commons-signs-download.html`: the maintainer's browser downloads the Commons drawings (no personal
  data is sent); `qb enhance commons-import` checks their SHA-1.
* `qb media` installs the pinned media revision (`data/enhance/pack.json`), and `qb build` checks every
  enhanced file against `data/enhance/derivatives.json` and rebuilds the pinned packs byte for byte.
* New validation check `enhanced_media`: every picture has a WebP, the SVGs pass the AndroidSVG lint, and
  every Commons drawing is credited.

### Contract

* `schema_version` stays 1; the additions are optional for consumers:
  * derivatives of `format` `"svg"` and the derivatives' `process`; the media's `credits[]`;
  * the media pack kind `images-svg`; the `images-webp` and `images-svg` packs point to the media revision;
  * the `master.sqlite` tables `media_processing` and `media_credits`.
* A WebP that would have the same size as the previous one is re-encoded, because apps recognise a new file
  by its size.

## [1.2.0] — 2026-11-07

### Dataset

* **Explanations (i) in Bulgarian** for all 1,440 questions of category B: 1,433 explanations (1,304 quoting the
  law word for word, 129 general) and 7 conflicts left out for the maintainer (`docs/explanations.md`). Shared
  questions give other categories explanations too.
  * Written with AI from the current texts of ЗДвП (ДВ бр. 55/2026), its Правилник and the ordinances on road
    signs and markings, under `data/explanations/style-guide.md`; every part linted and reviewed independently
    (`data/explanations/bg/review.json`).
  * Unofficial; the official question bank and the law prevail.
* The questions, answers and translations are unchanged from 1.1.0 (edition 2026-10-01).

### Tooling

* **Legal corpus** (`data/legal/`, `qb legal import|status|show|search`): the current text of ЗДвП
  (consolidated to ДВ бр. 55/2026), its Правилник, and the ordinances on road signs (2023) and markings
  (2001). Each act is taken from a government site with its checksum and split into articles, paragraphs,
  points and §; earlier wordings, amending acts, annexes and amendment notes are removed.
* **Explanations** (`qb explanations prepare|lint|merge|status`, `data/explanations/style-guide.md`,
  `docs/explanations.md`): unofficial Bulgarian explanations of the correct answers, written from the law.
  * The lint checks that every quote is word for word in the cited unit.
  * Conflicts with the official answer are listed for the maintainer instead of being explained.
  * `qb verify` repeats the quote check.
* The legal parser drops page furniture (print dates), repairs comparatives' hyphens, and leaves out text struck
  down by the Constitutional Court and editor's notes.

### Contract

* `schema_version` stays 1; the additions are optional for consumers:
  * `explanation-bg.json` in the core package and `files[]`;
  * the manifest's `explanations[]`;
  * the `master.sqlite` tables `legal_acts`, `question_explanations` and `explanation_references`.

## [1.1.0] — 2026-11-06

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

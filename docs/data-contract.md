# Data contract — schema version 1

This document is the **single source of truth** for the data exchanged between this
repository (producer) and its consumers, in particular the Android application
`bulgarian-driving-exam-android`. The machine-readable form lives in
`contract/schemas/*.schema.json` (JSON Schema 2020-12, generated from the Pydantic
models in `question_bank/models.py`). If this document and the schemas disagree,
the schemas win and this document is a bug.

## 1. Versioning

| Field | Meaning | Changes when |
|---|---|---|
| `schema_version` (integer) | Shape of the files and tables below | A consumer would mis-read the data (field removed/renamed/re-typed, semantics changed). Consumers MUST refuse a `schema_version` they do not support. |
| `dataset_version` (semver `MAJOR.MINOR.PATCH`) | One published build | MAJOR = `schema_version` change; MINOR = new official edition or questions added/removed; PATCH = corrections, metadata, rule fixes. |
| `source_edition` (ISO date) | Date in the official file names (`…_01.10.2026.html` → `2026-10-01`) | ИААА publishes a new array. |
| `rules_version` (ISO date) | Version of the curated exam rules | A legal/methodology change is reflected. |

Additive changes (new optional fields, new enum values documented as "ignore if
unknown") do not bump `schema_version`; consumers MUST ignore unknown fields.

## 2. Stable identifiers

All primary keys are **strings**, stable across dataset versions, so consumers can
keep user data (bookmarks, history, statistics) keyed by them.

| Entity | Rule | Example |
|---|---|---|
| source | fixed | `iaaa-eis` (official array), `avtoizpit` (comparison only, never in the dataset) |
| category | Official label → upper-case → Cyrillic look-alikes folded to Latin (А→A, В→B, С→C, Е→E, М→M, Т→T, К→K, Н→H, О→O, Р→P, Х→X) → remaining Cyrillic transliterated → keep `[A-Z0-9]` | `B`, `AM`, `CE` (from "C+E"), `C1E`, `D103` (from "D (103)"), `TTM` (from "Ттм") |
| variant | `<category>.<slug>` where slug = Bulgarian Streamlined transliteration of the variant description without the trailing "(След …)" note, lower-case, words joined by `-`; longer than 80 chars → first 64 chars at a word boundary + `-` + 6 hex chars of SHA-1 of the full slug | `B.bez-pravosposobnost-ili-s-pravosposobnost-za-kategoria-am` |
| section | `<variant>#s<N>` (N = number in "Раздел N.") | `B.bez-…-am#s4` |
| topic | slug of the section title without "Раздел N." — groups equal titles across variants | `pravila-za-dvizhenieto-po-patishtata` |
| question | `iaaa-<original ИААА ID>` | `iaaa-5300` |
| answer | `<question id>-a<position>` (position 1-based, source order) | `iaaa-5300-a1` |
| media | `m-` + first 16 hex chars of the SHA-256 of the **original** file bytes | `m-089e870fa3ce1b2d` |
| exam config | `<variant id>@<rules_version>` | `B.bez-…-am@2024-12-12` |

## 3. Why questions and variants are separate

The official source publishes one HTML file per **exam variant** (category +
candidate situation, e.g. "B — без правоспособност…", "B — загуба на
правоспособност по чл. 157"). The same question (same ИААА ID) appears in up to
11 files. Measured on edition 2026-10-01: text, answers, correct flags and media of
a shared ID are identical in every file, but **points differ for 1,211 IDs and the
section differs for 1,041 IDs**. Therefore:

* `questions` holds the canonical, variant-independent content (one row per ИААА ID);
* `variant_questions` holds what depends on the variant: section, points, position.

This is the only normalised design that preserves the source without inventing a
single "points" value per question.

## 4. Tables (master.sqlite and the Android import model)

All text is UTF-8. Booleans are `INTEGER` 0/1. No SQLite extensions, no
`WITHOUT ROWID`. `PRAGMA user_version` = `schema_version`.

| Table | Columns (PK first) | Notes |
|---|---|---|
| `dataset_info` | `key` TEXT PK, `value` TEXT | `schema_version`, `dataset_version`, `source_edition`, `rules_version`, `content_fingerprint`, `built_at` |
| `sources` | `id` TEXT PK, `name`, `source_url`, `attribution`, `license`, `redistribution_status`, `retrieved_at` | |
| `categories` | `id` TEXT PK, `name` (official label), `description` (NULL — not in source), `source_id` FK, `position` | |
| `variants` | `id` TEXT PK, `category_id` FK, `title`, `description`, `effective_note`, `source_url`, `source_sha256`, `source_edition`, `position`, `question_count` | one per official file |
| `topics` | `id` TEXT PK, `name` | |
| `sections` | `id` TEXT PK, `variant_id` FK, `category_id` FK, `topic_id` FK, `number`, `name` (full official title), `position` | |
| `questions` | `id` TEXT PK, `original_id`, `source_id` FK, `question_text`, `explanation` (NULL — the source has none), `answer_format` (`text`/`image`), `correct_count`, `content_hash` | |
| `answers` | `id` TEXT PK, `question_id` FK, `position`, `answer_text` (NULL for picture answers), `media_id` FK NULL, `is_correct` | |
| `media` | `id` TEXT PK, `kind` (`image`/`video`), `original_name`, `relative_path`, `mime_type`, `bytes`, `width`, `height`, `sha256`, `source_url`, `source_id` FK | media may be shared by several questions |
| `media_aliases` | `media_id` FK + `name` PK | other official file names with byte-identical content (the same picture is published under several names) |
| `media_derivatives` | `media_id` FK + `format` PK, `relative_path`, `mime_type`, `bytes`, `width`, `height`, `sha256` | e.g. WebP versions of PNG images for the app |
| `question_media` | `question_id` FK + `media_id` FK + `role` PK, `position` | `role` = `image` or `video` |
| `variant_questions` | `variant_id` FK + `question_id` FK PK, `section_id` FK, `points` (1–3), `position` | `position` = order inside the official file |
| `exam_configs` | `id` TEXT PK, `variant_id` FK, `status` (`official`/`unofficial`), `question_count`, `max_points`, `pass_points`, `duration_minutes`, `video_questions`, `max_video_plays`, `scoring`, `show_correct_count`, `section_quotas_json`, `points_mix_json`, `verification_json`, `evidence_json`, `notes_json` | JSON columns hold the same values as `exam-configs.json` |

Indexes: every foreign-key column (as the first column of an index), plus
`answers(question_id, position)`.

## 5. Files of a dataset release

```
manifest.json          entry point; checksums of everything else
categories.json        sources, categories → variants → sections, topics
questions.json         questions with answers, media references and assignments; media metadata
exam-configs.json      exam rules per variant with citations and verification status
master.sqlite          the same data in the tables above
```

### 5.1 `questions.json` (shape; values verified from the official file for category B)

```json
{
  "schema_version": 1,
  "dataset_version": "1.0.0",
  "media": [
    { "id": "m-…", "kind": "image", "original_name": "20243.png",
      "relative_path": "images/m-….png", "mime_type": "image/png",
      "bytes": 534212, "width": "…", "height": "…", "sha256": "…",
      "source_url": "https://public-eis.rta.government.bg/exam-questions/…/assets/20243.png",
      "source_id": "iaaa-eis",
      "derivatives": [ { "format": "webp", "relative_path": "images-webp/m-….webp", "…": "…" } ] }
  ],
  "questions": [
    { "id": "iaaa-5300", "original_id": "5300", "source_id": "iaaa-eis",
      "text": "Съединителят е предназначен:", "explanation": null,
      "answer_format": "text", "correct_count": 1, "content_hash": "…",
      "media": [],
      "answers": [
        { "id": "iaaa-5300-a1", "position": 1, "text": "да прекъсва силовата връзка между двигателя и предавателната кутия", "media_id": null, "is_correct": true },
        { "id": "iaaa-5300-a2", "position": 2, "text": "да осъществява връзка между двигателя и карданното предаване", "media_id": null, "is_correct": false },
        { "id": "iaaa-5300-a3", "position": 3, "text": "да съединява елементите на трансмисията с рамата", "media_id": null, "is_correct": false },
        { "id": "iaaa-5300-a4", "position": 4, "text": "да прекъсва връзката между предавателната кутия и карданното предаване", "media_id": null, "is_correct": false }
      ],
      "assignments": [
        { "variant_id": "B.bez-…-am", "category_id": "B", "section_id": "B.bez-…-am#s1", "points": 1, "position": 1 }
      ] }
  ]
}
```

### 5.2 `manifest.json`

Required top-level fields: `schema_version`, `dataset_version`, `source_edition`,
`rules_version`, `built_at` (UTC ISO-8601), `generator` {`name`, `version`,
`git_commit`}, `content_fingerprint`, `sources[]` (with `licensing`),
`source_snapshot[]` {`url`, `etag`, `last_modified`, `sha256`, `bytes`},
`counts` {`categories`, `variants`, `sections`, `topics`, `questions`, `answers`,
`assignments`, `media`, `images`, `videos`}, `category_counts` {category →
{`variants`, `questions`}}, `variant_counts`, `dataset_base_url` (download URL that `files[].path` is relative to), `files[]`
{`path`, `bytes`, `sha256`, `media_type`}, `media_base_url` (media release download URL; single
videos are `<media id>.mp4`), `media_packs[]` {`id`, `kind`, `url`, `bytes`, `sha256`,
`file_count`}, `licensing` {`attribution`, `license`, `redistribution_status`,
`notice_url`}, `completeness` {`status` = `complete`/`partial`, `checks[]`}.

### 5.3 `content_hash`

`content_hash` = lower-case hex SHA-256 of the UTF-8 bytes of the canonical JSON
of:

```json
{"answers":[{"correct":true,"media":null,"position":1,"text":"…"}, …],
 "media":[{"role":"image","sha256":"…"}],
 "text":"…"}
```

Canonicalisation: strings NFC-normalised with runs of whitespace collapsed to one
space and trimmed; answers ordered by position; media ordered by (role,
position); object keys sorted; separators `,` and `:` with no spaces; non-ASCII
characters written as-is (not `\u` escaped). Test vectors live in
`tests/data/content_hash_vectors.json`. `content_fingerprint` is the SHA-256 of
the sorted list of `"<question id>:<content_hash>"` lines plus the canonical JSON
of all assignments and exam configs — it does not depend on build time.

## 6. Releases and URLs

* Dataset release tag `vX.Y.Z` (marked *latest*): `manifest.json`,
  `dataset-core-vX.Y.Z.zip` (all files of §5), the loose files, the reports.
* Media release tag `media-YYYY.MM.DD` (never *latest*): `images-original.zip`,
  `images-webp.zip`, and every video as a single file `<media id>.mp4` (on-demand downloads).
  A dataset manifest references its media packs by absolute URL and SHA-256, so a
  media release is reused until the media change.
* Consumers discover the newest dataset through
  `https://github.com/slaviboy/bulgarian-driving-exam-database/releases/latest/download/manifest.json`
  (a redirect, not the rate-limited REST API).

## 7. Static vs user data

The dataset contains **only static question-bank data**. It never contains user
data. Consumers must store bookmarks, exam history, statistics and preferences
separately and key them by the stable IDs above, so that replacing the dataset
never deletes user data. The Android import rules are specified in
`docs/android-import-spec.md`.

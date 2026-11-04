# Android import specification (schema version 1)

How a consumer — first of all the Android app `bulgarian-driving-exam-android` — must obtain,
verify and import a dataset release. It complements `data-contract.md`; MUST/SHOULD are normative.

## 1. Discovery

* The newest release is described by
  `https://github.com/slaviboy/bulgarian-driving-exam-database/releases/latest/download/manifest.json`
  (an HTTP redirect, not the rate-limited REST API).
* An app SHOULD bundle one pinned release (dataset version + SHA-256 of the core zip) so that it works
  offline from the first launch.

## 2. Compatibility

1. Read `manifest.json` and validate it against `contract/schemas/manifest.schema.json` semantics.
2. `schema_version` MUST be a version the app supports (this document: `1`). Otherwise keep the
   installed dataset and tell the user an app update is needed.
3. Install only if `dataset_version` (semver) is newer than the installed one, or the installed
   dataset is missing/corrupt, or the user explicitly asks to reinstall. `content_fingerprint`
   equal to the installed one means nothing changed — skip the download.
4. `completeness.status` MUST be `complete`.

## 3. Download and verification

* Every entry of `files[]` is downloaded from `dataset_base_url + path` (or taken from the core zip)
  and MUST match `bytes` and `sha256` before anything is parsed.
* Media packs (`media_packs[]`) MUST match their `sha256`. Apps use `images-webp.zip`. Videos are
  single files `media_base_url + "<media id>.mp4"`, downloaded on demand (or all at once) and verified
  against the video's `sha256` in `questions.json`.
* Downloads SHOULD resume with HTTP Range requests and MUST be written to a staging directory; a
  partial download is never visible to the rest of the app.

## 4. Decoding

* JSON is UTF-8. Unknown fields MUST be ignored (additive changes do not bump `schema_version`);
  missing required fields MUST fail the import.
* Enumerations: `answer_format` ∈ {text, image, mixed}; media `kind`/`role` ∈ {image, video};
  exam `status` ∈ {official, unofficial}; `scoring` = all_or_nothing. Unknown enum values MUST fail the
  import of that dataset (not crash the app).

## 5. Semantic checks before writing anything

1. Counts equal `manifest.counts` (categories, variants, sections, questions, answers, assignments,
   media).
2. Every assignment references an existing variant, category and section, and the section belongs to
   the variant.
3. Every question has ≥ 2 answers and ≥ 1 correct answer; answer positions are 1..n.
4. Every media reference (question media and picture answers) exists in `questions.json → media`.
5. Every exam config references an existing variant; when `section_quotas` is present it sums to
   `question_count`; when `points_mix` is present it sums to `question_count` and `max_points`.

## 6. Mapping to Room

| Contract | Room table (content group) | Key |
|---|---|---|
| categories | `content_category` | `id` |
| variants | `content_variant` | `id`, FK `category_id` |
| sections | `content_section` | `id`, FK `variant_id` |
| topics | `content_topic` | `id` |
| questions | `content_question` | `id` |
| answers | `content_answer` | `id`, FK `question_id`, unique (`question_id`, `position`) |
| media (+ derivative used by the app) | `content_media` | `id` |
| question media | `content_question_media` | (`question_id`, `media_id`, `role`) |
| assignments | `content_variant_question` | (`variant_id`, `question_id`), FK `section_id` |
| exam configs | `content_exam_config` | `id`, FK `variant_id` |
| manifest data | `dataset_info` | single row |

Room's generated schema is the app's own; `master.sqlite` is **not** opened as a Room database
(Room validates its own identity hash). The importer reads the JSON files (or `master.sqlite` with
plain SQLite APIs) and inserts rows into the Room tables.

## 7. Atomicity and rollback

* All content rows are replaced inside **one database transaction**: delete all `content_*` rows,
  insert the new rows, re-count, run `PRAGMA foreign_key_check`, update `dataset_info`, commit.
  Any failure rolls back; the previous dataset stays fully usable.
* Media for the new dataset are extracted into the content-addressed pool **before** the
  transaction; files are named by media ID, so old and new datasets can share them. Files referenced
  neither by the new content nor by stored exam snapshots may be deleted after the commit.
* The previous package SHOULD be kept until the next successful import (re-import / rollback).

## 8. User data

* User data (bookmarks, progress, exam history, statistics, preferences) lives in separate tables that
  reference content **only by the stable string IDs** and have **no SQL foreign keys** to content
  tables, so replacing content can never delete or cascade into user data.
* A question whose `content_hash` changed SHOULD have its learning progress reset or flagged; its
  history is kept.
* A question that disappears from the dataset keeps its bookmark and history; it is hidden from
  practice and shown as "no longer in the official bank".
* Exam sessions SHOULD store a snapshot of the questions they contained so past results stay
  reviewable regardless of later content changes.

## 9. Exam simulation

Exam mode MUST use `exam-configs.json` and MUST NOT invent parameters. A config with
`status = official` can be offered as an official exam simulation; the app SHOULD show the
verification bases (`verification`) and notes. Generation rules are those of
`question_bank/exam_rules/generator.py` (quotas per section, exact points mix, exactly
`video_questions` video questions, questions grouped by section). Scoring is all-or-nothing per
question; the test shows each question's number of correct answers and points.

## 10. Schema evolution

A future `schema_version` 2 will be published alongside `1` for a transition period. Apps keep
importing the highest version they support; content tables can always be rebuilt from a stored
package, so content-table schema changes never require user-data migrations.

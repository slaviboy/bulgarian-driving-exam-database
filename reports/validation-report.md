# Validation report — dataset 1.2.0 (edition 2026-10-01)

**17/17 checks passed** · 0 errors · 25 warnings

| Check | Result | Items checked | Errors | Warnings | Description |
|---|---|---|---|---|---|
| `missing_questions` | ✅ pass | 23 | 0 | 0 | every variant has all of its questions |
| `missing_answers` | ✅ pass | 2476 | 0 | 0 | every question has ≥2 answers with text or picture |
| `invalid_correct_answers` | ✅ pass | 2476 | 0 | 0 | ≥1 correct answer, correct_count consistent |
| `broken_media_references` | ✅ pass | 887 | 0 | 0 | every media reference resolves |
| `missing_media_files` | ✅ pass | 1717 | 0 | 0 | every media file exists with its SHA-256 |
| `duplicate_questions` | ✅ pass | 2476 | 0 | 25 | no identical content under different IDs |
| `duplicate_answers` | ✅ pass | 2476 | 0 | 0 | no repeated answer inside a question |
| `invalid_references` | ✅ pass | 13763 | 0 | 0 | assignments point at existing variant/category/section |
| `incorrect_ordering` | ✅ pass | 13763 | 0 | 0 | answers, questions, sections and variants keep source order |
| `invalid_attribution` | ✅ pass | 2476 | 0 | 0 | every record has a known, attributed source |
| `exam_feasibility` | ✅ pass | 23 | 0 | 0 | every exam configuration can be generated (20 seeds each) |
| `translations` | ✅ pass | 22284 | 0 | 0 | translations match the current Bulgarian text (stale or missing ones are left out) |
| `json_schema` | ✅ pass | 3 | 0 | 0 | exports conform to contract/schemas |
| `sqlite_integrity` | ✅ pass | 1 | 0 | 0 | master.sqlite integrity, foreign keys, user_version |
| `translation_schema` | ✅ pass | 9 | 0 | 0 | translation files conform to contract/schemas |
| `explanations` | ✅ pass | 1433 | 0 | 0 | explanations match the current Bulgarian text and every quote is still in the cited act |
| `explanation_schema` | ✅ pass | 1 | 0 | 0 | explanation files conform to contract/schemas |

## Issues

| Severity | Check | Message |
|---|---|---|
| warning | `duplicate_questions` | identical content under IDs iaaa-5304, iaaa-7041 |
| warning | `duplicate_questions` | identical content under IDs iaaa-5319, iaaa-7047, iaaa-7275 |
| warning | `duplicate_questions` | identical content under IDs iaaa-5333, iaaa-7045, iaaa-7273 |
| warning | `duplicate_questions` | identical content under IDs iaaa-5354, iaaa-7053, iaaa-7281 |
| warning | `duplicate_questions` | identical content under IDs iaaa-5357, iaaa-7054, iaaa-7055 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6267, iaaa-6268 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6766, iaaa-6767 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6816, iaaa-7081 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6844, iaaa-7135 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6848, iaaa-7140 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6850, iaaa-7142 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6854, iaaa-7144 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6874, iaaa-7283 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6875, iaaa-7284 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6960, iaaa-6961 |
| warning | `duplicate_questions` | identical content under IDs iaaa-6970, iaaa-6971 |
| warning | `duplicate_questions` | identical content under IDs iaaa-7042, iaaa-7274 |
| warning | `duplicate_questions` | identical content under IDs iaaa-7043, iaaa-7269 |
| warning | `duplicate_questions` | identical content under IDs iaaa-7482, iaaa-7483 |
| warning | `duplicate_questions` | identical content under IDs iaaa-7654, iaaa-7655 |
| warning | `duplicate_questions` | identical content under IDs iaaa-8340, iaaa-8343 |
| warning | `duplicate_questions` | identical content under IDs iaaa-11680, iaaa-11682 |
| warning | `duplicate_questions` | identical content under IDs iaaa-11817, iaaa-11833 |
| warning | `duplicate_questions` | identical content under IDs iaaa-11820, iaaa-11836 |
| warning | `duplicate_questions` | identical content under IDs iaaa-11827, iaaa-11840 |

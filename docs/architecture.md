# Architecture

## Purpose

Turn the official Bulgarian driving-theory question array published by ИААА into a
validated, versioned, provenance-preserving dataset that applications (first of all
the Android app `bulgarian-driving-exam-android`) can consume offline.

## Pipeline

```
 official site ──discover──► source files (23 HTML + assets) ──extract──► raw records (per variant)
                                                                              │
 avtoizpit.com ──metadata / opt-in sample──► comparison + exam-rule evidence  │ normalise, deduplicate
                                                                              ▼
 curated exam rules (cited) ─────────────────────────────────────────► canonical model (Pydantic)
                                                                              │ validate
                                                                              ▼
                       data/exports/{manifest,categories,questions,exam-configs}.json + master.sqlite
                       data/media/{images,images-webp,videos}/          reports/*.{json,md}
                                                                              │ release gate
                                                                              ▼
                              GitHub Releases: dataset vX.Y.Z  +  media-YYYY.MM.DD
```

| Stage | Package | Responsibility |
|---|---|---|
| discover | `question_bank.extractor.discovery` | Read the official index and `manifest.txt`; detect editions, ETags, layout changes. AvtoIzpit metadata. Optional Playwright network capture for evidence. |
| fetch | `question_bank.extractor.clients`, `…downloaders` | Polite HTTPX client: timeouts, retries with back-off, rate limit, conditional requests, resumable downloads, state journal. |
| parse | `question_bank.extractor.parsers` | Strict BeautifulSoup parser of the official HTML; JSON parser for AvtoIzpit test sets. |
| process | `question_bank.processor.*` | Normalisation (NFC + whitespace only), deduplication by ИААА ID with conflict detection, validation. |
| store | `question_bank.database` | SQLite schema + migrations, `master.sqlite` builder. |
| export | `question_bank.exporter` | JSON files, manifest with checksums, release packages, media packs (incl. WebP derivatives). |
| report | `question_bank.reports` | Extraction, validation, category counts, dataset diff, source comparison, exam-rule evidence. |

## Architectural decisions

* **ADR-1 — Official source only in the dataset.** The dataset is built exclusively
  from `public-eis.rta.government.bg/exam-questions/`. AvtoIzpit data is used only
  for comparison reports and exam-rule evidence and is never merged.
* **ADR-2 — Questions vs variant assignments.** Points and sections vary per exam
  variant for the same question ID, so they live in `variant_questions` (see
  `data-contract.md` §3).
* **ADR-3 — Stable string IDs.** Derived deterministically from official
  identifiers so user data in apps survives dataset updates.
* **ADR-4 — Media outside git.** ≈590 MB of images and videos are published as
  GitHub Release assets (separately versioned media releases); only metadata and
  checksums are committed.
* **ADR-5 — Never invent content.** No fixing of wording, no generated
  explanations, no guessed correct answers; anything unparseable fails the build.
* **ADR-6 — Exam rules are curated data with citations.** Every number in
  `exam-configs.json` cites the ordinance article, the methodology table or an
  AvtoIzpit observation; variants without full evidence are marked `unofficial`.
* **ADR-7 — Publication by maintainer decision.** The source has no licence; the
  maintainer chose to publish with attribution (see `DATA_NOTICE.md`,
  `docs/licensing.md`). The release workflow refuses to publish a source whose
  `redistribution_status` is not in the allowed set.
* **ADR-8 — Reproducibility.** Given the same source snapshot the exports are
  byte-identical except `built_at`; `content_fingerprint` ignores build time.

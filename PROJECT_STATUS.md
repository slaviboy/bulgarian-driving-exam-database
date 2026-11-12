# Project status — bulgarian-driving-exam-database

_Last updated: 2026-11-12_

## Current phase

**Phases 1–5 complete; translations (`v1.1.0`), explanations (`v1.2.0`) and clean pictures (`v1.3.0`, latest)
added.** The pictures for apps are without the ИААА stamp and enlarged, and the road signs are also vectors (media
revision `media-2026.10.01-r2`). The Android application (separate private repository, Phases 6–10) consumes the
dataset; see "Consumers" below.

## Completed work

* **Phase 1 — Setup:** public repository, MIT licence (code only), `DATA_NOTICE.md`, data contract,
  architecture.
* **Phase 2 — Investigation:** source investigation, licensing record, exam rules with citations,
  AvtoIzpit metadata and a 44-test-set sample, Playwright network capture.
* **Phase 3 — Extraction:** polite HTTP client; strict official HTML parser (raw-count cross-check);
  incremental, resumable download of the 23 files and 982 assets with a state journal; copy
  verification of assets in other variant directories (one 64 KiB ranged request per copy).
* **Phase 4 — Database and validation:** canonical builder (conflicting duplicate IDs fail the
  build), content-addressed media with WebP derivatives and official-name aliases, JSON exports,
  `master.sqlite` (Room-compatible conventions), manifest with checksums/completeness/licensing,
  13 validation checks incl. exam-config feasibility, reports, AvtoIzpit source comparison,
  Android import specification.
* **Phase 5 — Publication:** README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG, issue/PR
  templates and labels, workflows `tests`, `validation`, `release`, `docs/releasing.md`.
  * Media release [`media-2026.10.01`](https://github.com/slaviboy/bulgarian-driving-exam-database/releases/tag/media-2026.10.01):
    59 assets, 604 MB.
  * Dataset release [`v1.0.0`](https://github.com/slaviboy/bulgarian-driving-exam-database/releases/tag/v1.0.0)
    (latest): 10 assets.
  * Verified anonymously: `releases/latest/download/manifest.json` → v1.0.0; every data file, the
    WebP pack and sample videos match their checksums. CI `tests` and `validation` green.
* **Translations — dataset v1.1.0:** unofficial translations of every question, text answer and label into
  English, Russian, Spanish, German, French, Portuguese, Greek, Turkish and Romanian.
  * Process (`docs/translations.md`): work packages, a binding style guide and pivot glossary, one AI
    translator per language, `qb translations lint` after every part, then an independent AI review per
    language (logged in `data/translations/<lang>/review.json`, 19–57 fixes each).
  * Export: `translation-<lang>.json`, the manifest's `languages[]` and four `master.sqlite` tables;
    `schema_version` stays 1. 9 × 2,476 questions current, 0 stale, 0 missing.
  * Dataset release [`v1.1.0`](https://github.com/slaviboy/bulgarian-driving-exam-database/releases/tag/v1.1.0)
    (latest), published by the `release` workflow: 18 assets, the media release `media-2026.10.01` reused.
  * Verified anonymously: `releases/latest/download/manifest.json` → v1.1.0 with 10 languages; the core
    package matches `SHA256SUMS`.

* **Explanations — dataset v1.2.0:** unofficial Bulgarian explanations of 1,433 questions of category B, written
  from the law (`docs/explanations.md`), with the legal corpus they quote.
* **Clean pictures — media revision r2, dataset v1.3.0:** docs/media-enhance.md.
  * Stamp removed from all 830 pictures (stamp score median 0.43 → −0.004); 527 scenes, photos and drawings
    enlarged with Real-ESRGAN under a content check; 303 signs and markings as SVG (Commons drawings, matched
    by hand on contact sheets, or traced).
  * Packs built locally: `images-webp.zip` 830 files, 44.7 MB; `images-svg.zip` 303 files, 0.9 MB; pinned in
    `data/enhance/pack.json`. `v1.3.0` build: 18/18 checks pass, 0 errors; `qb verify` OK.
  * Published 2026-11-12 from the maintainer machine (docs/releasing.md, option B): media release
    [`media-2026.10.01-r2`](https://github.com/slaviboy/bulgarian-driving-exam-database/releases/tag/media-2026.10.01-r2) (2 assets) and dataset release
    [`v1.3.0`](https://github.com/slaviboy/bulgarian-driving-exam-database/releases/tag/v1.3.0) (latest, 19 assets).
  * Verified anonymously: `releases/latest/download/manifest.json` → v1.3.0 with the packs of r2; the core package
    and both packs match their SHA-256.
  * On the tablet, AndroidSVG (through Coil, as in the app) draws all 303 SVGs; compared with the Chromium
    renders, only anti-aliasing differs.

## Consumers

* The Android application bundles a pinned release (core package and picture packs by SHA-256: `v1.3.0` with the
  WebP and SVG packs of r2; it shows the drawings' credits on its licences page) and installs newer releases from
  `releases/latest/download/manifest.json`, verifying the core package against `SHA256SUMS`. Its
  tests import the real `v1.1.0` (including 9 × 2,476 translations) and a synthetic next patch release derived
  from it; on devices it reported 2,476 questions, 23 variants and 830 verified pictures, matching this
  repository's counts.
* Compatibility promise for consumers: `schema_version` 1 stays readable; a breaking change increases it (MAJOR
  release), which the app reports as "app update required" instead of installing.

## Pending work

* Future editions: the daily `validation` job opens an issue when ИААА publishes a new array; then run the
  `release` workflow (docs/releasing.md). Questions that change need their translations updated (stale ones
  fall back to Bulgarian).

## Tests

* Passed: 171 (HTTP client, discovery, normalisation/IDs, parser on real excerpt, generator over
  many seeds, offline end-to-end build, content-hash vectors, Room-compatibility conventions, media
  copy checks, translation work packages, lint, merge, export and SQLite tables, release packaging, stamp
  model and removal, upscaling check, SVG sanitising, sign recipes and tracing, pinned media packs).
* Failed: none.

## Data counts (edition 2026-10-01, measured by the pipeline)

* 23 exam variants in 11 categories · 103 sections · 30 topics
* 2,476 unique questions · 13,763 question rows (assignments) · 7,893 answers
* 830 distinct pictures (925 official file names; 234 MB PNG, 20 MB WebP; enhanced from v1.3.0: 44.7 MB WebP,
  303 of them also as SVG, 0.9 MB) · 57 videos (350 MB)
* 25 groups of identical content under different ИААА IDs (reported, not merged)
* AvtoIzpit cross-check: 1,166 questions, 0 differences; section quotas observed for 22 variants

## Known limitations

* The source grants no licence; content is published by maintainer decision (DATA_NOTICE.md).
* Pass marks of the six loss-of-licence variants follow the category rule (not stated separately).
* C1 and D (103) section quotas follow the live simulator (the draft methodology differs).
* C1+E has no AvtoIzpit counterpart: law-only parameters, no observed points mix.
* No explanations exist in the source.
* The translations are unofficial and made with AI (then reviewed); the Bulgarian text prevails. Pictures that
  contain Bulgarian text are not translated.
* The enlarged pictures come from an AI upscaler, checked against the stamp-free originals; the original
  pictures remain the reference. Videos still carry the stamp.

## Next actions

* Keep publishing editions through the `release` workflow when the daily `validation` job reports a new array.

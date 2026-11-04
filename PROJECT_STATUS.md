# Project status — bulgarian-driving-exam-database

_Last updated: 2026-11-05_

## Current phase

**Phases 1–5 complete.** The dataset `v1.0.0` is published. The Android application (separate private
repository, Phases 6–10) consumes it; see "Consumers" below.

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

## Consumers

* The Android application bundles `v1.0.0` (core package and WebP images pinned by SHA-256) and installs newer
  releases from `releases/latest/download/manifest.json`, verifying the core package against `SHA256SUMS`. Its
  tests import the real `v1.0.0` and a synthetic `v1.0.1` derived from it; on devices it reported 2,476 questions,
  23 variants and 830 verified pictures, matching this repository's counts.
* Compatibility promise for consumers: `schema_version` 1 stays readable; a breaking change increases it (MAJOR
  release), which the app reports as "app update required" instead of installing.

## Pending work

* None for this repository's first release. Future editions: the daily `validation` job opens an
  issue when ИААА publishes a new array; then run the `release` workflow (docs/releasing.md).

## Tests

* Passed: 105 (HTTP client, discovery, normalisation/IDs, parser on real excerpt, generator over
  many seeds, offline end-to-end build, content-hash vectors, Room-compatibility conventions, media
  copy checks).
* Failed: none.

## Data counts (edition 2026-10-01, measured by the pipeline)

* 23 exam variants in 11 categories · 103 sections · 30 topics
* 2,476 unique questions · 13,763 question rows (assignments) · 7,893 answers
* 830 distinct pictures (925 official file names; 234 MB PNG, 20 MB WebP) · 57 videos (350 MB)
* 25 groups of identical content under different ИААА IDs (reported, not merged)
* AvtoIzpit cross-check: 1,166 questions, 0 differences; section quotas observed for 22 variants

## Known limitations

* The source grants no licence; content is published by maintainer decision (DATA_NOTICE.md).
* Pass marks of the six loss-of-licence variants follow the category rule (not stated separately).
* C1 and D (103) section quotas follow the live simulator (the draft methodology differs).
* C1+E has no AvtoIzpit counterpart: law-only parameters, no observed points mix.
* No explanations exist in the source.

## Next actions

* Keep publishing editions through the `release` workflow when the daily `validation` job reports a new array.

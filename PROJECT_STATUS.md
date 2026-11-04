# Project status — bulgarian-driving-exam-database

_Last updated: 2026-11-04_

## Current phase

**Phase 1 — Setup and architecture** (in progress)

## Completed work

* Public GitHub repository created: https://github.com/slaviboy/bulgarian-driving-exam-database
* Licence (MIT, code only), data notice, data contract v1 draft, architecture document.

## Pending work

* Phase 2 — Source investigation report, licensing record, exam-rule research, AvtoIzpit metadata + sample.
* Phase 3 — Extraction engine (HTTP client, discovery, parser, downloads).
* Phase 4 — Database, JSON exports, manifest, validation and reports.
* Phase 5 — Documentation, CI, media release and dataset release `v1.0.0`.

## Tests

* Passed: none yet (no code yet).
* Failed: none.

## Data counts

Measured during planning (read-only survey of edition 2026-10-01, not yet produced by the pipeline):
23 variant files · 13,763 question rows · 2,476 unique question IDs · 925 PNG (239 MB) · 57 MP4 (350 MB).

## Known limitations

* The source grants no licence; content is published by maintainer decision (see DATA_NOTICE.md).
* Exam parameters for loss-of-licence variants and the "(След 07.02.26г.)" D variants are not yet verified.

## Next actions

* Commit Phase 1, push, then start Phase 2.

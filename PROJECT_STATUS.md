# Project status — bulgarian-driving-exam-database

_Last updated: 2026-11-04_

## Current phase

**Phase 3 — Extraction engine** (next). Phases 1 and 2 are complete.

## Completed work

* **Phase 1 — Setup:** public repository, MIT licence (code only), `DATA_NOTICE.md`, data contract
  v1 (`docs/data-contract.md`), architecture (`docs/architecture.md`).
* **Phase 2 — Investigation:**
  * Python project skeleton, polite HTTP client (rate limits, retries, conditional and resumable
    downloads), discovery of the official manifest, AvtoIzpit metadata, Playwright network capture.
  * `docs/source-investigation.md` — structure, counts and HTTP behaviour of both sources.
  * `docs/licensing.md` — no licence found; publication by maintainer decision recorded.
  * `docs/exam-rules.md` — rules for all 23 variants with citations (Наредба № 38, ИААА
    methodology draft, AvtoIzpit observations).
  * Evidence in `reports/investigation/` (network capture, AvtoIzpit sub-categories and plan
    matches, sample summary, methodology quota tables).

## Pending work

* Phase 3 — HTML parser, resumable download of all files and assets, normalised records.
* Phase 4 — SQLite/JSON exports, manifest, schemas, validation, reports, source comparison,
  exam configurations with feasibility checks.
* Phase 5 — Documentation, CI, media release and dataset release `v1.0.0`.

## Tests

* Passed: 30 (HTTP client, discovery, normalisation/IDs).
* Failed: none.

## Data counts

From the investigation of edition 2026-10-01 (pipeline output follows in Phase 4):
23 variant files · 13,763 question rows · 2,476 unique question IDs · 925 PNG (239.0 MB) ·
57 MP4 (350.2 MB) · AvtoIzpit: 25 sub-categories, 22/23 variants matched, 44 test sets sampled.

## Known limitations

* The source grants no licence; content is published by maintainer decision (see DATA_NOTICE.md).
* Pass marks of the six loss-of-licence variants follow the category rule (not stated separately).
* Methodology Таблица 17 (C1) is internally inconsistent; C1 section quotas await observation mapping.
* C1+E has no AvtoIzpit counterpart (law-only parameters, no observed points mix).

## Next actions

* Implement the strict official HTML parser with fixtures, then the full download.

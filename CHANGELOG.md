# Changelog

All notable changes to the tooling, the data contract and the published datasets. Versions follow
[Semantic Versioning](https://semver.org/): dataset MAJOR = contract `schema_version` change, MINOR =
new official edition or questions added/removed, PATCH = corrections and metadata.

## [Unreleased]

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

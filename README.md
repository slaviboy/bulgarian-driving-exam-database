# bulgarian-driving-exam-database

Open-source tools, structured data schemas and versioned resources for Bulgarian driving licence
examination question banks.

[![tests](https://github.com/slaviboy/bulgarian-driving-exam-database/actions/workflows/tests.yml/badge.svg)](https://github.com/slaviboy/bulgarian-driving-exam-database/actions/workflows/tests.yml)
[![validation](https://github.com/slaviboy/bulgarian-driving-exam-database/actions/workflows/validation.yml/badge.svg)](https://github.com/slaviboy/bulgarian-driving-exam-database/actions/workflows/validation.yml)

This repository turns the official theory-exam question array of the Executive Agency
"Automobile Administration" (**ИААА**,
[public-eis.rta.government.bg/exam-questions](https://public-eis.rta.government.bg/exam-questions/))
into a validated, versioned dataset — JSON, SQLite and media packs — with full provenance, and keeps
it up to date.

> **Read [DATA_NOTICE.md](DATA_NOTICE.md) before reusing the question content.** ИААА publishes the
> array without a licence; it is republished here with attribution by decision of the maintainer.
> This project is not affiliated with ИААА. The MIT licence covers the code only.

## The dataset (v1.0.0, edition 2026-10-01)

| | |
|---|---|
| Exam variants (official files) | 23 in 11 categories: A, AM, B, C, C+E, C1, C1+E, D, D (103), D+E, Ттм |
| Questions | 2,476 unique (13,763 question rows across the variants) |
| Answers | 7,893 — multi-correct questions included, every question has ≥ 1 correct answer |
| Media | 830 pictures (234 MB PNG / 20 MB WebP) and 57 videos (350 MB) |
| Exam rules | official parameters for all 23 variants, each value cited (Наредба № 38, ИААА methodology, simulator observation) |

Download the latest release:

```
https://github.com/slaviboy/bulgarian-driving-exam-database/releases/latest/download/manifest.json
```

| File | Content |
|---|---|
| `manifest.json` | versions, counts, checksums of every file, media packs, source snapshot, licensing, completeness |
| `categories.json` | categories → exam variants → sections, topics |
| `questions.json` | questions with answers, media references, per-variant points/section/position; media metadata |
| `exam-configs.json` | exam rules per variant (questions, points, pass mark, duration, quotas, evidence) |
| `master.sqlite` | the same data in plain SQLite (schema in [docs/data-contract.md](docs/data-contract.md)) |
| `dataset-core-vX.Y.Z.zip` | all of the above in one archive |

Media are published in a separate release per edition (`media-2026.10.01`): `images-original.zip`,
`images-webp.zip` and every video as `<media id>.mp4`.

## Why points live on the variant, not the question

The same ИААА question appears in up to 11 exam variants. Its text, answers, correct markings and
media are identical everywhere, but **its points differ between variants for 1,211 questions and its
section for 1,041**. The dataset therefore separates canonical questions from per-variant assignments
— see [docs/data-contract.md §3](docs/data-contract.md).

## Quality

Every build is validated (missing questions/answers, correct-answer mapping, media files and
checksums, duplicates, references, ordering, attribution, JSON Schema conformance, SQLite integrity,
and a constructive feasibility proof of every exam configuration) — see `reports/`:

* [validation-report.md](reports/validation-report.md) · [extraction-report.md](reports/extraction-report.md) ·
  [category-counts.json](reports/category-counts.json) · [dataset-diff.md](reports/dataset-diff.md)
* [source-comparison.md](reports/source-comparison.md): 44 test sets of ИААА's online simulator
  (avtoizpit.com) — 1,166 questions compared, **0 differences**.

## Documentation

| Document | |
|---|---|
| [docs/architecture.md](docs/architecture.md) | pipeline and architectural decisions |
| [docs/data-contract.md](docs/data-contract.md) | identifiers, tables, files, hashing, versioning |
| [docs/android-import-spec.md](docs/android-import-spec.md) | how apps must verify and import releases |
| [docs/source-investigation.md](docs/source-investigation.md) | what the sources contain and how they behave |
| [docs/licensing.md](docs/licensing.md) | licensing findings and the publication decision |
| [docs/exam-rules.md](docs/exam-rules.md) | official exam parameters with citations |
| [docs/releasing.md](docs/releasing.md) | how releases are made |

## Using the tools

```
python -m venv .venv && .venv/Scripts/activate      # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .

qb discover            # list the official files of the current edition
qb extract             # download (incremental, resumable, 1 request/s) and parse them
qb media               # download pictures and videos, verify copies in other directories
qb build --dataset-version 1.0.0
qb verify              # re-verify exports, schemas, SQLite and the licensing gate
pytest -q
```

Opt-in research commands: `qb capture` (Playwright network capture), `qb avtoizpit metadata|sample|summarize`
(small, rate-limited sampling of the official simulator), `qb compare`, `qb rules methodology`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Question content is never edited by hand — report data
problems with the *Data issue* template.

## License

Code, schemas and documentation: [MIT](LICENSE). Question content: no licence — see
[DATA_NOTICE.md](DATA_NOTICE.md).

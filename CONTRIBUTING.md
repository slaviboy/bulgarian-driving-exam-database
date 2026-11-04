# Contributing

Thank you for helping keep the Bulgarian driving-exam question bank accurate and usable.

## Ground rules

* **The official ИААА array is the only source of question content.** Never add, reword or "fix"
  questions, answers or correct-answer markings by hand. If you believe the official data is wrong,
  open a *Data issue* — the dataset mirrors the source, errors included, and differences are
  documented instead.
* **Every exam-rule number needs a citation** (Наредба № 38 article, ИААА methodology paragraph or
  table, or an AvtoIzpit observation) in `data/exam-rules/exam-configs.source.json` and
  `docs/exam-rules.md`.
* Be polite to the sources: keep the rate limits in `question_bank/config.py`, never call
  authenticated or personal endpoints (e.g. AvtoIzpit vouchers), and keep AvtoIzpit sampling to the
  documented small, opt-in amount.

## Development setup

```
python -m venv .venv
.venv/Scripts/activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements-dev.txt
pip install -e .
pytest -q
ruff check question_bank tests && ruff format --check question_bank tests
```

## Building the dataset locally

```
qb extract                       # download (incrementally) and parse the 23 official files
qb media                         # download pictures and videos, verify copies
qb build --dataset-version X.Y.Z # exports, media packs, manifest, reports; fails on validation errors
qb verify                        # re-verify the exports (what CI runs)
```

## Pull requests

* Keep changes focused; include tests for parser, validator or builder changes.
* If the contract changes, regenerate the schemas (`qb schemas`) and update `docs/data-contract.md`
  and `CHANGELOG.md`. Breaking changes require a new `schema_version`.
* CI must be green (`tests`, `validation`).

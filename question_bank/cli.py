"""Command-line entry point: `qb <command>` (see `qb --help`)."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from question_bank import __version__
from question_bank.config import Settings, load_settings
from question_bank.fsutil import write_json
from question_bank.logging_setup import configure_logging

log = logging.getLogger("qb")

# Release gate: content is only published when its source status is in this allow-list (docs/licensing.md).
ALLOWED_REDISTRIBUTION = {"published_by_maintainer_decision", "permitted"}


def _write_json(path: Path, payload: Any) -> None:
    write_json(path, payload)


def _client(settings: Settings):
    from question_bank.extractor.clients.http import HttpClient

    return HttpClient(settings)


# ----------------------------------------------------------------------------- commands


def cmd_discover(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.extractor.discovery.official import discover_official

    with _client(settings) as client:
        manifest = discover_official(client)
    summary = {
        "discovered_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "index_url": manifest.index_url,
        "manifest_url": manifest.manifest_url,
        "manifest_sha256": manifest.sha256,
        "editions": sorted(str(e) for e in manifest.editions),
        "files": [asdict(f) | {"edition": str(f.edition)} for f in manifest.files],
    }
    _write_json(settings.cache_dir / "official-manifest.json", summary)
    for f in manifest.files:
        print(f"{f.order:>3}  {f.edition}  {f.category_token:<5} {f.description_words}")
    print(f"{len(manifest.files)} files, editions {summary['editions']}")
    return 0


def cmd_extract(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.extractor.pipeline import extract_official

    with _client(settings) as client:
        _manifest, extracted = extract_official(settings, client, force=args.force)
        requests = client.request_count
    total = sum(len(e.parsed.questions) for e in extracted)
    unique = len({q.original_id for e in extracted for q in e.parsed.questions})
    warnings = sum(len(e.parsed.warnings) for e in extracted)
    for e in extracted:
        counts = f"q={len(e.parsed.questions):>5}  s={len(e.parsed.sections)}"
        print(f"{e.source.order:>3}  {counts}  {e.parsed.title}")
    print(f"{len(extracted)} files · {total} question rows · {unique} unique IDs · {warnings} warnings")
    print(f"HTTP requests: {requests}")
    return 0


def cmd_media(settings: Settings, args: argparse.Namespace) -> int:
    from dataclasses import asdict as _asdict

    from rich.progress import BarColumn, MofNCompleteColumn, Progress, TextColumn, TimeRemainingColumn

    from question_bank.extractor.downloaders.media import collect_asset_refs, download_assets, verify_copies
    from question_bank.extractor.pipeline import load_extracted

    extracted = load_extracted(settings)
    if not extracted:
        raise SystemExit("run `qb extract` first")
    refs = collect_asset_refs(extracted)
    stats = {"downloaded": 0, "resumed": 0, "cached": 0, "bytes": 0}
    with _client(settings) as client:
        columns = [TextColumn("{task.description}"), BarColumn(), MofNCompleteColumn(), TimeRemainingColumn()]
        with Progress(*columns) as progress:
            task = progress.add_task("media", total=len(refs))

            def on_item(name, outcome):
                stats["downloaded" if outcome.downloaded else "cached"] += 1
                stats["resumed"] += int(outcome.resumed)
                stats["bytes"] += outcome.record.bytes
                progress.update(task, advance=1, description=name[:24].ljust(24))

            records = download_assets(settings, client, refs, progress=on_item)
        checks = [] if args.skip_verify else verify_copies(settings, client, refs, records)
        requests = client.request_count
    mismatches = [c for c in checks if not c.identical]
    _write_json(
        settings.cache_dir / "media-copy-checks.json",
        {"checked": len(checks), "mismatches": len(mismatches), "checks": [_asdict(c) for c in checks]},
    )
    print(
        f"{len(refs)} assets ({stats['bytes'] / 1e6:.1f} MB): {stats['downloaded']} downloaded "
        f"({stats['resumed']} resumed), {stats['cached']} already present; HTTP requests: {requests}"
    )
    print(f"copies verified: {len(checks)}, mismatches: {len(mismatches)}")
    return 1 if mismatches else 0


def cmd_schemas(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.build import write_schemas

    for path in write_schemas():
        print(f"wrote {path}")
    return 0


def cmd_verify(settings: Settings, args: argparse.Namespace) -> int:
    """Offline re-verification of the committed exports (used by CI)."""
    import jsonschema

    from question_bank.build import SCHEMAS_DIR, schema_documents
    from question_bank.exporter.json_export import FILE_NAMES
    from question_bank.fsutil import read_json
    from question_bank.processor.validation.validators import (
        ValidationReport,
        validate_exports,
        validate_manifest,
    )

    exports = settings.exports_dir
    problems = [i.message for i in validate_manifest(exports / FILE_NAMES["manifest"], exports)]
    for name, text in schema_documents().items():
        if (SCHEMAS_DIR / name).read_text(encoding="utf-8") != text:
            problems.append(f"contract/schemas/{name} is out of date (run `qb schemas`)")
    manifest = read_json(exports / FILE_NAMES["manifest"])
    jsonschema.validate(manifest, read_json(SCHEMAS_DIR / "manifest.schema.json"))
    if manifest["licensing"]["redistribution_status"] not in ALLOWED_REDISTRIBUTION:
        problems.append(
            f"redistribution status {manifest['licensing']['redistribution_status']!r} not allowed"
        )
    if manifest["completeness"]["status"] != "complete":
        problems.append("manifest completeness is not 'complete'")
    report = ValidationReport()
    paths = {k: exports / FILE_NAMES[k] for k in ("categories", "questions", "exam_configs", "sqlite")}
    validate_exports(report, paths, SCHEMAS_DIR)
    problems += [i.message for i in report.issues if i.severity == "error"]
    for problem in problems:
        print(f"FAIL {problem}")
    print(
        f"verified {len(manifest['files'])} files of dataset {manifest['dataset_version']}: "
        f"{'OK' if not problems else f'{len(problems)} problems'}"
    )
    return 1 if problems else 0


def cmd_build(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.build import run_build

    result = run_build(
        settings, args.dataset_version, webp=not args.no_webp, translations_dir=args.translations_dir
    )
    m = result.manifest
    print(f"dataset {m.dataset_version} · edition {m.source_edition} · completeness: {m.completeness.status}")
    print("counts: " + ", ".join(f"{k}={v}" for k, v in m.counts.items()))
    print(
        f"validation: {result.report.error_count} errors, {result.report.warning_count} warnings · "
        f"diff vs previous export: {result.diff}"
    )
    for check in m.completeness.checks:
        if not check.passed:
            print(f"  FAILED {check.name}: {check.detail}")
    print("release folders: " + ", ".join(str(p) for p in result.release_dirs))
    return 0 if result.report.ok and m.completeness.status == "complete" else 1


def cmd_compare(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.build import EXAM_RULES
    from question_bank.extractor.pipeline import load_extracted
    from question_bank.fsutil import read_json
    from question_bank.reports.comparison import compare_samples, write_comparison

    tables_path = settings.reports_dir / "investigation" / "methodology-2024-tables.json"
    result = compare_samples(
        load_extracted(settings),
        settings.data_dir / "avtoizpit" / "samples",
        read_json(EXAM_RULES),
        read_json(tables_path) if tables_path.exists() else None,
    )
    write_comparison(result, settings.reports_dir)
    print(result["summary"])
    for order, item in result["evidence"].items():
        method = [s["matches_methodology"] for s in item["samples"]]
        config = [s["matches_configuration"] for s in item["samples"]]
        print(f"#{order:>2} methodology {method} configured {config} observed {item['observed_quotas']}")
    return 0


def cmd_capture(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.extractor.discovery.browser_capture import capture_network, write_capture

    records = capture_network()
    out = settings.reports_dir / "investigation" / "network-capture.json"
    write_capture(records, out)
    print(f"{len(records)} requests recorded → {out}")
    return 0


def cmd_avtoizpit_metadata(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.extractor.discovery.avtoizpit import fetch_sub_categories, match_learning_plans
    from question_bank.extractor.discovery.official import discover_official

    with _client(settings) as client:
        raw, subs = fetch_sub_categories(client)
        manifest = discover_official(client)
    inv = settings.reports_dir / "investigation"
    _write_json(inv / "avtoizpit-sub-categories.json", raw)
    matches = match_learning_plans(manifest.files, subs)
    rows = [
        {
            "official_order": m.official_order,
            "official_file": m.official_file,
            "avtoizpit_sub_category": m.sub_category.name if m.sub_category else None,
            "sub_category_id": m.sub_category.id if m.sub_category else None,
            "learning_plan_id": m.learning_plan.id if m.learning_plan else None,
            "learning_plan": m.learning_plan.description if m.learning_plan else None,
            "candidates": m.candidates,
        }
        for m in matches
    ]
    _write_json(inv / "avtoizpit-plan-matches.json", rows)
    matched = sum(1 for m in matches if m.learning_plan)
    print(f"{len(subs)} AvtoIzpit sub-categories; {matched}/{len(matches)} official variants matched")
    for r in rows:
        if not r["learning_plan_id"]:
            print(f"  unmatched: #{r['official_order']} {r['official_file']} (candidates: {r['candidates']})")
    return 0


def cmd_avtoizpit_sample(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.extractor.discovery.avtoizpit import (
        assess_without_answers,
        fetch_sub_categories,
        generate_test_set,
        match_learning_plans,
    )
    from question_bank.extractor.discovery.official import discover_official

    if not 1 <= args.per_plan <= 3:
        raise SystemExit("--per-plan must be between 1 and 3 (agreed sampling limit)")
    out_dir = settings.data_dir / "avtoizpit" / "samples"
    only = {int(x) for x in args.only.split(",")} if args.only else None
    with _client(settings) as client:
        _raw, subs = fetch_sub_categories(client)
        manifest = discover_official(client)
        for m in match_learning_plans(manifest.files, subs):
            if not m.learning_plan or (only and m.official_order not in only):
                continue
            for n in range(1, args.per_plan + 1):
                target = out_dir / f"{m.official_order:02d}-plan{m.learning_plan.id}-{n}.json"
                if target.exists():
                    continue  # resume: never re-request a sample we already have
                test_set = generate_test_set(client, m.sub_category.id, m.learning_plan.id)
                record: dict[str, Any] = {
                    "official_order": m.official_order,
                    "official_file": m.official_file,
                    "sub_category_id": m.sub_category.id,
                    "learning_plan_id": m.learning_plan.id,
                    "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                    "test_set": test_set,
                }
                if args.assess:
                    record["assessment"] = assess_without_answers(client, test_set)
                _write_json(target, record)
                print(f"saved {target.name}")
        print(f"requests sent this run: {client.request_count}")
    return 0


def cmd_avtoizpit_summarize(settings: Settings, args: argparse.Namespace) -> int:
    """Reduce the raw samples (gitignored) to numbers only: counts, points mix, duration, videos."""
    from collections import Counter

    from question_bank.fsutil import read_json

    samples = sorted((settings.data_dir / "avtoizpit" / "samples").glob("*.json"))
    rows = []
    for path in samples:
        record = read_json(path)
        test_set = record["test_set"]
        questions = test_set["questions"]
        result = (record.get("assessment") or {}).get("result") or {}
        points = Counter(int(q["points"]) for q in questions)
        rows.append(
            {
                "sample": path.stem,
                "official_order": record["official_order"],
                "sub_category": test_set["subCategory"]["name"],
                "learning_plan_id": record["learning_plan_id"],
                "generated_at": record["generated_at"],
                "question_count": len(questions),
                "total_points": sum(int(q["points"]) for q in questions),
                "points_mix": {str(k): points[k] for k in sorted(points)},
                "exam_duration_minutes": test_set["subCategory"].get("examDurationMinutes"),
                "assessed_total_points": result.get("totalPoints"),
                "video_questions": sum(1 for q in questions if q.get("videoFileId")),
                "picture_questions": sum(1 for q in questions if q.get("pictureId")),
                "multi_correct_questions": sum(1 for q in questions if int(q["correctAnswersCount"]) > 1),
            }
        )
    out = settings.reports_dir / "investigation" / "avtoizpit-sample-summary.json"
    _write_json(out, {"samples": len(rows), "rows": rows})
    print(f"{len(rows)} samples summarised → {out}")
    return 0


def cmd_rules_methodology(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.exam_rules.methodology import METHODOLOGY_URL, extract_tables
    from question_bank.fsutil import sha256_file

    pdf = settings.cache_dir / "rules" / "Metodika_izpiti.pdf"
    if not pdf.exists():
        with _client(settings) as client:
            client.download(METHODOLOGY_URL, pdf)
    tables = extract_tables(pdf)
    out = settings.reports_dir / "investigation" / "methodology-2024-tables.json"
    _write_json(
        out,
        {
            "source_url": METHODOLOGY_URL,
            "source_sha256": sha256_file(pdf),
            "document_status": "draft ('Проект!', approving order number left blank)",
            "tables": tables,
        },
    )
    inconsistent = [t["table"] for t in tables if not t["consistent"]]
    print(f"{len(tables)} quota tables → {out}; internally inconsistent: {inconsistent or 'none'}")
    return 0


def cmd_translations_prepare(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.translations.prepare import prepare

    index = prepare(settings.exports_dir, settings.media_dir, args.out, parts=args.parts)
    print(
        f"{index['questions']} questions, {index['text_answers']} text answers "
        f"in {len(index['parts'])} parts → {args.out / 'source'}"
    )
    return 0


def cmd_translations_lint(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.translations import lint

    argv = ["--work", str(args.work), "--lang", args.lang, *args.rest]
    return lint.main(argv)


def cmd_translations_merge(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.translations.curated import MergeRefused, merge

    try:
        for code in args.lang.split(","):
            kwargs = {"curated_dir": args.curated_dir} if args.curated_dir else {}
            stats = merge(
                args.work,
                code.strip(),
                settings.exports_dir,
                allow_incomplete=args.allow_incomplete,
                **kwargs,
            )
            print(
                f"{stats['language']}: {stats['questions']} questions, {stats['answers']} answers merged "
                f"({stats['warnings']} lint warnings, {stats['accepted_exceptions']} accepted exceptions)"
            )
    except MergeRefused as e:
        print(f"refused: {e}")
        return 1
    return 0


def cmd_translations_status(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.fsutil import read_json
    from question_bank.translations import curated
    from question_bank.translations.lint import LANGUAGES

    bank = {
        q["id"]: q["content_hash"] for q in read_json(settings.exports_dir / "questions.json")["questions"]
    }
    print(f"{'lang':<5} {'current':>8} {'stale':>6} {'missing':>8}")
    for code in curated.languages():
        hashes = {qid: e["source_hash"] for qid, e in curated.load(code).questions.items()}
        current = sum(1 for qid, h in bank.items() if hashes.get(qid) == h)
        stale = sum(1 for qid, h in bank.items() if qid in hashes and hashes[qid] != h)
        missing = len(bank) - current - stale
        print(f"{code:<5} {current:>8} {stale:>6} {missing:>8}  {LANGUAGES[code].english_name}")
    return 0


# ----------------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qb", description=__doc__)
    parser.add_argument("--version", action="version", version=f"qb {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug output on the console")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="read the official index and manifest.txt").set_defaults(
        func=cmd_discover
    )
    extract = sub.add_parser("extract", help="download (incrementally) and parse every official variant file")
    extract.add_argument("--force", action="store_true", help="download again even if unchanged")
    extract.set_defaults(func=cmd_extract)
    media = sub.add_parser("media", help="download all referenced pictures and videos, verify copies")
    media.add_argument("--skip-verify", action="store_true", help="skip the cross-directory copy check")
    media.set_defaults(func=cmd_media)
    sub.add_parser("schemas", help="(re)generate contract/schemas from the models").set_defaults(
        func=cmd_schemas
    )
    sub.add_parser("compare", help="compare AvtoIzpit samples with the official array").set_defaults(
        func=cmd_compare
    )
    sub.add_parser("verify", help="re-verify committed exports offline (CI)").set_defaults(func=cmd_verify)
    build = sub.add_parser("build", help="build exports, media packs, manifest and reports; validate")
    build.add_argument("--dataset-version", required=True, help="semantic version of this dataset build")
    build.add_argument("--no-webp", action="store_true", help="skip WebP derivatives (faster, for testing)")
    build.add_argument(
        "--translations-dir",
        type=Path,
        help="curated translations to use instead of data/translations (testing)",
    )
    build.set_defaults(func=cmd_build)
    sub.add_parser("capture", help="record the source pages' network requests (Playwright)").set_defaults(
        func=cmd_capture
    )

    avtoizpit = sub.add_parser("avtoizpit", help="AvtoIzpit metadata and opt-in sampling")
    av_sub = avtoizpit.add_subparsers(dest="avtoizpit_command", required=True)
    av_sub.add_parser(
        "metadata", help="GET public sub-categories and match them to official variants"
    ).set_defaults(func=cmd_avtoizpit_metadata)
    sample = av_sub.add_parser("sample", help="opt-in: generate a few test sets per matched variant")
    sample.add_argument("--per-plan", type=int, default=2, help="test sets per learning plan (1-3)")
    sample.add_argument(
        "--assess", action="store_true", help="also submit each set unanswered to see the result"
    )
    sample.add_argument("--only", help="comma-separated official order numbers to sample")
    sample.set_defaults(func=cmd_avtoizpit_sample)
    av_sub.add_parser("summarize", help="numbers-only summary of the collected samples").set_defaults(
        func=cmd_avtoizpit_summarize
    )

    rules = sub.add_parser("rules", help="exam-rule research tools")
    rules_sub = rules.add_subparsers(dest="rules_command", required=True)
    rules_sub.add_parser(
        "methodology", help="extract the per-section quota tables from the ИААА methodology PDF (dev extra)"
    ).set_defaults(func=cmd_rules_methodology)

    translations = sub.add_parser("translations", help="work packages and checks for translations")
    tr_sub = translations.add_subparsers(dest="translations_command", required=True)
    prep = tr_sub.add_parser(
        "prepare", help="split the exported question bank into translation work packages"
    )
    prep.add_argument("--out", type=Path, required=True, help="work folder (source/ is written inside it)")
    prep.add_argument("--parts", type=int, default=25, help="number of parts (default 25)")
    prep.set_defaults(func=cmd_translations_prepare)
    lint_p = tr_sub.add_parser("lint", help="check a language in a work folder (same as tools/lint.py)")
    lint_p.add_argument("--work", type=Path, required=True)
    lint_p.add_argument("--lang", required=True)
    lint_p.add_argument(
        "rest", nargs=argparse.REMAINDER, help="--part N | --labels | --ui | --all | --coverage"
    )
    lint_p.set_defaults(func=cmd_translations_lint)
    merge_p = tr_sub.add_parser("merge", help="write data/translations/<lang>/ from a finished work package")
    merge_p.add_argument("--work", type=Path, required=True)
    merge_p.add_argument("--lang", required=True, help="language code(s), comma-separated")
    merge_p.add_argument("--curated-dir", type=Path, help="write here instead of data/translations (testing)")
    merge_p.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="merge finished parts only (test builds, never releases)",
    )
    merge_p.set_defaults(func=cmd_translations_merge)
    tr_sub.add_parser("status", help="current, stale and missing translations per language").set_defaults(
        func=cmd_translations_status
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    configure_logging(settings.log_dir, verbose=args.verbose)
    return int(args.func(settings, args) or 0)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

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
    if (settings.data_dir / "enhance" / "pack.json").exists():
        from question_bank.media_enhance.pack import install_pinned

        with _client(settings) as client:
            result = install_pinned(
                settings.data_dir / "enhance",
                settings.media_dir,
                settings.data_dir.parent / "release",
                settings.cache_dir / "media-packs",
                client,
            )
        print(f"enhanced pictures of {result['tag']}: {result['files']} files verified and installed")
    return 1 if mismatches else 0


def cmd_schemas(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.build import write_schemas

    for path in write_schemas():
        print(f"wrote {path}")
    return 0


def _verify_explanations(exports: Path) -> list[str]:
    """Every quote of the curated explanations is word for word in the corpus; the export fits its schema."""
    from question_bank.build import SCHEMAS_DIR
    from question_bank.explanations import curated
    from question_bank.explanations.export import FILE_NAME, validate_explanation_exports
    from question_bank.legal.corpus import load as load_corpus

    problems = []
    entries = curated.load()
    if entries:
        corpus = load_corpus()
        for question_id, entry in entries.items():
            for ref in entry["references"]:
                result = corpus.check(ref["act"], ref["unit"], ref["quote"])
                if not result.ok:
                    problems.append(f"explanation {question_id}: {result.message}")
    exported = exports / FILE_NAME
    if exported.exists():
        problems += [i.message for i in validate_explanation_exports([exported], SCHEMAS_DIR)]
    return problems


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
    problems += _verify_explanations(exports)
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


def cmd_explanations_prepare(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.explanations.prepare import prepare

    only = [s.strip() for s in args.only.split(",")] if args.only else None
    index = prepare(
        settings.exports_dir,
        settings.media_dir,
        args.out,
        args.category,
        part_size=args.part_size,
        redo=args.redo,
        only=only,
    )
    parts = len(index["parts"])
    print(f"{index['questions']} questions of category {args.category} in {parts} parts → {args.out}")
    return 0


def _explanation_findings(settings: Settings, entries: dict, expected: list[str] | None):
    from question_bank.explanations.bank import load_bank
    from question_bank.explanations.lint import check_all
    from question_bank.legal.corpus import load

    bank, _, _ = load_bank(settings.exports_dir)
    return check_all(entries, bank, load(), expected)


def cmd_explanations_lint(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.fsutil import read_json

    index = read_json(args.work / "source" / "index.json")
    parts = [args.part] if args.part else [p["part"] for p in index["parts"]]
    errors = 0
    for part in parts:
        out = args.work / "out" / f"part-{part:02d}.json"
        source = read_json(args.work / "source" / f"part-{part:02d}.json")
        if not out.exists():
            print(f"part {part}: {out.name} not written yet")
            errors += 1
            continue
        entries = read_json(out)["explanations"]
        findings = _explanation_findings(settings, entries, [q["id"] for q in source["questions"]])
        part_errors = sum(1 for f in findings if f.level == "error")
        errors += part_errors
        for finding in findings:
            print(f"part {part}: {finding}")
        print(f"part {part}: {len(entries)} entries, {part_errors} errors")
    return 1 if errors else 0


def cmd_explanations_merge(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.explanations.curated import MergeRefused, merge
    from question_bank.legal.corpus import load

    try:
        stats = merge(args.work, settings.exports_dir, load(), [args.part] if args.part else None)
    except MergeRefused as e:
        print(f"refused: {e}")
        return 1
    print(
        f"{stats['parts']} parts: {stats['explanations']} explanations, "
        f"{stats['conflicts']} conflicts merged; "
        f"{stats['total']} explanations in data/explanations/bg"
    )
    return 0


def cmd_explanations_status(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.explanations import curated
    from question_bank.explanations.bank import load_bank

    bank, _, _ = load_bank(settings.exports_dir)
    explanations, conflicts = curated.load(), curated.load_conflicts()
    categories = sorted({c for q in bank.values() for c in q.categories})
    print(f"{'category':<9} {'questions':>9} {'current':>8} {'stale':>6} {'conflicts':>9} {'missing':>8}")
    for category in categories:
        ids = [q.id for q in bank.values() if category in q.categories]
        hashes = {i: explanations[i]["source_hash"] for i in ids if i in explanations}
        current = sum(1 for i, h in hashes.items() if h == bank[i].content_hash)
        stale = len(hashes) - current
        conflict = sum(1 for i in ids if i in conflicts)
        missing = len(ids) - current - stale - conflict
        print(f"{category:<9} {len(ids):>9} {current:>8} {stale:>6} {conflict:>9} {missing:>8}")
    findings = _explanation_findings(settings, explanations, None)
    errors = [f for f in findings if f.level == "error"]
    for finding in errors:
        print(finding)
    print(f"curated: {len(explanations)} explanations, {len(conflicts)} conflicts, {len(errors)} errors")
    return 1 if errors else 0


def cmd_legal_import(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.legal.corpus import write_act
    from question_bank.legal.extract import text_of
    from question_bank.legal.parse import parse

    parsed = parse(text_of(args.file))
    entry = write_act(parsed, args.act, args.file)
    print(
        f"{entry['short']}: {entry['units']} units, consolidated to {entry['consolidated_to']}, "
        f"{len(parsed.repealed)} repealed → data/legal/{args.act}.json"
    )
    return 0


def cmd_legal_status(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.legal.corpus import load

    corpus = load()
    for entry in corpus.meta["acts"]:
        act = corpus.acts.get(entry["id"])
        units = len(act.units) if act else 0
        consolidated = entry.get("consolidated_to") or "-"
        print(f"{entry['id']:<8} {entry['short']:<26} {units:>5} units  {consolidated}")
        print(f"{'':<8} later amendments: {entry.get('later_amendments', '-')}")
    return 0


def cmd_legal_show(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.legal.corpus import load

    act = load().acts[args.act]
    found = act.resolve(args.unit)
    if found is None:
        print(f"{act.short}: {args.unit} does not exist")
        return 1
    unit, text = found
    print(f"{act.short}, {unit}: {text}")
    return 0


def cmd_legal_search(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.legal.corpus import load

    corpus = load()
    acts = [args.act] if args.act else list(corpus.acts)
    for act_id in acts:
        for unit, text in corpus.search(act_id, args.words, limit=args.limit):
            print(f"[{act_id}] {unit}: {text[:300]}")
    return 0


def _enhance_dir(settings: Settings) -> Path:
    """Committed inputs and decisions of the picture enhancement."""
    return settings.data_dir / "enhance"


def _picture_paths(settings: Settings, only: str | None = None) -> list[Path]:
    paths = sorted((settings.media_dir / "images").glob("m-*.png"))
    if only:
        wanted = {s.strip() for s in only.split(",")}
        paths = [p for p in paths if p.stem in wanted]
    return paths


def cmd_enhance_stamp_fit(settings: Settings, args: argparse.Namespace) -> int:
    from PIL import Image

    from question_bank.media_enhance.fit import fit_shifts, measure_tile, refine_tile
    from question_bank.media_enhance.stamp import StampModel, save_shifts

    out = _enhance_dir(settings) / "stamp"
    paths = _picture_paths(settings)
    tile, stats = measure_tile(paths)
    print(
        f"tile: {stats['stamp_pixels']} stamp pixels, opacity ≤ {stats['max_opacity']}/255, "
        f"{stats['pictures']} pictures, exact agreement {stats['exact_agreement_median_stamp_pixels']:.0%}"
    )
    groups: dict[tuple[int, int], list[Path]] = {}
    for path in paths:
        with Image.open(path) as image:
            groups.setdefault(image.size, []).append(path)
    model = StampModel(tile)
    model.shifts = {(e["row"], e["col"], e["element"]): (e["dy"], e["dx"]) for e in fit_shifts(groups, model)}
    refined, refine_stats = refine_tile(paths, model)
    print(f"refined tile: {refine_stats['refined_pixels_changed']} pixels changed")
    model = StampModel(refined)
    entries = fit_shifts(groups, model)
    model.save_tile(out)
    save_shifts(out, entries, {"tile_statistics": stats, "refinement": refine_stats})
    moved = len({(e["row"], e["col"]) for e in entries if (e["dy"], e["dx"]) != (0, 0)})
    tiles = len({(e["row"], e["col"]) for e in entries})
    print(f"shifts: {tiles} tiles measured, {moved} off the regular lattice → {out}")
    return 0


def cmd_enhance_clean(settings: Settings, args: argparse.Namespace) -> int:
    from dataclasses import asdict as _asdict

    from question_bank.media_enhance.clean import clean_all, summary
    from question_bank.media_enhance.stamp import StampModel

    model = StampModel.load(_enhance_dir(settings) / "stamp")
    out = settings.media_dir / "enhance" / "clean"
    results = clean_all(_picture_paths(settings, args.only), model, out)
    report = summary(results)
    _write_json(out / "report.json", {**report, "pictures_detail": [_asdict(r) for r in results]})
    print(
        f"{report['pictures']} pictures cleaned → {out}; stamp score median "
        f"{report['score_before_median']} → {report['score_after_median']}, "
        f"max |after| {report['score_after_max_abs']}; {len(report['flagged'])} flagged for review"
    )
    return 0


def cmd_enhance_review(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.fsutil import read_json
    from question_bank.media_enhance.review import Row, write_sheet

    clean_dir = settings.media_dir / "enhance" / "clean"
    up_dir = settings.media_dir / "enhance" / "upscaled"
    report = read_json(clean_dir / "report.json")
    detail = {d["media_id"]: d for d in report["pictures_detail"]}
    up_report = up_dir / "report.json"
    upscaled = {d["media_id"]: d for d in read_json(up_report)["pictures"]} if up_report.exists() else {}
    ids = [s.strip() for s in args.only.split(",")] if args.only else sorted(detail)
    if args.flagged:
        ids = [f["media_id"] for f in report["flagged"]]
    rows = []
    for mid in ids[: args.limit]:
        d = detail[mid]
        images = [
            ("official", settings.media_dir / "images" / f"{mid}.png"),
            ("stamp removed", clean_dir / f"{mid}.png"),
        ]
        notes = [
            f"stamp score {d['score_before']} → {d['score_after']} · {d['changed_pixels']} pixels changed"
        ]
        if mid in upscaled:
            u = upscaled[mid]
            images.append((f"Real-ESRGAN, {u['scale']:g}×", up_dir / f"{mid}.png"))
            notes.append(
                f"content check: PSNR {u['blur_psnr']} dB (≥ 30), SSIM {u['ssim']} (≥ 0.9), "
                f"worst window {u['ssim_worst_window']}"
            )
        rows.append(Row(f"{mid} · {d['width']}×{d['height']}", images, notes, width=min(d["width"] * 2, 720)))
    out = settings.media_dir / "enhance" / "review" / f"{args.name}.html"
    lead = (
        "Official picture, stamp removed and enlarged, all shown at the same size. Zoom in to check details."
    )
    write_sheet(out, args.name, lead, rows)
    print(f"{len(rows)} rows → {out}")
    return 0


def cmd_enhance_upscale(settings: Settings, args: argparse.Namespace) -> int:
    from dataclasses import asdict as _asdict

    from question_bank.fsutil import read_json
    from question_bank.media_enhance.upscale import UpscaleResult, find_binary, scale_for_size, upscale_all

    clean_dir = settings.media_dir / "enhance" / "clean"
    out = settings.media_dir / "enhance" / args.into
    inventory = read_json(_enhance_dir(settings) / "inventory.json")["pictures"]
    classes = {c.strip() for c in args.classes.split(",")} if args.classes else None
    ids = [
        p.stem
        for p in _picture_paths(settings, args.only)
        if classes is None or inventory[p.stem]["class"] in classes
    ]
    scales = {
        mid: args.scale or scale_for_size(inventory[mid]["width"], inventory[mid]["height"]) for mid in ids
    }
    results = []
    for start in range(0, len(ids), args.batch):  # batches keep the temporary 4× files small
        chunk = ids[start : start + args.batch]
        results += upscale_all(clean_dir, out, find_binary(settings.data_dir), chunk, scales)
        print(f"  {min(start + args.batch, len(ids))}/{len(ids)}", flush=True)
    report_path = out / "report.json"
    previous = read_json_if_exists(report_path)
    fields = set(UpscaleResult.__dataclass_fields__)
    merged = {d["media_id"]: d for d in previous.get("pictures", []) if set(d) == fields}
    merged.update({r.media_id: _asdict(r) for r in results})
    flagged = [d for d in merged.values() if not UpscaleResult(**d).ok]
    pictures = sorted(merged.values(), key=lambda d: d["media_id"])
    _write_json(report_path, {"flagged": [d["media_id"] for d in flagged], "pictures": pictures})
    print(f"{len(results)} pictures enlarged → {out}; {len(flagged)} flagged by the content check")
    return 0


def read_json_if_exists(path: Path) -> dict:
    from question_bank.fsutil import read_json

    return read_json(path) if path.exists() else {}


def cmd_enhance_pack(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.exporter.packages import media_release_tag
    from question_bank.fsutil import read_json
    from question_bank.media_enhance.commons import load_catalogue
    from question_bank.media_enhance.pack import build

    edition = read_json(settings.exports_dir / "manifest.json")["source_edition"]
    tag = f"{media_release_tag(edition)}-r{args.revision}"
    result = build(
        _enhance_dir(settings),
        settings.media_dir,
        settings.data_dir.parent / "release",
        tag,
        commons_catalogue=load_catalogue(settings.cache_dir / "commons"),
    )
    for kind, pack in result["packs"].items():
        print(
            f"{kind}: {pack['file_count']} files, {pack['bytes'] / 2**20:.1f} MB, "
            f"sha256 {pack['sha256'][:12]}…"
        )
    print(
        f"{result['media']} pictures ({result['svg']} with SVG) → release/{tag}; "
        "pinned in data/enhance/pack.json"
    )
    return 0


def cmd_enhance_signs_build(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.media_enhance.signs import build_all

    out = settings.media_dir / "enhance" / "signs"
    report = build_all(
        _enhance_dir(settings),
        settings.cache_dir / "commons",
        out,
        only={s.strip() for s in args.only.split(",")} if args.only else None,
    )
    _write_json(out / "report.json", report)
    failed = [r for r in report["recipes"] if r.get("error")]
    for r in failed:
        print(f"{r['media_id']}: {r['error']}")
    composed = len(report["recipes"]) - len(failed)
    print(f"{composed} sign pictures composed → {out / 'svg'}; {len(failed)} failed")
    if args.sheet:
        from question_bank.media_enhance.review import Row, write_sheet

        rows = []
        for r in report["recipes"]:
            if r.get("error"):
                continue
            mid = r["media_id"]
            rows.append(
                Row(
                    f"{mid} · {r['width']}×{r['height']}",
                    [
                        ("official", settings.media_dir / "images" / f"{mid}.png"),
                        ("stamp removed", settings.media_dir / "enhance" / "clean" / f"{mid}.png"),
                        ("vector", out / "svg" / f"{mid}.svg"),
                    ],
                    r["sources"] + r["notes"],
                    width=min(r["width"] * 2, 720),
                )
            )
        sheet = settings.media_dir / "enhance" / "review" / f"{args.sheet}.html"
        write_sheet(sheet, args.sheet, "Official picture, stamp removed, and the vector version.", rows)
        print(f"review sheet → {sheet}")
    return 1 if failed else 0


def cmd_enhance_commons_import(settings: Settings, args: argparse.Namespace) -> int:
    from question_bank.media_enhance.commons import CommonsImportError, import_zip

    cache = settings.cache_dir / "commons"
    try:
        stats = import_zip(args.zip, cache)
    except CommonsImportError as e:
        print(f"refused: {e}")
        return 1
    print(
        f"{stats['imported']} of {stats['files']} sign drawings imported → {cache} "
        f"({stats['missing']} not downloaded, {stats['rejected']} rejected)"
    )
    return 1 if stats["rejected"] else 0


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

    explanations = sub.add_parser("explanations", help="work packages and checks for the explanations")
    ex_sub = explanations.add_subparsers(dest="explanations_command", required=True)
    ex_prep = ex_sub.add_parser("prepare", help="work packages of the questions of a category")
    ex_prep.add_argument("--out", type=Path, required=True, help="work folder (source/ and out/ inside it)")
    ex_prep.add_argument("--category", required=True, help="category id, e.g. B")
    ex_prep.add_argument("--part-size", type=int, default=100)
    ex_prep.add_argument("--redo", action="store_true", help="include questions that are already explained")
    ex_prep.add_argument("--only", help="comma-separated question numbers or IDs (a pilot)")
    ex_prep.set_defaults(func=cmd_explanations_prepare)
    ex_lint = ex_sub.add_parser("lint", help="check written parts of a work package")
    ex_lint.add_argument("--work", type=Path, required=True)
    ex_lint.add_argument("--part", type=int)
    ex_lint.set_defaults(func=cmd_explanations_lint)
    ex_merge = ex_sub.add_parser("merge", help="write finished parts into data/explanations/bg")
    ex_merge.add_argument("--work", type=Path, required=True)
    ex_merge.add_argument("--part", type=int)
    ex_merge.set_defaults(func=cmd_explanations_merge)
    ex_sub.add_parser("status", help="coverage per category; checks the curated explanations").set_defaults(
        func=cmd_explanations_status
    )

    enhance = sub.add_parser("enhance", help="clean, sharp pictures: stamp removal, review sheets")
    en_sub = enhance.add_subparsers(dest="enhance_command", required=True)
    en_sub.add_parser(
        "stamp-fit", help="measure the ИААА stamp tile and its shifts from the pictures (data/enhance/stamp)"
    ).set_defaults(func=cmd_enhance_stamp_fit)
    en_clean = en_sub.add_parser(
        "clean", help="remove the stamp from every picture (data/media/enhance/clean)"
    )
    en_clean.add_argument("--only", help="comma-separated media IDs")
    en_clean.set_defaults(func=cmd_enhance_clean)
    en_review = en_sub.add_parser("review", help="HTML sheet: official picture next to the cleaned one")
    en_review.add_argument("--name", default="stamp", help="sheet name (file name without .html)")
    en_review.add_argument("--only", help="comma-separated media IDs")
    en_review.add_argument("--flagged", action="store_true", help="only pictures flagged by the stamp score")
    en_review.add_argument("--limit", type=int, default=1000)
    en_review.set_defaults(func=cmd_enhance_review)
    en_up = en_sub.add_parser("upscale", help="enlarge cleaned pictures with Real-ESRGAN (local GPU)")
    en_up.add_argument("--only", help="comma-separated media IDs")
    en_up.add_argument("--classes", help="inventory classes to enlarge, comma-separated (default: all)")
    en_up.add_argument(
        "--scale", type=float, help="fixed scale (default: about 1400 px on the long side, 2-4×)"
    )
    en_up.add_argument("--batch", type=int, default=60, help="pictures per Real-ESRGAN run")
    en_up.add_argument("--into", default="upscaled", help="output folder below data/media/enhance")
    en_up.set_defaults(func=cmd_enhance_upscale)
    en_signs = en_sub.add_parser("signs-build", help="compose the sign recipes into SVGs and raster copies")
    en_signs.add_argument("--only", help="comma-separated media IDs")
    en_signs.add_argument("--sheet", help="also write a review sheet with this name")
    en_signs.set_defaults(func=cmd_enhance_signs_build)
    en_pack = en_sub.add_parser("pack", help="build the enhanced media packs and pin them (data/enhance)")
    en_pack.add_argument("--revision", type=int, required=True, help="media revision number (tag suffix -rN)")
    en_pack.set_defaults(func=cmd_enhance_pack)
    en_commons = en_sub.add_parser(
        "commons-import", help="import the sign SVGs saved by tools/commons-signs-download.html"
    )
    en_commons.add_argument("zip", type=Path, help="bg-road-signs-commons.zip")
    en_commons.set_defaults(func=cmd_enhance_commons_import)

    legal = sub.add_parser("legal", help="the legal corpus the explanations quote (data/legal)")
    legal_sub = legal.add_subparsers(dest="legal_command", required=True)
    imp = legal_sub.add_parser("import", help="split an act's published file (docx, pdf or txt) into units")
    imp.add_argument("--act", required=True, help="act id from data/legal/sources.json")
    imp.add_argument("--file", type=Path, required=True, help="the file downloaded from source_url")
    imp.set_defaults(func=cmd_legal_import)
    legal_status = legal_sub.add_parser("status", help="acts, units and consolidation dates")
    legal_status.set_defaults(func=cmd_legal_status)
    show = legal_sub.add_parser("show", help="print one unit, e.g. 'чл. 50, ал. 1'")
    show.add_argument("--act", required=True)
    show.add_argument("unit")
    show.set_defaults(func=cmd_legal_show)
    search = legal_sub.add_parser("search", help="units containing all the given words")
    search.add_argument("--act", help="limit to one act")
    search.add_argument("--limit", type=int, default=30)
    search.add_argument("words", nargs="+")
    search.set_defaults(func=cmd_legal_search)
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

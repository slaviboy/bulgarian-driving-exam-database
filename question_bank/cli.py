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


# ----------------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qb", description=__doc__)
    parser.add_argument("--version", action="version", version=f"qb {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="debug output on the console")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="read the official index and manifest.txt").set_defaults(
        func=cmd_discover
    )
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

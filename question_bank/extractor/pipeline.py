"""Extraction stage: discover → fetch (incremental, resumable) → parse, with provenance for every file."""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from question_bank.config import Settings
from question_bank.extractor.clients.http import HttpClient
from question_bank.extractor.discovery.official import OfficialFile, OfficialManifest, discover_official
from question_bank.extractor.downloaders.fetch import fetch
from question_bank.extractor.downloaders.state import StateJournal
from question_bank.extractor.parsers.official_html import ParsedVariantFile, parse_variant_file
from question_bank.fsutil import read_json, write_json

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceFileInfo:
    order: int
    url: str
    relative_path: str
    directory: str
    edition: str
    sha256: str
    bytes: int
    etag: str | None
    last_modified: str | None
    fetched_at: str


@dataclass(frozen=True)
class ExtractedFile:
    source: SourceFileInfo
    parsed: ParsedVariantFile


def raw_path(settings: Settings, official: OfficialFile) -> Path:
    return settings.raw_dir / official.directory / official.file_name


def parsed_path(settings: Settings, order: int) -> Path:
    return settings.cache_dir / "parsed" / f"{order:02d}.json"


def extract_official(
    settings: Settings, client: HttpClient, *, force: bool = False
) -> tuple[OfficialManifest, list[ExtractedFile]]:
    manifest = discover_official(client)
    journal = StateJournal(settings.state_file, settings.data_dir)
    extracted: list[ExtractedFile] = []
    for official in manifest.files:
        outcome = fetch(client, journal, official.url, raw_path(settings, official), force=force)
        record = outcome.record
        html = journal.local_path(record).read_text(encoding="utf-8")
        parsed = parse_variant_file(html)
        info = SourceFileInfo(
            order=official.order,
            url=official.url,
            relative_path=official.relative_path,
            directory=official.directory,
            edition=official.edition.isoformat(),
            sha256=record.sha256,
            bytes=record.bytes,
            etag=record.etag,
            last_modified=record.last_modified,
            fetched_at=record.fetched_at,
        )
        write_json(parsed_path(settings, official.order), {"source": asdict(info), "parsed": asdict(parsed)})
        log.info(
            "variant extracted",
            extra={
                "order": official.order,
                "title": parsed.title,
                "questions": len(parsed.questions),
                "sections": len(parsed.sections),
                "downloaded": outcome.downloaded,
                "resumed": outcome.resumed,
            },
        )
        extracted.append(ExtractedFile(info, parsed))
    return manifest, extracted


def load_extracted(settings: Settings) -> list[ExtractedFile]:
    """Re-load the parsed records written by `extract_official` (no network)."""
    from question_bank.extractor.parsers.official_html import ParsedAnswer, ParsedQuestion, ParsedSection

    files = []
    for path in sorted((settings.cache_dir / "parsed").glob("*.json")):
        raw = read_json(path)
        p = raw["parsed"]
        parsed = ParsedVariantFile(
            title=p["title"],
            category_label=p["category_label"],
            description=p["description"],
            sections=tuple(ParsedSection(**s) for s in p["sections"]),
            questions=tuple(
                ParsedQuestion(
                    original_id=q["original_id"],
                    points=q["points"],
                    section_number=q["section_number"],
                    position=q["position"],
                    text=q["text"],
                    answers=tuple(ParsedAnswer(**a) for a in q["answers"]),
                    images=tuple(q["images"]),
                    videos=tuple(q["videos"]),
                )
                for q in p["questions"]
            ),
            warnings=tuple(p["warnings"]),
        )
        files.append(ExtractedFile(SourceFileInfo(**raw["source"]), parsed))
    return files

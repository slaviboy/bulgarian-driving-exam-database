from __future__ import annotations

import json
from datetime import date

import httpx
import pytest
import respx

from question_bank.config import OFFICIAL_INDEX_URL
from question_bank.extractor.clients.http import HttpClient
from question_bank.extractor.discovery.avtoizpit import match_learning_plans, parse_sub_categories
from question_bank.extractor.discovery.official import LayoutChangedError, discover_official, parse_manifest


@pytest.fixture
def manifest_text(fixtures_dir) -> str:
    return (fixtures_dir / "official" / "manifest.txt").read_text(encoding="utf-8")


def test_parse_real_manifest(manifest_text):
    files = parse_manifest(manifest_text)
    assert [f.order for f in files] == list(range(1, 24))
    assert {f.edition for f in files} == {date(2026, 10, 1)}
    trolleybus = files[18]
    assert trolleybus.category_token == "D" and trolleybus.description_words.startswith("103_")
    assert trolleybus.url.startswith(OFFICIAL_INDEX_URL) and "%D1%81" in trolleybus.url  # percent-encoded
    assert trolleybus.asset_url("5_video.mp4").endswith("/assets/5_video.mp4")


def test_parse_manifest_rejects_unknown_layout():
    with pytest.raises(LayoutChangedError):
        parse_manifest("something/else.pdf\n")
    with pytest.raises(LayoutChangedError):
        parse_manifest("\n\n")


@respx.mock
def test_discover_fails_loudly_when_index_stops_using_manifest(fast_settings):
    respx.get(OFFICIAL_INDEX_URL).mock(return_value=httpx.Response(200, text="<html>new site</html>"))
    with HttpClient(fast_settings) as client, pytest.raises(LayoutChangedError):
        discover_official(client)


@respx.mock
def test_discover_reads_manifest(fast_settings, manifest_text):
    respx.get(OFFICIAL_INDEX_URL).mock(return_value=httpx.Response(200, text="fetch('manifest.txt')"))
    respx.get(OFFICIAL_INDEX_URL + "manifest.txt").mock(
        return_value=httpx.Response(200, content=manifest_text.encode("utf-8"))
    )
    with HttpClient(fast_settings) as client:
        manifest = discover_official(client)
    assert len(manifest.files) == 23 and len(manifest.sha256) == 64


def test_match_real_learning_plans(fixtures_dir, manifest_text):
    subs = parse_sub_categories(
        json.loads((fixtures_dir / "avtoizpit" / "sub-categories.json").read_text(encoding="utf-8"))
    )
    matches = {m.official_order: m for m in match_learning_plans(parse_manifest(manifest_text), subs)}
    assert sum(1 for m in matches.values() if m.learning_plan) == 22
    assert matches[14].learning_plan is None  # C1+E has no AvtoIzpit sub-category
    assert matches[19].sub_category.name == "D (103)" and matches[19].learning_plan.id == 285
    assert matches[9].learning_plan.id == 233  # not the "държавна поръчка" plan 235
    assert matches[17].learning_plan.id == 340  # "(След 07.02.26г.)" note without a space
    assert all(m.candidates <= 1 for m in matches.values())

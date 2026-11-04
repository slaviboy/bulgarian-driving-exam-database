from __future__ import annotations

import httpx
import respx

from question_bank.extractor.clients.http import HttpClient
from question_bank.extractor.downloaders.media import RANGE_BYTES, compare_copy

URL = "https://example.test/dir/assets/5_video.mp4"
DATA = bytes(i % 251 for i in range(300_000))


def _ranged(body: bytes):
    def handler(request: httpx.Request) -> httpx.Response:
        start, end = (int(x) for x in request.headers["Range"].removeprefix("bytes=").split("-"))
        assert end - start + 1 <= RANGE_BYTES
        return httpx.Response(
            206, content=body[start : end + 1], headers={"Content-Range": f"bytes {start}-{end}/{len(body)}"}
        )

    return handler


@respx.mock
def test_identical_copy(fast_settings, tmp_path):
    local = tmp_path / "5_video.mp4"
    local.write_bytes(DATA)
    respx.get(URL).mock(side_effect=_ranged(DATA))
    with HttpClient(fast_settings) as client:
        check = compare_copy(client, URL, local, "5_video.mp4", "dir")
    assert check.identical and check.method == "range"


@respx.mock
def test_copy_with_other_size_or_content_is_reported(fast_settings, tmp_path):
    local = tmp_path / "5_video.mp4"
    local.write_bytes(DATA)
    respx.get(URL).mock(side_effect=_ranged(DATA + b"x"))
    with HttpClient(fast_settings) as client:
        assert not compare_copy(client, URL, local, "5_video.mp4", "dir").identical
    respx.get(URL).mock(side_effect=_ranged(bytes(len(DATA))))
    with HttpClient(fast_settings) as client:
        check = compare_copy(client, URL, local, "5_video.mp4", "dir")
    assert not check.identical and "differ" in check.detail


@respx.mock
def test_server_ignoring_ranges_is_compared_in_full(fast_settings, tmp_path):
    local = tmp_path / "small.png"
    local.write_bytes(b"\x89PNG small")
    respx.get(URL).mock(return_value=httpx.Response(200, content=b"\x89PNG small"))
    with HttpClient(fast_settings) as client:
        check = compare_copy(client, URL, local, "small.png", "dir")
    assert check.identical and check.method == "full"

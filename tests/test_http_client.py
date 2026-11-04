from __future__ import annotations

import hashlib
import json

import httpx
import pytest
import respx

from question_bank.extractor.clients.http import HttpClient, HttpError, IntegrityError, RateLimiter

URL = "https://example.test/file.bin"
BODY = bytes(range(256)) * 400  # 102,400 bytes
SHA = hashlib.sha256(BODY).hexdigest()


def make_client(settings, sleeps=None):
    return HttpClient(settings, sleep=(sleeps.append if sleeps is not None else (lambda _s: None)))


@respx.mock
def test_retries_retryable_status_then_succeeds(fast_settings):
    route = respx.get(URL).mock(
        side_effect=[httpx.Response(503), httpx.Response(502), httpx.Response(200, content=b"ok")]
    )
    with make_client(fast_settings) as client:
        assert client.get_bytes(URL) == b"ok"
        assert route.call_count == 3


@respx.mock
def test_gives_up_after_max_retries(fast_settings):
    respx.get(URL).mock(return_value=httpx.Response(500))
    with make_client(fast_settings) as client, pytest.raises(HttpError) as err:
        client.get_bytes(URL)
    assert err.value.status == 500
    assert client.request_count == fast_settings.max_retries + 1


@respx.mock
def test_non_retryable_status_fails_immediately(fast_settings):
    respx.get(URL).mock(return_value=httpx.Response(404))
    with make_client(fast_settings) as client, pytest.raises(HttpError) as err:
        client.get_bytes(URL)
    assert err.value.status == 404
    assert client.request_count == 1


@respx.mock
def test_honours_retry_after(fast_settings):
    respx.get(URL).mock(side_effect=[httpx.Response(429, headers={"Retry-After": "7"}), httpx.Response(200)])
    sleeps: list[float] = []
    with make_client(fast_settings, sleeps) as client:
        client.get_bytes(URL)
    assert 7.0 in sleeps


@respx.mock
def test_transport_errors_are_retried(fast_settings):
    respx.get(URL).mock(side_effect=[httpx.ConnectError("boom"), httpx.Response(200, content=b"x")])
    with make_client(fast_settings) as client:
        assert client.get_bytes(URL) == b"x"


def test_rate_limiter_enforces_interval_per_host():
    now = [100.0]
    slept: list[float] = []

    def sleep(seconds: float) -> None:
        slept.append(seconds)
        now[0] += seconds

    limiter = RateLimiter({"a.test": 2.0}, default_interval=0.5, clock=lambda: now[0], sleep=sleep)
    assert limiter.wait("a.test") == 0.0
    now[0] += 0.5
    assert limiter.wait("a.test") == pytest.approx(1.5)
    assert limiter.wait("b.test") == 0.0  # other hosts are independent
    assert slept == [pytest.approx(1.5)]


@respx.mock
def test_download_verifies_and_moves_into_place(fast_settings, tmp_path):
    respx.get(URL).mock(return_value=httpx.Response(200, content=BODY, headers={"ETag": '"v1"'}))
    dest = tmp_path / "out" / "file.bin"
    with make_client(fast_settings) as client:
        result = client.download(URL, dest, expected_sha256=SHA, expected_bytes=len(BODY))
    assert dest.read_bytes() == BODY
    assert result.sha256 == SHA and result.bytes == len(BODY) and not result.resumed
    assert result.etag == '"v1"'
    assert not dest.with_name("file.bin.part").exists()


@respx.mock
def test_download_resumes_partial_file_with_range(fast_settings, tmp_path):
    dest = tmp_path / "file.bin"
    half = len(BODY) // 2
    dest.with_name("file.bin.part").write_bytes(BODY[:half])
    dest.with_name("file.bin.part.json").write_text(json.dumps({"url": URL, "etag": '"v1"'}))

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Range"] == f"bytes={half}-"
        assert request.headers["If-Range"] == '"v1"'
        return httpx.Response(
            206,
            content=BODY[half:],
            headers={"Content-Range": f"bytes {half}-{len(BODY) - 1}/{len(BODY)}", "ETag": '"v1"'},
        )

    respx.get(URL).mock(side_effect=handler)
    with make_client(fast_settings) as client:
        result = client.download(URL, dest, expected_sha256=SHA)
    assert result.resumed
    assert dest.read_bytes() == BODY
    assert result.sha256 == SHA


@respx.mock
def test_download_restarts_when_server_ignores_range(fast_settings, tmp_path):
    dest = tmp_path / "file.bin"
    dest.with_name("file.bin.part").write_bytes(b"garbage-prefix")
    dest.with_name("file.bin.part.json").write_text(json.dumps({"url": URL, "etag": '"old"'}))
    respx.get(URL).mock(return_value=httpx.Response(200, content=BODY))
    with make_client(fast_settings) as client:
        result = client.download(URL, dest, expected_sha256=SHA)
    assert not result.resumed
    assert dest.read_bytes() == BODY


@respx.mock
def test_download_rejects_wrong_checksum_and_cleans_up(fast_settings, tmp_path):
    respx.get(URL).mock(return_value=httpx.Response(200, content=BODY))
    dest = tmp_path / "file.bin"
    with make_client(fast_settings) as client, pytest.raises(IntegrityError):
        client.download(URL, dest, expected_sha256="0" * 64)
    assert not dest.exists()
    assert not dest.with_name("file.bin.part").exists()


@respx.mock
def test_download_requests_identity_encoding(fast_settings, tmp_path):
    """Regression: a gzip transfer would make Content-Length, ranges and checksums refer to other bytes."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Accept-Encoding"] == "identity"
        return httpx.Response(200, content=BODY, headers={"Content-Length": str(len(BODY))})

    respx.get(URL).mock(side_effect=handler)
    with make_client(fast_settings) as client:
        assert client.download(URL, tmp_path / "f.bin").sha256 == SHA


@respx.mock
def test_conditional_get_returns_not_modified(fast_settings):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["If-None-Match"] == '"abc"'
        return httpx.Response(304)

    respx.get(URL).mock(side_effect=handler)
    with make_client(fast_settings) as client:
        assert client.conditional_get(URL, etag='"abc"').status_code == 304

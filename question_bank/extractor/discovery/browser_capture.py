"""Optional evidence tool: load the source pages in headless Chromium and record their network requests.

Used to document what the websites actually request (docs/source-investigation.md) instead of
guessing endpoints. It only loads pages; it never clicks, submits forms or starts tests.
Requires the `browser` extra and `python -m playwright install chromium`.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from question_bank.fsutil import write_json

log = logging.getLogger(__name__)

DEFAULT_PAGES = (
    "https://public-eis.rta.government.bg/exam-questions/",
    "https://avtoizpit.com/listovki#/sub-categories",
)


def capture_network(pages: tuple[str, ...] = DEFAULT_PAGES, settle_ms: int = 4000) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "install the 'browser' extra and run: python -m playwright install chromium"
        ) from exc

    records: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(locale="bg-BG")
        page = context.new_page()
        current = {"page": ""}

        def on_finished(request: Any) -> None:
            response = request.response()
            headers = response.headers if response else {}
            records.append(
                {
                    "page": current["page"],
                    "method": request.method,
                    "url": request.url,
                    "resource_type": request.resource_type,
                    "status": response.status if response else None,
                    "content_type": headers.get("content-type"),
                    "content_length": headers.get("content-length"),
                }
            )

        page.on("requestfinished", on_finished)
        for url in pages:
            current["page"] = url
            log.info("capturing network requests", extra={"page": url})
            page.goto(url, wait_until="networkidle", timeout=60_000)
            page.wait_for_timeout(settle_ms)
        browser.close()
    return records


def write_capture(records: list[dict[str, Any]], out_file: Path) -> None:
    payload = {"captured_at": datetime.now(UTC).isoformat(timespec="seconds"), "requests": records}
    write_json(out_file, payload)

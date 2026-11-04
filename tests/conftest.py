from __future__ import annotations

from pathlib import Path

import pytest

from question_bank.config import Settings

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def fast_settings(tmp_path: Path) -> Settings:
    """Settings with no waiting between requests and no back-off, writing into a temp directory."""
    return Settings(
        data_dir=tmp_path / "data",
        reports_dir=tmp_path / "reports",
        timeout_seconds=5,
        max_retries=3,
        backoff_base_seconds=0.0,
        host_intervals={},
        default_interval_seconds=0.0,
    )


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES

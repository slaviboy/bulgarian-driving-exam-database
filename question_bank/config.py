"""Runtime settings, read from environment variables with safe defaults (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from question_bank import __version__

REPO_ROOT = Path(__file__).resolve().parent.parent

OFFICIAL_INDEX_URL = "https://public-eis.rta.government.bg/exam-questions/"
OFFICIAL_HOST = "public-eis.rta.government.bg"
AVTOIZPIT_BASE_URL = "https://avtoizpit.com/"
AVTOIZPIT_HOST = "avtoizpit.com"
PROJECT_URL = "https://github.com/slaviboy/bulgarian-driving-exam-database"


def _float(name: str, default: float) -> float:
    value = os.environ.get(name)
    return float(value) if value else default


def _int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


@dataclass(frozen=True)
class Settings:
    """Everything that influences how the tool talks to the sources and where it writes."""

    data_dir: Path = REPO_ROOT / "data"
    reports_dir: Path = REPO_ROOT / "reports"
    timeout_seconds: float = 60.0
    max_retries: int = 4
    backoff_base_seconds: float = 1.5
    # Minimum pause between two requests to the same host. AvtoIzpit is a live application, so it is
    # treated more gently than the static file server of the official array.
    host_intervals: dict[str, float] = field(
        default_factory=lambda: {OFFICIAL_HOST: 1.0, AVTOIZPIT_HOST: 2.0}
    )
    default_interval_seconds: float = 1.0
    user_agent: str = f"bulgarian-driving-exam-database/{__version__} (+{PROJECT_URL})"

    @property
    def cache_dir(self) -> Path:
        return self.data_dir / "cache"

    @property
    def raw_dir(self) -> Path:
        """Downloaded official files, mirrored by their path below the official index URL."""
        return self.data_dir / "raw"

    @property
    def media_dir(self) -> Path:
        return self.data_dir / "media"

    @property
    def exports_dir(self) -> Path:
        return self.data_dir / "exports"

    @property
    def state_file(self) -> Path:
        return self.cache_dir / "state.json"

    @property
    def log_dir(self) -> Path:
        return self.cache_dir / "logs"


def load_settings() -> Settings:
    data_dir = Path(os.environ.get("QB_DATA_DIR", REPO_ROOT / "data"))
    reports_dir = Path(os.environ.get("QB_REPORTS_DIR", REPO_ROOT / "reports"))
    official = _float("QB_OFFICIAL_INTERVAL_SECONDS", 1.0)
    avtoizpit = max(_float("QB_AVTOIZPIT_INTERVAL_SECONDS", 2.0), 2.0)  # never faster than 1 request / 2 s
    return Settings(
        data_dir=data_dir,
        reports_dir=reports_dir,
        timeout_seconds=_float("QB_TIMEOUT_SECONDS", 60.0),
        max_retries=_int("QB_MAX_RETRIES", 4),
        host_intervals={OFFICIAL_HOST: official, AVTOIZPIT_HOST: avtoizpit},
    )

"""File-system helpers. All generated text uses LF line endings so checksums are identical on every OS."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def write_bytes_atomic(path: Path, data: bytes) -> None:
    """Write via a temporary file in the same directory and rename into place."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_text(path: Path, text: str) -> None:
    write_bytes_atomic(path, text.encode("utf-8"))


def dumps_json(payload: Any, *, indent: int | None = 2) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=indent, default=str) + "\n"


def write_json(path: Path, payload: Any, *, indent: int | None = 2) -> None:
    write_text(path, dumps_json(payload, indent=indent))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

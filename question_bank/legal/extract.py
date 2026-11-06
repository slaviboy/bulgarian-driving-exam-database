"""Plain text of a legal act from the file a government site publishes (DOCX, PDF or text)."""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ExtractError(RuntimeError):
    pass


def docx_text(path: Path) -> str:
    """One line per Word paragraph (table cells are paragraphs too)."""
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    lines = []
    for paragraph in root.iter(_W + "p"):
        parts = []
        for node in paragraph.iter():
            if node.tag == _W + "t" and node.text:
                parts.append(node.text)
            elif node.tag in (_W + "tab", _W + "br"):
                parts.append(" ")
        lines.append("".join(parts))
    return "\n".join(lines)


def pdf_text(path: Path) -> str:
    """Text of a PDF through Poppler's ``pdftotext`` (reading order, UTF-8)."""
    tool = shutil.which("pdftotext")
    if tool is None:
        raise ExtractError("pdftotext (Poppler) is needed to read PDF files")
    result = subprocess.run([tool, "-enc", "UTF-8", str(path), "-"], capture_output=True, check=False)
    if result.returncode != 0:
        raise ExtractError(f"pdftotext failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout.decode("utf-8")


def text_of(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return docx_text(path)
    if suffix == ".pdf":
        return pdf_text(path)
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    raise ExtractError(f"unsupported file type {suffix!r} (docx, pdf or txt)")

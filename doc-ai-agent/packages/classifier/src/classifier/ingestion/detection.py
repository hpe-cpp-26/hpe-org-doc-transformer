from __future__ import annotations

import re
from typing import Any

from .utils import split_words


def detect_doc_info(text: str, *, title: str | None = None) -> dict[str, Any]:
    words = split_words(text)
    word_count = len(words)

    doc_type = "prose"
    if word_count < 150:
        doc_type = "short"
    elif _is_code_doc(text):
        doc_type = "code"
    elif _is_list_doc(text):
        doc_type = "list"
    elif _is_structured_doc(text):
        doc_type = "structured"

    extracted_title = title if title is not None else _extract_title(text, doc_type)

    return {
        "doc_type": doc_type,
        "word_count": word_count,
        "title": extracted_title,
    }


def _extract_title(text: str, doc_type: str) -> str | None:
    if doc_type == "short":
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    first = lines[0]
    if first.startswith("#"):
        return first.lstrip("#").strip()
    if first.isupper() and len(first) < 60:
        return first.strip()
    if len(first) < 80 and first.endswith(":"):
        return first.rstrip(":").strip()
    sentence = text.strip().split(".")[0].strip()
    words = sentence.split()
    return " ".join(words[:12]) if words else None


def _is_list_doc(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    bullet_lines = [line for line in lines if _looks_like_bullet(line)]
    return len(bullet_lines) / len(lines) >= 0.4


def _looks_like_bullet(line: str) -> bool:
    return bool(re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", line))


def _is_structured_doc(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    heading_lines = [line for line in lines if re.match(r"^#+\s+", line)]
    return len(heading_lines) >= 2


def _is_code_doc(text: str) -> bool:
    if "```" in text:
        return True
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    code_like = sum(
        1
        for line in lines
        if re.search(r"[;{}()<>]|def\s+|class\s+|function\s+|=>", line)
    )
    return code_like / len(lines) >= 0.3

"""Hide leading staff-bio paragraphs. The topic card stays."""
from __future__ import annotations

import re

_MAX_BIO_CHARS = 480
_MAX_DROP = 2
_ROLE = re.compile(
    r"(?:"
    r"\b(?:editor|writer|reporter|intern|correspondent|columnist|contributor)\b|"
    r"associate director|shopping editor|"
    r"編輯|記者|作者|實習|專欄|"
    r"編集者|編集部|インターン"
    r")",
    re.I,
)
_BIO_SHAPE = re.compile(
    r"(?:"
    r"\bis (?:an?|the)\b|\bcovers\b|\bwrites for\b|\bjoined\b|"
    r"擔任|現為|"
    r"です。"
    r")",
    re.I,
)
_AT_PUB = re.compile(
    r"\bat\b.{0,48}\b(?:who what wear|vogue|wwd|elle|harper)\b",
    re.I,
)


def is_staff_bio_paragraph(text: str) -> bool:
    chunk = (text or "").strip()
    if not chunk or len(chunk) > _MAX_BIO_CHARS:
        return False
    if not _ROLE.search(chunk):
        return False
    return bool(_BIO_SHAPE.search(chunk) or _AT_PUB.search(chunk))


def drop_leading_staff_bios(text: str) -> str:
    """Drop at most two opening staff-bio paragraphs. Empty result is allowed."""
    raw = (text or "").strip()
    if not raw:
        return ""
    parts = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
    if len(parts) == 1:
        parts = [p.strip() for p in raw.splitlines() if p.strip()]
    kept: list[str] = []
    dropped = 0
    started = False
    for part in parts:
        if not started and dropped < _MAX_DROP and is_staff_bio_paragraph(part):
            dropped += 1
            continue
        started = True
        kept.append(part)
    return "\n\n".join(kept)

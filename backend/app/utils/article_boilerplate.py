"""Strip share/nav chrome from extracted article text. MD-M2 ≤150."""
from __future__ import annotations

import re
from typing import Any

_NOISE_LINE = re.compile(
    r"^(?:"
    r"facebook|whatsapp|instagram|pinterest|twitter|linkedin|threads|"
    r"跳至分類|jump to categor(?:y|ies)|"
    r"photo credit:?.*|圖片來源:?.*|"
    r"share this|分享此文|分享到"
    r")$",
    re.I,
)
_NOISE_EXACT = frozenset({"x", "facebook", "whatsapp", "instagram", "twitter"})
_NOISE_TOKENS = (
    "share",
    "social",
    "breadcrumb",
    "newsletter",
    "sharebar",
    "related-post",
    "related_post",
)


def strip_boilerplate_nodes(soup: Any) -> None:
    if soup is None or not hasattr(soup, "find_all"):
        return
    for tag in list(soup.find_all(True)):
        cid = " ".join(tag.get("class") or [])
        tid = str(tag.get("id") or "")
        blob = f"{cid} {tid}".lower()
        if any(tok in blob for tok in _NOISE_TOKENS):
            tag.decompose()


def clean_extracted_text(text: str) -> str:
    lines = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower() in _NOISE_EXACT:
            continue
        if _NOISE_LINE.match(line):
            continue
        lines.append(line)
    return "\n\n".join(lines)[:5000]

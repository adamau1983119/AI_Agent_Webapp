"""Strip share/nav chrome from extracted article text. MD-M2 ≤150."""
from __future__ import annotations

import re
from typing import Any

_NOISE_LINE = re.compile(
    r"^(?:"
    r"facebook|whatsapp|instagram|pinterest|twitter|linkedin|threads|"
    r"advertisement|sponsored|"
    r"跳至分類[:：]?.*|jump to categor(?:y|ies)[:：]?.*|"
    r"photo credit[:：]?.*|圖片來源[:：]?.*|"
    r"share this|分享此文|分享本文|分享到|"
    r"加入討論|關注我們|追蹤我們|follow us|"
    r"複製連結|copy link|"
    r"在 google 上將我們加入偏好來源|"
    r"add us to your preferred sources on google"
    r")$",
    re.I,
)
_CUTOFF = re.compile(
    r"^(?:"
    r"選購.{0,48}|shop .{0,40}|shop the look|shop now|"
    r".{0,48}最新影片|latest videos|"
    r"探索更多|相關閱讀|你可能也喜歡|"
    r"explore more|read more|related stories|you may also like|"
    r"訂閱電子報|newsletter|"
    r"副購物編輯|shopping editor"
    r")$",
    re.I,
)
_NOISE_EXACT = frozenset({
    "x", "facebook", "whatsapp", "instagram", "twitter", "pinterest",
    "advertisement", "share", "分享",
})
_HANDLE = re.compile(r"^@[\w.]+$")
_ONLY_WRAP = re.compile(r"^[（(\[【「『）)\]】」』]+$")
_NOISE_TOKENS = (
    "share", "social", "breadcrumb", "newsletter", "sharebar",
    "related-post", "related_post", "related-stories", "advert",
    "preferred-source", "affiliate", "commerce", "shop-the",
    "product-card", "product-widget", "product-module",
    "recirc", "video-playlist", "latest-video", "author-bio",
)


def _match_key(line: str) -> str:
    t = re.sub(r"^[（(\[【「『\s]+", "", line.strip())
    t = re.sub(r"[）)\]】」』\s]+$", "", t)
    return t.strip().rstrip("：:").strip()


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
        key = _match_key(line)
        if not key or _ONLY_WRAP.match(line):
            continue
        if _CUTOFF.match(key):
            break
        if line.lower() in _NOISE_EXACT or key.lower() in _NOISE_EXACT:
            continue
        if _HANDLE.match(key):
            continue
        if _NOISE_LINE.match(line) or _NOISE_LINE.match(key):
            continue
        if "圖片來源" in line and len(line) <= 40:
            continue
        lines.append(line)
    return "\n\n".join(lines)[:5000]


def apply_display_clean_to_topic(topic: dict) -> None:
    """Filter shopping/share chrome in-memory. Do not persist."""
    if not isinstance(topic, dict):
        return
    sources = topic.get("sources") or []
    if sources and isinstance(sources[0], dict):
        raw = sources[0].get("original_content")
        if isinstance(raw, str) and raw.strip():
            sources[0]["original_content"] = clean_extracted_text(raw)
    ts = topic.get("translated_source_content")
    if isinstance(ts, str) and ts.strip():
        topic["translated_source_content"] = clean_extracted_text(ts)
    i18n = topic.get("source_content_i18n")
    if isinstance(i18n, dict):
        cleaned = {}
        for lang, val in i18n.items():
            if isinstance(val, str) and val.strip():
                cleaned[lang] = clean_extracted_text(val)
            else:
                cleaned[lang] = val
        topic["source_content_i18n"] = cleaned

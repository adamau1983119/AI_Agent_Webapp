"""Strip share/nav chrome from extracted article text. MD-M2 ≤150."""
from __future__ import annotations

import re
from typing import Any, List

from app.utils.article_extract_quality import mega_menu_hits

_NOISE_LINE = re.compile(
    r"^(?:"
    r"facebook|whatsapp|instagram|pinterest|twitter|linkedin|threads|"
    r"advertisement|sponsored|advertiser content|"
    r"跳至分類[:：]?.*|jump to categor(?:y|ies)[:：]?.*|"
    r"跳至主要內容|skip to(?:\s+the)?\s+main\s+content|"
    r"photo credit[:：]?.*|圖片來源[:：]?.*|"
    r"share this(?:\s+article)?(?:\s+on\b.*)?|分享此文|分享本文|分享到|"
    r"在.{1,24}上分享(?:此文)?|"
    r"以電子郵件分享.*|列印此文|print this(?:\s+article)?|"
    r"加入討論|關注我們|追蹤我們|follow us|"
    r"複製連結|copy link|comments?|save|"
    r"取得我們的\s*app|get our\s*app|"
    r"若你透過連結購買.*|vox media may earn|"
    r"點擊訂閱即表示.*|by submitting your email|"
    r"在 google 上將我們加入偏好來源|"
    r"add us (?:as a )?google preferred source|"
    r"add us to your preferred sources on google|"
    r"popbee\s+popbee\s+circle.*|city\s+guide\s+popcast"
    r")$",
    re.I,
)
_CUTOFF = re.compile(
    r"^(?:"
    r"選購.{0,48}|shop .{0,40}|shop the look|shop now|"
    r".{0,48}最新影片|latest videos|"
    r"探索更多|相關閱讀|相關文章|你可能也喜歡|延伸閱讀|"
    r"explore more|read more|related (?:stories|articles)|you may also like|"
    r"訂閱電子報|newsletter|訂閱我們的\s*newsletter|"
    r"most popular|editor.?s?\s*pick|see more:|wwd recommends|"
    r"儲存這篇文章|save this story|save story|"
    r"副購物編輯|shopping editor"
    r")$",
    re.I,
)
_CTA_PREFIX = re.compile(
    r"^(?:加入\s*popbee\s*會員|加入\s*popbee\s*circle|立即登記)",
    re.I,
)
_NOISE_EXACT = frozenset({
    "x", "facebook", "whatsapp", "instagram", "twitter", "pinterest",
    "advertisement", "share", "分享", "立即登記",
    "時尚", "配件", "美妝", "成衣", "美妝特輯", "商業", "零售",
    "fashion", "accessories", "beauty", "business", "retail",
    "ready to wear",
})
_HANDLE = re.compile(r"^@[\w.]+$")
_PHOTO_BY = re.compile(r"^[\w\s.\-·'’]{2,40}/@[\w.]+$", re.I)
_ONLY_WRAP = re.compile(r"^[（(\[【「『）)\]】」』]+$")
_BODY_START = re.compile(r"[。．.!？?…]")
_NOISE_TOKENS = (
    "share", "social", "breadcrumb", "newsletter", "sharebar",
    "related-post", "related_post", "related-stories", "advert",
    "preferred-source", "affiliate", "commerce", "shop-the",
    "product-card", "product-widget", "product-module",
    "recirc", "video-playlist", "latest-video", "author-bio",
)
_BODY_MIN = 56


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


def _is_chrome_line(line: str, key: str) -> bool:
    if line.lower() in _NOISE_EXACT or key.lower() in _NOISE_EXACT:
        return True
    if _HANDLE.match(key) or _PHOTO_BY.match(key):
        return True
    if _NOISE_LINE.match(line) or _NOISE_LINE.match(key):
        return True
    if _CTA_PREFIX.match(key) or _CTA_PREFIX.match(line):
        return True
    if mega_menu_hits(line) >= 4:
        return True
    if "圖片來源" in line and len(line) <= 40:
        return True
    return False


def _looks_like_body(line: str) -> bool:
    if _CTA_PREFIX.match(line) or mega_menu_hits(line) >= 4:
        return False
    if len(line) >= _BODY_MIN:
        return True
    return len(line) >= 40 and bool(_BODY_START.search(line))


def _drop_leading_recirc(lines: List[str]) -> List[str]:
    for i, line in enumerate(lines):
        if _looks_like_body(line):
            return lines[i:]
    return lines


def clean_extracted_text(text: str) -> str:
    lines: List[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        key = _match_key(line)
        if not key or _ONLY_WRAP.match(line):
            continue
        if _CUTOFF.match(key):
            break
        if _CTA_PREFIX.match(key) or _CTA_PREFIX.match(line):
            if lines:
                break
            continue
        if _is_chrome_line(line, key):
            continue
        lines.append(line)
    lines = _drop_leading_recirc(lines)
    return "\n\n".join(lines)[:5000]


def looks_like_chrome_body(text: str) -> bool:
    """True when display text is still nav/CTA shell after clean."""
    from app.utils.article_extract_quality import text_quality

    return bool(text_quality(text).get("is_shell"))


def apply_display_clean_to_topic(topic: dict) -> None:
    """Filter shopping/share chrome in-memory. Prefer content_clean for display."""
    if not isinstance(topic, dict):
        return
    sources = topic.get("sources") or []
    if sources and isinstance(sources[0], dict):
        clean = sources[0].get("content_clean")
        if isinstance(clean, str) and clean.strip():
            sources[0]["original_content"] = clean_extracted_text(clean)
        else:
            raw = sources[0].get("original_content")
            if isinstance(raw, str) and raw.strip():
                cleaned = clean_extracted_text(raw)
                sources[0]["original_content"] = cleaned
                sources[0]["content_clean"] = cleaned
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

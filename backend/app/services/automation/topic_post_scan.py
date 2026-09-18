"""Post-produce scan: content_clean + penalty/hide. MD-M2 ≤150."""
from __future__ import annotations

import os
import re
from typing import Any, Dict

from app.utils.article_boilerplate import clean_extracted_text
from app.utils.article_extract_quality import text_quality


def _log(tag: str, **fields: Any) -> None:
    try:
        from app.utils.logger import log_cost_event

        log_cost_event(tag, **fields)
    except Exception:
        pass

_MIN_CLEAN = 80
_SLIDE = re.compile(r"(?m)^\s*\d+\s*/\s*\d+\s*$")
_SEVERE = re.compile(
    r"paywall|subscribers?\s+only|會員才能|完整內容僅限|"
    r"login\s+to\s+(continue|read)|sign\s+in\s+to\s+read",
    re.I,
)
_LIGHT = re.compile(
    r"newsletter|訂閱|subscribe|加入.?會員|尊享禮遇|立即登記|"
    r"延伸閱讀|相關閱讀|you may also like|editor.?s?\s*pick",
    re.I,
)


def visible_floor() -> int:
    try:
        return max(1, int(os.getenv("TOPIC_VISIBLE_FLOOR_PER_CATEGORY", "3")))
    except ValueError:
        return 3


def _cut_slideshow(text: str) -> str:
    m = _SLIDE.search(text or "")
    if not m or m.start() < 80:
        return text
    return (text or "")[: m.start()].rstrip()


def scan_text(raw: str) -> Dict[str, Any]:
    """Return content_clean, sort_penalty, hide_card, reason. Prefer sink over hide."""
    src = (raw or "").strip()
    if not src:
        return {
            "content_clean": "",
            "sort_penalty": 0,
            "hide_card": False,
            "reason": "",
        }
    stepped = _cut_slideshow(src)
    clean = clean_extracted_text(stepped)
    if len(clean) < _MIN_CLEAN and len(src) >= _MIN_CLEAN:
        clean = clean_extracted_text(src) if len(clean) < 40 else clean
        if len(clean) < _MIN_CLEAN:
            clean = src[:5000]
    q = text_quality(clean)
    penalty = 0
    reason = ""
    hide = False
    if q.get("is_shell"):
        # Wide-gate: sink chrome; do not hide the card.
        penalty = 70
        reason = f"chrome_shell:{q.get('reason') or 'shell'}"
        clean = ""
    elif _SEVERE.search(src) and len(clean) < _MIN_CLEAN:
        # Empty + paywall: sink hard; hide only when truly empty after clean.
        penalty = 80
        reason = "severe_paywall_or_empty"
        hide = len(clean) < 40
    elif _LIGHT.search(src) and len(clean) < len(src) * 0.55:
        penalty = 25
        reason = "noise_trimmed"
    elif len(clean) < 120:
        penalty = 15
        reason = "short_body"
    _log(
        "TOPIC_POST_SCAN",
        penalty=penalty,
        hide=hide,
        reason=reason or "ok",
        cjk=q.get("cjk"),
        mega=q.get("mega_hits"),
    )
    if penalty >= 70:
        _log(
            "TOPIC_CARD_SINK",
            penalty=penalty,
            reason=reason,
            chars=len(clean),
        )
    return {
        "content_clean": clean[:5000],
        "sort_penalty": penalty,
        "hide_card": hide,
        "reason": reason,
    }


def apply_scan_to_source(
    source: Dict[str, Any],
    *,
    fallback_text: str = "",
) -> Dict[str, Any]:
    """Mutate source with content_clean; return scan result for topic fields."""
    raw = (
        (source.get("original_content") or "").strip()
        or (fallback_text or "").strip()
    )
    result = scan_text(raw)
    source["content_clean"] = result["content_clean"]
    if raw and not source.get("original_content"):
        source["original_content"] = raw[:8000]
    return result


def fact_text_from_topic(topic: Dict[str, Any]) -> str:
    """Prefer content_clean → summary_flash → original → title."""
    sources = topic.get("sources") or []
    if isinstance(sources, list) and sources and isinstance(sources[0], dict):
        clean = str(sources[0].get("content_clean") or "").strip()
        if clean:
            return clean
        top = str(topic.get("content_clean") or "").strip()
        if top:
            return top
        orig = str(sources[0].get("original_content") or "").strip()
        if orig:
            return clean_extracted_text(orig) or orig
    flash = str(topic.get("summary_flash") or "").strip()
    if flash:
        return flash
    return str(
        topic.get("original_title") or topic.get("title") or ""
    ).strip()


def stamp_scan_on_topic(topic: Dict[str, Any], scan: Dict[str, Any]) -> None:
    topic["content_clean"] = scan.get("content_clean") or ""
    topic["sort_penalty"] = int(scan.get("sort_penalty") or 0)
    if scan.get("hide_card"):
        topic["hidden"] = True
        topic["hidden_reason"] = str(scan.get("reason") or "post_scan")[:200]

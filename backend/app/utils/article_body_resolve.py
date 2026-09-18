"""Resolve article body: RSS first, then HTTP. Wide-gate; MD-M2 ≤150."""
from __future__ import annotations

from typing import Any, Dict

from app.utils.article_extract_quality import accept_extracted_body, text_quality


def _log(tag: str, **fields: Any) -> None:
    try:
        from app.utils.logger import log_cost_event

        log_cost_event(tag, **fields)
    except Exception:
        pass


def _empty() -> Dict[str, Any]:
    return {
        "images": [],
        "original_content": None,
        "language": None,
        "style": None,
        "success": False,
    }


def _merge_images(base: Dict[str, Any], extra: Dict[str, Any]) -> None:
    for img in extra.get("images") or []:
        if img not in base.setdefault("images", []):
            base["images"].append(img)


def _adopt(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    if src.get("original_content"):
        dst["original_content"] = src["original_content"]
        dst["success"] = bool(src.get("success"))
    if src.get("language") and not dst.get("language"):
        dst["language"] = src["language"]
    if src.get("style") and not dst.get("style"):
        dst["style"] = src["style"]
    _merge_images(dst, src)


async def resolve_article_body(
    extractor: Any,
    link: str,
    rss_html: str = "",
) -> Dict[str, Any]:
    """Prefer RSS HTML body; HTTP only if RSS weak. Shell never counts as success body."""
    out = _empty()
    rss = (rss_html or "").strip()
    if rss:
        rss_info = extractor.extract_from_html_content(rss, link or "")
        body = (rss_info.get("original_content") or "").strip()
        if body and accept_extracted_body(body):
            _adopt(out, rss_info)
            q = text_quality(body)
            _log(
                "TOPIC_EXTRACT_RSS_FIRST",
                cjk=q.get("cjk"),
                chars=q.get("chars"),
                mega=q.get("mega_hits"),
            )
            _log(
                "TOPIC_EXTRACT_QUALITY",
                source="rss",
                ok=1,
                cjk=q.get("cjk"),
                mega=q.get("mega_hits"),
            )
            return out
        if body:
            _log(
                "TOPIC_EXTRACT_QUALITY",
                source="rss",
                ok=0,
                reason="rss_shell_or_weak",
            )
            _merge_images(out, rss_info)

    http_info = await extractor.extract_article_info(link)
    http_body = (http_info.get("original_content") or "").strip()
    if http_body and accept_extracted_body(http_body) and http_info.get("success"):
        # Only adopt HTTP body when RSS did not already provide a good body.
        if not out.get("original_content"):
            _adopt(out, http_info)
            q = text_quality(http_body)
            _log(
                "TOPIC_EXTRACT_QUALITY",
                source="http",
                ok=1,
                cjk=q.get("cjk"),
                mega=q.get("mega_hits"),
            )
        else:
            _merge_images(out, http_info)
    else:
        _merge_images(out, http_info)
        if http_body or http_info.get("error"):
            q = text_quality(http_body)
            _log(
                "TOPIC_EXTRACT_QUALITY",
                source="http",
                ok=0,
                reason=q.get("reason") or http_info.get("error") or "weak",
            )
    return out

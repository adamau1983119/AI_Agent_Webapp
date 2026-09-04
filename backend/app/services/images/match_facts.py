"""Match facts for featured photos. MD-M2 ≤150. Do not call translation/Flash."""
from __future__ import annotations

from typing import Any, Dict, Mapping

FEATURED_CAP = 4
_FACT_MAX = 2000


def featured_slots(existing_count: int, cap: int = FEATURED_CAP) -> int:
    return max(0, cap - max(0, int(existing_count)))


def match_fact_text(topic: Mapping[str, Any]) -> str:
    """Priority: summary_flash → sources[0].original_content → title."""
    flash = str(topic.get("summary_flash") or "").strip()
    if flash:
        return flash[:_FACT_MAX]
    sources = topic.get("sources") or []
    if isinstance(sources, list) and sources and isinstance(sources[0], dict):
        orig = str(sources[0].get("original_content") or "").strip()
        if orig:
            return orig[:_FACT_MAX]
    title = str(
        topic.get("original_title") or topic.get("title") or ""
    ).strip()
    return title[:_FACT_MAX]


def topic_gallery_urls(topic: Dict[str, Any]) -> list:
    urls = topic.get("preview_images") or []
    if isinstance(urls, list):
        return [u for u in urls if u][:FEATURED_CAP]
    return []

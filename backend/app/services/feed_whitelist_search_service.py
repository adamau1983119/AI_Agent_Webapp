"""
在 DEFAULT_RSS_SOURCES 白名單內依關鍵字搜尋（name / url / role），供 GET /channels/feeds/search。
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set

from app.models.channel import DEFAULT_RSS_SOURCES, ChannelCategory, ChannelRegion


def search_whitelist_feeds(query: str, limit: int = 30) -> List[Dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q or len(q) > 120:
        return []

    tokens = [t for t in re.split(r"\s+", q) if t]
    if not tokens:
        return []

    seen_urls: Set[str] = set()
    out: List[Dict[str, Any]] = []

    for cat in ChannelCategory:
        regions_map = DEFAULT_RSS_SOURCES.get(cat) or {}
        for reg in ChannelRegion:
            feeds = regions_map.get(reg) or []
            for src in feeds:
                if len(out) >= limit:
                    return out
                url = (src.get("url") or "").strip()
                if not url or url in seen_urls:
                    continue
                hay = " ".join(
                    [
                        str(src.get("name") or ""),
                        url,
                        str(src.get("role") or ""),
                        cat.value,
                        reg.value,
                    ]
                ).lower()
                if all(tok in hay for tok in tokens):
                    seen_urls.add(url)
                    out.append(
                        {
                            "name": (src.get("name") or "").strip() or "RSS",
                            "url": url,
                            "role": (src.get("role") or "").strip() or "",
                            "category": cat.value,
                            "region": reg.value,
                        }
                    )
    return out

"""先監測後生產：shadow log 與 fail-open 合併。不改 finalize。"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Set

from app.models.topic import Category
from app.services.automation.topic_card_gates import should_skip_entry
from app.services.automation.topic_card_select_config import max_per_source

logger = logging.getLogger(__name__)


def _title_key(topic: Dict[str, Any]) -> str:
    return (topic.get("original_title") or topic.get("title") or "").strip()


def log_shadow_batch(topics: List[Dict[str, Any]], category: Category) -> None:
    cap = max_per_source()
    used: Set[str] = set()
    for topic in topics:
        title = _title_key(topic)
        src = topic.get("source") or topic.get("source_name") or ""
        link = ""
        sources = topic.get("sources") or []
        if sources and isinstance(sources[0], dict):
            link = str(sources[0].get("url") or "")
        reason = should_skip_entry(title, link, category, src, used, cap)
        if reason:
            logger.info(
                "TOPIC_CARD_SELECT shadow would_skip=%s title=%s",
                reason,
                title[:80],
            )
        elif src:
            used.add(src)


def merge_legacy_fill(
    selected: List[Dict[str, Any]],
    legacy: List[Dict[str, Any]],
    count: int,
) -> List[Dict[str, Any]]:
    out = list(selected)
    seen = {_title_key(t) for t in out if _title_key(t)}
    for topic in legacy:
        if len(out) >= count:
            break
        key = _title_key(topic)
        if not key or key in seen:
            continue
        out.append(topic)
        seen.add(key)
    if len(selected) < count:
        logger.info(
            "TOPIC_CARD_SELECT_FALLBACK had=%s need=%s filled=%s",
            len(selected),
            count,
            len(out),
        )
    return out[:count]

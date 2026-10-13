"""自選主題卡補上與大眾卡相同的三語成套。"""
from __future__ import annotations

from typing import Any, Dict, List

from app.utils.topic_languages import supported_languages, usable_cached_title


def _pack_missing(topic: Dict[str, Any]) -> bool:
    titles = dict(topic.get("titles_i18n") or {})
    descs = dict(topic.get("description_i18n") or {})
    need_desc = bool((topic.get("description") or topic.get("summary_flash") or "").strip())
    for lang in supported_languages():
        if usable_cached_title(titles.get(lang), lang) is None:
            return True
        if need_desc and usable_cached_title(descs.get(lang)) is None:
            return True
    return False


async def ensure_channel_topic_packs(topics: List[Dict[str, Any]]) -> bool:
    """缺三語包才呼叫既有 finalize。回傳是否有跑預載。"""
    ids = [str(topic.get("id")) for topic in topics if topic.get("id") and _pack_missing(topic)]
    if not ids:
        return False
    from app.services.automation.topic_card_finalize import finalize_produced_cards

    await finalize_produced_cards(ids)
    return True

"""產卡後契約收口：三語標題（既有 preload）+ 源文 i18n。MD-M2 ≤150。

寫入前必須 usable_cached_title／title_matches_display_language；不改 _pack_ok。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.services.automation.topic_triple_preload import preload_topic_titles
from app.utils.cost_controls import topic_triple_preload_cap
from app.utils.logger import log_cost_event
from app.utils.topic_languages import supported_languages, usable_cached_title

logger = logging.getLogger(__name__)


async def finalize_produced_cards(topic_ids: List[str]) -> Dict[str, Any]:
    """先跑既有標題成套預載（含 _pack_ok），再補 source_content_i18n。"""
    title_stats = await preload_topic_titles(topic_ids)
    from app.services.repositories.topic_repository import TopicRepository
    from app.services.translation.source_article_translator import (
        resolve_source_article_translation,
    )

    repo = TopicRepository()
    cap = topic_triple_preload_cap()
    filled = skipped = 0
    for topic_id in topic_ids:
        if filled >= cap:
            break
        topic = await repo.get_topic_by_id(topic_id)
        if not topic:
            skipped += 1
            continue
        for lang in supported_languages():
            if filled >= cap:
                break
            cached = dict(topic.get("source_content_i18n") or {})
            if usable_cached_title((cached.get(lang) or "")[:500], lang):
                continue
            text = await resolve_source_article_translation(
                topic, lang, save_cache=True, on_demand=True
            )
            if usable_cached_title((text or "")[:500], lang):
                filled += 1
                topic = await repo.get_topic_by_id(topic_id) or topic
            else:
                skipped += 1
    log_cost_event(
        "TOPIC_CARD_FINALIZE",
        processed=len(topic_ids),
        source_filled=filled,
        skipped=skipped,
        titles=title_stats.get("status"),
    )
    return {
        "status": "ok",
        "titles": title_stats,
        "source_filled": filled,
        "skipped": skipped,
    }

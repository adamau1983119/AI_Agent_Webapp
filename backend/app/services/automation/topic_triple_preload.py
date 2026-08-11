"""產卡後 DeepL 批次預載 en/ja → topic_translations + titles_i18n（OPS-I18N）。

MD-M2：本檔 ≤150 行（目前約 93 行）；擴充請拆 topic_triple_preload_sync.py。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from app.models.topic_translation import TranslationType
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.deepl_provider import translate_with_fallback
from app.utils.cost_controls import topic_triple_preload_cap, topic_triple_preload_enabled
from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)
_PRELOAD_LANGS = ("en", "ja")


async def preload_topic_titles(topic_ids: List[str]) -> Dict[str, Any]:
    """批次預載標題；受 TOPIC_TRIPLE_PRELOAD_CAP 限制（每語言 1 次 DeepL）。"""
    if not topic_triple_preload_enabled():
        return {"status": "disabled", "processed": 0, "translated": 0}
    cap = topic_triple_preload_cap()
    repo = TopicRepository()
    trans_repo = TopicTranslationRepository()
    processed = translated = skipped = 0

    for topic_id in topic_ids:
        if translated >= cap:
            logger.info("TOPIC_TRIPLE_PRELOAD cap=%s reached", cap)
            break
        processed += 1
        topic = await repo.get_topic_by_id(topic_id)
        if not topic:
            continue
        title_src = (topic.get("title") or topic.get("original_title") or "").strip()
        if not title_src:
            skipped += 1
            continue
        titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
        src_lang = topic.get("display_language") or "zh-TW"
        if src_lang == "zh-TW":
            titles_i18n.setdefault("zh-TW", title_src)
        changed = False
        for lang in _PRELOAD_LANGS:
            if translated >= cap:
                break
            if titles_i18n.get(lang):
                continue
            cached = await trans_repo.get_translation(
                topic_id, lang, TranslationType.STANDARD
            )
            if cached and cached.get("cached_title"):
                titles_i18n[lang] = cached["cached_title"][:200]
                changed = True
                continue
            try:
                title_t, provider = await translate_with_fallback(
                    title_src[:500], lang, title_src[:500]
                )
                await trans_repo.upsert_translation({
                    "topic_id": topic_id,
                    "lang": lang,
                    "type": TranslationType.STANDARD,
                    "cached_title": title_t[:200],
                    "cached_content": None,
                    "provider": provider,
                })
                titles_i18n[lang] = title_t[:200]
                translated += 1
                changed = True
                log_cost_event(
                    "TRANSLATION_PRELOAD",
                    topic_id=topic_id,
                    lang=lang,
                    provider=provider,
                )
            except Exception as exc:
                logger.warning("preload %s %s: %s", topic_id, lang, exc)
                skipped += 1
        if changed:
            await repo.update_topic(topic_id, {
                "titles_i18n": titles_i18n,
                "updated_at": datetime.utcnow(),
            })

    return {
        "status": "ok",
        "processed": processed,
        "translated": translated,
        "skipped": skipped,
        "cap": cap,
    }

"""產卡後 DeepL 批次預載 → topic_translations + titles_i18n（OPS-I18N）。

MD-M2：本檔 ≤150 行；擴充請拆 topic_triple_preload_sync.py。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from app.models.topic_translation import TranslationType
from app.services.automation.topic_title_normalize import normalize_topic_title_for_display_lang
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.deepl_provider import translate_with_fallback
from app.utils.cost_controls import topic_triple_preload_cap, topic_triple_preload_enabled
from app.utils.logger import log_cost_event
from app.utils.topic_languages import (
    normalize_topic_language,
    preload_languages_for,
    usable_cached_title,
)

logger = logging.getLogger(__name__)


async def preload_topic_titles(topic_ids: List[str]) -> Dict[str, Any]:
    """批次預載：先正規化收集語言 title，再 DeepL 其餘 supported 語言。"""
    if not topic_triple_preload_enabled():
        return {"status": "disabled", "processed": 0, "translated": 0}
    cap = topic_triple_preload_cap()
    repo = TopicRepository()
    trans_repo = TopicTranslationRepository()
    processed = translated = skipped = 0
    did_norm = False

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

        try:
            title_src, did_norm = await normalize_topic_title_for_display_lang(
                topic_id, topic, repo=repo, trans_repo=trans_repo
            )
            if did_norm:
                translated += 1
                topic = await repo.get_topic_by_id(topic_id) or topic
        except Exception as exc:
            logger.warning("preload normalize %s: %s", topic_id, exc)
            skipped += 1
            continue

        titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
        display_lang = normalize_topic_language(topic.get("display_language"))
        if usable_cached_title(title_src):
            titles_i18n.setdefault(display_lang, title_src[:200])
        changed = False

        for lang in preload_languages_for(display_lang):
            if translated >= cap:
                break
            if usable_cached_title(titles_i18n.get(lang)):
                continue
            cached = await trans_repo.get_translation(
                topic_id, lang, TranslationType.STANDARD
            )
            cached_title = usable_cached_title(
                (cached or {}).get("cached_title") if cached else None
            )
            if cached_title:
                titles_i18n[lang] = cached_title[:200]
                changed = True
                continue
            try:
                title_t, provider = await translate_with_fallback(
                    title_src[:500], lang, title_src[:500]
                )
                if provider == "fallback" or usable_cached_title(title_t) is None:
                    skipped += 1
                    continue
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

        if changed or did_norm:
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

"""產卡後：依 display_language 正規化 canonical title（取代 topic_preload_zh）。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from app.models.topic_translation import TranslationType
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.deepl_provider import translate_with_fallback
from app.utils.logger import log_cost_event
from app.utils.topic_languages import (
    normalize_topic_language,
    title_script_mismatch,
    usable_cached_title,
)


async def normalize_topic_title_for_display_lang(
    topic_id: str,
    topic: Dict[str, Any],
    *,
    repo: TopicRepository,
    trans_repo: TopicTranslationRepository,
) -> Tuple[str, bool]:
    """確保 title／titles_i18n[display_language] 符合收集語言腳本。回傳 (譯文源, 是否新翻譯)。"""
    display_lang = normalize_topic_language(topic.get("display_language"))
    titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
    cached = usable_cached_title(titles_i18n.get(display_lang))

    if cached and not title_script_mismatch(cached, display_lang):
        if (topic.get("title") or "").strip() != cached:
            await repo.update_topic(topic_id, {
                "title": cached[:200],
                "updated_at": datetime.utcnow(),
            })
        return cached, False

    title_src = (topic.get("title") or topic.get("original_title") or "").strip()
    if usable_cached_title(title_src) is None and topic.get("original_title"):
        title_src = str(topic.get("original_title") or "").strip()
    if not title_src:
        return "", False

    if not title_script_mismatch(title_src, display_lang):
        if not cached:
            titles_i18n[display_lang] = title_src[:200]
            await repo.update_topic(topic_id, {
                "titles_i18n": titles_i18n,
                "updated_at": datetime.utcnow(),
            })
        return title_src, False

    title_t, provider = await translate_with_fallback(
        title_src[:500], display_lang, title_src[:500]
    )
    if provider == "fallback" or usable_cached_title(title_t) is None:
        return title_src, False

    titles_i18n[display_lang] = title_t[:200]
    patch: Dict[str, Any] = {
        "title": title_t[:200],
        "titles_i18n": titles_i18n,
        "updated_at": datetime.utcnow(),
    }
    if not topic.get("original_title"):
        patch["original_title"] = title_src
    await trans_repo.upsert_translation({
        "topic_id": topic_id,
        "lang": display_lang,
        "type": TranslationType.STANDARD,
        "cached_title": title_t[:200],
        "cached_content": None,
        "provider": provider,
    })
    await repo.update_topic(topic_id, patch)
    log_cost_event(
        "TRANSLATION_PRELOAD",
        topic_id=topic_id,
        lang=display_lang,
        provider=provider,
    )
    return title_t, True

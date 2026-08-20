"""產卡後：依 display_language 正規化 canonical title（Flash 成套；取代 DeepL）。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from app.models.topic_translation import TranslationProvider, TranslationType
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.flash_pack_provider import translate_title_desc_pack
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
    desc_i18n: Dict[str, str] = dict(topic.get("description_i18n") or {})
    cached = usable_cached_title(titles_i18n.get(display_lang), display_lang)

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

    desc_src = (topic.get("description") or topic.get("summary_flash") or title_src)[:800]
    title_t, desc_t, provider = await translate_title_desc_pack(
        title_src[:500], desc_src, display_lang
    )
    if provider == "fallback" or usable_cached_title(title_t, display_lang) is None:
        return title_src, False

    titles_i18n[display_lang] = title_t[:200]
    if desc_t:
        desc_i18n[display_lang] = desc_t[:200]
    patch: Dict[str, Any] = {
        "title": title_t[:200],
        "titles_i18n": titles_i18n,
        "description_i18n": desc_i18n,
        "updated_at": datetime.utcnow(),
    }
    if not topic.get("original_title"):
        patch["original_title"] = title_src
    await trans_repo.upsert_translation({
        "topic_id": topic_id,
        "lang": display_lang,
        "type": TranslationType.STANDARD,
        "cached_title": title_t[:200],
        "cached_content": (desc_t or "")[:400],
        "provider": provider or TranslationProvider.FLASH,
    })
    await repo.update_topic(topic_id, patch)
    log_cost_event(
        "TRANSLATION_PRELOAD",
        topic_id=topic_id,
        lang=display_lang,
        provider=provider,
    )
    return title_t, True

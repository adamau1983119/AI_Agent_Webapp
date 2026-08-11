"""產卡後：display_language=zh-TW 但 RSS 英文標題 → DeepL 繁中（MD-M2 拆檔）。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

from app.models.topic_translation import TranslationType
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.deepl_provider import translate_with_fallback
from app.utils.logger import log_cost_event


def title_needs_zh_tw(title: str, display_lang: str) -> bool:
    if (display_lang or "zh-TW") != "zh-TW":
        return False
    text = (title or "").strip()
    if not text:
        return False
    return not any("\u4e00" <= c <= "\u9fff" for c in text)


async def ensure_zh_tw_title(
    topic_id: str,
    topic: Dict[str, Any],
    *,
    repo: TopicRepository,
    trans_repo: TopicTranslationRepository,
) -> Tuple[str, bool]:
    """若需繁中化：更新 title／titles_i18n／original_title。回傳 (有效標題源, 是否已翻譯)。"""
    title_src = (topic.get("title") or topic.get("original_title") or "").strip()
    display_lang = topic.get("display_language") or "zh-TW"
    titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})

    cached_zh = titles_i18n.get("zh-TW")
    if cached_zh and any("\u4e00" <= c <= "\u9fff" for c in cached_zh):
        if topic.get("title") != cached_zh:
            await repo.update_topic(topic_id, {
                "title": cached_zh[:200],
                "updated_at": datetime.utcnow(),
            })
        return cached_zh, False

    if not title_needs_zh_tw(title_src, display_lang):
        return title_src, False

    title_zh, provider = await translate_with_fallback(
        title_src[:500], "zh-TW", title_src[:500]
    )
    titles_i18n["zh-TW"] = title_zh[:200]
    patch: Dict[str, Any] = {
        "title": title_zh[:200],
        "titles_i18n": titles_i18n,
        "updated_at": datetime.utcnow(),
    }
    if not topic.get("original_title"):
        patch["original_title"] = title_src
    await trans_repo.upsert_translation({
        "topic_id": topic_id,
        "lang": "zh-TW",
        "type": TranslationType.STANDARD,
        "cached_title": title_zh[:200],
        "cached_content": None,
        "provider": provider,
    })
    await repo.update_topic(topic_id, patch)
    log_cost_event(
        "TRANSLATION_PRELOAD",
        topic_id=topic_id,
        lang="zh-TW",
        provider=provider,
    )
    return title_zh, True

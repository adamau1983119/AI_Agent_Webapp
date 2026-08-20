"""
源文章完整新聞報道翻譯服務 (Source Article Full News Translation Service)
支援多語言 (zh-TW/en/ja) 新聞稿翻譯與 MongoDB 快取。
遵循《開發人員必讀規則》規則 17 & 19。
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.config import settings
from app.utils.logger import log_cost_event
from app.utils.topic_languages import (
    normalize_topic_language,
    title_matches_display_language,
)

logger = logging.getLogger(__name__)

_LANG_LABELS = {
    "zh-TW": "Traditional Chinese (繁體中文)",
    "en": "English",
    "ja": "Japanese (日本語)",
}

_MAX_SOURCE_INPUT_CHARS = 4500


def _flash_model() -> str:
    return getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL


async def resolve_source_article_translation(
    topic: Dict[str, Any],
    target_language: str,
    *,
    save_cache: bool = True,
) -> str:
    """
    取得或翻譯主題之完整新聞報道內容。
    快取優先：若已在 source_content_i18n 則直接回傳；
    若無則調用 DeepSeek Flash 完整翻譯新聞報道並寫入 DB。
    """
    lang = normalize_topic_language(target_language)
    topic_id = str(topic.get("id") or "")

    # 1. 提取快取
    cached_map = dict(topic.get("source_content_i18n") or {})
    cached_text = (cached_map.get(lang) or "").strip()
    if cached_text and title_matches_display_language(cached_text[:500], lang):
        return cached_text

    # 2. 提取原始文章內容
    sources = topic.get("sources") or []
    raw_content = ""
    if sources and isinstance(sources, list) and isinstance(sources[0], dict):
        raw_content = (sources[0].get("original_content") or "").strip()
    if not raw_content:
        raw_content = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()

    if not raw_content:
        return ""

    # 3. 檢查原始內容是否已是目標語言
    source_lang = str((sources[0].get("language") if sources and isinstance(sources[0], dict) else "") or "")
    if source_lang and normalize_topic_language(source_lang) == lang:
        return raw_content
    if lang == "en" and title_matches_display_language(raw_content[:400], "en"):
        return raw_content

    # 4. 調用 DeepSeek Flash 進行新聞全文翻譯
    label = _LANG_LABELS.get(lang, lang)
    prompt = (
        f"You are an expert news and media translator. Translate the following news article completely into natural, professional, and fluent {label}.\n"
        "REQUIREMENTS:\n"
        f"1. You MUST translate the full text into {label}. Keep all original paragraph structures intact.\n"
        "2. Faithfully preserve all factual details, names, quotes, dates, metrics, and context.\n"
        "3. Do not summarize, truncate, or omit content. Do not add markdown code fences or conversational greetings.\n"
        "4. Return only the translated article body.\n\n"
        f"SOURCE ARTICLE:\n{raw_content[:_MAX_SOURCE_INPUT_CHARS]}"
    )

    try:
        from app.services.ai.ai_service_factory import AIServiceFactory

        ai = AIServiceFactory.get_service(settings.AI_SERVICE)
        translated = await ai._call_api(prompt, model=_flash_model(), max_tokens=2500)
        translated_text = (translated or "").strip()

        if len(translated_text) >= 10 and title_matches_display_language(translated_text[:500], lang):
            cached_map[lang] = translated_text
            topic["source_content_i18n"] = cached_map
            topic["translated_source_content"] = translated_text

            if save_cache and topic_id:
                try:
                    from app.services.repositories.topic_repository import TopicRepository

                    repo = TopicRepository()
                    await repo.update_topic(topic_id, {"source_content_i18n": cached_map})
                except Exception as db_err:
                    logger.warning("Failed to save source_content_i18n to db: %s", db_err)

            log_cost_event("SOURCE_ARTICLE_TRANSLATE_SUCCESS", topic_id=topic_id, lang=lang)
            return translated_text
        else:
            logger.warning("Translated source article failed language check for %s", lang)
            return raw_content
    except Exception as exc:
        logger.warning("Failed to translate source article for topic %s: %s", topic_id, exc)
        return raw_content

"""
源文章完整新聞報道翻譯服務 (Source Article Full News Translation Service)
支援多語言 (zh-TW/en/ja) 新聞稿翻譯、On-Demand 即時補抓與 MongoDB 快取。
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
    若無且未爬取正文則 On-Demand 補抓；
    若語言同源則直接快取，異源則調用 DeepSeek Flash 完整翻譯。
    """
    lang = normalize_topic_language(target_language)
    topic_id = str(topic.get("id") or "")

    # 1. 提取快取
    cached_map = dict(topic.get("source_content_i18n") or {})
    cached_text = (cached_map.get(lang) or "").strip()
    if cached_text and len(cached_text) > 20 and title_matches_display_language(cached_text[:500], lang):
        topic["translated_source_content"] = cached_text
        return cached_text

    # 2. 提取原始文章內容
    sources = topic.get("sources") or []
    raw_content = ""
    source_url = ""
    source_lang = ""
    if sources and isinstance(sources, list) and isinstance(sources[0], dict):
        raw_content = (sources[0].get("original_content") or "").strip()
        source_url = str(sources[0].get("url") or "")
        source_lang = str(sources[0].get("language") or "")

    # 若歷史資料未抓取到全文，執行 On-Demand 即時補抓
    if (not raw_content or len(raw_content) < 80) and source_url:
        try:
            from app.utils.article_extractor import ArticleExtractor
            extractor = ArticleExtractor()
            ext_info = await extractor.extract_article_info(source_url)
            if ext_info.get("success") and ext_info.get("original_content"):
                raw_content = ext_info["original_content"].strip()
                if isinstance(sources[0], dict):
                    sources[0]["original_content"] = raw_content
                    if ext_info.get("language") and not source_lang:
                        sources[0]["language"] = ext_info["language"]
                        source_lang = ext_info["language"]
                    if ext_info.get("images") and not sources[0].get("images"):
                        sources[0]["images"] = ext_info["images"]
                    topic["sources"] = sources
                    if save_cache and topic_id:
                        try:
                            from app.services.repositories.topic_repository import TopicRepository
                            repo = TopicRepository()
                            await repo.update_topic(topic_id, {"sources": sources})
                        except Exception as db_s_err:
                            logger.warning("Failed saving on-demand sources for topic %s: %s", topic_id, db_s_err)
        except Exception as on_demand_err:
            logger.warning("On-demand extract failed for %s: %s", source_url, on_demand_err)

    if not raw_content:
        raw_content = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()

    if not raw_content:
        return ""

    # 3. 檢查原始內容是否已是目標語言
    is_same_lang = False
    if source_lang and normalize_topic_language(source_lang) == lang:
        is_same_lang = True
    elif lang == "zh-TW" and title_matches_display_language(raw_content[:400], "zh-TW"):
        is_same_lang = True
    elif lang == "en" and title_matches_display_language(raw_content[:400], "en"):
        is_same_lang = True
    elif lang == "ja" and title_matches_display_language(raw_content[:400], "ja"):
        is_same_lang = True

    if is_same_lang:
        cached_map[lang] = raw_content
        topic["source_content_i18n"] = cached_map
        topic["translated_source_content"] = raw_content
        if save_cache and topic_id:
            try:
                from app.services.repositories.topic_repository import TopicRepository
                repo = TopicRepository()
                await repo.update_topic(topic_id, {"source_content_i18n": cached_map})
            except Exception as db_err:
                logger.warning("Failed to save source_content_i18n to db: %s", db_err)
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
            topic["translated_source_content"] = raw_content
            return raw_content
    except Exception as exc:
        logger.warning("Failed to translate source article for topic %s: %s", topic_id, exc)
        topic["translated_source_content"] = raw_content
        return raw_content

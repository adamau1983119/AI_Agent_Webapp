"""
主題標題／摘要「譯為目前語言」（v7 Phase 2）
cache-first topic_translations → DeepL standard；kol_style → Flash 按需。
"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.models.topic_translation import TranslationType, TranslationProvider
from app.services.translation.deepl_provider import translate_with_fallback
from app.services.translation.inflight_guard import with_inflight, translation_key
from app.utils.logger import log_cost_event
import logging

logger = logging.getLogger(__name__)

_SUPPORTED = frozenset({"zh-TW", "en", "ja"})


def normalize_language(lang: Optional[str]) -> str:
    if not lang:
        return "zh-TW"
    raw = str(lang).strip()
    low = raw.lower()
    if low in ("zh", "zh-tw", "zh-hk", "zh-hant"):
        return "zh-TW"
    if low.startswith("en"):
        return "en"
    if low in ("ja", "jp", "ja-jp"):
        return "ja"
    return raw if raw in _SUPPORTED else "zh-TW"


class TopicDisplayTranslationService:
    def __init__(self):
        self.topic_repo = TopicRepository()
        self.trans_repo = TopicTranslationRepository()

    async def translate_display(
        self,
        topic_id: str,
        target_language: str,
        translation_type: str = TranslationType.STANDARD,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        topic = await self.topic_repo.get_topic_by_id(topic_id)
        if not topic:
            return None, "topic_not_found"

        target = normalize_language(target_language)
        collection_lang = normalize_language(topic.get("display_language") or "zh-TW")
        trans_type = (
            TranslationType.KOL
            if translation_type == TranslationType.KOL
            else TranslationType.STANDARD
        )

        if target == collection_lang and trans_type == TranslationType.STANDARD:
            return self._build_result(topic, target, collection_lang, cached=True), None

        key = translation_key(topic_id, target, trans_type)

        async def _work():
            cached = await self.trans_repo.get_translation(topic_id, target, trans_type)
            if cached and cached.get("cached_title"):
                log_cost_event("I18N_CACHE_HIT", topic_id=topic_id, lang=target, type=trans_type)
                return self._from_cache(topic, target, collection_lang, cached), None

            log_cost_event("CACHE_MISS", topic_id=topic_id, lang=target, type=trans_type)
            summary_flash = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()
            if not summary_flash:
                return None, "empty_content"

            if trans_type == TranslationType.KOL:
                title, content, provider = await self._kol_style(topic, summary_flash, target)
            else:
                title, content, provider = await self._standard(topic, summary_flash, target)

            await self.trans_repo.upsert_translation({
                "topic_id": topic_id,
                "lang": target,
                "type": trans_type,
                "cached_title": title[:200],
                "cached_content": (content or "")[:400],
                "provider": provider,
            })
            await self._sync_titles_i18n(topic_id, topic, target, title, content)
            topic_updated = await self.topic_repo.get_topic_by_id(topic_id) or topic
            return self._build_result(
                topic_updated, target, collection_lang,
                cached=False,
                override_title=title,
                override_desc=content,
            ), None

        return await with_inflight(key, _work)

    async def _standard(
        self, topic: Dict[str, Any], summary_flash: str, target: str
    ) -> Tuple[str, str, str]:
        title_src = (topic.get("title") or summary_flash)[:500]
        title_t, p1 = await translate_with_fallback(title_src, target, summary_flash)
        body_t, p2 = await translate_with_fallback(summary_flash, target, summary_flash)
        provider = p1 if p1 == "deepl" else p2
        return title_t, body_t, provider

    async def _kol_style(
        self, topic: Dict[str, Any], summary_flash: str, target: str
    ) -> Tuple[str, str, str]:
        from app.config import settings
        from app.services.ai.ai_service_factory import AIServiceFactory

        lang_labels = {"zh-TW": "繁體中文", "en": "English", "ja": "日本語"}
        flash_model = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL
        ai = AIServiceFactory.get_service(settings.AI_SERVICE)
        prompt = (
            f"將以下摘要改寫為{lang_labels.get(target, target)}網紅社群貼文風格"
            f"（標題一行、內文約150字）：\n{summary_flash[:400]}"
        )
        try:
            raw = await ai._call_api(prompt, model=flash_model)
            lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip()]
            title = lines[0][:200] if lines else topic.get("title", "")[:200]
            content = "\n".join(lines[1:])[:400] if len(lines) > 1 else raw[:400]
            return title, content, TranslationProvider.FLASH
        except Exception as e:
            logger.warning("kol_style Flash 失敗: %s", e)
            return await self._standard(topic, summary_flash, target)

    async def _sync_titles_i18n(
        self, topic_id: str, topic: Dict[str, Any], target: str, title: str, desc: Optional[str]
    ) -> None:
        titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
        desc_i18n: Dict[str, str] = dict(topic.get("description_i18n") or {})
        titles_i18n[target] = title
        if desc:
            desc_i18n[target] = desc[:200]
        await self.topic_repo.update_topic(topic_id, {
            "titles_i18n": titles_i18n,
            "description_i18n": desc_i18n,
            "updated_at": datetime.utcnow(),
        })

    def _from_cache(
        self, topic: Dict[str, Any], target: str, collection_lang: str, cached: Dict[str, Any]
    ) -> Dict[str, Any]:
        return self._build_result(
            topic, target, collection_lang, cached=True,
            override_title=cached.get("cached_title"),
            override_desc=cached.get("cached_content"),
        )

    def _build_result(
        self,
        topic: Dict[str, Any],
        target: str,
        collection_lang: str,
        cached: bool,
        override_title: Optional[str] = None,
        override_desc: Optional[str] = None,
    ) -> Dict[str, Any]:
        titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
        desc_i18n: Dict[str, str] = dict(topic.get("description_i18n") or {})

        if target == collection_lang:
            title = topic.get("title") or ""
            description = topic.get("description")
        elif override_title:
            title = override_title
            description = override_desc or desc_i18n.get(target) or topic.get("description")
        elif target in titles_i18n and titles_i18n[target]:
            title = titles_i18n[target]
            description = desc_i18n.get(target) or topic.get("description")
        else:
            title = topic.get("title") or ""
            description = topic.get("description")

        original = topic.get("original_title") or None
        if original and original.strip() == (title or "").strip():
            original = None

        return {
            "topic_id": topic["id"],
            "title": title,
            "description": description,
            "target_language": target,
            "display_language": collection_lang,
            "original_title": original,
            "cached": cached,
            "titles_i18n": titles_i18n,
            "description_i18n": desc_i18n,
        }


topic_display_translation_service = TopicDisplayTranslationService()

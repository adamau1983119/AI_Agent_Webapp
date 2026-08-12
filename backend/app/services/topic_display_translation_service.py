"""主題標題／摘要「譯為目前語言」— DeepSeek Flash 成套（一語一包）。"""
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.models.topic_translation import TranslationType, TranslationProvider
from app.services.translation.flash_pack_provider import translate_title_desc_pack
from app.services.translation.inflight_guard import with_inflight, translation_key
from app.utils.logger import log_cost_event
from app.utils.topic_languages import (
    normalize_topic_language as normalize_language,
    title_script_mismatch,
    usable_cached_title,
)
import logging

logger = logging.getLogger(__name__)


def _pack_ready(title: Optional[str], desc: Optional[str], need_desc: bool) -> bool:
    if usable_cached_title(title) is None:
        return False
    if need_desc and usable_cached_title(desc) is None:
        return False
    return True


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
        need_desc = bool((topic.get("description") or topic.get("summary_flash") or "").strip())

        if target == collection_lang and trans_type == TranslationType.STANDARD:
            title = (topic.get("title") or "").strip()
            if not title_script_mismatch(title, collection_lang):
                return self._build_result(topic, target, collection_lang, cached=True), None

        key = translation_key(topic_id, target, trans_type)

        async def _work():
            return await self._translate_work(
                topic_id, topic, target, collection_lang, trans_type, need_desc
            )

        return await with_inflight(key, _work)

    async def _translate_work(
        self, topic_id, topic, target, collection_lang, trans_type, need_desc
    ):
        titles_i18n = dict(topic.get("titles_i18n") or {})
        desc_i18n = dict(topic.get("description_i18n") or {})
        if _pack_ready(titles_i18n.get(target), desc_i18n.get(target), need_desc):
            log_cost_event("I18N_CACHE_HIT", topic_id=topic_id, lang=target, type=trans_type)
            return self._build_result(topic, target, collection_lang, cached=True), None

        cached = await self.trans_repo.get_translation(topic_id, target, trans_type)
        c_title = usable_cached_title((cached or {}).get("cached_title") if cached else None)
        c_desc = usable_cached_title((cached or {}).get("cached_content") if cached else None)
        if cached and _pack_ready(c_title, c_desc, need_desc):
            log_cost_event("I18N_CACHE_HIT", topic_id=topic_id, lang=target, type=trans_type)
            await self._sync_pack(topic_id, topic, target, c_title, c_desc or "")
            topic = await self.topic_repo.get_topic_by_id(topic_id) or topic
            return self._from_cache(topic, target, collection_lang, {
                **cached, "cached_title": c_title, "cached_content": c_desc,
            }), None

        log_cost_event("CACHE_MISS", topic_id=topic_id, lang=target, type=trans_type)
        from app.utils.cost_controls import deepseek_configured
        if not deepseek_configured():
            return None, "deepseek_not_configured"

        summary = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()
        if not summary:
            return None, "empty_content"

        if trans_type == TranslationType.KOL:
            title, content, provider = await self._kol_style(topic, summary, target)
        else:
            title, content, provider = await self._standard(topic, summary, target)

        if provider == "fallback" or not _pack_ready(title, content, need_desc):
            return None, "translation_fallback"

        await self.trans_repo.upsert_translation({
            "topic_id": topic_id,
            "lang": target,
            "type": trans_type,
            "cached_title": title[:200],
            "cached_content": (content or "")[:400],
            "provider": provider,
        })
        await self._sync_pack(topic_id, topic, target, title, content or "")
        topic_updated = await self.topic_repo.get_topic_by_id(topic_id) or topic
        return self._build_result(
            topic_updated, target, collection_lang,
            cached=False, override_title=title, override_desc=content,
        ), None

    async def _standard(self, topic, summary_flash, target):
        title_src = (topic.get("title") or summary_flash)[:500]
        desc_src = (topic.get("description") or summary_flash)[:800]
        return await translate_title_desc_pack(title_src, desc_src, target)

    async def _kol_style(self, topic, summary_flash, target):
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
            if usable_cached_title(title) is None:
                return await self._standard(topic, summary_flash, target)
            return title, content, TranslationProvider.FLASH
        except Exception as e:
            logger.warning("kol_style Flash 失敗: %s", e)
            return await self._standard(topic, summary_flash, target)

    async def _sync_pack(self, topic_id, topic, target, title, desc):
        """一語一包寫入；禁止只寫 title。"""
        titles_i18n: Dict[str, str] = dict(topic.get("titles_i18n") or {})
        desc_i18n: Dict[str, str] = dict(topic.get("description_i18n") or {})
        titles_i18n[target] = title[:200]
        desc_i18n[target] = (desc or "")[:200]
        await self.topic_repo.update_topic(topic_id, {
            "titles_i18n": titles_i18n,
            "description_i18n": desc_i18n,
            "updated_at": datetime.utcnow(),
        })

    def _from_cache(self, topic, target, collection_lang, cached):
        return self._build_result(
            topic, target, collection_lang, cached=True,
            override_title=cached.get("cached_title"),
            override_desc=cached.get("cached_content"),
        )

    def _build_result(
        self, topic, target, collection_lang, cached,
        override_title=None, override_desc=None,
    ):
        titles_i18n = dict(topic.get("titles_i18n") or {})
        desc_i18n = dict(topic.get("description_i18n") or {})
        need_desc = bool((topic.get("description") or topic.get("summary_flash") or "").strip())

        # 一語一包優先（含 target==收集語但 title 仍為英文腳本的情況）
        if _pack_ready(override_title, override_desc, need_desc):
            title = override_title
            description = override_desc if need_desc else topic.get("description")
        elif _pack_ready(titles_i18n.get(target), desc_i18n.get(target), need_desc):
            title = titles_i18n[target]
            description = desc_i18n.get(target) if need_desc else topic.get("description")
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

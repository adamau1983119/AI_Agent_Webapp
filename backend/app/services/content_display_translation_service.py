"""詳情長文按需同語：Flash 譯 article/script → Mongo i18n 快取（MD-M2 ≤150）。"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional, Tuple

from app.config import settings
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.topic_repository import TopicRepository
from app.utils.cost_controls import deepseek_configured
from app.utils.logger import log_cost_event
from app.utils.topic_languages import normalize_topic_language, usable_cached_title

logger = logging.getLogger(__name__)
_FLASH_RETRIES = 2
_FLASH_RETRY_DELAY_SEC = 1.5


async def _flash_long_text(text: str, target: str, field: str) -> Optional[str]:
    """長文：複用 pack prompt（title=field 標籤、description=正文）。"""
    label = {"zh-TW": "Traditional Chinese", "en": "English", "ja": "Japanese"}.get(
        target, target
    )
    from app.services.ai.ai_service_factory import AIServiceFactory

    flash = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL
    ai = AIServiceFactory.get_service(settings.AI_SERVICE)
    prompt = (
        f"Translate the following {field} into {label}. "
        "Return ONLY JSON: {\"title\":\"ok\",\"description\":\"<full translation>\"}. "
        "Preserve structure; no [Fallback-] prefix.\n"
        f"{(text or '')[:6000]}"
    )
    last_err: Optional[Exception] = None
    for attempt in range(_FLASH_RETRIES + 1):
        try:
            raw = await ai._call_api(prompt, model=flash, max_tokens=4096)
            from app.services.translation.flash_pack_provider import _parse_json

            data = _parse_json(raw)
            out = usable_cached_title(str(data.get("description") or ""))
            if out:
                return out
            last_err = ValueError("empty_translation")
        except Exception as exc:
            last_err = exc
            logger.warning(
                "content flash %s fail attempt=%s: %s", field, attempt + 1, exc
            )
        if attempt < _FLASH_RETRIES:
            await asyncio.sleep(_FLASH_RETRY_DELAY_SEC)
    logger.warning("content flash %s exhausted: %s", field, last_err)
    return None


class ContentDisplayTranslationService:
    def __init__(self):
        self.content_repo = ContentRepository()
        self.topic_repo = TopicRepository()

    async def resolve_for_ui(
        self, topic_id: str, ui_lang: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """回傳 content 文檔（article/script 已換成 ui_lang）；失敗 err。"""
        content = await self.content_repo.get_content_by_topic_id(topic_id)
        if not content:
            return None, "content_not_found"
        topic = await self.topic_repo.get_topic_by_id(topic_id)
        collection = normalize_topic_language(
            (topic or {}).get("display_language") or "zh-TW"
        )
        target = normalize_topic_language(ui_lang)
        if target == collection:
            out = dict(content)
            out["content_language"] = collection
            out["translation_pending"] = False
            return out, None

        article = (content.get("article") or "").strip()
        script = (content.get("script") or "").strip()
        art_i18n: Dict[str, str] = dict(content.get("article_i18n") or {})
        scr_i18n: Dict[str, str] = dict(content.get("script_i18n") or {})

        need_a, need_s = bool(article), bool(script)
        have_a = (not need_a) or bool(usable_cached_title(art_i18n.get(target)))
        have_s = (not need_s) or bool(usable_cached_title(scr_i18n.get(target)))
        if have_a and have_s:
            out = self._overlay(content, art_i18n, scr_i18n, target, need_a, need_s)
            out["translation_pending"] = False
            return out, None

        if not deepseek_configured():
            return None, "deepseek_not_configured"

        log_cost_event("CACHE_MISS", topic_id=topic_id, lang=target, type="content_body")
        if need_a and not have_a:
            translated = await _flash_long_text(article, target, "article")
            if not translated:
                return self._pending_fallback(content, collection), "translation_fallback"
            art_i18n[target] = translated
        if need_s and not have_s:
            translated = await _flash_long_text(script, target, "script")
            if not translated:
                return self._pending_fallback(content, collection), "translation_fallback"
            scr_i18n[target] = translated

        cid = content.get("id") or topic_id
        await self.content_repo.update_content(
            cid,
            {"article_i18n": art_i18n, "script_i18n": scr_i18n},
            create_version=False,
        )
        content["article_i18n"] = art_i18n
        content["script_i18n"] = scr_i18n
        out = self._overlay(content, art_i18n, scr_i18n, target, need_a, need_s)
        out["translation_pending"] = False
        return out, None

    def _pending_fallback(self, content: Dict[str, Any], collection: str) -> Dict[str, Any]:
        out = dict(content)
        out["content_language"] = collection
        out["translation_pending"] = True
        return out

    def _overlay(self, content, art_i18n, scr_i18n, target, need_a, need_s):
        out = dict(content)
        if need_a:
            out["article"] = art_i18n.get(target) or content.get("article")
        if need_s:
            out["script"] = scr_i18n.get(target) or content.get("script")
        out["content_language"] = target
        return out


content_display_translation_service = ContentDisplayTranslationService()

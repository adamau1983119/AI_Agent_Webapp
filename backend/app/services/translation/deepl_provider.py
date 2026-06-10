"""
DeepL 翻譯 + D4 字串 Fallback（v7 Phase 2）
"""
import logging
from typing import Optional

import httpx

from app.config import settings
from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)

_DEEPL_LANG = {
    "zh-TW": "ZH-HANT",
    "en": "EN-US",
    "ja": "JA",
}

_FALLBACK_PREFIX = {
    "ja": "[Fallback-JA]",
    "en": "[Fallback-EN]",
    "zh-TW": "[Fallback-ZH]",
}


def _fallback_text(lang: str, summary_flash: str) -> str:
    prefix = _FALLBACK_PREFIX.get(lang, "[Fallback]")
    log_cost_event(
        "TRANSLATION_FALLBACK_TRIGGERED",
        lang=lang,
        chars=len(summary_flash),
    )
    return f"{prefix} {summary_flash}"


async def translate_deepl_once(text: str, target_lang: str) -> Optional[str]:
    """單次 DeepL；失敗回 None（不重試、不 Fallback）。"""
    source = (text or "").strip()
    if not source:
        return None
    api_key = getattr(settings, "DEEPL_API_KEY", "") or ""
    if not api_key:
        return None
    deepl_lang = _DEEPL_LANG.get(target_lang)
    if not deepl_lang:
        return None
    timeout = float(getattr(settings, "TRANSLATION_TIMEOUT_SEC", 5) or 5)
    base_url = getattr(settings, "DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                base_url,
                data={
                    "auth_key": api_key,
                    "text": source[:5000],
                    "target_lang": deepl_lang,
                },
            )
            resp.raise_for_status()
            translations = resp.json().get("translations") or []
            if translations:
                return translations[0].get("text", source).strip()
    except Exception as e:
        logger.warning("DeepL 單次失敗 (%s): %s", target_lang, e)
    return None


async def translate_with_fallback(
    text: str,
    target_lang: str,
    summary_flash_for_fallback: Optional[str] = None,
) -> tuple[str, str]:
    """
    DeepL 翻譯；失敗或逾時 → 字串 Fallback。
    Returns: (translated_text, provider)
    """
    source = (text or "").strip()
    fallback_src = (summary_flash_for_fallback or source or "").strip()
    if not source:
        return _fallback_text(target_lang, fallback_src), "fallback"

    api_key = getattr(settings, "DEEPL_API_KEY", "") or ""
    if not api_key:
        return _fallback_text(target_lang, fallback_src), "fallback"

    deepl_lang = _DEEPL_LANG.get(target_lang)
    if not deepl_lang:
        return _fallback_text(target_lang, fallback_src), "fallback"

    timeout = float(getattr(settings, "TRANSLATION_TIMEOUT_SEC", 5) or 5)
    base_url = getattr(settings, "DEEPL_API_URL", "https://api-free.deepl.com/v2/translate")

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                base_url,
                data={
                    "auth_key": api_key,
                    "text": source[:5000],
                    "target_lang": deepl_lang,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            translations = data.get("translations") or []
            if translations:
                return translations[0].get("text", source).strip(), "deepl"
    except Exception as e:
        logger.warning("DeepL 失敗 (%s): %s", target_lang, e)

    return _fallback_text(target_lang, fallback_src), "fallback"

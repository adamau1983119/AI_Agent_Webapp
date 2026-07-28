"""
Discover 標題／摘要 DeepL（標題 ≤20 字；摘要 ≤400；重試後 Fallback）
"""
import logging
from typing import Optional

from app.config import settings
from app.services.translation.deepl_provider import translate_deepl_once
from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)

PUBLIC_TITLE_MAX_CHARS = 20
PUBLIC_SUMMARY_MAX_CHARS = 400


def _title_fallback(lang: str, source: str) -> str:
    """無 DeepL 時仍讓 zh-TW／ja 標題可區分（CD-4-3）。"""
    log_cost_event(
        "TRANSLATION_FALLBACK_TRIGGERED",
        lang=lang,
        chars=len(source),
    )
    prefix = {"ja": "【仮】", "zh-TW": "【暫】"}.get(lang, "")
    budget = max(0, PUBLIC_TITLE_MAX_CHARS - len(prefix))
    return f"{prefix}{source[:budget]}"


def _summary_fallback(lang: str, source: str, *, en_hint: str = "") -> str:
    """摘要 fallback：zh-TW 用 Flash 原文；en／ja 優先英文提示。"""
    log_cost_event(
        "TRANSLATION_FALLBACK_TRIGGERED",
        lang=lang,
        chars=len(source or en_hint),
    )
    if lang == "zh-TW":
        return (source or en_hint)[:PUBLIC_SUMMARY_MAX_CHARS]
    if lang == "en":
        return (en_hint or source or "").strip()[:PUBLIC_SUMMARY_MAX_CHARS]
    base = (en_hint or source or "").strip()
    prefix = "【仮】" if lang == "ja" else ""
    return f"{prefix}{base}"[:PUBLIC_SUMMARY_MAX_CHARS]


async def _flash_translate_summary(text: str, target_lang: str) -> Optional[str]:
    """DeepL 不可用時，以 Flash 補日文／英文／繁中摘要（讀取路徑仍零 LLM）。"""
    lang_name = {
        "ja": "日本語",
        "zh-TW": "繁體中文",
        "en": "English",
    }.get(target_lang)
    source = (text or "").strip()
    if not lang_name or not source:
        return None
    try:
        from app.services.ai.ai_service_factory import AIServiceFactory

        ai = AIServiceFactory.get_service(settings.AI_SERVICE)
        flash = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL
        prompt = (
            f"將下列摘要翻譯成{lang_name}。只輸出譯文，不要解釋或加標題。\n\n"
            f"{source[:350]}"
        )
        out = await ai._call_api(prompt, model=flash, max_tokens=600)
        out = (out or "").strip()
        return out[:PUBLIC_SUMMARY_MAX_CHARS] if out else None
    except Exception as e:
        logger.warning("Flash 摘要翻譯失敗 (%s): %s", target_lang, e)
        return None


async def translate_public_title(text: str, target_lang: str) -> str:
    title, _ = await translate_public_title_with_meta(text, target_lang)
    return title


async def translate_public_title_with_meta(text: str, target_lang: str) -> tuple[str, str]:
    """回傳 (標題, provider) — provider: deepl | fallback。"""
    from app.models.topic_translation import TranslationProvider

    source = (text or "").strip()
    if not source:
        return "", TranslationProvider.FALLBACK
    retries = int(getattr(settings, "MAX_TRANSLATION_RETRIES", 3) or 3)
    for _ in range(retries):
        translated = await translate_deepl_once(source, target_lang)
        if translated:
            return translated[:PUBLIC_TITLE_MAX_CHARS], TranslationProvider.DEEPL
    logger.info("Discover 標題 DeepL 重試耗盡 (%s)，走 Fallback", target_lang)
    return _title_fallback(target_lang, source), TranslationProvider.FALLBACK


async def translate_public_summary_with_meta(
    text: str,
    target_lang: str,
    *,
    en_hint: str = "",
) -> tuple[str, str]:
    """回傳 (摘要, provider) — deepl | flash | fallback。"""
    from app.models.topic_translation import TranslationProvider

    source = (text or "").strip()
    if not source and not (en_hint or "").strip():
        return "", TranslationProvider.FALLBACK
    # Flash 摘要多為繁中：zh-TW 直接沿用，避免再燒一輪翻譯
    if target_lang == "zh-TW" and source:
        return source[:PUBLIC_SUMMARY_MAX_CHARS], TranslationProvider.FALLBACK
    # RSS 原文為英文：en 優先用 en_hint，零 LLM
    if target_lang == "en" and (en_hint or "").strip():
        return en_hint.strip()[:PUBLIC_SUMMARY_MAX_CHARS], TranslationProvider.FALLBACK
    retries = int(getattr(settings, "MAX_TRANSLATION_RETRIES", 3) or 3)
    for _ in range(retries):
        translated = await translate_deepl_once(source or en_hint, target_lang)
        if translated:
            return translated[:PUBLIC_SUMMARY_MAX_CHARS], TranslationProvider.DEEPL
    flash_out = await _flash_translate_summary(source or en_hint, target_lang)
    if flash_out:
        logger.info("Discover 摘要改用 Flash 翻譯 (%s)", target_lang)
        return flash_out, TranslationProvider.FLASH
    logger.info("Discover 摘要 DeepL／Flash 皆失敗 (%s)，走 Fallback", target_lang)
    return (
        _summary_fallback(target_lang, source, en_hint=en_hint),
        TranslationProvider.FALLBACK,
    )

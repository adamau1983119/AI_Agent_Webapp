"""
Discover 標題 DeepL（≤20 字 · 最多 MAX_TRANSLATION_RETRIES 次）
"""
import logging

from app.config import settings
from app.services.translation.deepl_provider import translate_deepl_once
from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)

PUBLIC_TITLE_MAX_CHARS = 20


def _title_fallback(lang: str, source: str) -> str:
    log_cost_event(
        "TRANSLATION_FALLBACK_TRIGGERED",
        lang=lang,
        chars=len(source),
    )
    return source[:PUBLIC_TITLE_MAX_CHARS]


async def translate_public_title(text: str, target_lang: str) -> str:
    """單卡單語標題翻譯；逾重試次數走字串 Fallback。"""
    source = (text or "").strip()
    if not source:
        return ""
    retries = int(getattr(settings, "MAX_TRANSLATION_RETRIES", 3) or 3)
    for _ in range(retries):
        translated = await translate_deepl_once(source, target_lang)
        if translated:
            return translated[:PUBLIC_TITLE_MAX_CHARS]
    logger.info("Discover 標題 DeepL 重試耗盡 (%s)，走 Fallback", target_lang)
    return _title_fallback(target_lang, source)

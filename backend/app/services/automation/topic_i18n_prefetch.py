"""
Collect-time: honest display_language + DeepL titles/descriptions for all UI langs.
en/ja slots are forced valid — CJK under en is rewritten.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.services.automation.title_lang_detect import (
    detect_title_language,
    resolve_stored_display_language,
    text_matches_lang,
)
from app.services.translation.deepl_provider import translate_deepl_once
from app.utils.cost_controls import topic_i18n_prefetch_enabled

logger = logging.getLogger(__name__)
_LANGS = ("zh-TW", "en", "ja")


async def _deepl_with_retry(text: str, target: str) -> str | None:
    for _ in range(2):
        out = await translate_deepl_once(text, target)
        if out and not out.startswith("[Fallback"):
            return out
    return None


async def _fill_i18n(base: str, native_lang: str, existing: dict[str, str]) -> dict[str, str]:
    out = {
        k: v
        for k, v in dict(existing or {}).items()
        if isinstance(v, str) and v.strip() and text_matches_lang(v, k)
    }
    text = (base or "").strip()
    if not text:
        return out
    if text_matches_lang(text, native_lang):
        out.setdefault(native_lang, text)
    elif native_lang not in out:
        out[native_lang] = text

    if not topic_i18n_prefetch_enabled():
        return out

    missing = [lang for lang in _LANGS if lang not in out]
    if missing:
        results = await asyncio.gather(
            *[_deepl_with_retry(text, lang) for lang in missing]
        )
        for lang, translated in zip(missing, results):
            if translated and text_matches_lang(translated, lang):
                out[lang] = translated
            elif translated:
                out[lang] = translated
            else:
                logger.warning("topic_i18n missing target=%s", lang)
    return out


async def finalize_topic_languages(
    topic: dict[str, Any],
    *,
    source_title: str,
    requested_lang: str,
    translation_applied: bool,
) -> dict[str, Any]:
    stored = str(topic.get("title") or "").strip()
    source = (source_title or "").strip()
    lang = resolve_stored_display_language(
        source_title=source,
        stored_title=stored,
        requested_lang=requested_lang,
        translation_applied=translation_applied,
    )
    topic["display_language"] = lang

    titles = dict(topic.get("titles_i18n") or {})
    if stored and text_matches_lang(stored, lang):
        titles[lang] = stored
    if source:
        src_lang = detect_title_language(source)
        if text_matches_lang(source, src_lang):
            titles.setdefault(src_lang, source)

    titles = await _fill_i18n(stored, lang, titles)
    if titles:
        topic["titles_i18n"] = titles

    desc = str(topic.get("description") or "").strip()
    if desc:
        descriptions = await _fill_i18n(
            desc, lang, dict(topic.get("description_i18n") or {})
        )
        if descriptions:
            topic["description_i18n"] = descriptions
    return topic

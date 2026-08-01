"""
Collect-time: honest display_language + DeepL titles/descriptions for all UI langs.
Cost tradeoff intentional — topic cards must match supported languages without wait.
"""
from __future__ import annotations

from typing import Any

from app.services.automation.title_lang_detect import (
    detect_title_language,
    resolve_stored_display_language,
)
from app.services.translation.deepl_provider import translate_deepl_once
from app.utils.cost_controls import topic_i18n_prefetch_enabled

_LANGS = ("zh-TW", "en", "ja")


async def _fill_i18n(base: str, native_lang: str, existing: dict[str, str]) -> dict[str, str]:
    out = dict(existing or {})
    text = (base or "").strip()
    if not text:
        return out
    out.setdefault(native_lang, text)
    if not topic_i18n_prefetch_enabled():
        return out
    for target in _LANGS:
        if out.get(target):
            continue
        translated = await translate_deepl_once(text, target)
        if translated and not translated.startswith("[Fallback"):
            out[target] = translated
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
    if stored:
        titles.setdefault(lang, stored)
    if source:
        titles.setdefault(detect_title_language(source), source)
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

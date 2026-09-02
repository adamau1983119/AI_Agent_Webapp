"""Content Locale resolver — ui_lang 成套 overlay（MD-M2 ≤150）。"""
from __future__ import annotations

import copy
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.topic_translation import TranslationProvider, TranslationType
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.flash_pack_provider import translate_packs_batch
from app.utils.topic_languages import (
    normalize_topic_language,
    title_script_mismatch,
    usable_cached_title,
)

logger = logging.getLogger(__name__)
_LIST_BATCH = 5
_LIST_MAX_BATCHES = 6


def _need_desc(topic: Dict[str, Any]) -> bool:
    return bool((topic.get("description") or topic.get("summary_flash") or "").strip())


def _pack_ready(
    title: Optional[str], desc: Optional[str], need_desc: bool, lang: Optional[str] = None
) -> bool:
    if usable_cached_title(title, lang) is None:
        return False
    if need_desc and usable_cached_title(desc) is None:
        return False
    return True


def apply_locale_overlay(topic: Dict[str, Any], ui_lang: str) -> Dict[str, Any]:
    """快取優先；locale_resolved=False 表示仍為收集語 fallback。"""
    out = copy.deepcopy(topic)
    lang = normalize_topic_language(ui_lang)
    collection = normalize_topic_language(out.get("display_language") or "zh-TW")
    need = _need_desc(out)
    titles = dict(out.get("titles_i18n") or {})
    descs = dict(out.get("description_i18n") or {})
    src_i18n = dict(out.get("source_content_i18n") or {})
    if src_i18n.get(lang):
        out["translated_source_content"] = src_i18n[lang]
    t, d = titles.get(lang), descs.get(lang)
    if _pack_ready(t, d, need, lang):
        out["title"] = t[:200]
        if need and d:
            out["description"] = d[:200]
        out["content_locale"] = lang
        out["locale_resolved"] = True
        return out
    raw = (out.get("title") or "").strip()
    if lang == collection and not title_script_mismatch(raw, collection):
        out["content_locale"] = collection
        out["locale_resolved"] = True
        return out
    out["content_locale"] = collection
    out["locale_resolved"] = False
    return out


async def _write_pack(
    topic_id: str, lang: str, title_t: str, desc_t: str, repo, trans_repo
) -> None:
    topic = await repo.get_topic_by_id(topic_id)
    if not topic:
        return
    titles_i18n = dict(topic.get("titles_i18n") or {})
    desc_i18n = dict(topic.get("description_i18n") or {})
    titles_i18n[lang] = title_t[:200]
    desc_i18n[lang] = (desc_t or "")[:200]
    await trans_repo.upsert_translation({
        "topic_id": topic_id, "lang": lang, "type": TranslationType.STANDARD,
        "cached_title": title_t[:200], "cached_content": (desc_t or "")[:400],
        "provider": TranslationProvider.FLASH,
    })
    await repo.update_topic(topic_id, {
        "titles_i18n": titles_i18n, "description_i18n": desc_i18n,
        "updated_at": datetime.utcnow(),
    })


async def resolve_topic_locale(
    topic: Dict[str, Any], ui_lang: str, *, translate_on_miss: bool = False
) -> Dict[str, Any]:
    out = apply_locale_overlay(topic, ui_lang)
    if out.get("locale_resolved") or not translate_on_miss:
        return out
    tid = str(out.get("id") or "")
    if not tid:
        return out
    from app.services.topic_display_translation_service import topic_display_translation_service

    result, err = await topic_display_translation_service.translate_display(
        tid, ui_lang, TranslationType.STANDARD
    )
    if err or not result:
        return out
    fresh = await TopicRepository().get_topic_by_id(tid)
    return apply_locale_overlay(fresh or out, ui_lang)


async def resolve_topics_list_locale(
    topics: List[Dict[str, Any]], ui_lang: str, *, translate_on_miss: bool = False
) -> List[Dict[str, Any]]:
    """列表：預設只 overlay 快取。translate_on_miss 才批次 Flash（產卡 finalize 寫齊）。"""
    lang = normalize_topic_language(ui_lang)
    repo, trans_repo = TopicRepository(), TopicTranslationRepository()
    by_id = {str(t.get("id")): t for t in topics if t.get("id")}
    resolved = {tid: apply_locale_overlay(t, lang) for tid, t in by_id.items()}
    misses = [t for tid, t in by_id.items() if not resolved[tid].get("locale_resolved")]
    if translate_on_miss and misses:
        from app.utils.cost_controls import deepseek_configured

        if deepseek_configured():
            batches = 0
            idx = 0
            while idx < len(misses) and batches < _LIST_MAX_BATCHES:
                chunk = misses[idx : idx + _LIST_BATCH]
                idx += _LIST_BATCH
                batches += 1
                items = []
                for t in chunk:
                    title_src = (
                        t.get("original_title") or t.get("title") or ""
                    ).strip()
                    if not title_src:
                        continue
                    desc_src = (
                        t.get("description") or t.get("summary_flash") or ""
                    ).strip()
                    items.append({
                        "id": t["id"],
                        "title": title_src[:500],
                        "description": desc_src[:800],
                    })
                if not items:
                    continue
                mapped = await translate_packs_batch(items, lang)
                for tid, pack in mapped.items():
                    await _write_pack(tid, lang, pack[0], pack[1], repo, trans_repo)
            for tid in list(resolved.keys()):
                if not resolved[tid].get("locale_resolved"):
                    fresh = await repo.get_topic_by_id(tid)
                    if fresh:
                        resolved[tid] = apply_locale_overlay(fresh, lang)
    return [resolved[str(t.get("id"))] for t in topics if t.get("id") in resolved]

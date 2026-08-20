"""產卡後 Flash 成套預載 → topic_translations + titles/description_i18n。

MD-M2：本檔 ≤150；批次呼叫見 flash_pack_provider。
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.models.topic_translation import TranslationProvider, TranslationType
from app.services.automation.topic_title_normalize import normalize_topic_title_for_display_lang
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.flash_pack_provider import translate_packs_batch
from app.utils.cost_controls import (
    deepseek_configured,
    topic_triple_preload_cap,
    topic_triple_preload_enabled,
)
from app.utils.logger import log_cost_event
from app.utils.topic_languages import (
    normalize_topic_language,
    preload_languages_for,
    usable_cached_title,
)

logger = logging.getLogger(__name__)


def _pack_ready(
    title, desc, need_desc: bool, lang: Optional[str] = None
) -> bool:
    if usable_cached_title(title, lang) is None:
        return False
    if need_desc and usable_cached_title(desc) is None:
        return False
    return True


async def _write_pack(repo, trans_repo, topic, lang, title_t, desc_t) -> None:
    topic_id = topic["id"]
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
    topic["titles_i18n"], topic["description_i18n"] = titles_i18n, desc_i18n
    log_cost_event("TRANSLATION_PRELOAD", topic_id=topic_id, lang=lang, provider="deepseek_flash")


async def preload_topic_titles(topic_ids: List[str]) -> Dict[str, Any]:
    """批次預載：正規化收集語言後，Flash 成套預載其餘語言（每批 ≤5）。"""
    if not topic_triple_preload_enabled():
        return {"status": "disabled", "processed": 0, "translated": 0}
    if not deepseek_configured():
        logger.warning("TOPIC_TRIPLE_PRELOAD skipped: DEEPSEEK_API_KEY empty")
        return {"status": "deepseek_not_configured", "processed": 0, "translated": 0}

    cap = topic_triple_preload_cap()
    repo, trans_repo = TopicRepository(), TopicTranslationRepository()
    processed = translated = skipped = 0
    pending: Dict[str, List[Tuple[Dict[str, Any], Dict[str, str]]]] = {}

    for topic_id in topic_ids:
        if translated >= cap:
            break
        processed += 1
        topic = await repo.get_topic_by_id(topic_id)
        if not topic:
            continue
        try:
            title_src, did_norm = await normalize_topic_title_for_display_lang(
                topic_id, topic, repo=repo, trans_repo=trans_repo
            )
            if did_norm:
                translated += 1
                topic = await repo.get_topic_by_id(topic_id) or topic
        except Exception as exc:
            logger.warning("preload normalize %s: %s", topic_id, exc)
            skipped += 1
            continue

        title_src = (topic.get("title") or title_src or "").strip()
        if not usable_cached_title(title_src):
            skipped += 1
            continue
        display_lang = normalize_topic_language(topic.get("display_language"))
        titles_i18n = dict(topic.get("titles_i18n") or {})
        desc_i18n = dict(topic.get("description_i18n") or {})
        titles_i18n.setdefault(display_lang, title_src[:200])
        desc_src = (topic.get("description") or topic.get("summary_flash") or "").strip()
        need_desc = bool(desc_src)
        if need_desc:
            desc_i18n.setdefault(display_lang, desc_src[:200])
        topic["titles_i18n"], topic["description_i18n"] = titles_i18n, desc_i18n

        for lang in preload_languages_for(display_lang):
            if translated >= cap:
                break
            if _pack_ready(titles_i18n.get(lang), desc_i18n.get(lang), need_desc, lang):
                continue
            cached = await trans_repo.get_translation(topic_id, lang, TranslationType.STANDARD)
            c_t = usable_cached_title(
                (cached or {}).get("cached_title") if cached else None, lang
            )
            c_d = usable_cached_title((cached or {}).get("cached_content") if cached else None)
            if cached and _pack_ready(c_t, c_d, need_desc, lang):
                await _write_pack(repo, trans_repo, topic, lang, c_t, c_d or "")
                continue
            title_input = (topic.get("original_title") or title_src)[:500]
            pending.setdefault(lang, []).append((topic, {
                "id": topic_id,
                "title": title_input,
                "description": desc_src[:800],
            }))

    for lang, rows in pending.items():
        i = 0
        while i < len(rows) and translated < cap:
            chunk = rows[i:i + 5]
            i += 5
            mapped = await translate_packs_batch([r[1] for r in chunk], lang)
            for topic, item in chunk:
                pack = mapped.get(item["id"])
                if not pack:
                    skipped += 1
                    continue
                await _write_pack(repo, trans_repo, topic, lang, pack[0], pack[1])
                translated += 1
                if translated >= cap:
                    break

    return {
        "status": "ok",
        "processed": processed,
        "translated": translated,
        "skipped": skipped,
        "cap": cap,
    }

"""DeepSeek Flash：title+description 成套翻譯（標準路徑；MD-M2 ≤150）。"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings
from app.models.topic_translation import TranslationProvider
from app.utils.topic_languages import normalize_topic_language, usable_cached_title

logger = logging.getLogger(__name__)

_LANG = {
    "zh-TW": "Traditional Chinese (繁體中文)",
    "en": "English",
    "ja": "Japanese (日本語)",
}
_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.I)


def _flash_model() -> str:
    return getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL


def _parse_json(raw: str) -> Any:
    text = (raw or "").strip()
    m = _FENCE.search(text)
    if m:
        text = m.group(1).strip()
    return json.loads(text)


def _pack_ok(
    title: Optional[str],
    desc: Optional[str],
    need_desc: bool,
    target_lang: Optional[str] = None,
) -> bool:
    if usable_cached_title(title, target_lang) is None:
        return False
    if need_desc and usable_cached_title(desc) is None:
        return False
    return True


async def translate_title_desc_pack(
    title: str,
    description: str,
    target_lang: str,
) -> Tuple[Optional[str], Optional[str], str]:
    """單卡成套。失敗回 (None, None, fallback)。"""
    src_title = (title or "").strip()
    src_desc = (description or "").strip()
    if not src_title:
        return None, None, "fallback"
    need_desc = bool(src_desc)
    lang = normalize_topic_language(target_lang)
    label = _LANG.get(lang, lang)
    prompt = (
        f"Translate the following topic card completely into natural, fluent {label}. "
        f"You MUST translate both title and description into {label} (do not leave text in the source language). "
        "Return ONLY JSON: {\"title\":\"...\",\"description\":\"...\"}. "
        "Keep meaning; do not add [Fallback-] prefixes.\n"
        f"title: {src_title[:500]}\n"
        f"description: {(src_desc or src_title)[:800]}"
    )
    try:
        from app.services.ai.ai_service_factory import AIServiceFactory

        ai = AIServiceFactory.get_service(settings.AI_SERVICE)
        raw = await ai._call_api(prompt, model=_flash_model(), max_tokens=800)
        data = _parse_json(raw)
        out_t = usable_cached_title(str(data.get("title") or ""), lang)
        out_d = usable_cached_title(str(data.get("description") or ""))
        if not _pack_ok(out_t, out_d, need_desc, lang):
            return None, None, "fallback"
        return out_t, (out_d or "")[:400], TranslationProvider.FLASH
    except Exception as exc:
        logger.warning("flash_pack single fail (%s): %s", lang, exc)
        return None, None, "fallback"


async def translate_packs_batch(
    items: List[Dict[str, str]],
    target_lang: str,
) -> Dict[str, Tuple[str, str]]:
    """批次 ≤5：items=[{id,title,description}] → {id:(title,desc)}。"""
    batch = [it for it in items if (it.get("id") and (it.get("title") or "").strip())][:5]
    if not batch:
        return {}
    lang = normalize_topic_language(target_lang)
    label = _LANG.get(lang, lang)
    payload = [
        {
            "id": it["id"],
            "title": (it.get("title") or "")[:500],
            "description": (it.get("description") or it.get("title") or "")[:800],
        }
        for it in batch
    ]
    prompt = (
        f"Translate each topic card completely into natural, fluent {label}. "
        f"You MUST translate both title and description of every item into {label} (do not leave text in the source language). "
        "Return ONLY a JSON array of "
        "{\"id\":\"...\",\"title\":\"...\",\"description\":\"...\"}. "
        "Keep the same ids; no markdown.\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    try:
        from app.services.ai.ai_service_factory import AIServiceFactory

        ai = AIServiceFactory.get_service(settings.AI_SERVICE)
        raw = await ai._call_api(prompt, model=_flash_model(), max_tokens=2500)
        data = _parse_json(raw)
        if not isinstance(data, list):
            return {}
        out: Dict[str, Tuple[str, str]] = {}
        need_by_id = {
            it["id"]: bool((it.get("description") or "").strip()) for it in batch
        }
        for row in data:
            if not isinstance(row, dict):
                continue
            tid = str(row.get("id") or "")
            title = usable_cached_title(str(row.get("title") or ""), lang)
            desc = usable_cached_title(str(row.get("description") or ""))
            if not tid or not _pack_ok(title, desc, need_by_id.get(tid, False), lang):
                continue
            out[tid] = (title[:200], (desc or "")[:400])
        return out
    except Exception as exc:
        logger.warning("flash_pack batch fail (%s): %s", lang, exc)
        return {}

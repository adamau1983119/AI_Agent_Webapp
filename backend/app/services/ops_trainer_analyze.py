"""Analyze screenshot/text into structure slots via DeepSeek (ops-only)."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

import httpx

from app.schemas.ops_trainer import AnalyzeResponse, StructureSlots
from app.services.ai.deepseek import DeepSeekService

logger = logging.getLogger(__name__)

_META = """You are an ops style analyst. Extract a social-post writing skeleton from the input.
Return JSON ONLY with keys:
language (zh-TW|en|ja), domain (fashion|food|trend), length_bucket (short|long),
write_profile (news_recap|hook_gossip), ref_type (positive|negative),
structure {prefix,fact,quote,context,ending}, body_text, notes.
Rules: structure slots are STYLE patterns (media tag + who/when, quote shape, ending habit),
NOT a copy of the news facts. Prefer news_recap for sourced recap; hook_gossip for gossip hook.
If text looks AI-generic, set ref_type=negative. No markdown.
"""


def _extract_json(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("analyze_no_json")
    return json.loads(text[start : end + 1])


async def _fetch_url_text(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "OpsTrainer/1.0"})
            r.raise_for_status()
            body = r.text or ""
            return body[:8000]
    except Exception as exc:
        logger.warning("ops_trainer url fetch fail: %s", exc)
        return ""


async def analyze_input(
    *,
    text: str = "",
    image_data_url: Optional[str] = None,
    source_url: Optional[str] = None,
    language_hint: Optional[str] = None,
) -> AnalyzeResponse:
    blob = (text or "").strip()
    if source_url and not blob:
        blob = await _fetch_url_text(source_url)
    if not blob and not image_data_url:
        raise ValueError("analyze_empty_input")

    hint = f"\nPreferred language hint: {language_hint}\n" if language_hint else "\n"
    user_prompt = _META + hint + f"SOURCE_TEXT:\n{blob[:8000]}\n"
    if source_url:
        user_prompt += f"SOURCE_URL: {source_url}\n"

    client = DeepSeekService()
    raw = await client.generate_multimodal(user_prompt, image_data_url=image_data_url)
    data = _extract_json(raw)
    struct = data.get("structure") or {}
    lang = str(data.get("language") or language_hint or "zh-TW")
    if lang not in ("zh-TW", "en", "ja"):
        lang = "zh-TW"
    domain = str(data.get("domain") or "trend")
    if domain not in ("fashion", "food", "trend"):
        domain = "trend"
    length = str(data.get("length_bucket") or "short")
    if length not in ("short", "long"):
        length = "short"
    profile = str(data.get("write_profile") or "news_recap")
    if profile not in ("news_recap", "hook_gossip"):
        profile = "news_recap"
    ref = str(data.get("ref_type") or "positive")
    if ref not in ("positive", "negative"):
        ref = "positive"
    return AnalyzeResponse(
        language=lang,  # type: ignore[arg-type]
        domain=domain,  # type: ignore[arg-type]
        length_bucket=length,  # type: ignore[arg-type]
        write_profile=profile,  # type: ignore[arg-type]
        ref_type=ref,  # type: ignore[arg-type]
        structure=StructureSlots(
            prefix=str(struct.get("prefix") or "")[:500],
            fact=str(struct.get("fact") or "")[:800],
            quote=str(struct.get("quote") or "")[:500],
            context=str(struct.get("context") or "")[:800],
            ending=str(struct.get("ending") or "")[:500],
        ),
        body_text=str(data.get("body_text") or blob)[:12000],
        notes=str(data.get("notes") or "")[:500],
    )

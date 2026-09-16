"""LLM generate helpers for compose (split for MD-M2)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.schemas.alter_ego import ComposeRequest
from app.services.ai.llm_factory import get_llm_client
from app.services.compose_parse import extract_json_object, normalize_pack
from app.services.compose_prompt import build_compose_prompt

logger = logging.getLogger(__name__)


def norm_pack(
    raw: Dict[str, Any],
    max_chars: int,
    request: ComposeRequest,
    fact: str,
) -> Dict[str, Any]:
    return normalize_pack(
        raw,
        max_chars,
        platform=request.platform,
        fact=fact,
        topic_title=request.topic_title,
    )


async def generate_compose_part(
    *,
    user_id: str,
    request: ComposeRequest,
    part: str,
    max_chars: int,
    lang: str,
    fact: str,
    overlay: str,
    base_body: str = "",
) -> Dict[str, Any]:
    snippets = [s for s in (request.preserve_snippets or []) if str(s).strip()][:8]
    prompt = build_compose_prompt(
        platform=request.platform,
        style=request.style,
        max_chars=max_chars,
        part=part,
        language=lang,
        topic_title=request.topic_title,
        context_summary=fact,
        dna_overlay=overlay,
        preserve_snippets=snippets,
        revision_intent=request.revision_intent or "",
        base_body=base_body or request.base_body or "",
    )
    client = get_llm_client("alter_ego")
    last_err: Optional[Exception] = None
    pack: Optional[Dict[str, Any]] = None
    for _attempt in range(2):
        try:
            raw = await client.generate(prompt)
            pack = norm_pack(extract_json_object(raw), max_chars, request, fact)
            if part == "body" and pack.get("short_body"):
                continue
            break
        except ValueError as exc:
            last_err = exc
            logger.warning("[AE_COMPOSE_PARSE_FAIL] user_id=%s err=%s", user_id, exc)
    if pack is None:
        raise ValueError(f"compose_fail:{type(last_err).__name__}")
    return pack

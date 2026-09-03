"""Public post composer: Flash-only JIT pack + 1-credit charge after success."""
from __future__ import annotations

import logging
import secrets
from typing import Optional

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.schemas.alter_ego import ComposeRequest, ComposeResponse
from app.services.ai.llm_factory import get_llm_client
from app.services.compose_caps import clamp_max_chars
from app.services.compose_parse import extract_json_object, normalize_pack
from app.services.compose_prompt import build_compose_prompt, dna_tone_overlay
from app.services.credit_ledger_service import (
    InsufficientCreditsError,
    credit_ledger_service,
)
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository
from app.utils.topic_languages import normalize_topic_language

logger = logging.getLogger(__name__)
_dna_repo = AlterEgoDnaRepository()
UNLOCK_COST = 1


async def _optional_overlay(user_id: str) -> str:
    try:
        doc = await _dna_repo.get_by_user(user_id)
        if not doc or not doc.get("dna_json"):
            return ""
        return dna_tone_overlay(AlterEgoDnaJson.model_validate(doc["dna_json"]))
    except Exception:
        return ""


async def _charge(user_id: str, request: ComposeRequest) -> int:
    action = "ae_compose" if request.part == "all" else "ae_compose_part"
    key = f"compose:{user_id}:{request.topic_id or 'none'}:{request.part}:{secrets.token_hex(8)}"
    return await credit_ledger_service.decr_credits(
        user_id,
        UNLOCK_COST,
        action=action,
        idempotency_key=key,
        topic_id=request.topic_id,
    )


async def compose_pack(user_id: str, request: ComposeRequest) -> ComposeResponse:
    max_chars = clamp_max_chars(request.platform, request.max_chars)
    lang = normalize_topic_language(request.language)
    fact = (request.context_summary or request.topic_title or "").strip()
    await credit_ledger_service.ensure_initial_balance(user_id)
    if await credit_ledger_service.get_balance(user_id) < UNLOCK_COST:
        raise InsufficientCreditsError("need=1")

    prompt = build_compose_prompt(
        platform=request.platform,
        style=request.style,
        max_chars=max_chars,
        part=request.part,
        language=lang,
        topic_title=request.topic_title,
        context_summary=fact,
        dna_overlay=await _optional_overlay(user_id),
    )
    client = get_llm_client("alter_ego")
    last_err: Optional[Exception] = None
    pack = None
    for _attempt in range(2):
        try:
            raw = await client.generate(prompt)
            pack = normalize_pack(extract_json_object(raw), max_chars)
            break
        except ValueError as exc:
            last_err = exc
            logger.warning("[AE_COMPOSE_PARSE_FAIL] user_id=%s err=%s", user_id, exc)
    if pack is None:
        raise ValueError(f"compose_fail:{type(last_err).__name__}")

    balance = await _charge(user_id, request)
    return ComposeResponse(
        titles=pack["titles"],
        body=pack["body"],
        hashtag_sets=pack["hashtag_sets"],
        credits_charged=UNLOCK_COST,
        balance_after=balance,
        max_chars=max_chars,
    )

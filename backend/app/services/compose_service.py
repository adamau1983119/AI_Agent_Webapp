"""Public post composer: Flash-only JIT pack + 1-credit charge after success."""
from __future__ import annotations

import secrets
from typing import List

from app.models.alter_ego_dna import AlterEgoDnaJson
from app.schemas.alter_ego import ComposeRequest, ComposeResponse
from app.services.compose_caps import clamp_max_chars
from app.services.compose_generate import generate_compose_part
from app.services.compose_prompt import dna_tone_overlay
from app.services.credit_ledger_service import (
    InsufficientCreditsError,
    credit_ledger_service,
)
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository
from app.utils.topic_languages import normalize_topic_language

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

    overlay = await _optional_overlay(user_id)
    titles: List[str] = ["", "", ""]
    body = ""
    hashtag_sets: List[List[str]] = [[], [], []]
    short_body = False
    kw = dict(
        user_id=user_id,
        request=request,
        max_chars=max_chars,
        lang=lang,
        fact=fact,
        overlay=overlay,
    )

    if request.part == "all":
        body_pack = await generate_compose_part(**kw, part="body")
        body = body_pack["body"]
        short_body = bool(body_pack.get("short_body"))
        meta = await generate_compose_part(**kw, part="meta", base_body=body)
        titles = meta["titles"]
        hashtag_sets = meta["hashtag_sets"]
    else:
        pack = await generate_compose_part(
            **kw, part=request.part, base_body=request.base_body or ""
        )
        titles = pack["titles"]
        body = pack["body"]
        hashtag_sets = pack["hashtag_sets"]
        short_body = bool(pack.get("short_body"))

    balance = await _charge(user_id, request)
    return ComposeResponse(
        titles=titles,
        body=body,
        hashtag_sets=hashtag_sets,
        credits_charged=UNLOCK_COST,
        balance_after=balance,
        max_chars=max_chars,
        short_body=short_body,
    )

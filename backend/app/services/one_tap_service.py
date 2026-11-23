"""One-tap post pack: generate free (balance gate), charge 20 only after share success."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.database import get_database
from app.models.alter_ego_dna import AlterEgoDnaJson
from app.schemas.alter_ego import (
    ComposeRequest,
    OneTapChargeResponse,
    OneTapGenerateResponse,
    OneTapLatestResponse,
)
from app.services.compose_caps import clamp_max_chars
from app.services.compose_generate import generate_compose_part
from app.services.compose_prompt import dna_tone_overlay
from app.services.credit_ledger_service import (
    InsufficientCreditsError,
    credit_ledger_service,
)
from app.services.repositories.alter_ego_repository import AlterEgoDnaRepository
from app.utils.topic_languages import normalize_topic_language

ONE_TAP_COST = 20
ONE_TAP_MAX_CHARS = 500
COLL = "one_tap_packs"
_dna_repo = AlterEgoDnaRepository()


async def _optional_overlay(user_id: str) -> str:
    try:
        doc = await _dna_repo.get_by_user(user_id)
        if not doc or not doc.get("dna_json"):
            return ""
        return dna_tone_overlay(AlterEgoDnaJson.model_validate(doc["dna_json"]))
    except Exception:
        return ""


async def generate_one_tap_pack(
    user_id: str,
    *,
    language: str,
    topic_id: Optional[str],
    topic_title: str,
    context_summary: str,
    domain: Optional[str] = None,
    surface: str = "public",
) -> OneTapGenerateResponse:
    """LLM compose (≤500) with no debit. Requires balance ≥ 20."""
    await credit_ledger_service.ensure_initial_balance(user_id)
    balance = await credit_ledger_service.get_balance(user_id)
    if balance < ONE_TAP_COST:
        raise InsufficientCreditsError(f"need={ONE_TAP_COST}")

    lang = normalize_topic_language(language)
    max_chars = clamp_max_chars("facebook", ONE_TAP_MAX_CHARS)
    fact = (context_summary or topic_title or "").strip()
    request = ComposeRequest(
        platform="facebook",
        style="casual",
        max_chars=max_chars,
        part="all",
        language=lang,  # type: ignore[arg-type]
        topic_id=topic_id,
        topic_title=topic_title or "",
        context_summary=fact[:1500],
        domain=domain if domain in ("fashion", "food", "trend") else None,  # type: ignore[arg-type]
    )
    overlay = await _optional_overlay(user_id)
    kw: Dict[str, Any] = dict(
        user_id=user_id,
        request=request,
        max_chars=max_chars,
        lang=lang,
        fact=fact,
        overlay=overlay,
    )
    body_pack = await generate_compose_part(**kw, part="body")
    body = body_pack["body"]
    short_body = bool(body_pack.get("short_body"))
    meta = await generate_compose_part(**kw, part="meta", base_body=body)
    titles: List[str] = meta["titles"]
    hashtag_sets: List[List[str]] = meta["hashtag_sets"]

    pack_token = secrets.token_hex(16)
    now = datetime.now(timezone.utc)
    db = await get_database()
    await db[COLL].insert_one(
        {
            "pack_token": pack_token,
            "user_id": user_id,
            "topic_id": (topic_id or "").strip() or None,
            "surface": surface if surface in ("public", "my_channel") else "public",
            "titles": titles,
            "body": body,
            "hashtag_sets": hashtag_sets,
            "max_chars": max_chars,
            "short_body": short_body,
            "charged": False,
            "created_at": now,
        }
    )
    return OneTapGenerateResponse(
        pack_token=pack_token,
        titles=titles,
        body=body,
        hashtag_sets=hashtag_sets,
        max_chars=max_chars,
        short_body=short_body,
        credits_required=ONE_TAP_COST,
        balance=balance,
    )


async def charge_one_tap_pack(
    user_id: str,
    *,
    pack_token: str,
) -> OneTapChargeResponse:
    """Debit 20 after share/download success. Idempotent per pack_token."""
    token = (pack_token or "").strip()
    if not token or len(token) > 64:
        raise ValueError("invalid_pack_token")

    db = await get_database()
    doc = await db[COLL].find_one({"pack_token": token, "user_id": user_id})
    if not doc:
        raise ValueError("pack_not_found")

    topic_id = doc.get("topic_id")
    idem_key = f"one_tap_charge:{user_id}:{token}"

    if doc.get("charged"):
        balance = await credit_ledger_service.get_balance(user_id)
        return OneTapChargeResponse(
            credits_charged=0,
            balance_after=balance,
            already_charged=True,
        )

    await credit_ledger_service.ensure_initial_balance(user_id)
    balance = await credit_ledger_service.decr_credits(
        user_id,
        ONE_TAP_COST,
        action="ae_one_tap_pack",
        idempotency_key=idem_key,
        topic_id=topic_id,
    )
    await db[COLL].update_one(
        {"pack_token": token, "user_id": user_id},
        {"$set": {"charged": True, "charged_at": datetime.now(timezone.utc)}},
    )
    return OneTapChargeResponse(
        credits_charged=ONE_TAP_COST,
        balance_after=balance,
        already_charged=False,
    )


async def get_latest_one_tap_pack(
    user_id: str,
    *,
    topic_id: str,
) -> Optional[OneTapLatestResponse]:
    """Return newest pack for user+topic so UI can restore after leave/share."""
    tid = (topic_id or "").strip()
    if not tid or len(tid) > 64:
        return None
    db = await get_database()
    doc = await db[COLL].find_one(
        {"user_id": user_id, "topic_id": tid},
        sort=[("created_at", -1)],
    )
    if not doc:
        return None
    return OneTapLatestResponse(
        pack_token=str(doc.get("pack_token") or ""),
        titles=list(doc.get("titles") or []),
        body=str(doc.get("body") or ""),
        hashtag_sets=list(doc.get("hashtag_sets") or []),
        max_chars=int(doc.get("max_chars") or ONE_TAP_MAX_CHARS),
        short_body=bool(doc.get("short_body")),
        charged=bool(doc.get("charged")),
        credits_required=ONE_TAP_COST,
    )

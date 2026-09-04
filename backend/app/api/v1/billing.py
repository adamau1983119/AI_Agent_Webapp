"""Billing: packs, wallet snapshot, Stripe Checkout + webhook."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.middleware.jwt_auth import get_current_user
from app.services.credit_ledger_service import credit_ledger_service
from app.services.credits.credit_packs import get_pack, list_packs
from app.services.credits.credit_stripe import (
    create_checkout_session,
    parse_checkout_completed,
    stripe_ready,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutBody(BaseModel):
    pack_id: str = Field(..., min_length=2, max_length=16)


@router.get("/packs")
async def get_packs(current_user: dict = Depends(get_current_user)):
    _ = current_user
    return {"data": list_packs()}


@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    await credit_ledger_service.ensure_login_grants(user_id)
    return await credit_ledger_service.get_wallet_snapshot(user_id)


@router.post("/checkout")
async def start_checkout(
    body: CheckoutBody,
    current_user: dict = Depends(get_current_user),
):
    if not stripe_ready():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="stripe_not_configured",
        )
    try:
        get_pack(body.pack_id)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unknown_pack",
        ) from exc
    try:
        url = create_checkout_session(current_user["id"], body.pack_id)
    except Exception as exc:
        logger.warning("stripe checkout failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="stripe_checkout_failed",
        ) from exc
    return {"checkout_url": url}


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature") or ""
    try:
        parsed = parse_checkout_completed(payload, sig)
    except Exception as exc:
        logger.warning("stripe webhook rejected: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="stripe_webhook_invalid",
        ) from exc
    if not parsed:
        return {"ok": True, "ignored": True}
    await credit_ledger_service.add_purchased(
        parsed["user_id"],
        parsed["credits"],
        idempotency_key=f"stripe:{parsed['session_id']}",
        action="purchase",
        meta={"pack_id": parsed["pack_id"], "session_id": parsed["session_id"]},
    )
    return {"ok": True}

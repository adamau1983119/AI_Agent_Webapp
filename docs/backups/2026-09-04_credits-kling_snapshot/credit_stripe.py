"""Stripe Checkout helpers. Empty keys → not ready (local 503)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import settings
from app.services.credits.credit_packs import get_pack

try:
    import stripe
except Exception:  # pragma: no cover
    stripe = None


def stripe_ready() -> bool:
    key = str(getattr(settings, "STRIPE_SECRET_KEY", "") or "").strip()
    return bool(stripe) and bool(key)


def _frontend() -> str:
    return str(getattr(settings, "FRONTEND_URL", "") or "http://localhost:3000").rstrip("/")


def create_checkout_session(user_id: str, pack_id: str) -> str:
    pack = get_pack(pack_id)
    stripe.api_key = str(settings.STRIPE_SECRET_KEY).strip()
    session = stripe.checkout.Session.create(
        mode="payment",
        client_reference_id=user_id,
        success_url=_frontend() + "/settings?tab=billing&billing=success",
        cancel_url=_frontend() + "/settings?tab=billing&billing=cancel",
        line_items=[
            {
                "price_data": {
                    "currency": pack["currency"],
                    "unit_amount": pack["amount_cents"],
                    "product_data": {
                        "name": f"Alter Ego {pack['credits']} credits",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "user_id": user_id,
            "pack_id": pack["id"],
            "credits": str(pack["credits"]),
        },
    )
    url = getattr(session, "url", None) or session.get("url")
    if not url:
        raise RuntimeError("stripe_no_url")
    return str(url)


def parse_checkout_completed(payload: bytes, sig: str) -> Optional[Dict[str, Any]]:
    secret = str(getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or "").strip()
    if not stripe_ready() or not secret:
        raise RuntimeError("stripe_not_configured")
    event = stripe.Webhook.construct_event(payload, sig, secret)
    if hasattr(event, "to_dict"):
        event = event.to_dict()
    if event.get("type") != "checkout.session.completed":
        return None
    session = event["data"]["object"]
    if str(session.get("payment_status") or "") != "paid":
        return None
    meta = session.get("metadata") or {}
    user_id = str(meta.get("user_id") or session.get("client_reference_id") or "")
    pack_id = str(meta.get("pack_id") or "")
    credits = int(meta.get("credits") or 0)
    session_id = str(session.get("id") or "")
    if not user_id or not pack_id or credits <= 0 or not session_id:
        return None
    get_pack(pack_id)
    return {
        "user_id": user_id,
        "pack_id": pack_id,
        "credits": credits,
        "session_id": session_id,
    }

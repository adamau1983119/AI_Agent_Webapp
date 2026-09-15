"""Match a paid Checkout session to a pack by amount, not metadata credits."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.credits.credit_packs import get_pack


def paid_pack_from_session(session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if str(session.get("payment_status") or "") != "paid":
        return None
    meta = session.get("metadata") or {}
    pack_id = str(meta.get("pack_id") or "")
    try:
        pack = get_pack(pack_id)
    except KeyError:
        return None
    currency = str(session.get("currency") or "").lower()
    try:
        amount_total = int(session.get("amount_total") or 0)
    except (TypeError, ValueError):
        return None
    if currency != str(pack["currency"]).lower():
        return None
    if amount_total != int(pack["amount_cents"]):
        return None
    user_id = str(meta.get("user_id") or session.get("client_reference_id") or "")
    session_id = str(session.get("id") or "")
    if not user_id or not session_id:
        return None
    return {
        "user_id": user_id,
        "pack_id": pack["id"],
        "credits": int(pack["credits"]),
        "session_id": session_id,
        "amount_cents": amount_total,
        "currency": currency,
        "livemode": bool(session.get("livemode")),
    }

"""
Alter Ego re-extract 計費閘門（PD-AE2-04：首次免費 1 次）
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.services.credit_ledger_service import InsufficientCreditsError, credit_ledger_service


def plan_reextract(dna_doc: Optional[Dict[str, Any]]) -> str:
    """回傳 first_extract | free_reextract | charge_reextract。"""
    if not dna_doc or dna_doc.get("dna_status") != "active" or not dna_doc.get("dna_json"):
        return "first_extract"
    if not dna_doc.get("free_reextract_used"):
        return "free_reextract"
    return "charge_reextract"


async def charge_reextract(user_id: str, dna_doc: Dict[str, Any]) -> None:
    version = dna_doc.get("current_dna_version_id") or "na"
    await credit_ledger_service.ensure_initial_balance(user_id)
    await credit_ledger_service.decr_credits(
        user_id,
        1,
        action="ae_reextract",
        idempotency_key=f"ae-reextract:{user_id}:{version}",
    )


async def mark_free_reextract_used(dna_repo, user_id: str) -> None:
    collection = await dna_repo._get_collection()
    await collection.update_one(
        {"user_id": user_id},
        {"$set": {"free_reextract_used": True}},
    )


__all__ = [
    "plan_reextract",
    "charge_reextract",
    "mark_free_reextract_used",
    "InsufficientCreditsError",
]

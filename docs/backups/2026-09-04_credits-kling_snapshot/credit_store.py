"""Mongo credit_wallets — source of truth (not Redis)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.database import get_database
from app.services.credits.credit_wallet import empty_wallet, expire_lots

COLLECTION = "credit_wallets"


async def wallets_col():
    db = await get_database()
    return db[COLLECTION]


async def load_wallet(user_id: str) -> Optional[Dict[str, Any]]:
    col = await wallets_col()
    doc = await col.find_one({"user_id": user_id})
    if not doc:
        return None
    doc.pop("_id", None)
    return doc


async def save_wallet(wallet: Dict[str, Any]) -> None:
    col = await wallets_col()
    payload = {key: value for key, value in wallet.items() if key != "_id"}
    await col.update_one(
        {"user_id": wallet["user_id"]},
        {"$set": payload},
        upsert=True,
    )


async def load_or_migrate(user_id: str) -> Dict[str, Any]:
    existing = await load_wallet(user_id)
    if existing:
        existing["lots"] = expire_lots(existing.get("lots") or [])
        return existing
    wallet = empty_wallet(user_id)
    from app.services.credits.credit_ledger_io import ledger_collection

    col = await ledger_collection()
    last = await col.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
    if last and "balance_after" in last:
        wallet["purchased"] = max(0, int(last["balance_after"]))
    initial = await col.find_one({"user_id": user_id, "action": "initial_grant"})
    wallet["legacy_initial"] = bool(initial)
    return wallet

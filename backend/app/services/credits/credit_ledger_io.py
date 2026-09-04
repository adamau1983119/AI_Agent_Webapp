"""Mongo ledger + Redis idempotency helpers for credits."""
from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime
from typing import Any, Dict, Optional

from app.database import get_database
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)
_IDEMPOTENCY_PREFIX = "my_channel:idempotency:"
_IDEMPOTENCY_TTL = 86400 * 7


def idempotency_cache_key(user_id: str, key: str) -> str:
    return f"{_IDEMPOTENCY_PREFIX}{user_id}:{key}"


async def ledger_collection():
    db = await get_database()
    return db["credit_ledger"]


async def get_idempotency(user_id: str, key: str) -> Optional[Dict[str, Any]]:
    if cache_service.enabled and cache_service.redis_client:
        try:
            raw = await cache_service.redis_client.get(idempotency_cache_key(user_id, key))
            if raw:
                return json.loads(raw)
        except Exception as exc:
            logger.debug("idempotency redis read: %s", exc)
    col = await ledger_collection()
    doc = await col.find_one({"user_id": user_id, "idempotency_key": key})
    if doc:
        return {
            "balance_after": doc.get("balance_after"),
            "transaction_id": doc.get("transaction_id"),
        }
    return None


async def store_idempotency(user_id: str, key: str, payload: Dict[str, Any]) -> None:
    if cache_service.enabled and cache_service.redis_client:
        try:
            await cache_service.redis_client.setex(
                idempotency_cache_key(user_id, key),
                _IDEMPOTENCY_TTL,
                json.dumps(payload, default=str),
            )
        except Exception as exc:
            logger.debug("idempotency redis write: %s", exc)


async def insert_txn(
    user_id: str,
    delta: int,
    *,
    action: str,
    idempotency_key: str,
    balance_after: int,
    topic_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> int:
    existing = await get_idempotency(user_id, idempotency_key)
    if existing is not None:
        return int(existing["balance_after"])
    txn_id = f"txn_{secrets.token_urlsafe(12)}"
    entry = {
        "transaction_id": txn_id,
        "user_id": user_id,
        "action": action,
        "amount": delta,
        "balance_after": balance_after,
        "topic_id": topic_id,
        "idempotency_key": idempotency_key,
        "timestamp": datetime.utcnow(),
        "meta": meta or {},
    }
    col = await ledger_collection()
    await col.insert_one(entry)
    await store_idempotency(
        user_id, idempotency_key, {"balance_after": balance_after, "transaction_id": txn_id}
    )
    return balance_after

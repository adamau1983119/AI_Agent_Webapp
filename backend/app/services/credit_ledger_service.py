"""
MyChannel 點數帳本（Redis balance + Mongo ledger · MC-1）
"""
from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime
from typing import Any, Dict, Optional

from app.database import get_database
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

INITIAL_CREDITS = 5
UNLOCK_COST = 1
_BALANCE_PREFIX = "my_channel:credits:"
_IDEMPOTENCY_PREFIX = "my_channel:idempotency:"
_IDEMPOTENCY_TTL = 86400 * 7


class InsufficientCreditsError(Exception):
    """餘額不足（MC-5 · 402）"""


def _balance_key(user_id: str) -> str:
    return f"{_BALANCE_PREFIX}{user_id}"


def _idempotency_key(user_id: str, key: str) -> str:
    return f"{_IDEMPOTENCY_PREFIX}{user_id}:{key}"


class CreditLedgerService:
    """Redis 餘額 + Mongo 交易紀錄。"""

    async def _ledger_collection(self):
        db = await get_database()
        return db["credit_ledger"]

    async def get_balance(self, user_id: str) -> int:
        if cache_service.enabled and cache_service.redis_client:
            try:
                raw = await cache_service.redis_client.get(_balance_key(user_id))
                if raw is not None:
                    return int(raw)
            except Exception as e:
                logger.warning("credit balance redis read failed: %s", e)

        col = await self._ledger_collection()
        doc = await col.find_one({"user_id": user_id}, sort=[("timestamp", -1)])
        if doc and "balance_after" in doc:
            return int(doc["balance_after"])
        return 0

    async def ensure_initial_balance(self, user_id: str) -> int:
        balance = await self.get_balance(user_id)
        if balance > 0:
            return balance

        col = await self._ledger_collection()
        existing = await col.find_one({"user_id": user_id, "action": "initial_grant"})
        if existing:
            return int(existing.get("balance_after", INITIAL_CREDITS))

        return await self._apply_delta(
            user_id,
            INITIAL_CREDITS,
            action="initial_grant",
            idempotency_key=f"initial:{user_id}",
        )

    async def add_credits(self, user_id: str, amount: int, admin_id: str) -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        await self.ensure_initial_balance(user_id)
        return await self._apply_delta(
            user_id,
            amount,
            action="admin_add",
            idempotency_key=f"admin:{admin_id}:{secrets.token_hex(8)}",
            meta={"admin_id": admin_id},
        )

    async def decr_credits(
        self,
        user_id: str,
        amount: int,
        *,
        action: str,
        idempotency_key: str,
        topic_id: Optional[str] = None,
    ) -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")

        cached = await self._get_idempotency(user_id, idempotency_key)
        if cached is not None:
            return int(cached["balance_after"])

        await self.ensure_initial_balance(user_id)
        balance = await self.get_balance(user_id)
        if balance < amount:
            raise InsufficientCreditsError(f"balance={balance}, need={amount}")

        new_balance = await self._apply_delta(
            user_id,
            -amount,
            action=action,
            idempotency_key=idempotency_key,
            topic_id=topic_id,
        )
        await self._store_idempotency(
            user_id,
            idempotency_key,
            {"balance_after": new_balance, "action": action, "topic_id": topic_id},
        )
        return new_balance

    async def _apply_delta(
        self,
        user_id: str,
        delta: int,
        *,
        action: str,
        idempotency_key: str,
        topic_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        existing = await self._get_idempotency(user_id, idempotency_key)
        if existing is not None:
            return int(existing["balance_after"])

        current = await self.get_balance(user_id)
        new_balance = current + delta
        if new_balance < 0:
            raise InsufficientCreditsError(f"balance={current}, delta={delta}")

        if cache_service.enabled and cache_service.redis_client:
            try:
                if delta >= 0:
                    await cache_service.redis_client.incrby(_balance_key(user_id), delta)
                else:
                    await cache_service.redis_client.decrby(_balance_key(user_id), abs(delta))
            except Exception as e:
                logger.warning("credit balance redis write failed: %s", e)

        txn_id = f"txn_{secrets.token_urlsafe(12)}"
        entry = {
            "transaction_id": txn_id,
            "user_id": user_id,
            "action": action,
            "amount": delta,
            "balance_after": new_balance,
            "topic_id": topic_id,
            "idempotency_key": idempotency_key,
            "timestamp": datetime.utcnow(),
            "meta": meta or {},
        }
        col = await self._ledger_collection()
        await col.insert_one(entry)
        await self._store_idempotency(
            user_id, idempotency_key, {"balance_after": new_balance, "transaction_id": txn_id}
        )
        return new_balance

    async def _get_idempotency(self, user_id: str, key: str) -> Optional[Dict[str, Any]]:
        if cache_service.enabled and cache_service.redis_client:
            try:
                raw = await cache_service.redis_client.get(_idempotency_key(user_id, key))
                if raw:
                    return json.loads(raw)
            except Exception as e:
                logger.debug("idempotency redis read: %s", e)

        col = await self._ledger_collection()
        doc = await col.find_one({"user_id": user_id, "idempotency_key": key})
        if doc:
            return {"balance_after": doc.get("balance_after"), "transaction_id": doc.get("transaction_id")}
        return None

    async def _store_idempotency(self, user_id: str, key: str, payload: Dict[str, Any]) -> None:
        if cache_service.enabled and cache_service.redis_client:
            try:
                await cache_service.redis_client.setex(
                    _idempotency_key(user_id, key),
                    _IDEMPOTENCY_TTL,
                    json.dumps(payload, default=str),
                )
            except Exception as e:
                logger.debug("idempotency redis write: %s", e)


credit_ledger_service = CreditLedgerService()

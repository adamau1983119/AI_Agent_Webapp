"""Credit ledger: Mongo wallet SoT + audit log. Redis is cache-only."""
from __future__ import annotations

import secrets
from typing import Any, Dict, Optional

from app.services.automation.topic_day_hkt import today_hkt_str
from app.services.credits.credit_grants import apply_grant, plan_login_grant
from app.services.credits.credit_ledger_io import get_idempotency, insert_txn, store_idempotency
from app.services.credits.credit_store import empty_wallet, load_or_migrate, load_wallet, save_wallet
from app.services.credits.credit_wallet import (
    expire_lots,
    fifo_debit,
    free_remaining,
    total_balance,
    utcnow,
)

UNLOCK_COST = 1


class InsufficientCreditsError(Exception):
    """餘額不足（MC-5 · 402）"""


class CreditLedgerService:
    async def get_balance(self, user_id: str) -> int:
        return total_balance(await load_or_migrate(user_id))

    async def get_wallet_snapshot(self, user_id: str) -> Dict[str, int]:
        wallet = await load_wallet(user_id) or empty_wallet(user_id)
        lots = expire_lots(wallet.get("lots") or [])
        return {
            "balance": free_remaining(lots) + int(wallet.get("purchased") or 0),
            "free": free_remaining(lots),
            "purchased": int(wallet.get("purchased") or 0),
            "welcome_count": int(wallet.get("welcome_count") or 0),
        }

    async def ensure_initial_balance(self, user_id: str) -> int:
        return await self.ensure_login_grants(user_id)

    async def ensure_login_grants(self, user_id: str) -> int:
        wallet = await load_or_migrate(user_id)
        now = utcnow()
        plan = plan_login_grant(wallet, today_hkt_str(), now)
        if not plan:
            await save_wallet(wallet)
            return total_balance(wallet)
        wallet = apply_grant(wallet, plan, now, f"lot_{secrets.token_urlsafe(8)}")
        await save_wallet(wallet)
        amount = int(plan.get("amount") or 0)
        if amount > 0:
            await insert_txn(
                user_id,
                amount,
                action=f"login_{plan['kind']}",
                idempotency_key=f"login_grant:{user_id}:{plan['hkt_day']}",
                balance_after=total_balance(wallet),
                meta={"kind": plan["kind"], "hkt_day": plan["hkt_day"]},
            )
        return total_balance(wallet)

    async def add_credits(self, user_id: str, amount: int, admin_id: str) -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        await self.ensure_login_grants(user_id)
        return await self.add_purchased(
            user_id,
            amount,
            idempotency_key=f"admin:{admin_id}:{secrets.token_hex(8)}",
            action="admin_add",
            meta={"admin_id": admin_id},
        )

    async def add_purchased(
        self,
        user_id: str,
        amount: int,
        *,
        idempotency_key: str,
        action: str = "purchase",
        meta: Optional[Dict[str, Any]] = None,
    ) -> int:
        if amount <= 0:
            raise ValueError("amount_must_be_positive")
        cached = await get_idempotency(user_id, idempotency_key)
        if cached is not None:
            return int(cached["balance_after"])
        wallet = await load_or_migrate(user_id)
        wallet["lots"] = expire_lots(wallet.get("lots") or [])
        wallet["purchased"] = int(wallet.get("purchased") or 0) + amount
        await save_wallet(wallet)
        return await insert_txn(
            user_id,
            amount,
            action=action,
            idempotency_key=idempotency_key,
            balance_after=total_balance(wallet),
            meta=meta,
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
        cached = await get_idempotency(user_id, idempotency_key)
        if cached is not None:
            return int(cached["balance_after"])
        await self.ensure_login_grants(user_id)
        wallet = await load_or_migrate(user_id)
        if total_balance(wallet) < amount:
            raise InsufficientCreditsError(
                f"balance={total_balance(wallet)}, need={amount}"
            )
        wallet = fifo_debit(wallet, amount)
        await save_wallet(wallet)
        new_balance = await insert_txn(
            user_id,
            -amount,
            action=action,
            idempotency_key=idempotency_key,
            balance_after=total_balance(wallet),
            topic_id=topic_id,
        )
        await store_idempotency(
            user_id,
            idempotency_key,
            {"balance_after": new_balance, "action": action, "topic_id": topic_id},
        )
        return new_balance


credit_ledger_service = CreditLedgerService()

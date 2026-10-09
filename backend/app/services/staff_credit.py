"""發文同事：餘額低於 60 時補 60，同一香港日最多 10 次。"""
from __future__ import annotations

from app.services.automation.topic_day_hkt import today_hkt_str
from app.services.credits.credit_ledger_io import insert_txn
from app.services.credits.credit_store import load_or_migrate, save_wallet, try_grant_purchase
from app.services.credits.credit_wallet import total_balance
from app.services.repositories.user_repository import UserRepository
from app.services.staff_identity import is_staff_credit_email, next_staff_refill


async def maybe_staff_refill(user_id: str) -> int:
    user = await UserRepository().get_user_by_id(user_id)
    email = (user or {}).get("email")
    wallet = await load_or_migrate(user_id)
    if not is_staff_credit_email(email):
        return total_balance(wallet)
    day = today_hkt_str()
    same_day = str(wallet.get("staff_refill_hkt") or "") == day
    used = int(wallet.get("staff_refill_count") or 0) if same_day else 0
    amount = next_staff_refill(total_balance(wallet), used)
    if not amount:
        return total_balance(wallet)
    key = f"staff:{user_id}:{day}:{used + 1}"
    applied = await try_grant_purchase(user_id, amount, key)
    wallet = await load_or_migrate(user_id)
    if not applied:
        return total_balance(wallet)
    wallet["staff_refill_hkt"] = day
    wallet["staff_refill_count"] = used + 1
    await save_wallet(wallet)
    balance = total_balance(wallet)
    await insert_txn(
        user_id,
        amount,
        action="staff_refill",
        idempotency_key=key,
        balance_after=balance,
        meta={"hkt_day": day, "n": used + 1},
    )
    return balance

"""Pure wallet math: expiry, totals, FIFO debit (free lots then purchased)."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

LOT_DAYS = 7
UNIT_SCALE = 10


def utcnow() -> datetime:
    return datetime.utcnow()


def as_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(tzinfo=None) if value.tzinfo else value
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", ""))
    return None


def empty_wallet(user_id: str) -> Dict[str, Any]:
    return {
        "user_id": user_id,
        "lots": [],
        "purchased": 0,
        "welcome_count": 0,
        "last_grant_hkt": None,
        "legacy_initial": False,
        "fulfilled_keys": [],
        "unit_scale": UNIT_SCALE,
    }


def apply_unit_scale(wallet: Dict[str, Any]) -> bool:
    """舊單位餘額乘 10 一次。已是新單位則不動。"""
    if int(wallet.get("unit_scale") or 0) >= UNIT_SCALE:
        return False
    for lot in wallet.get("lots") or []:
        if not isinstance(lot, dict):
            continue
        lot["remaining"] = int(lot.get("remaining") or 0) * UNIT_SCALE
        if "amount" in lot:
            lot["amount"] = int(lot.get("amount") or 0) * UNIT_SCALE
    wallet["purchased"] = int(wallet.get("purchased") or 0) * UNIT_SCALE
    wallet["unit_scale"] = UNIT_SCALE
    return True


def expire_lots(lots: List[dict], now: Optional[datetime] = None) -> List[dict]:
    now = now or utcnow()
    kept: List[dict] = []
    for lot in lots or []:
        rem = int(lot.get("remaining") or 0)
        if rem <= 0:
            continue
        exp = as_dt(lot.get("expires_at"))
        if exp is not None and exp <= now:
            continue
        kept.append(dict(lot))
    return kept


def free_remaining(lots: List[dict]) -> int:
    return sum(int(item.get("remaining") or 0) for item in lots)


def total_balance(wallet: dict, now: Optional[datetime] = None) -> int:
    lots = expire_lots(wallet.get("lots") or [], now)
    return free_remaining(lots) + int(wallet.get("purchased") or 0)


def make_lot(amount: int, kind: str, now: datetime, lot_id: str) -> dict:
    return {
        "id": lot_id,
        "kind": kind,
        "remaining": int(amount),
        "expires_at": now + timedelta(days=LOT_DAYS),
        "granted_at": now,
    }


def fifo_debit(
    wallet: Dict[str, Any],
    amount: int,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    if amount <= 0:
        raise ValueError("amount_must_be_positive")
    now = now or utcnow()
    lots = expire_lots(list(wallet.get("lots") or []), now)
    lots.sort(key=lambda lot: as_dt(lot.get("expires_at")) or datetime.max)
    need = amount
    new_lots: List[dict] = []
    for lot in lots:
        rem = int(lot.get("remaining") or 0)
        take = min(rem, need)
        updated = dict(lot)
        updated["remaining"] = rem - take
        need -= take
        if updated["remaining"] > 0:
            new_lots.append(updated)
    purchased = int(wallet.get("purchased") or 0)
    if need > 0:
        if purchased < need:
            raise ValueError("insufficient")
        purchased -= need
    out = dict(wallet)
    out["lots"] = new_lots
    out["purchased"] = purchased
    return out

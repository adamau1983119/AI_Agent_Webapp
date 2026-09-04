"""Welcome 10×3 then daily +5 with free cap 10 (HKT day, 7-day lots)."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from app.services.credits.credit_wallet import expire_lots, free_remaining, make_lot

WELCOME_PER_LOGIN = 10
WELCOME_TOPUP_LEGACY = 5
DAILY_LOGIN_CREDITS = 5
FREE_CAP = 10
WELCOME_LOGINS = 3


def plan_login_grant(wallet: dict, hkt_day: str, now: datetime) -> Optional[Dict[str, Any]]:
    lots = expire_lots(wallet.get("lots") or [], now)
    if wallet.get("last_grant_hkt") == hkt_day:
        return None
    welcome = int(wallet.get("welcome_count") or 0)
    if welcome < WELCOME_LOGINS:
        if welcome == 0 and wallet.get("legacy_initial"):
            amount, kind = WELCOME_TOPUP_LEGACY, "legacy_topup"
        else:
            amount, kind = WELCOME_PER_LOGIN, "welcome"
        return {
            "amount": amount,
            "kind": kind,
            "welcome_count": welcome + 1,
            "hkt_day": hkt_day,
        }
    room = FREE_CAP - free_remaining(lots)
    if room <= 0:
        return {
            "amount": 0,
            "kind": "daily_skip_cap",
            "welcome_count": welcome,
            "hkt_day": hkt_day,
        }
    return {
        "amount": min(DAILY_LOGIN_CREDITS, room),
        "kind": "daily",
        "welcome_count": welcome,
        "hkt_day": hkt_day,
    }


def apply_grant(wallet: dict, plan: dict, now: datetime, lot_id: str) -> dict:
    out = dict(wallet)
    out["lots"] = expire_lots(out.get("lots") or [], now)
    out["last_grant_hkt"] = plan["hkt_day"]
    out["welcome_count"] = int(plan["welcome_count"])
    amount = int(plan.get("amount") or 0)
    if amount > 0:
        lots = list(out["lots"])
        lots.append(make_lot(amount, str(plan["kind"]), now, lot_id))
        out["lots"] = lots
    if plan.get("kind") == "legacy_topup":
        out["legacy_initial"] = False
    return out

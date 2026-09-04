"""Unit tests: welcome lots, daily cap, FIFO debit, Stripe packs."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "pydantic_settings" not in sys.modules:
    mock_ps = MagicMock()

    class DummyBaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    mock_ps.BaseSettings = DummyBaseSettings
    mock_ps.SettingsConfigDict = dict
    sys.modules["pydantic_settings"] = mock_ps

for mod in ["yaml", "pytz", "bson", "pymongo", "motor", "loguru", "redis"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from app.services.credits.credit_grants import apply_grant, plan_login_grant
from app.services.credits.credit_packs import get_pack, list_packs
from app.services.credits.credit_wallet import (
    empty_wallet,
    expire_lots,
    fifo_debit,
    make_lot,
    total_balance,
)


NOW = datetime(2026, 9, 4, 10, 0, 0)


class TestCreditGrants(unittest.TestCase):
    def test_welcome_three_times_ten(self):
        wallet = empty_wallet("u1")
        total = 0
        for day in ("2026-09-04", "2026-09-05", "2026-09-06"):
            plan = plan_login_grant(wallet, day, NOW)
            self.assertEqual(plan["amount"], 10)
            wallet = apply_grant(wallet, plan, NOW, f"lot-{day}")
            total += 10
        self.assertEqual(wallet["welcome_count"], 3)
        self.assertEqual(total_balance(wallet), 30)

    def test_same_day_idempotent(self):
        wallet = empty_wallet("u1")
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        wallet = apply_grant(wallet, plan, NOW, "lot-a")
        self.assertIsNone(plan_login_grant(wallet, "2026-09-04", NOW))

    def test_legacy_topup_then_two_tens(self):
        wallet = empty_wallet("u1")
        wallet["purchased"] = 5
        wallet["legacy_initial"] = True
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 5)
        wallet = apply_grant(wallet, plan, NOW, "lot-legacy")
        plan2 = plan_login_grant(wallet, "2026-09-05", NOW)
        self.assertEqual(plan2["amount"], 10)
        wallet = apply_grant(wallet, plan2, NOW, "lot-2")
        plan3 = plan_login_grant(wallet, "2026-09-06", NOW)
        self.assertEqual(plan3["amount"], 10)
        wallet = apply_grant(wallet, plan3, NOW, "lot-3")
        self.assertEqual(total_balance(wallet), 30)

    def test_daily_plus_five_after_welcome(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 3
        wallet["last_grant_hkt"] = "2026-09-03"
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 5)
        self.assertEqual(plan["kind"], "daily")

    def test_free_cap_ten_skips_daily(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 3
        wallet["last_grant_hkt"] = "2026-09-03"
        wallet["lots"] = [make_lot(10, "welcome", NOW, "full")]
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 0)
        self.assertEqual(plan["kind"], "daily_skip_cap")

    def test_daily_clips_to_cap(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 3
        wallet["last_grant_hkt"] = "2026-09-03"
        wallet["lots"] = [make_lot(8, "welcome", NOW, "eight")]
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 2)


class TestCreditWallet(unittest.TestCase):
    def test_expired_lot_ignored(self):
        lot = make_lot(10, "daily", NOW - timedelta(days=8), "old")
        kept = expire_lots([lot], NOW)
        self.assertEqual(kept, [])

    def test_fifo_free_then_purchased(self):
        wallet = empty_wallet("u1")
        early = make_lot(2, "daily", NOW, "early")
        later = make_lot(3, "daily", NOW + timedelta(days=1), "later")
        wallet["lots"] = [later, early]
        wallet["purchased"] = 4
        out = fifo_debit(wallet, 6)
        self.assertEqual(total_balance(out), 3)
        self.assertEqual(out["purchased"], 3)
        self.assertEqual(sum(int(x["remaining"]) for x in out["lots"]), 0)


class TestCreditPacks(unittest.TestCase):
    def test_three_packs_no_usd1(self):
        packs = {row["id"]: row for row in list_packs()}
        self.assertEqual(set(packs), {"usd3", "usd5", "usd10"})
        self.assertEqual(get_pack("usd3")["credits"], 180)
        self.assertEqual(get_pack("usd5")["credits"], 350)
        self.assertEqual(get_pack("usd10")["credits"], 800)
        with self.assertRaises(KeyError):
            get_pack("usd1")


if __name__ == "__main__":
    unittest.main()

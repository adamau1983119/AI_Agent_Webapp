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
    def test_welcome_once_one_hundred(self):
        wallet = empty_wallet("u1")
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 100)
        self.assertEqual(plan["kind"], "welcome")
        wallet = apply_grant(wallet, plan, NOW, "lot-welcome")
        self.assertEqual(wallet["welcome_count"], 1)
        self.assertEqual(total_balance(wallet, NOW), 100)
        nxt = plan_login_grant(wallet, "2026-09-05", NOW)
        self.assertEqual(nxt["kind"], "daily_skip_cap")
        self.assertEqual(nxt["amount"], 0)

    def test_same_day_idempotent(self):
        wallet = empty_wallet("u1")
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        wallet = apply_grant(wallet, plan, NOW, "lot-a")
        self.assertEqual(wallet["last_grant_amount"], 100)
        self.assertEqual(wallet["last_grant_kind"], "welcome")
        self.assertIsNone(plan_login_grant(wallet, "2026-09-04", NOW))

    def test_legacy_topup_then_daily(self):
        wallet = empty_wallet("u1")
        wallet["purchased"] = 50
        wallet["legacy_initial"] = True
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 50)
        self.assertEqual(plan["kind"], "legacy_topup")
        wallet = apply_grant(wallet, plan, NOW, "lot-legacy")
        plan2 = plan_login_grant(wallet, "2026-09-05", NOW)
        self.assertEqual(plan2["kind"], "daily")
        self.assertEqual(plan2["amount"], 10)
        wallet = apply_grant(wallet, plan2, NOW, "lot-2")
        self.assertEqual(total_balance(wallet, NOW), 110)

    def test_daily_plus_twenty_after_welcome(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 1
        wallet["last_grant_hkt"] = "2026-09-03"
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 20)
        self.assertEqual(plan["kind"], "daily")

    def test_free_cap_sixty_skips_daily(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 1
        wallet["last_grant_hkt"] = "2026-09-03"
        wallet["lots"] = [make_lot(60, "welcome", NOW, "full")]
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 0)
        self.assertEqual(plan["kind"], "daily_skip_cap")

    def test_daily_clips_to_cap(self):
        wallet = empty_wallet("u1")
        wallet["welcome_count"] = 1
        wallet["last_grant_hkt"] = "2026-09-03"
        wallet["lots"] = [make_lot(50, "welcome", NOW, "fifty")]
        plan = plan_login_grant(wallet, "2026-09-04", NOW)
        self.assertEqual(plan["amount"], 10)

    def test_existing_balance_scales_once(self):
        from app.services.credits.credit_wallet import apply_unit_scale

        wallet = empty_wallet("u1")
        wallet["unit_scale"] = 0
        wallet["purchased"] = 4
        wallet["lots"] = [make_lot(3, "daily", NOW, "old")]
        self.assertTrue(apply_unit_scale(wallet))
        self.assertEqual(wallet["purchased"], 40)
        self.assertEqual(wallet["lots"][0]["remaining"], 30)
        self.assertFalse(apply_unit_scale(wallet))


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
        out = fifo_debit(wallet, 6, NOW)
        self.assertEqual(total_balance(out, NOW), 3)
        self.assertEqual(out["purchased"], 3)
        self.assertEqual(sum(int(x["remaining"]) for x in out["lots"]), 0)


class TestCreditPacks(unittest.TestCase):
    def test_three_packs_no_usd1(self):
        packs = {row["id"]: row for row in list_packs()}
        self.assertEqual(set(packs), {"usd3", "usd5", "usd10"})
        self.assertEqual(get_pack("usd3")["credits"], 1800)
        self.assertEqual(get_pack("usd5")["credits"], 3500)
        self.assertEqual(get_pack("usd10")["credits"], 8000)
        with self.assertRaises(KeyError):
            get_pack("usd1")


class TestPaidPackFromSession(unittest.TestCase):
    def _session(self, **over):
        base = {
            "id": "cs_test_abc",
            "payment_status": "paid",
            "currency": "usd",
            "amount_total": 300,
            "livemode": False,
            "client_reference_id": "user_1",
            "metadata": {"user_id": "user_1", "pack_id": "usd3", "credits": "180"},
        }
        base.update(over)
        return base

    def test_matches_usd3(self):
        from app.services.credits.credit_fulfill import paid_pack_from_session

        out = paid_pack_from_session(self._session())
        self.assertEqual(out["credits"], 1800)
        self.assertEqual(out["amount_cents"], 300)

    def test_rejects_wrong_amount(self):
        from app.services.credits.credit_fulfill import paid_pack_from_session

        self.assertIsNone(paid_pack_from_session(self._session(amount_total=1)))

    def test_rejects_unpaid(self):
        from app.services.credits.credit_fulfill import paid_pack_from_session

        self.assertIsNone(paid_pack_from_session(self._session(payment_status="unpaid")))

    def test_rejects_wrong_currency(self):
        from app.services.credits.credit_fulfill import paid_pack_from_session

        self.assertIsNone(paid_pack_from_session(self._session(currency="hkd")))

    def test_credits_from_pack_not_metadata(self):
        from app.services.credits.credit_fulfill import paid_pack_from_session

        session = self._session()
        session["metadata"] = {
            "user_id": "user_1",
            "pack_id": "usd3",
            "credits": "9999",
        }
        out = paid_pack_from_session(session)
        self.assertEqual(out["credits"], 1800)


if __name__ == "__main__":
    unittest.main()

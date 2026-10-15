"""Monthly books export splits gross, fee, and net. No customer email."""
from __future__ import annotations

import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock
from zoneinfo import ZoneInfo

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

from app.services.credits import credit_books as books

_HKT = ZoneInfo("Asia/Hong_Kong")


class MonthBooksTests(unittest.TestCase):
    def test_october_charge_keeps_gross_fee_and_net(self):
        created = int(datetime(2026, 10, 15, 12, 32, tzinfo=_HKT).timestamp())
        available = int(datetime(2026, 10, 22, 12, 0, tzinfo=_HKT).timestamp())
        page = {
            "data": [
                {
                    "id": "txn_live_1",
                    "type": "charge",
                    "reporting_category": "charge",
                    "currency": "hkd",
                    "amount": 2354,
                    "fee": 184,
                    "net": 2170,
                    "created": created,
                    "available_on": available,
                    "source": "ch_live_1",
                }
            ],
            "has_more": False,
        }
        fake = MagicMock()
        fake.BalanceTransaction.list.return_value = page
        old_stripe = books.stripe
        old_key = books.settings.STRIPE_SECRET_KEY
        books.stripe = fake
        books.settings.STRIPE_SECRET_KEY = "sk_test_books"
        try:
            payload = books.list_month_books("2026-10")
        finally:
            books.stripe = old_stripe
            books.settings.STRIPE_SECRET_KEY = old_key
        row = payload["rows"][0]
        self.assertEqual(row["kind"], "income")
        self.assertEqual(row["created_hkt"], "2026-10-15")
        self.assertEqual(row["available_hkt"], "2026-10-22")
        self.assertEqual(row["gross"], "23.54")
        self.assertEqual(row["fee"], "1.84")
        self.assertEqual(row["net"], "21.70")
        self.assertEqual(row["charge_id"], "ch_live_1")
        self.assertNotIn("email", row)
        kwargs = fake.BalanceTransaction.list.call_args.kwargs
        self.assertLess(kwargs["created"]["gte"], created)
        self.assertGreater(kwargs["created"]["lt"], created)

    def test_bad_month_is_rejected(self):
        with self.assertRaises(ValueError):
            books.list_month_books("2026-13")

    def test_token_must_match_exactly(self):
        old = books.settings.BOOKS_READ_TOKEN
        books.settings.BOOKS_READ_TOKEN = "books-token-test"
        try:
            self.assertTrue(books.books_token_ok("books-token-test"))
            self.assertFalse(books.books_token_ok("books-token-tes"))
        finally:
            books.settings.BOOKS_READ_TOKEN = old


if __name__ == "__main__":
    unittest.main()

"""Checkout sends a one-time receipt to the buyer email."""
from __future__ import annotations

import sys
import unittest
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

from app.services.credits import credit_stripe as stripe_mod


class CheckoutReceiptTests(unittest.TestCase):
    def _create(self, email: str) -> dict:
        captured: dict = {}

        def create(**kwargs):
            captured.update(kwargs)
            return {"url": "https://checkout.stripe.test/pay"}

        fake = MagicMock()
        fake.checkout.Session.create.side_effect = create
        old_stripe = stripe_mod.stripe
        old_key = stripe_mod.settings.STRIPE_SECRET_KEY
        stripe_mod.stripe = fake
        stripe_mod.settings.STRIPE_SECRET_KEY = "sk_test_receipt"
        try:
            stripe_mod.create_checkout_session("user-1", "usd3", email)
        finally:
            stripe_mod.stripe = old_stripe
            stripe_mod.settings.STRIPE_SECRET_KEY = old_key
        return captured

    def test_buyer_email_is_the_receipt(self):
        payload = self._create("a.adam1983119@gmail.com")
        self.assertEqual(payload["customer_email"], "a.adam1983119@gmail.com")
        self.assertEqual(
            payload["payment_intent_data"],
            {"receipt_email": "a.adam1983119@gmail.com"},
        )
        self.assertEqual(payload["metadata"]["credits"], "900")
        self.assertEqual(payload["mode"], "payment")

    def test_missing_email_does_not_invent_a_receipt(self):
        payload = self._create("")
        self.assertNotIn("customer_email", payload)
        self.assertNotIn("payment_intent_data", payload)


if __name__ == "__main__":
    unittest.main()

"""識別信箱與發文同事補點（純函式）。"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.staff_identity import (
    MAIL_SINK,
    MARKER_EMAIL,
    deliver_to,
    is_marker_email,
    is_staff_credit_email,
    next_staff_refill,
)


class StaffIdentityTests(unittest.TestCase):
    def test_marker_mail_goes_to_ops_inbox(self):
        self.assertTrue(is_marker_email(MARKER_EMAIL.upper()))
        self.assertEqual(deliver_to(MARKER_EMAIL), MAIL_SINK)
        self.assertEqual(deliver_to("someone@example.com"), "someone@example.com")

    def test_staff_refill_stops_at_floor_and_ten(self):
        self.assertEqual(next_staff_refill(59, 0), 60)
        self.assertIsNone(next_staff_refill(60, 0))
        self.assertIsNone(next_staff_refill(10, 10))
        self.assertEqual(next_staff_refill(0, 9), 60)

    def test_staff_list_defaults_to_ops_inbox(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STAFF_CREDIT_EMAILS", None)
            self.assertTrue(is_staff_credit_email(MAIL_SINK))
            self.assertFalse(is_staff_credit_email(MARKER_EMAIL))

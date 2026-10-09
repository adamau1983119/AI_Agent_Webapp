"""畫面語言只認 X-Language；週報退訂與驗證信分開。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

for mod in ["yaml", "pytz", "bson", "pymongo", "motor", "loguru", "redis"]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

os.environ.setdefault("JWT_SECRET", "test-weekly-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from app.config_module import settings
from app.services.weekly_mail_page import render_unsubscribe_page
from app.services.weekly_mail_rules import topic_title, weekly_eligible
from app.services.weekly_mail_token import create_unsubscribe_token, read_unsubscribe_token
from app.services.weekly_mail_webhook import recipient_emails, verify_resend_signature
from app.utils.ui_language import open_oauth_language, screen_language, seal_oauth_language

settings.JWT_SECRET = os.environ["JWT_SECRET"]
settings.JWT_ALGORITHM = "HS256"


class _Req:
    def __init__(self, headers):
        self.headers = headers


class LanguageMailTests(unittest.TestCase):
    def test_screen_language_ignores_accept_language(self):
        req = _Req({"X-Language": "ja", "Accept-Language": "en"})
        self.assertEqual(screen_language(req), "ja")
        self.assertIsNone(screen_language(_Req({"Accept-Language": "en"})))
        self.assertIsNone(screen_language(_Req({"X-Language": "fr"})))

    def test_oauth_state_roundtrip(self):
        sealed = seal_oauth_language("en")
        self.assertEqual(open_oauth_language(sealed), "en")
        self.assertIsNone(open_oauth_language("not-a-token"))
        self.assertIsNone(seal_oauth_language("fr"))

    def test_unsubscribe_token_is_not_an_access_token(self):
        token = create_unsubscribe_token("user_1", "A@Example.com")
        claim = read_unsubscribe_token(token)
        self.assertEqual(claim["email"], "a@example.com")
        self.assertIsNone(read_unsubscribe_token("nope"))

    def test_weekly_eligible_keeps_account_mail_separate(self):
        base = {"status": "active", "email_verified": True, "email": "a@b.com"}
        self.assertTrue(weekly_eligible(base))
        opted = dict(base, weekly_mail_opt_out=True)
        self.assertFalse(weekly_eligible(opted))
        bounced = dict(base, email_deliverable=False)
        self.assertFalse(weekly_eligible(bounced))

    def test_topic_title_falls_back_to_original(self):
        doc = {"title": "原文", "titles_i18n": {"zh-TW": "繁中標題"}, "original_title": "Original"}
        self.assertEqual(topic_title(doc, "zh-TW"), "繁中標題")
        self.assertEqual(topic_title(doc, "ja"), "Original")

    def test_resend_signature_and_recipients(self):
        secret = "whsec_" + base64.b64encode(b"k" * 24).decode()
        key = b"k" * 24
        body = b'{"type":"email.bounced","data":{"to":["A@B.com"]}}'
        stamp = str(int(time.time()))
        signed = f"msg.{stamp}.".encode() + body
        digest = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
        headers = {
            "svix-id": "msg",
            "svix-timestamp": stamp,
            "svix-signature": f"v1,{digest}",
        }
        self.assertTrue(verify_resend_signature(secret, body, headers))
        self.assertFalse(verify_resend_signature("", body, headers))
        emails = recipient_emails({"data": {"to": ["A@B.com"]}})
        self.assertEqual(emails, ["a@b.com"])

    def test_page_uses_the_account_language(self):
        page = render_unsubscribe_page("ja", ok=True)
        self.assertIn("週次メールを停止しました", page)
        self.assertIn("確認メール", page)


if __name__ == "__main__":
    unittest.main()

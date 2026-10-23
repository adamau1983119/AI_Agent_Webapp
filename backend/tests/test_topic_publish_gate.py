"""入選三關。不連外站、不打模型。"""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, patch

from app.services.automation.topic_publish_gate import (
    block_reason,
    body_is_complete,
    rejection,
)


def _words(n: int) -> str:
    return " ".join(["story"] * n)


def _cjk(n: int) -> str:
    return "報" * n


class TestTopicPublishGate(unittest.TestCase):
    def test_english_short_fails(self):
        self.assertFalse(body_is_complete(_words(40)))

    def test_english_150_passes(self):
        self.assertTrue(body_is_complete(_words(150)))

    def test_cjk_counts_characters_not_spaces(self):
        self.assertFalse(body_is_complete(_cjk(80)))
        self.assertTrue(body_is_complete(_cjk(150)))

    def test_continue_reading_fails_even_if_long(self):
        self.assertFalse(body_is_complete(_words(160) + " Continue reading"))

    def test_membership_mention_in_long_body_passes(self):
        text = _words(160) + " 多數需事先加入會員或獎勵計畫。"
        self.assertIsNone(block_reason(url="https://example.com/a", body=text))

    def test_premium_url_blocks(self):
        reason = block_reason(
            url="https://www.bbcgoodfood.com/premium/lemon",
            body=_words(200),
        )
        self.assertEqual(reason, "paywall")

    def test_declared_paywall_blocks(self):
        reason = block_reason(
            url="https://example.com/story",
            body=_cjk(200),
            paywall_declared=True,
        )
        self.assertEqual(reason, "paywall")

    def test_image_fail_after_text_ok(self):
        async def _run():
            with patch(
                "app.services.images.jpeg_compress.fetch_and_compress",
                new=AsyncMock(side_effect=ValueError("not_an_image")),
            ):
                return await rejection(
                    url="https://example.com/story",
                    body=_words(160),
                    images=["https://cdn.example/a.jpg"],
                )

        import asyncio

        self.assertEqual(asyncio.run(_run()), "image")


if __name__ == "__main__":
    unittest.main()

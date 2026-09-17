"""Unit tests for topic post-scan (no live LLM / DB)."""
from __future__ import annotations

import unittest

from app.services.automation.topic_post_scan import (
    apply_scan_to_source,
    fact_text_from_topic,
    scan_text,
)
from app.services.automation.topic_visible_floor import apply_visible_floor
from app.services.images.match_facts import match_fact_text


class TestTopicPostScan(unittest.TestCase):
    def test_popbee_membership_cut_from_clean(self):
        raw = (
            "這是一篇真正的時尚報導，介紹春夏外套與剪裁細節，"
            "設計師表示今年強調結構與材質層次。" * 3
            + "\n\n加入 POPBEE 會員\n尊享禮遇\n立即登記\n"
            "相關閱讀\n另一篇購物文"
        )
        r = scan_text(raw)
        self.assertNotIn("加入 POPBEE", r["content_clean"])
        self.assertNotIn("相關閱讀", r["content_clean"])
        self.assertIn("時尚報導", r["content_clean"])
        self.assertFalse(r["hide_card"])

    def test_slideshow_nm_cut(self):
        body = ("主文段落說明餐廳背景與菜色。" * 10) + "\n\n1/12\n圖說噪音\n2/12\n"
        r = scan_text(body)
        self.assertNotIn("1/12", r["content_clean"])
        self.assertIn("餐廳", r["content_clean"])

    def test_severe_paywall_may_hide(self):
        raw = "subscribers only\nlogin to continue\npaywall"
        r = scan_text(raw)
        self.assertTrue(r["hide_card"])
        self.assertGreaterEqual(r["sort_penalty"], 80)

    def test_short_clean_keeps_body_not_empty(self):
        raw = "短訊：" + ("真實內容保留。" * 20)
        r = scan_text(raw)
        self.assertGreaterEqual(len(r["content_clean"]), 80)

    def test_apply_scan_writes_content_clean(self):
        src = {"original_content": ("真實新聞正文。" * 30) + "\nnewsletter\n"}
        scan = apply_scan_to_source(src)
        self.assertTrue(src.get("content_clean"))
        self.assertEqual(src["content_clean"], scan["content_clean"])

    def test_fact_and_match_prefer_clean(self):
        topic = {
            "summary_flash": "flash only",
            "sources": [
                {
                    "content_clean": "clean body for facts",
                    "original_content": "noisy original with shop now junk",
                }
            ],
        }
        self.assertEqual(fact_text_from_topic(topic), "clean body for facts")
        self.assertEqual(match_fact_text(topic), "clean body for facts")

    def test_visible_floor_unhides(self):
        topics = [
            {"category": "fashion", "hidden": True, "sort_penalty": 80},
            {"category": "fashion", "hidden": True, "sort_penalty": 25},
            {"category": "fashion", "hidden": True, "sort_penalty": 15},
        ]
        apply_visible_floor(topics)
        visible = [t for t in topics if not t.get("hidden")]
        self.assertGreaterEqual(len(visible), 3)


if __name__ == "__main__":
    unittest.main()

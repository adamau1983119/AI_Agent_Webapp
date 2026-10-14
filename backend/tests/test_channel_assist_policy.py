"""建立頻道助手回答規則：11 類、缺地區改全球、分析次數。"""
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.channel_assist_policy import (
    ASSIST_CATEGORIES,
    decide_quota,
    finalize_intent,
)
from app.services.channel_assist_service import ChannelAssistService


class TestFinalizeIntent(unittest.TestCase):
    def test_eleven_categories_only(self):
        self.assertEqual(len(ASSIST_CATEGORIES), 11)
        self.assertNotIn("other", ASSIST_CATEGORIES)
        self.assertNotIn("lego", ASSIST_CATEGORIES)

    def test_outside_catalog_skips_sources(self):
        parsed = finalize_intent({"category": "pets", "region": "japan"})
        self.assertTrue(parsed["out_of_catalog"])
        self.assertIsNone(parsed["category"])
        self.assertIsNone(parsed["region"])

    def test_removed_categories_are_outside(self):
        for raw in ("other", "lego", "cosplay"):
            parsed = finalize_intent({"category": raw, "region": "taiwan"})
            self.assertTrue(parsed["out_of_catalog"], raw)

    def test_unknown_region_becomes_global(self):
        parsed = finalize_intent({"category": "food", "region": "france"})
        self.assertEqual(parsed["category"], "food")
        self.assertEqual(parsed["region"], "global")
        self.assertTrue(parsed["region_defaulted"])
        self.assertFalse(parsed["clarification_needed"])

    def test_missing_region_becomes_global(self):
        parsed = finalize_intent({"category": "beauty", "region": None})
        self.assertEqual(parsed["region"], "global")
        self.assertTrue(parsed["region_defaulted"])

    def test_explicit_global_is_not_a_fallback(self):
        parsed = finalize_intent({
            "category": "tech",
            "region": "global",
            "region_defaulted": False,
        })
        self.assertEqual(parsed["region"], "global")
        self.assertFalse(parsed["region_defaulted"])

    def test_known_region_stays(self):
        parsed = finalize_intent({
            "category": "fashion",
            "region": "jp",
            "split_channel": True,
            "keywords": ["穿搭"],
        })
        self.assertEqual(parsed["region"], "japan")
        self.assertFalse(parsed["region_defaulted"])
        self.assertTrue(parsed["split_channel"])
        self.assertEqual(parsed["keywords"], ["穿搭"])

    def test_prompt_is_expert_and_lists_eleven(self):
        prompt = ChannelAssistService()._build_assist_prompt("法國美食", "zh-TW")
        self.assertIn("頻道定位專家", prompt)
        self.assertIn("不追問", prompt)
        self.assertIn("beauty", prompt)
        self.assertIn("growth", prompt)
        self.assertNotIn("entertainment|other", prompt)


class TestQuota(unittest.TestCase):
    def test_tenth_and_thirtieth_still_run(self):
        tenth = decide_quota(9, 0, "2026-10-15", "2026-10-15")
        self.assertTrue(tenth["allowed"])
        self.assertTrue(tenth["last_analysis"])
        self.assertEqual(tenth["pending"], 10)
        thirtieth = decide_quota(0, 29, "2026-10-15", "2026-10-15")
        self.assertTrue(thirtieth["allowed"])
        self.assertTrue(thirtieth["last_analysis"])
        self.assertEqual(thirtieth["day_count"], 30)

    def test_over_cap_does_not_increment(self):
        blocked = decide_quota(10, 3, "2026-10-15", "2026-10-15")
        self.assertFalse(blocked["allowed"])
        self.assertEqual(blocked["pending"], 10)
        self.assertEqual(blocked["day_count"], 3)
        day_blocked = decide_quota(2, 30, "2026-10-15", "2026-10-15")
        self.assertFalse(day_blocked["allowed"])
        self.assertEqual(day_blocked["pending"], 2)

    def test_new_day_resets_daily_not_pending(self):
        rolled = decide_quota(4, 30, "2026-10-14", "2026-10-15")
        self.assertTrue(rolled["allowed"])
        self.assertEqual(rolled["pending"], 5)
        self.assertEqual(rolled["day_count"], 1)
        still_blocked = decide_quota(10, 30, "2026-10-14", "2026-10-15")
        self.assertFalse(still_blocked["allowed"])
        self.assertEqual(still_blocked["pending"], 10)


if __name__ == "__main__":
    unittest.main()

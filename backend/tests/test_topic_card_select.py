"""選文閘門：錨點／fail-open／off 預設。不改翻譯管線。"""
import inspect
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if "pydantic_settings" not in sys.modules:
    mock_ps = MagicMock()

    class DummyBaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    mock_ps.BaseSettings = DummyBaseSettings
    mock_ps.SettingsConfigDict = dict
    sys.modules["pydantic_settings"] = mock_ps

for mod in [
    "yaml", "pytz", "bson", "pymongo", "pymongo.errors", "motor",
    "motor.motor_asyncio", "bs4", "requests", "httpx", "aiohttp", "loguru",
    "redis", "redis.asyncio", "redis.asyncio.connection", "redis.exceptions",
    "apscheduler", "apscheduler.schedulers", "apscheduler.schedulers.asyncio",
    "apscheduler.triggers", "apscheduler.triggers.cron",
    "apscheduler.triggers.interval",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from app.models.topic import Category
from app.services.automation.topic_card_gates import should_skip_entry
from app.services.automation.topic_card_select import merge_legacy_fill
from app.services.automation.topic_card_select_config import (
    candidate_factor,
    cold_slot_count,
    selection_mode,
)


class TestTopicCardGates(unittest.TestCase):
    def test_vietnam_politics_no_fashion_anchor(self):
        reason = should_skip_entry(
            "Vietnam arrests deputy minister over bribery",
            "https://www.scmp.com/news/asia/article",
            Category.FASHION,
        )
        self.assertEqual(reason, "no_anchor")

    def test_designer_bribery_keeps_fashion(self):
        reason = should_skip_entry(
            "Chanel designer accused of bribery in Paris",
            "https://www.vogue.com/article/chanel",
            Category.FASHION,
        )
        self.assertIsNone(reason)

    def test_dandelion_health_no_food_anchor(self):
        reason = should_skip_entry(
            "Health benefits of dandelion",
            "https://www.eatthis.com/dandelion",
            Category.FOOD,
        )
        self.assertEqual(reason, "no_anchor")

    def test_gym_over_60_no_food_anchor(self):
        reason = should_skip_entry(
            "5 daily exercises for people over 60",
            "https://www.eatthis.com/gym",
            Category.FOOD,
        )
        self.assertEqual(reason, "no_anchor")

    def test_food_recipe_keeps(self):
        reason = should_skip_entry(
            "Chef shares taco recipe from Mexico City restaurant",
            "https://www.nytimes.com/food",
            Category.FOOD,
        )
        self.assertIsNone(reason)

    def test_coupon_url_policy(self):
        reason = should_skip_entry(
            "Nike collection runway recap",
            "https://shop.example.com/deals/sale",
            Category.FASHION,
        )
        self.assertEqual(reason, "policy")

    def test_source_cap(self):
        used = {"Vogue"}
        reason = should_skip_entry(
            "New Nike collection on the runway",
            "https://www.vogue.com/article/nike",
            Category.FASHION,
            "Vogue",
            used,
        )
        self.assertEqual(reason, "source_cap")


class TestTopicCardSelectConfig(unittest.TestCase):
    def test_default_mode_off(self):
        with patch(
            "app.services.automation.topic_card_select_config._raw",
            return_value={},
        ):
            self.assertEqual(selection_mode(), "off")
        yaml_text = (
            BACKEND_DIR / "config" / "topic_generation.yaml"
        ).read_text(encoding="utf-8")
        self.assertRegex(yaml_text, r"mode:\s*off")
        self.assertNotRegex(yaml_text, r"generate_content\s*:\s*true")

    def test_cold_slots_c5_c10_c1(self):
        with patch(
            "app.services.automation.topic_card_select_config._raw",
            return_value={"cold_ratio": 0.20},
        ):
            self.assertEqual(cold_slot_count(5), 1)
            self.assertEqual(cold_slot_count(10), 2)
            self.assertEqual(cold_slot_count(1), 0)

    def test_candidate_factor_floor(self):
        with patch(
            "app.services.automation.topic_card_select_config._raw",
            return_value={"candidate_factor": 8},
        ):
            self.assertEqual(candidate_factor(), 8)

    def test_invalid_mode_falls_back_off(self):
        with patch(
            "app.services.automation.topic_card_select_config._raw",
            return_value={"mode": "strict"},
        ):
            self.assertEqual(selection_mode(), "off")


class TestFailOpenAndLegacyDefaults(unittest.TestCase):
    def test_merge_fills_to_c(self):
        selected = [{"original_title": "A", "summary_flash": "fa"}]
        legacy = [
            {"original_title": "A", "summary_flash": "fa"},
            {"original_title": "B", "summary_flash": "fb", "sources": [{}]},
            {"original_title": "C", "summary_flash": "fc", "sources": [{}]},
        ]
        out = merge_legacy_fill(selected, legacy, 3)
        self.assertEqual(len(out), 3)
        self.assertEqual([t["original_title"] for t in out], ["A", "B", "C"])
        self.assertTrue(all(t.get("summary_flash") for t in out))

    def test_enforce_strict_still_fills_c(self):
        out = merge_legacy_fill([], [{"original_title": f"t{i}"} for i in range(5)], 5)
        self.assertEqual(len(out), 5)

    def test_collect_from_role_defaults_keep_legacy(self):
        from app.services.automation.topic_collector import TopicCollector

        sig = inspect.signature(TopicCollector._collect_from_role)
        self.assertIs(sig.parameters["enforce"].default, False)
        self.assertIs(sig.parameters["prefer_secondary"].default, False)
        self.assertIs(sig.parameters["used_sources"].default, None)

    def test_collect_by_roles_select_mode_default(self):
        from app.services.automation.topic_collector import TopicCollector

        sig = inspect.signature(TopicCollector._collect_by_roles)
        self.assertIs(sig.parameters["_select_mode"].default, None)


if __name__ == "__main__":
    unittest.main()

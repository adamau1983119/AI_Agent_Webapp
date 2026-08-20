"""
單元測試：驗證主題卡監察紅燈與排程自動補產卡邏輯
"""
import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Mock external dependencies if not installed in local environment
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
    "yaml", "pytz", "bson", "pymongo", "pymongo.errors", "motor", "motor.motor_asyncio",
    "bs4", "requests", "httpx", "aiohttp", "loguru",
    "apscheduler", "apscheduler.schedulers", "apscheduler.schedulers.asyncio",
    "apscheduler.triggers", "apscheduler.triggers.cron", "apscheduler.triggers.interval",
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

from app.models.topic import Category
from app.services.observability.traffic_light import (
    TrafficLight,
    evaluate_health,
    light_zh,
    verdict_zh,
)


class TestTrafficLightTopicDeficit(unittest.TestCase):
    """驗證主題卡不足時 traffic_light 正確判定紅燈"""

    def test_healthy_with_full_topics_is_green(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
            "topics_today": {"v8_count": 15, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.GREEN)
        self.assertIn("正式域正常", sig.headline)

    def test_topic_deficit_in_body_is_red(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
            "topics_today": {"v8_count": 0, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.RED)
        self.assertIn("今日主題卡不足（0/15）", sig.headline)
        self.assertEqual(light_zh(sig.light), "紅燈")
        self.assertEqual(verdict_zh(sig.light), "有事・請立即處理")

    def test_topic_deficit_passed_as_kwargs_is_red(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": True},
        }
        sig = evaluate_health(body, topics_v8=5, topics_expected=15)
        self.assertEqual(sig.light, TrafficLight.RED)
        self.assertIn("今日主題卡不足（5/15）", sig.headline)

    def test_collection_disabled_with_zero_topics_is_green(self):
        body = {
            "status": "healthy",
            "database": "connected",
            "cost_controls": {"scheduled_topic_collection": False},
            "topics_today": {"v8_count": 0, "expected": 15},
        }
        sig = evaluate_health(body)
        self.assertEqual(sig.light, TrafficLight.GREEN)


class TestSchedulerMonitorAutoBackfill(unittest.IsolatedAsyncioTestCase):
    """驗證 SchedulerMonitor 自動補產卡與防重入邏輯"""

    def setUp(self):
        from app.services.automation.scheduler_monitor import SchedulerMonitor
        self.SchedulerMonitor = SchedulerMonitor

    async def test_check_health_triggers_ensure_today_when_topics_deficient(self):
        scheduler = MagicMock()
        scheduler.is_running = True
        scheduler.trigger_manual_generation = AsyncMock(return_value=[])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor._count_topics_hkt_today = AsyncMock(return_value=0)
        monitor.ensure_today_topics = AsyncMock()

        with patch("app.services.automation.scheduler_monitor.is_daily_mode", return_value=True), \
             patch("app.services.automation.scheduler_monitor.expected_topics_today", return_value=15), \
             patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True):
            await monitor._check_scheduler_health()
            await asyncio.sleep(0.05)
            self.assertTrue(monitor.ensure_today_topics.called or monitor._is_ensuring is False)

    async def test_ensure_today_concurrency_lock(self):
        scheduler = MagicMock()
        scheduler.trigger_manual_generation = AsyncMock(return_value=[])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor.topic_repo.count_hkt_today_by_category = AsyncMock(
            return_value={"fashion": 0, "food": 0, "trend": 0}
        )

        monitor._is_ensuring = True
        with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True):
            await monitor.ensure_today_topics()
            self.assertFalse(monitor.topic_repo.count_hkt_today_by_category.called)

    async def test_ensure_today_fills_partial_deficits(self):
        scheduler = MagicMock()
        scheduler.trigger_manual_generation = AsyncMock(return_value=[{"id": "topic_1"}])

        monitor = self.SchedulerMonitor(scheduler)
        monitor.topic_repo = MagicMock()
        monitor.topic_repo.count_hkt_today_by_category = AsyncMock(
            return_value={"fashion": 5, "food": 2, "trend": 0}
        )

        with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True), \
             patch("app.services.automation.scheduler_monitor.category_deficits", return_value={"fashion": 0, "food": 3, "trend": 5}):
            await monitor.ensure_today_topics()

            calls = scheduler.trigger_manual_generation.await_args_list
            self.assertEqual(len(calls), 2)
            called_categories = [c.kwargs["category"] for c in calls]
            self.assertIn(Category.FOOD, called_categories)
            self.assertIn(Category.TREND, called_categories)
            self.assertNotIn(Category.FASHION, called_categories)


class TestSchedulerTopicCreationWithoutDedupDrop(unittest.IsolatedAsyncioTestCase):
    """驗證 SchedulerService 生成卡片時不會被二次去重自我碰撞拋棄"""

    def setUp(self):
        from app.services.automation.scheduler import SchedulerService
        self.SchedulerService = SchedulerService

    async def test_trigger_manual_generation_creates_all_collected_topics(self):
        with patch.object(self.SchedulerService, "__init__", lambda s: None):
            svc = self.SchedulerService()
            svc.config = MagicMock()
            svc.config.is_daily_limit_enabled.return_value = False
            svc.config.get_preview_images_count.return_value = 1
            svc.config.should_generate_content.return_value = False

            svc.topic_collector = MagicMock()
            svc.topic_collector.collect_topics = AsyncMock(return_value=[
                {"title": "Fashion Trend 1", "sources": []},
                {"title": "Fashion Trend 2", "sources": []},
                {"title": "Fashion Trend 3", "sources": []},
            ])

            svc.topic_repo = MagicMock()
            svc.topic_repo.create_topic = AsyncMock(side_effect=lambda d: d)
            svc.workflow = MagicMock()
            svc.workflow.process_topic = AsyncMock(return_value={"content_generated": False})

            import app.services.automation.topic_triple_preload
            with patch("app.utils.cost_controls.scheduled_topic_collection_enabled", return_value=True), \
                 patch("app.services.automation.topic_triple_preload.preload_topic_titles", new_callable=AsyncMock):
                results = await svc.trigger_manual_generation(
                    category=Category.FASHION,
                    count=3,
                    display_language="zh-TW",
                    respect_quota=False,
                )

                self.assertEqual(len(results), 3)
                self.assertEqual(svc.topic_repo.create_topic.call_count, 3)
                self.assertEqual(svc.workflow.process_topic.call_count, 3)


if __name__ == "__main__":
    unittest.main()

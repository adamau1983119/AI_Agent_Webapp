"""HKT 每日配額與分類缺口（防重複產卡）。"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.automation.topic_day_hkt import category_deficits


def test_category_deficits_full_quota():
    current = {"fashion": 5, "food": 5, "trend": 5}
    assert category_deficits(current) == {"fashion": 0, "food": 0, "trend": 0}


def test_category_deficits_partial():
    current = {"fashion": 5, "food": 3, "trend": 0}
    assert category_deficits(current) == {"fashion": 0, "food": 2, "trend": 5}


def test_category_deficits_over_quota_clamped():
    current = {"fashion": 8, "food": 2, "trend": 5}
    assert category_deficits(current) == {"fashion": 0, "food": 3, "trend": 0}


@pytest.mark.asyncio
async def test_ensure_today_only_fills_deficits(monkeypatch):
    from app.models.topic import Category
    from app.services.automation.scheduler_monitor import SchedulerMonitor

    monkeypatch.setattr(
        "app.utils.cost_controls.scheduled_topic_collection_enabled",
        lambda: True,
    )

    scheduler = MagicMock()
    scheduler.trigger_manual_generation = AsyncMock(return_value=[])

    monitor = SchedulerMonitor(scheduler)
    monitor.topic_repo = MagicMock()
    monitor.topic_repo.count_hkt_today_by_category = AsyncMock(
        return_value={"fashion": 5, "food": 5, "trend": 2}
    )

    await monitor.ensure_today_topics()

    calls = scheduler.trigger_manual_generation.await_args_list
    assert len(calls) == 1
    assert calls[0].kwargs["category"] == Category.TREND
    assert calls[0].kwargs["count"] == 3
    assert calls[0].kwargs["respect_quota"] is True

"""HKT calendar-day helpers for topic schedule (daily mode).

Aligns monitor / ensure_today with topic_generation.yaml daily_generation
(Asia/Hong_Kong) and UTC-naive generated_at written by SchedulerService.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    from backports.zoneinfo import ZoneInfo  # type: ignore

HKT = ZoneInfo("Asia/Hong_Kong")
UTC = ZoneInfo("UTC")
_CATEGORIES = ("fashion", "food", "trend")


def today_hkt_str() -> str:
    return datetime.now(HKT).strftime("%Y-%m-%d")


def hkt_day_utc_bounds(date_str: str | None = None) -> Tuple[datetime, datetime]:
    """Naive UTC [start, end] for Mongo queries on generated_at (utcnow)."""
    if date_str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        start_hkt = datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=HKT)
    else:
        now = datetime.now(HKT)
        start_hkt = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=HKT)
    end_hkt = start_hkt + timedelta(days=1) - timedelta(microseconds=1)
    start_utc = start_hkt.astimezone(UTC).replace(tzinfo=None)
    end_utc = end_hkt.astimezone(UTC).replace(tzinfo=None)
    return start_utc, end_utc


def expected_topics_today() -> int:
    from app.config.topic_config import get_topic_config

    cfg = get_topic_config()
    return sum(cfg.get_category_count(c) for c in _CATEGORIES)


def category_counts() -> Dict[str, int]:
    from app.config.topic_config import get_topic_config

    cfg = get_topic_config()
    return {c: cfg.get_category_count(c) for c in _CATEGORIES}


def is_daily_mode() -> bool:
    from app.config.topic_config import get_topic_config

    return get_topic_config().get_collection_mode() == "daily"

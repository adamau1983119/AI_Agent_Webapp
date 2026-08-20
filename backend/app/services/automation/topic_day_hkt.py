"""HKT calendar-day helpers for topic schedule (daily mode).

Aligns monitor / ensure_today with topic_generation.yaml daily_generation
(Asia/Hong_Kong) and UTC-naive generated_at written by SchedulerService.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Tuple

try:
    from zoneinfo import ZoneInfo
    HKT = ZoneInfo("Asia/Hong_Kong")
    UTC = ZoneInfo("UTC")
except Exception:  # pragma: no cover
    from datetime import timezone
    HKT = timezone(timedelta(hours=8))
    UTC = timezone.utc
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


def hkt_today_topics_filter(*, include_legacy: bool = False) -> Dict:
    """Mongo filter：HKT 今日 + 可選世代過濾。"""
    from app.utils.topic_pipeline import list_topics_generation_filter

    start_utc, end_utc = hkt_day_utc_bounds()
    clauses = [{"generated_at": {"$gte": start_utc, "$lte": end_utc}}]
    gen_f = list_topics_generation_filter(include_legacy=include_legacy)
    if gen_f:
        clauses.append(gen_f)
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def category_deficits(current_by_category: Dict[str, int]) -> Dict[str, int]:
    """各分類距離 yaml 配額尚缺幾張（不小於 0）。"""
    targets = category_counts()
    return {
        cat: max(0, targets.get(cat, 0) - int(current_by_category.get(cat, 0)))
        for cat in _CATEGORIES
    }


def is_daily_mode() -> bool:
    from app.config.topic_config import get_topic_config

    return get_topic_config().get_collection_mode() == "daily"

"""
紅／綠燈判定（Incident 風格）。一目了然：green=沒事，red=有事。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class TrafficLight(str, Enum):
    GREEN = "green"
    RED = "red"


@dataclass(frozen=True)
class Signal:
    light: TrafficLight
    headline: str
    detail: str
    channel_hint: str  # crash | cost


def evaluate_health(body: dict[str, Any] | None, *, error: str | None = None) -> Signal:
    if error:
        return Signal(
            TrafficLight.RED,
            "無法連線正式域",
            error,
            "crash",
        )
    if not body:
        return Signal(
            TrafficLight.RED,
            "健康檢查無資料",
            "health body 為空",
            "crash",
        )
    status = str(body.get("status") or body.get("health") or "").lower()
    db = body.get("database")
    db_ok = db == "connected" or (
        isinstance(db, dict) and db.get("status") == "connected"
    )
    if status not in ("healthy", "ok") or not db_ok:
        return Signal(
            TrafficLight.RED,
            "正式域不健康",
            f"status={status!r} database={db!r}",
            "crash",
        )
    cc = body.get("cost_controls") or {}
    return Signal(
        TrafficLight.GREEN,
        "正式域正常（無事）",
        (
            f"status={status}；"
            f"collection={cc.get('scheduled_topic_collection')}；"
            f"translation={cc.get('ai_topic_translation')}；"
            f"fallback={cc.get('ai_topic_fallback')}"
        ),
        "cost",
    )


def light_zh(light: TrafficLight) -> str:
    return "紅燈" if light is TrafficLight.RED else "綠燈"


def verdict_zh(light: TrafficLight) -> str:
    return "有事・請立即處理" if light is TrafficLight.RED else "沒事・系統正常"

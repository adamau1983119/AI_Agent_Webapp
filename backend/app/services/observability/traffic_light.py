"""
紅／綠燈判定（Incident 風格）。一目了然：green=沒事，red=有事。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


def evaluate_health(
    body: dict[str, Any] | None,
    *,
    error: str | None = None,
    topics_v8: int | None = None,
    topics_expected: int | None = None,
) -> Signal:
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
    collection_on = (
        cc.get("scheduled_topic_collection") is True
        or str(cc.get("scheduled_topic_collection", "")).lower() == "true"
    )

    # 檢查主題卡數量（若有傳入，或由 body["topics_today"] 提供）
    v8_cnt = topics_v8
    exp_cnt = topics_expected
    if v8_cnt is None and isinstance(body.get("topics_today"), dict):
        v8_cnt = body["topics_today"].get("v8_count")
        exp_cnt = body["topics_today"].get("expected")

    # 若產卡開啟且已過 04:00 HKT（產卡時間），主題數不足則判定紅燈
    if collection_on and v8_cnt is not None and exp_cnt is not None:
        try:
            from zoneinfo import ZoneInfo
            hkt_hour = datetime.now(ZoneInfo("Asia/Hong_Kong")).hour
        except Exception:
            try:
                from datetime import timezone, timedelta
                hkt_hour = datetime.now(timezone(timedelta(hours=8))).hour
            except Exception:
                hkt_hour = 12

        if hkt_hour >= 4 and v8_cnt < exp_cnt:
            return Signal(
                TrafficLight.RED,
                f"今日主題卡不足（{v8_cnt}/{exp_cnt}）",
                (
                    f"HKT 今日產卡數 {v8_cnt} 未達預期 {exp_cnt}；"
                    f"collection={cc.get('scheduled_topic_collection')}；"
                    f"status={status}"
                ),
                "cost",
            )

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

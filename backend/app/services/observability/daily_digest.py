"""
初期每日營運報告：綠燈也寄一封（一天一次 HKT）。
OBS_DAILY_DIGEST_ENABLED=true 才作動；與「紅燈才告警」並行。
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.services.observability.alert_mailer import send_alert_email
from app.services.observability.channels import AlertChannel
from app.services.observability.ops_agent import DEFAULT_HEALTH, fetch_health
from app.services.observability.traffic_light import (
    TrafficLight,
    evaluate_health,
    light_zh,
    verdict_zh,
)

logger = logging.getLogger("observability.daily_digest")
_HKT = ZoneInfo("Asia/Hong_Kong")
_last_digest_day = ""


def digest_enabled() -> bool:
    return os.getenv("OBS_DAILY_DIGEST_ENABLED", "false").lower() == "true"


def _digest_hour() -> int:
    try:
        return int(os.getenv("OBS_DAILY_DIGEST_HOUR_HKT", "8"))
    except ValueError:
        return 8


def _today_hkt() -> str:
    return datetime.now(_HKT).strftime("%Y-%m-%d")


def _past_digest_hour() -> bool:
    return datetime.now(_HKT).hour >= _digest_hour()


async def send_daily_digest_now(*, health_url: str = DEFAULT_HEALTH) -> dict[str, Any]:
    """強制寄今日報告（略過「一天一次」鎖；腳本／手動用）。"""
    return await _send_digest(health_url, force=True)


async def maybe_send_daily_digest(*, health_url: str = DEFAULT_HEALTH) -> dict[str, Any]:
    """Watchdog 呼叫：啟用＋已到 HKT 時段＋今日未寄 → 寄一封。"""
    global _last_digest_day
    if not digest_enabled():
        return {"status": "digest_disabled"}
    day = _today_hkt()
    if day == _last_digest_day:
        return {"status": "already_sent", "day": day}
    if not _past_digest_hour():
        return {"status": "too_early", "hour_hkt": _digest_hour()}
    return await _send_digest(health_url, force=False)


async def _send_digest(health_url: str, *, force: bool) -> dict[str, Any]:
    global _last_digest_day
    err: str | None = None
    body: dict[str, Any] | None = None
    try:
        body = fetch_health(health_url)
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    signal = evaluate_health(body, error=err)
    lamp = light_zh(signal.light)
    verdict = verdict_zh(signal.light)
    day = _today_hkt()
    cc = (body or {}).get("cost_controls") or {}
    title = f"每日營運報告 {day}"
    detail = (
        f"【{lamp}】{verdict}。"
        f"正式域 health：{signal.detail}。"
        f"產卡收集={cc.get('scheduled_topic_collection')}；"
        f"翻譯={cc.get('ai_topic_translation')}；"
        f"備援={cc.get('ai_topic_fallback')}。"
        f"說明：初期每日一封；紅燈另有即時告警。"
    )
    channel = (
        AlertChannel.CRASH
        if signal.light is TrafficLight.RED
        else AlertChannel.COST
    )
    ok = await send_alert_email(
        channel,
        title,
        detail=detail,
        extra={
            "traffic_light": signal.light.value,
            "report_type": "daily_digest",
            "day_hkt": day,
            "health_url": health_url,
        },
    )
    if ok and not force:
        _last_digest_day = day
    elif ok and force:
        _last_digest_day = day
    out = {
        "status": "digest_sent" if ok else "digest_failed",
        "traffic_light": signal.light.value,
        "day": day,
        "title": title,
    }
    logger.info("DAILY_DIGEST %s", out)
    return out

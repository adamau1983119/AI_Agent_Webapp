"""每日基本檢查：≥HKT 時段寄一封；Mongo ledger 稽核。"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from typing import Any
try:
    from zoneinfo import ZoneInfo
    _HKT = ZoneInfo("Asia/Hong_Kong")
except Exception:
    from datetime import timezone, timedelta
    _HKT = timezone(timedelta(hours=8))
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


async def send_daily_digest_now(*, health_url: str | None = None) -> dict[str, Any]:
    return await _send_digest(health_url or resolve_health_url(), force=True, source="manual")


async def maybe_send_daily_digest(*, health_url: str | None = None) -> dict[str, Any]:
    global _last_digest_day
    if not digest_enabled():
        return {"status": "digest_disabled"}
    day = _today_hkt()
    if day == _last_digest_day or await was_digest_sent(day):
        _last_digest_day = day
        return {"status": "already_sent", "day": day}
    if not _past_digest_hour():
        return {"status": "too_early", "hour_hkt": _digest_hour()}
    return await _send_digest(
        health_url or resolve_health_url(), force=False, source="watchdog"
    )


async def _send_digest(
    health_url: str, *, force: bool, source: str = "watchdog"
) -> dict[str, Any]:
    global _last_digest_day
    err: str | None = None
    body: dict[str, Any] | None = None
    try:
        body = await asyncio.to_thread(fetch_health, health_url)
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    try:
        topics_v8, topics_all, topics_expected = await topics_hkt_summary()
    except Exception as exc:  # noqa: BLE001
        logger.warning("topics_hkt_summary unexpected: %s", exc)
        topics_v8, topics_all, topics_expected = -1, -1, 15
    signal = evaluate_health(
        body,
        error=err,
        topics_v8=topics_v8 if topics_v8 >= 0 else None,
        topics_expected=topics_expected if topics_expected > 0 else None,
    )
    day = _today_hkt()
    cc = (body or {}).get("cost_controls") or {}
    topics_line = (
        f"今日產卡(v8)={topics_v8}/{topics_expected}（HKT；全日含舊={topics_all}）；"
        if topics_v8 >= 0
        else "今日產卡=查詢失敗；"
    )
    title = f"每日基本檢查 {day}"
    detail = (
        f"【{light_zh(signal.light)}】{verdict_zh(signal.light)}。"
        f"正式域 health：{signal.detail}。{topics_line}"
        f"pipeline={cc.get('topic_pipeline_version')}；"
        f"產卡收集={cc.get('scheduled_topic_collection')}；"
        f"三語預載={cc.get('topic_triple_preload')}（cap={cc.get('topic_triple_preload_cap')}）；"
        f"收集翻譯={cc.get('ai_topic_translation')}；備援={cc.get('ai_topic_fallback')}。"
        f"說明：每日必寄基本檢查；紅燈另寄即時告警。來源={source}。"
    )
    channel = (
        AlertChannel.CRASH if signal.light is TrafficLight.RED else AlertChannel.COST
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
            "source": source,
        },
    )
    out = {
        "status": "digest_sent" if ok else "digest_failed",
        "traffic_light": signal.light.value,
        "day": day,
        "title": title,
        "source": source,
    }
    await record_digest_attempt(
        {
            "day_hkt": day,
            "status": out["status"],
            "title": title,
            "traffic_light": signal.light.value,
            "health_url": health_url,
            "source": source,
        }
    )
    if ok:
        _last_digest_day = day
    logger.info("DAILY_DIGEST %s", out)
    return out


async def digest_health_blob() -> dict[str, Any]:
    return {
        "enabled": digest_enabled(),
        "hour_hkt": _digest_hour(),
        "health_url": resolve_health_url(),
        "latest": await latest_digest_summary(),
    }

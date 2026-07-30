"""
Observability 告警分派。

預設 skipped。OBS_ALERTING_ENABLED + 通道開 → logged；
再加 OBS_ALERT_EMAIL_SEND=true → 寄中文電郵（async 背景）。
不改 email_service 主路；未掛 main 則正式站仍不受影響。
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from app.services.observability.channels import (
    AlertChannel,
    channel_enabled,
    master_enabled,
    ops_email,
)

logger = logging.getLogger("observability.alert")


def _email_send_enabled() -> bool:
    return os.getenv("OBS_ALERT_EMAIL_SEND", "false").lower() == "true"


def emit_alert(
    channel: AlertChannel,
    title: str,
    *,
    detail: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    payload: dict[str, Any] = {
        "ts": ts,
        "channel": channel.value,
        "title": title,
        "detail": detail,
        "ops_email": ops_email(),
        "extra": extra or {},
        "master_enabled": master_enabled(),
        "channel_enabled": channel_enabled(channel),
        "email_send": _email_send_enabled(),
    }
    if not payload["master_enabled"] or not payload["channel_enabled"]:
        payload["status"] = "skipped"
        logger.info("OBS_ALERT_SKIPPED %s", payload)
        return payload

    payload["status"] = "logged"
    logger.warning("OBS_ALERT_LOGGED %s", payload)

    if payload["email_send"]:
        try:
            from app.services.observability.alert_mailer import send_alert_email

            async def _run() -> None:
                ok = await send_alert_email(
                    channel, title, detail=detail, extra=extra
                )
                logger.info("OBS_ALERT_EMAIL ok=%s", ok)

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_run())
                payload["status"] = "email_queued"
            except RuntimeError:
                ok = asyncio.run(
                    send_alert_email(
                        channel, title, detail=detail, extra=extra
                    )
                )
                payload["status"] = "email_sent" if ok else "email_failed"
        except Exception as exc:  # noqa: BLE001 — 告警不可拖垮主路
            logger.error("OBS_ALERT_EMAIL error: %s", exc)
            payload["status"] = "email_error"
    return payload


def emit_crash(title: str, detail: str = "", **extra: Any) -> dict[str, Any]:
    return emit_alert(AlertChannel.CRASH, title, detail=detail, extra=extra or None)


def emit_cost(title: str, detail: str = "", **extra: Any) -> dict[str, Any]:
    return emit_alert(AlertChannel.COST, title, detail=detail, extra=extra or None)


def emit_customer(title: str, detail: str = "", **extra: Any) -> dict[str, Any]:
    return emit_alert(
        AlertChannel.CUSTOMER, title, detail=detail, extra=extra or None
    )

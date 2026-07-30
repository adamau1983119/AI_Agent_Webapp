"""
24h Watchdog + 初期每日營運報告（綠燈也寄）。
OBS_WATCHDOG_ENABLED / OBS_DAILY_DIGEST_ENABLED 分別閘控。
"""
from __future__ import annotations

import asyncio
import logging
import os

from app.services.observability.daily_digest import (
    digest_enabled,
    maybe_send_daily_digest,
)
from app.services.observability.ops_agent import run_ops_agent_once

logger = logging.getLogger("observability.watchdog")


def _interval_sec() -> int:
    try:
        return max(60, int(os.getenv("OBS_WATCHDOG_INTERVAL_SEC", "300")))
    except ValueError:
        return 300


def watchdog_enabled() -> bool:
    return os.getenv("OBS_WATCHDOG_ENABLED", "false").lower() == "true"


async def watchdog_loop() -> None:
    if not watchdog_enabled() and not digest_enabled():
        logger.info("WATCHDOG_SKIP disabled")
        return
    logger.info(
        "WATCHDOG_START interval=%ss digest=%s",
        _interval_sec(),
        digest_enabled(),
    )
    while True:
        try:
            if watchdog_enabled():
                out = await asyncio.to_thread(run_ops_agent_once)
                logger.info(
                    "WATCHDOG_TICK light=%s status=%s",
                    out.get("traffic_light"),
                    out.get("status"),
                )
            if digest_enabled():
                dig = await maybe_send_daily_digest()
                logger.info("DIGEST_TICK %s", dig.get("status"))
        except Exception as exc:  # noqa: BLE001
            logger.error("WATCHDOG_TICK_ERROR %s", exc)
        await asyncio.sleep(_interval_sec())

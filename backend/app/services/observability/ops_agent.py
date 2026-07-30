"""
Ops Agent：讀正式域 /health → 紅／綠燈；預設僅紅燈才寄信。
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from app.services.observability.alert_dispatcher import emit_cost, emit_crash
from app.services.observability.traffic_light import TrafficLight, evaluate_health

logger = logging.getLogger("observability.ops_agent")
DEFAULT_HEALTH = "https://api.ai-alterego.com/health"
_last_red_key = ""
_last_red_sent_at = 0.0


def fetch_health(url: str, timeout: float = 20.0) -> dict[str, Any]:
    with urlopen(url, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read().decode("utf-8"))


def _only_on_red() -> bool:
    return os.getenv("OBS_ALERT_ONLY_ON_RED", "true").lower() == "true"


def _cooldown_sec() -> int:
    try:
        return max(60, int(os.getenv("OBS_ALERT_COOLDOWN_SEC", "3600")))
    except ValueError:
        return 3600


def _red_cooled(headline: str) -> bool:
    global _last_red_key, _last_red_sent_at
    now = time.time()
    if headline == _last_red_key and (now - _last_red_sent_at) < _cooldown_sec():
        return True
    return False


def _mark_red_sent(headline: str) -> None:
    global _last_red_key, _last_red_sent_at
    _last_red_key = headline
    _last_red_sent_at = time.time()


def run_ops_agent_once(*, health_url: str = DEFAULT_HEALTH) -> dict[str, Any]:
    err: str | None = None
    body: dict[str, Any] | None = None
    try:
        body = fetch_health(health_url)
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        err = f"無法讀取 {health_url}：{exc}"

    signal = evaluate_health(body, error=err)
    base: dict[str, Any] = {
        "traffic_light": signal.light.value,
        "headline": signal.headline,
        "verdict": (
            "有事・請立即處理"
            if signal.light is TrafficLight.RED
            else "沒事・系統正常"
        ),
        "health_url": health_url,
    }
    if signal.light is TrafficLight.GREEN and _only_on_red():
        out = {
            "status": "green_quiet",
            "channel": signal.channel_hint,
            "title": signal.headline,
            "detail": signal.detail,
            **base,
        }
        logger.info("OPS_AGENT_GREEN_QUIET")
        return out

    if signal.light is TrafficLight.RED and _red_cooled(signal.headline):
        return {
            "status": "red_cooldown",
            "channel": "crash",
            "title": signal.headline,
            "detail": signal.detail,
            **base,
        }

    kw = {k: str(v) for k, v in base.items()}
    if signal.light is TrafficLight.RED:
        result = emit_crash(signal.headline, detail=signal.detail, **kw)
        if result.get("status") in ("email_sent", "email_queued", "logged"):
            _mark_red_sent(signal.headline)
    else:
        result = emit_cost(signal.headline, detail=signal.detail, **kw)
    return {**result, **base}

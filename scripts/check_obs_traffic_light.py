#!/usr/bin/env python3
"""
驗證紅／綠燈：正式域應 green_quiet（異常才寄）；靜態列檔案行數。

  python scripts/check_obs_traffic_light.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MAX = 150
PYS = [
    BACKEND / "app/services/observability/traffic_light.py",
    BACKEND / "app/services/observability/ops_agent.py",
    BACKEND / "app/services/observability/ops_watchdog.py",
    BACKEND / "app/services/observability/alert_mailer.py",
]


def main() -> int:
    fails = 0
    for p in PYS:
        n = len(p.read_text(encoding="utf-8").splitlines())
        ok = n <= MAX
        print(f"{'PASS' if ok else 'FAIL'} | {p.name} lines={n}")
        fails += 0 if ok else 1

    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    os.environ["OBS_ALERT_ONLY_ON_RED"] = "true"
    os.environ.pop("OBS_ALERTING_ENABLED", None)
    os.environ.pop("OBS_ALERT_EMAIL_SEND", None)

    from app.services.observability.ops_agent import run_ops_agent_once
    from app.services.observability.traffic_light import (
        TrafficLight,
        evaluate_health,
        light_zh,
        verdict_zh,
    )

    sig = evaluate_health({"status": "healthy", "database": {"status": "connected"}})
    assert sig.light is TrafficLight.GREEN
    print(f"PASS | mock green 【{light_zh(sig.light)}】{verdict_zh(sig.light)}")

    sig_r = evaluate_health(None, error="連線逾時")
    assert sig_r.light is TrafficLight.RED
    print(f"PASS | mock red 【{light_zh(sig_r.light)}】{verdict_zh(sig_r.light)}")

    live = run_ops_agent_once()
    if live.get("traffic_light") == "green" and live.get("status") == "green_quiet":
        print("PASS | live formal domain green_quiet (no spam email)")
    elif live.get("traffic_light") == "red":
        print(f"PASS | live RED detected status={live.get('status')}")
    else:
        print(f"FAIL | unexpected live={live}")
        fails += 1

    if fails:
        print(f"FAIL | {fails}")
        return 1
    print("PASS | traffic light OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Observability Atom-1 靜態結案：檔案存在、行數 ≤150、三通道、emit 預設 skipped。

  python scripts/check_observability_static.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MAX_LINES = 150

FILES = [
    BACKEND / "app" / "config" / "observability_channels.json",
    BACKEND / "app" / "services" / "observability" / "channels.py",
    BACKEND / "app" / "services" / "observability" / "alert_dispatcher.py",
    BACKEND / "app" / "services" / "observability" / "alert_mailer.py",
    BACKEND / "app" / "services" / "observability" / "ops_agent.py",
    BACKEND / "app" / "services" / "observability" / "ops_watchdog.py",
    BACKEND / "app" / "services" / "observability" / "traffic_light.py",
    BACKEND / "app" / "services" / "observability" / "__init__.py",
    ROOT / "docs" / "v8_observability_alerting.md",
]


def _lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> int:
    fails = 0
    for path in FILES:
        if not path.is_file():
            print(f"FAIL | missing {path.relative_to(ROOT)}")
            fails += 1
            continue
        n = _lines(path)
        if path.suffix == ".py" and n > MAX_LINES:
            print(f"FAIL | {path.name} lines={n} > {MAX_LINES}")
            fails += 1
        else:
            print(f"PASS | {path.relative_to(ROOT)} lines={n}")

    sys.path.insert(0, str(BACKEND))
    os.environ.pop("OBS_ALERTING_ENABLED", None)
    os.environ.pop("OBS_ALERT_CRASH", None)

    from app.services.observability import AlertChannel, emit_crash
    from app.services.observability.channels import channel_specs, load_recipe

    recipe = load_recipe()
    for key in ("crash", "cost", "customer"):
        if key not in recipe["channels"]:
            print(f"FAIL | recipe missing channel {key}")
            fails += 1
        else:
            print(f"PASS | recipe.channel={key}")

    specs = channel_specs()
    if set(specs.keys()) != set(AlertChannel):
        print("FAIL | channel_specs mismatch enum")
        fails += 1
    else:
        print("PASS | channel_specs == AlertChannel")

    if recipe.get("safety", {}).get("mutate_email_service") is not False:
        print("FAIL | safety.mutate_email_service must be false")
        fails += 1
    else:
        print("PASS | safety.mutate_email_service=false")

    if recipe.get("safety", {}).get("gated_by_env") is not True:
        print("FAIL | safety.gated_by_env must be true")
        fails += 1
    else:
        print("PASS | safety.gated_by_env=true")

    out = emit_crash("static-check", detail="noop")
    if out.get("status") != "skipped":
        print(f"FAIL | default emit status={out.get('status')!r} want skipped")
        fails += 1
    else:
        print("PASS | emit_crash default skipped (prod-safe)")

    if fails:
        print(f"FAIL | {fails} checks")
        return 1
    print("PASS | observability static OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

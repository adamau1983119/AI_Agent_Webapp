#!/usr/bin/env python3
"""
唯讀閘：對照 collection_min_cost_recipe.json 列印 Variables，
並可檢查 /health cost_controls（不改任何 env／不觸發產卡）。

  python scripts/check_collection_min_cost.py
  python scripts/check_collection_min_cost.py --phase before
  python scripts/check_collection_min_cost.py --phase after \\
      --health https://api.ai-alterego.com/health
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "backend" / "app" / "config" / "collection_min_cost_recipe.json"


def _load() -> dict[str, Any]:
    return json.loads(RECIPE.read_text(encoding="utf-8"))


def _print_vars(recipe: dict[str, Any]) -> None:
    print("=== Railway Variables（最小成本 · 只開 collection）===")
    for k, v in recipe["railway_variables"].items():
        print(f"  {k}={v}")
    print("=== 勿動（leave_unchanged）===")
    for k in recipe["leave_unchanged"]:
        print(f"  {k}")
    dt5 = recipe["dt5"]
    print(
        f"=== DT-5 === {dt5['alert_type']} "
        f"threshold_cny={dt5['threshold_cny_recommended']} (platform alert)"
    )


def _fetch_health(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=20) as resp:  # noqa: S310 — 使用者指定 URL
        return json.loads(resp.read().decode("utf-8"))


def _check_phase(
    cc: dict[str, Any], expected: dict[str, Any], label: str
) -> int:
    fails = 0
    for key, want in expected.items():
        got = cc.get(key)
        ok = got is want
        mark = "PASS" if ok else "FAIL"
        print(f"{mark} | cost_controls.{key}={got!r} want={want!r} ({label})")
        if not ok:
            fails += 1
    return fails


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("before", "after", "print"),
        default="print",
        help="print=只列配方；before/after=對 /health 驗 cost_controls",
    )
    parser.add_argument(
        "--health",
        default="",
        help="例：https://api.ai-alterego.com/health",
    )
    args = parser.parse_args()
    recipe = _load()
    _print_vars(recipe)

    if args.phase == "print":
        print("PASS | recipe loaded (no health check)")
        return 0

    if not args.health:
        print("FAIL | --phase before|after 需要 --health URL")
        return 1

    try:
        body = _fetch_health(args.health)
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        print(f"FAIL | health fetch: {exc}")
        return 1

    cc = body.get("cost_controls") or {}
    key = (
        "health_cost_controls_expected_before"
        if args.phase == "before"
        else "health_cost_controls_expected_after"
    )
    fails = _check_phase(cc, recipe[key], args.phase)
    db = body.get("database")
    db_ok = db == "connected" or (
        isinstance(db, dict) and db.get("status") == "connected"
    )
    print(f"{'PASS' if db_ok else 'WARN'} | database={db!r}")
    if fails:
        print(f"FAIL | {fails} cost_controls mismatch")
        return 1
    print(f"PASS | phase={args.phase} cost_controls OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

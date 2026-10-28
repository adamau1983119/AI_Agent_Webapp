#!/usr/bin/env python3
"""Roll up week snapshots in [period-start, period-end]. Read-only JSON stdout.

  python scripts/marketing_period_rollup.py --period-start 2026-10-01 --period-end 2026-10-31
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import SCHEMA_VERSION, SNAP_COL, boot_backend  # noqa: E402

SUM_KEYS = (
    "external_new_users",
    "successful_generations",
    "email_subscribers_new",
    "ads_spend_hkd",
    "ads_clicks",
    "ads_impr",
    "ga4_sign_up",
    "ga4_generate_post",
    "ga4_purchase",
    "revenue_usd",
)


async def _rollup(start: str, end: str) -> dict:
    boot_backend()
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()
    cur = db[SNAP_COL].find(
        {
            "period_type": "week",
            "period_start": {"$gte": start},
            "period_end": {"$lte": end},
        },
        {"_id": 0},
    )
    weeks = await cur.to_list(200)
    weeks.sort(key=lambda w: w.get("period_start") or "")
    sums = {k: 0.0 for k in SUM_KEYS}
    for w in weeks:
        core = w.get("core") or {}
        for k in SUM_KEYS:
            v = core.get(k)
            if isinstance(v, (int, float)):
                sums[k] += v
    last = weeks[-1] if weeks else {}
    last_core = last.get("core") or {}
    out = {
        "schema_version": SCHEMA_VERSION,
        "period_type": "rollup",
        "period_start": start,
        "period_end": end,
        "weeks_included": len(weeks),
        "rolled_up_from": [w.get("period_start") for w in weeks],
        "core": {
            **sums,
            "external_total_users": last_core.get("external_total_users"),
            "email_subscribers_total": last_core.get("email_subscribers_total"),
            "active_users_30d": last_core.get("active_users_30d"),
            "valid_members": last_core.get("valid_members"),
        },
        "source_notes": "sum of week cores in range; totals/active from last week doc",
    }
    await close_mongo_connection()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Roll up marketing week snapshots")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    args = p.parse_args()
    print(json.dumps(asyncio.run(_rollup(args.period_start, args.period_end)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

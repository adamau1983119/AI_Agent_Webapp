#!/usr/bin/env python3
"""Export week snapshot(s) to CSV for Google Sheet / Looker. No PII.

  python scripts/marketing_period_export_sheet.py --period-start 2026-10-20 --out docs/evidence/marketing/ops_weekly.csv
  python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import SCHEMA_VERSION, SNAP_COL, boot_backend  # noqa: E402

COLS = (
    "period_start",
    "period_end",
    "schema_version",
    "provisional",
    "traffic_light",
    "external_new_users",
    "external_total_users",
    "valid_members",
    "active_users_30d",
    "successful_generations",
    "email_subscribers_total",
    "email_subscribers_new",
    "ads_spend_hkd",
    "ads_clicks",
    "ads_impr",
    "ga4_sign_up",
    "ga4_generate_post",
    "ga4_purchase",
    "revenue_usd",
    "revenue_hkd_equiv",
    "founder_noise",
)


def _row(doc: dict) -> dict:
    core = doc.get("core") or {}
    out = {k: "" for k in COLS}
    out["period_start"] = doc.get("period_start") or ""
    out["period_end"] = doc.get("period_end") or ""
    out["schema_version"] = doc.get("schema_version", SCHEMA_VERSION)
    out["provisional"] = doc.get("provisional")
    for k in COLS:
        if k in ("period_start", "period_end", "schema_version", "provisional"):
            continue
        if k in core:
            out[k] = core.get(k)
        elif k in doc:
            out[k] = doc.get(k)
    return out


async def _load(start: str | None, all_weeks: bool) -> list[dict]:
    boot_backend()
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()
    q: dict = {"period_type": "week"}
    if start and not all_weeks:
        q["period_start"] = start
    cur = db[SNAP_COL].find(q, {"_id": 0})
    weeks = await cur.to_list(500)
    weeks.sort(key=lambda w: w.get("period_start") or "")
    await close_mongo_connection()
    return weeks


def main() -> int:
    p = argparse.ArgumentParser(description="Export marketing snapshots to CSV for Sheet/Looker")
    p.add_argument("--period-start", help="Single week start YYYY-MM-DD")
    p.add_argument("--all", action="store_true", help="All week snapshots")
    p.add_argument("--out", required=True, help="CSV path")
    args = p.parse_args()
    if not args.all and not args.period_start:
        print("need --period-start or --all", file=sys.stderr)
        return 2
    weeks = asyncio.run(_load(args.period_start, args.all))
    path = Path(args.out)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(COLS))
        w.writeheader()
        for doc in weeks:
            w.writerow(_row(doc))
    print(f"wrote {len(weeks)} row(s) → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

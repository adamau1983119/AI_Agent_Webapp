#!/usr/bin/env python3
"""Funnel: external signup → first successful compose. No email lists.

  python scripts/marketing_period_funnel_signup_compose.py --period-start 2026-10-20 --period-end 2026-10-26
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import (  # noqa: E402
    GEN_ACTIONS,
    SCHEMA_VERSION,
    as_utc_naive,
    boot_backend,
    filter_external_users,
    hkt_bounds,
    parse_ymd,
    staff_emails,
)


async def _run(start_s: str, end_s: str) -> dict:
    boot_backend()
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    start_d, end_d = parse_ymd(start_s), parse_ymd(end_s)
    t0, t1 = hkt_bounds(start_d, end_d)
    await connect_to_mongo()
    db = await get_database()
    staff = staff_emails()
    users = await db.users.find({}, {"email": 1, "id": 1, "created_at": 1}).to_list(50000)
    ext = filter_external_users(users, staff)
    by_id = {u["id"]: u for u in ext if u.get("id")}
    new_ids = {
        u["id"]
        for u in ext
        if (c := as_utc_naive(u.get("created_at"))) and t0 <= c <= t1 and u.get("id")
    }
    gens = await db.credit_ledger.find(
        {"action": {"$in": list(GEN_ACTIONS)}},
        {"user_id": 1, "created_at": 1, "action": 1},
    ).to_list(100000)
    first_compose: dict[str, object] = {}
    for g in gens:
        uid = g.get("user_id")
        if uid not in by_id:
            continue
        ts = as_utc_naive(g.get("created_at"))
        if ts is None:
            continue
        prev = first_compose.get(uid)
        if prev is None or ts < prev:  # type: ignore[operator]
            first_compose[uid] = ts
    composed_ever = set(first_compose)
    composed_in_period = {
        uid
        for uid, ts in first_compose.items()
        if t0 <= ts <= t1  # type: ignore[operator]
    }
    new_with_compose = new_ids & composed_ever
    new_with_compose_in_period = new_ids & composed_in_period
    lag_hours: list[float] = []
    for uid in new_with_compose:
        u = by_id[uid]
        c0 = as_utc_naive(u.get("created_at"))
        c1 = first_compose.get(uid)
        if c0 and c1:
            lag_hours.append((c1 - c0).total_seconds() / 3600.0)  # type: ignore[operator]
    lag_hours.sort()
    mid = lag_hours[len(lag_hours) // 2] if lag_hours else None
    out = {
        "schema_version": SCHEMA_VERSION,
        "period_start": start_s,
        "period_end": end_s,
        "funnel": {
            "external_total": len(ext),
            "external_new_in_period": len(new_ids),
            "new_with_any_compose": len(new_with_compose),
            "new_with_compose_in_period": len(new_with_compose_in_period),
            "new_without_compose": len(new_ids - composed_ever),
            "external_ever_composed": len(composed_ever),
            "median_hours_signup_to_first_compose": mid,
        },
        "breakpoint": (
            "signup_to_first_compose"
            if len(new_ids) and len(new_with_compose) < len(new_ids)
            else "none_or_n_a"
        ),
        "source_notes": (
            "external only; compose=ae_compose|ae_compose_part; no PII; "
            "GA4 sign_up ≠ Mongo new"
        ),
    }
    await close_mongo_connection()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Signup→compose funnel (external, no PII)")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    args = p.parse_args()
    print(json.dumps(asyncio.run(_run(args.period_start, args.period_end)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

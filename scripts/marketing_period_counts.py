#!/usr/bin/env python3
"""Read-only marketing period counts (Mongo). JSON stdout. No PII lists.

  python scripts/marketing_period_counts.py --period-start 2026-10-20 --period-end 2026-10-26
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import timedelta
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
    prev_week,
    staff_emails,
)


async def _counts(start_s: str, end_s: str) -> dict:
    boot_backend()
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    start_d, end_d = parse_ymd(start_s), parse_ymd(end_s)
    t0, t1 = hkt_bounds(start_d, end_d)
    await connect_to_mongo()
    db = await get_database()
    staff = staff_emails()
    users = await db.users.find({}, {"email": 1, "id": 1, "created_at": 1, "last_login_at": 1, "email_verified": 1, "weekly_mail_opt_out": 1}).to_list(50000)
    ext = filter_external_users(users, staff)
    by_id = {u.get("id"): u for u in ext if u.get("id")}

    def in_period(dt) -> bool:
        x = as_utc_naive(dt)
        return x is not None and t0 <= x <= t1

    new_u = [u for u in ext if in_period(u.get("created_at"))]
    total = len(ext)
    since_30 = t1 - timedelta(days=30)
    gen = await db.credit_ledger.find(
        {"action": {"$in": list(GEN_ACTIONS)}, "timestamp": {"$gte": t0, "$lte": t1}, "amount": {"$lt": 0}}
    ).to_list(20000)
    debit = await db.credit_ledger.find(
        {"timestamp": {"$gte": t0, "$lte": t1}, "amount": {"$lt": 0}}
    ).to_list(50000)
    gen_uids = {g["user_id"] for g in gen if g.get("user_id") in by_id}
    debit_uids = {d["user_id"] for d in debit if d.get("user_id") in by_id}
    valid = gen_uids & debit_uids
    gen_all = await db.credit_ledger.find(
        {"action": {"$in": list(GEN_ACTIONS)}, "timestamp": {"$gte": since_30, "$lte": t1}, "amount": {"$lt": 0}}
    ).to_list(50000)
    gen30 = {g["user_id"] for g in gen_all if g.get("user_id") in by_id}
    active30 = {
        uid
        for uid, u in by_id.items()
        if (as_utc_naive(u.get("last_login_at")) and as_utc_naive(u.get("last_login_at")) >= since_30)
        or uid in gen30
    }
    subs = [
        u
        for u in ext
        if u.get("email_verified") and u.get("weekly_mail_opt_out") is not True
    ]
    subs_new = [u for u in subs if in_period(u.get("created_at"))]
    ps, pe = prev_week(start_d, end_d)
    out = {
        "schema_version": SCHEMA_VERSION,
        "period_type": "week",
        "period_start": start_s,
        "period_end": end_s,
        "prev_week": {"period_start": ps.isoformat(), "period_end": pe.isoformat()},
        "core": {
            "external_new_users": len(new_u),
            "external_total_users": total,
            "valid_members": len(valid),
            "active_users_30d": len(active30),
            "successful_generations": len([g for g in gen if g.get("user_id") in by_id]),
            "email_subscribers_total": len(subs),
            "email_subscribers_new": len(subs_new),
        },
        "source_notes": "Mongo read-only; GEN=ae_compose|ae_compose_part; email=verified & not weekly_mail_opt_out; no PII",
        "handfill_hints": ["ads_spend_hkd", "ads_clicks", "ads_impr", "ga4_sign_up", "ga4_generate_post", "ga4_purchase", "revenue_usd", "founder_noise", "provisional", "traffic_light"],
    }
    await close_mongo_connection()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Marketing period counts (Mongo read-only)")
    p.add_argument("--period-start", required=True, help="YYYY-MM-DD HKT")
    p.add_argument("--period-end", required=True, help="YYYY-MM-DD HKT inclusive")
    args = p.parse_args()
    print(json.dumps(asyncio.run(_counts(args.period_start, args.period_end)), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

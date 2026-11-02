"""Shared Sheet row shape for export CSV + push Sheets API. No PII."""
from __future__ import annotations

from typing import Any

from marketing_period_lib import SCHEMA_VERSION, SNAP_COL, boot_backend

SHEET_COLS: tuple[str, ...] = (
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


def snapshot_to_row(doc: dict[str, Any]) -> dict[str, Any]:
    core = doc.get("core") or {}
    out: dict[str, Any] = {k: "" for k in SHEET_COLS}
    out["period_start"] = doc.get("period_start") or ""
    out["period_end"] = doc.get("period_end") or ""
    out["schema_version"] = doc.get("schema_version", SCHEMA_VERSION)
    out["provisional"] = doc.get("provisional")
    for k in SHEET_COLS:
        if k in ("period_start", "period_end", "schema_version", "provisional"):
            continue
        if k in core:
            out[k] = core.get(k)
        elif k in doc:
            out[k] = doc.get(k)
    return out


def row_values(row: dict[str, Any]) -> list[Any]:
    return [row.get(k, "") for k in SHEET_COLS]


async def load_week_snapshots(start: str | None, all_weeks: bool) -> list[dict]:
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

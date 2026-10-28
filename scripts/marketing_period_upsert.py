#!/usr/bin/env python3
"""Upsert marketing_period_snapshots. Requires --env production. No PII.

  python scripts/marketing_period_upsert.py --env production --file draft.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import SCHEMA_VERSION, SNAP_COL, boot_backend  # noqa: E402

REQUIRED = ("period_type", "period_start", "period_end", "core")


def _load(path: str | None) -> dict:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise SystemExit("draft must be a JSON object")
    for k in REQUIRED:
        if k not in doc:
            raise SystemExit(f"missing field: {k}")
    if doc.get("schema_version") not in (None, SCHEMA_VERSION, 1):
        raise SystemExit(f"unsupported schema_version (want {SCHEMA_VERSION})")
    doc["schema_version"] = SCHEMA_VERSION
    # Strip accidental PII keys
    for bad in ("emails", "email_list", "users", "user_ids"):
        doc.pop(bad, None)
    return doc


async def _upsert(doc: dict) -> dict:
    boot_backend()
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()
    now = datetime.utcnow()
    doc["updated_at"] = now
    doc.setdefault("created_at", now)
    key = {"period_type": doc["period_type"], "period_start": doc["period_start"]}
    await db[SNAP_COL].update_one(key, {"$set": doc}, upsert=True)
    saved = await db[SNAP_COL].find_one(key, {"_id": 0})
    await close_mongo_connection()
    return saved or doc


def main() -> int:
    p = argparse.ArgumentParser(description="Upsert marketing_period_snapshots")
    p.add_argument("--env", required=True, choices=["production"], help="Must be production")
    p.add_argument("--file", help="JSON draft path (default stdin)")
    args = p.parse_args()
    if args.env != "production":
        print("refusing non-production env", file=sys.stderr)
        return 2
    doc = _load(args.file)
    out = asyncio.run(_upsert(doc))
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

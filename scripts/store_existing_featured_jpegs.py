"""Compress existing featured image rows into image_jpegs, keyed by row id."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)
os.environ.setdefault("ENVIRONMENT", "development")

from app.database import close_mongo_connection, connect_to_mongo, get_database
from app.services.images.jpeg_store import persist_source_jpeg


async def main() -> None:
    await connect_to_mongo()
    db = await get_database()
    rows = await db.images.find(
        {"topic_id": {"$regex": r"^topic_(fashion|food|trend)_2026100"}},
        {"id": 1, "url": 1, "topic_id": 1},
    ).to_list(length=80)
    rows.sort(key=lambda row: 0 if "20261004160323_3" in str(row.get("topic_id") or "") else 1)
    ok = 0
    skipped = 0
    for row in rows:
        image_id = str(row.get("id") or "")
        if await persist_source_jpeg(image_id, row.get("url") or ""):
            ok += 1
            print("ok", image_id)
        else:
            skipped += 1
            print("skip", image_id)
    print("done", ok, skipped, "of", len(rows))
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

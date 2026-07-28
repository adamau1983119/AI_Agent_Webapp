#!/usr/bin/env python3
"""手動觸發 Alter Ego 週 batch（PD-AE2-01 · 開發／受控環境）。"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))


async def _main() -> int:
    from app.database import connect_to_mongo, close_mongo_connection
    from app.services.alter_ego_weekly_batch import alter_ego_weekly_batch

    await connect_to_mongo()
    try:
        result = await alter_ego_weekly_batch.run_all()
        print(result)
        return 0
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))

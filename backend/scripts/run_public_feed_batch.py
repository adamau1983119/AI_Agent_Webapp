#!/usr/bin/env python3
"""
手動觸發 Discover 公共主題牆單批（dev only）。
用法（backend 目錄）: python -m scripts.run_public_feed_batch
"""
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    from app.database import connect_to_mongo, close_mongo_connection
    from app.services.cache_service import cache_service
    from app.services.public_feed.public_feed_pipeline import run_public_feed_batch

    await connect_to_mongo()
    await cache_service.connect()
    try:
        stats = await run_public_feed_batch()
        print("public_feed_batch:", stats)
    finally:
        await cache_service.disconnect()
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

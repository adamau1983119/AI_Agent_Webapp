#!/usr/bin/env python3
"""
PF-B Mongo 證據（PD-B / CD-B-1）：批次後 topic_translations 含 zh-TW + ja。
用法: python scripts/check_pf_b_mongo.py
（會 chdir 至 backend 以載入 .env）
"""
from __future__ import annotations

import asyncio
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))


async def main() -> int:
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()

    topics = (
        await db.topics.find({"public_feed_flag": True})
        .sort("created_at", -1)
        .limit(10)
        .to_list(10)
    )
    if not topics:
        print("FAIL | no public_feed topics in Mongo")
        await close_mongo_connection()
        return 1

    topic_ids = [t["id"] for t in topics if t.get("id")]
    rows = await db.topic_translations.find({"topic_id": {"$in": topic_ids}}).to_list(200)
    by_topic: dict[str, list] = defaultdict(list)
    for row in rows:
        by_topic[row["topic_id"]].append(row)

    passed = 0
    checks = 0
    print("=== PF-B Mongo evidence (latest public_feed topics) ===")
    for topic in topics[:5]:
        tid = topic.get("id", "")
        langs = sorted({r.get("lang") for r in by_topic[tid]})
        both = "zh-TW" in langs and "ja" in langs
        checks += 1
        if both:
            passed += 1
        flash_len = len(topic.get("summary_flash") or "")
        print(
            f"{'PASS' if both else 'FAIL'} | {tid} | langs={langs} | "
            f"source_country={topic.get('source_country')!r} | "
            f"is_trend_alert={topic.get('is_trend_alert')} | summary_flash_len={flash_len}"
        )
        for lang in ("zh-TW", "ja"):
            match = next((r for r in by_topic[tid] if r.get("lang") == lang), None)
            if match:
                title = (match.get("cached_title") or "")[:40]
                print(f"       [{lang}] type={match.get('type')} provider={match.get('provider')} title={title!r}")

    print("---")
    print(f"{passed}/{checks} cards with zh-TW + ja topic_translations")
    ok = passed >= 1 and passed == checks
    if ok:
        print("PF-B Mongo gate: PASS (CD-B-1 data layer)")
    else:
        print("PF-B Mongo gate: FAIL — run: cd backend && python -m scripts.run_public_feed_batch")
    await close_mongo_connection()
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

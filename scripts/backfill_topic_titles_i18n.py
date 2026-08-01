#!/usr/bin/env python3
"""Backfill recent topics: honest display_language + titles_i18n via finalize atom."""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


async def main() -> int:
    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    os.environ.setdefault("ENABLE_TOPIC_I18N_PREFETCH", "true")

    from app.database import close_mongo_connection, connect_to_mongo, get_database
    from app.services.automation.topic_i18n_prefetch import finalize_topic_languages

    await connect_to_mongo()
    db = await get_database()
    since = datetime.now(timezone.utc) - timedelta(days=2)
    cursor = db.topics.find(
        {"$or": [{"generated_at": {"$gte": since}}, {"created_at": {"$gte": since}}]}
    ).limit(60)

    n_ok = 0
    async for doc in cursor:
        title = str(doc.get("title") or "")
        source = str(doc.get("original_title") or title)
        patch = {
            "title": title,
            "description": str(doc.get("description") or ""),
            "display_language": doc.get("display_language"),
            "original_title": source,
            "titles_i18n": dict(doc.get("titles_i18n") or {}),
            "description_i18n": dict(doc.get("description_i18n") or {}),
        }
        await finalize_topic_languages(
            patch,
            source_title=source,
            requested_lang=str(doc.get("display_language") or "zh-TW"),
            translation_applied=False,
        )
        upd = {
            "display_language": patch["display_language"],
            "titles_i18n": patch.get("titles_i18n") or {},
            "description_i18n": patch.get("description_i18n") or {},
        }
        if not doc.get("original_title"):
            upd["original_title"] = source
        await db.topics.update_one({"_id": doc["_id"]}, {"$set": upd})
        n_ok += 1
        keys = list(upd["titles_i18n"])
        print(
            f"OK | {doc.get('id') or doc['_id']} lang={upd['display_language']} "
            f"titles={keys} desc={list(upd['description_i18n'])}"
        )

    await close_mongo_connection()
    print(f"PASS | updated={n_ok}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

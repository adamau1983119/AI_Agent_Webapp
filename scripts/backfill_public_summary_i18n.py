"""
一次性：為現有 public_feed 卡回填 summary_i18n（zh-TW／ja／en）+ translations
用法（於 backend 目錄）:
  python ..\\scripts\\backfill_public_summary_i18n.py
"""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.models.topic_translation import TranslationType
from app.services.public_feed.deepl_title import translate_public_summary_with_meta
from app.services.public_feed.public_feed_cache import refresh_feed_cache
from app.services.repositories.topic_translation_repository import TopicTranslationRepository


async def main() -> None:
    await connect_to_mongo()
    db = await get_database()
    topics = await db.topics.find(
        {"public_feed_flag": True},
        {
            "id": 1,
            "title": 1,
            "summary_flash": 1,
            "description": 1,
            "sources": 1,
            "titles_i18n": 1,
            "summary_i18n": 1,
            "preview_images": 1,
            "category": 1,
            "source": 1,
            "source_lang": 1,
            "created_at": 1,
            "generated_at": 1,
            "original_title": 1,
        },
    ).to_list(length=50)
    print(f"found {len(topics)} public feed topics")
    trans_repo = TopicTranslationRepository()
    await trans_repo.ensure_indexes()

    for t in topics:
        tid = t.get("id")
        summary = (t.get("summary_flash") or t.get("description") or "").strip()
        title_en = (t.get("title") or t.get("original_title") or "").strip()
        snippet = ""
        sources = t.get("sources") or []
        if sources and isinstance(sources[0], dict):
            snippet = (sources[0].get("title") or "")[:200]
        en_hint = f"{title_en}. {snippet}".strip()
        if not summary and not en_hint:
            print(f"skip {tid}: empty")
            continue

        summary_zh, p_zh = await translate_public_summary_with_meta(
            summary, "zh-TW", en_hint=en_hint
        )
        summary_ja, p_ja = await translate_public_summary_with_meta(
            summary, "ja", en_hint=en_hint
        )
        summary_en, p_en = await translate_public_summary_with_meta(
            summary, "en", en_hint=en_hint
        )
        i18n = {"zh-TW": summary_zh, "ja": summary_ja, "en": summary_en}
        await db.topics.update_one({"id": tid}, {"$set": {"summary_i18n": i18n}})
        t["summary_i18n"] = i18n
        for lang, body, provider, title_default in (
            ("zh-TW", summary_zh, p_zh, title_en),
            ("ja", summary_ja, p_ja, title_en),
            ("en", summary_en, p_en, title_en),
        ):
            existing = await trans_repo.get_translation(tid, lang, TranslationType.STANDARD)
            title = (existing or {}).get("cached_title") or title_default
            if lang == "en":
                title = title_en
            await trans_repo.upsert_translation({
                "topic_id": tid,
                "lang": lang,
                "type": TranslationType.STANDARD,
                "cached_title": str(title)[:200],
                "cached_content": (body or "")[:400] or None,
                "provider": provider,
            })
        print(f"ok {tid} zh={p_zh} ja={p_ja} en={p_en}")
        print(f"  en[:80]={summary_en[:80]!r}")

    await refresh_feed_cache(topics)
    print("cache refreshed")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

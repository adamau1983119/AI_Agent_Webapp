"""Re-extract today's broken public fashion cards. Not a translation-core change."""
from __future__ import annotations

import asyncio
import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)
os.environ.setdefault("ENVIRONMENT", "development")

from app.database import close_mongo_connection, connect_to_mongo
from app.models.image import ImageSource, ImageType
from app.services.automation.topic_post_scan import apply_scan_to_source
from app.services.repositories.image_repository import ImageRepository
from app.services.repositories.topic_repository import TopicRepository
from app.services.translation.source_article_translator import resolve_source_article_translation
from app.utils.article_extract_quality import body_is_storable, looks_like_toc
from app.utils.article_extractor import ArticleExtractor

TOPIC_IDS = []


def _urls(info: dict) -> list[str]:
    out: list[str] = []
    for u in info.get("images") or []:
        if isinstance(u, str) and u.startswith("http") and u not in out:
            out.append(u)
        if len(out) >= 4:
            break
    return out


async def repair_one(tid: str, extractor: ArticleExtractor, topics: TopicRepository, images: ImageRepository) -> None:
    topic = await topics.get_topic_by_id(tid)
    if not topic:
        print("MISSING", tid)
        return
    sources = topic.get("sources") or [{}]
    url = (sources[0] or {}).get("url") or ""
    print("====", tid, url)
    info = await extractor.extract_article_info(url)
    body = (info.get("original_content") or "").strip()
    pics = _urls(info)
    print("extract", len(body), "imgs", len(pics), "ok", info.get("success"))
    if not body_is_storable(body):
        print("SKIP_NOT_STORABLE", len(body))
        return
    sources[0]["original_content"] = body[:8000]
    sources[0]["images"] = pics or sources[0].get("images") or []
    if info.get("language"):
        sources[0]["language"] = info["language"]
    scan = apply_scan_to_source(sources[0])
    topic["sources"] = sources
    topic["content_clean"] = scan.get("content_clean") or body
    topic["source_content_i18n"] = {}
    topic["translated_source_content"] = ""
    patch = {
        "sources": sources,
        "content_clean": topic["content_clean"],
        "source_content_i18n": {},
        "translated_source_content": "",
    }
    if pics and not (topic.get("preview_images") or []):
        patch["preview_images"] = pics
        existing = await images.get_images_by_topic_id(tid)
        if not existing:
            now = datetime.utcnow()
            for i, img_url in enumerate(pics):
                hid = hashlib.md5(img_url.encode()).hexdigest()[:10]
                image_id = f"{tid}_repair_{hid}"
                await images.create_image(
                    {
                        "id": image_id,
                        "topic_id": tid,
                        "url": img_url,
                        "source": ImageSource.SOURCE_ARTICLE.value,
                        "image_type": ImageType.SOURCE.value,
                        "order": i,
                        "fetched_at": now,
                    }
                )
                from app.services.images.jpeg_store import persist_source_jpeg

                await persist_source_jpeg(image_id, img_url)
    await topics.update_topic(tid, patch)
    zh = await resolve_source_article_translation(topic, "zh-TW", save_cache=True, on_demand=True)
    print("zh_len", len(zh or ""), "head", (zh or "")[:90].replace("\n", " "))


async def main() -> None:
    await connect_to_mongo()
    from app.database import get_database

    db = await get_database()
    rows = await db.topics.find(
        {"category": {"$in": ["fashion", "food", "trend"]}},
        {"id": 1, "sources": 1, "preview_images": 1, "generated_at": 1},
    ).sort("generated_at", -1).limit(40).to_list(40)
    ids = []
    for t in rows:
        src = (t.get("sources") or [{}])[0] or {}
        oc = src.get("original_content") or ""
        if len(oc) < 400 or looks_like_toc(oc):
            ids.append(t.get("id"))
    print("WEAK", len(ids))
    extractor = ArticleExtractor()
    topics = TopicRepository()
    images = ImageRepository()
    for tid in ids:
        if not tid:
            continue
        await repair_one(tid, extractor, topics, images)
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

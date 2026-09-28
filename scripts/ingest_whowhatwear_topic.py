"""
Real ingest: Who What Wear URL → extract (HTTP/RSS-quality body+images) → Mongo topic.
No canned LLM sample. Run: PYTHONPATH=backend python scripts/ingest_whowhatwear_topic.py
"""
from __future__ import annotations

import asyncio
import hashlib
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

# Ensure Settings loads backend/.env (same DB as uvicorn)
import os

os.chdir(BACKEND)
if (BACKEND / ".env").exists():
    os.environ.setdefault("ENVIRONMENT", "development")

from app.database import connect_to_mongo, close_mongo_connection
from app.models.image import ImageSource, ImageType
from app.models.topic import Category, Status
from app.services.repositories.image_repository import ImageRepository
from app.services.repositories.topic_repository import TopicRepository
from app.utils.article_extractor import ArticleExtractor
from app.utils.logger import log_cost_event

WWW_URL = (
    "https://www.whowhatwear.com/fashion/celebrity/"
    "tom-bateman-the-love-hypothesis-interview-2026"
)
TOPIC_ID = "www_tom_bateman_love_hypothesis_20260918"


def _pick_images(urls: list[str], cap: int = 4) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    # Prefer Future CDN article photos only (skip trackers / logos)
    ranked = sorted(
        urls,
        key=lambda u: (0 if "cdn.mos.cms.futurecdn.net" in (u or "") else 1, len(u or "")),
    )
    for u in ranked:
        if not u or not u.startswith("http"):
            continue
        low = u.lower()
        if "futurecdn.net" not in low:
            continue
        if any(
            x in low
            for x in (
                "logo",
                "favicon",
                "sprite",
                "flexiimages",
                "scorecard",
                "analytics",
                ".svg",
                ".gif",
                ".png",
            )
        ):
            continue
        if not any(low.split("?")[0].endswith(ext) for ext in (".jpg", ".jpeg", ".webp")):
            continue
        key = u.split("?")[0]
        # collapse size variants: id-2000-80.jpg → id
        base = key.rsplit("/", 1)[-1]
        stem = base.split("-")[0] if "-" in base else base.split(".")[0]
        if stem in seen:
            continue
        seen.add(stem)
        # prefer mid size if available later; keep first unique stem
        out.append(u)
        if len(out) >= cap:
            break
    return out


async def main() -> None:
    await connect_to_mongo()
    topic_repo = TopicRepository()
    image_repo = ImageRepository()
    extractor = ArticleExtractor()

    existing = await topic_repo.get_topic_by_id(TOPIC_ID)
    if existing and "--force" not in sys.argv:
        print(f"TOPIC_EXISTS {TOPIC_ID}")
        imgs = await image_repo.get_images_by_topic_id(TOPIC_ID)
        print(f"IMAGES {len(imgs)}")
        for im in imgs[:8]:
            print(" ", im.get("id"), (im.get("url") or "")[:90])
        print("Re-run with --force to replace")
        await close_mongo_connection()
        return

    if existing and "--force" in sys.argv:
        for im in await image_repo.get_images_by_topic_id(TOPIC_ID):
            try:
                await image_repo.delete_image(im["id"])
            except Exception:
                pass
        try:
            await topic_repo.hard_delete_topic(TOPIC_ID)
        except Exception as e:
            print("DELETE_TOPIC", e)

    info = await extractor.extract_article_info(WWW_URL)
    # Supplement: scrape futurecdn JPEGs from raw HTML (same page, not canned placeholders)
    try:
        import httpx
        import re

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            html = (await client.get(WWW_URL, headers=extractor.headers)).text
        extra = re.findall(
            r"https://cdn\.mos\.cms\.futurecdn\.net/[A-Za-z0-9_-]+\.(?:jpg|jpeg|webp)",
            html,
            flags=re.I,
        )
        merged = list(info.get("images") or []) + extra
        info["images"] = list(dict.fromkeys(merged))
    except Exception as e:
        print("HTML_SUPPLEMENT", e)

    log_cost_event(
        "TOPIC_IMAGE_EXTRACT",
        success=bool(info.get("success")),
        image_count=len(info.get("images") or []),
        body_len=len((info.get("original_content") or "")),
        url=WWW_URL[:120],
    )
    if not info.get("success"):
        print("EXTRACT_FAIL", info.get("error"))
        await close_mongo_connection()
        sys.exit(1)

    body = (info.get("original_content") or "").strip()
    images = _pick_images(list(info.get("images") or []), 4)
    if not images:
        print("EXTRACT_NO_IMAGES")
        await close_mongo_connection()
        sys.exit(1)

    title = "Tom Bateman on Favorite Rom-Coms, Lili Reinhart, and Making TikToks"
    summary = body[:400] if body else title
    now = datetime.utcnow()

    topic_data = {
        "id": TOPIC_ID,
        "title": title,
        "original_title": title,
        "category": Category.FASHION.value if hasattr(Category.FASHION, "value") else "fashion",
        "status": Status.PENDING.value if hasattr(Status.PENDING, "value") else "pending",
        "description": summary,
        "summary_flash": summary[:280],
        "summaryFlash": summary[:280],
        "source": "Who What Wear",
        "sources": [
            {
                "name": "Who What Wear",
                "url": WWW_URL,
                "type": "rss_article",
                "images": images,
                "original_content": body[:20000],
                "language": info.get("language") or "en",
                "verified": True,
                "verified_at": now.isoformat(),
                "reliability": "high",
            }
        ],
        "preview_images": images[:4],
        "generated_at": now,
        "created_at": now,
        "updated_at": now,
    }
    topic = await topic_repo.create_topic(topic_data)
    print(f"TOPIC_CREATED {topic.get('id')}")

    for i, url in enumerate(images):
        hid = hashlib.md5(url.encode()).hexdigest()[:10]
        await image_repo.create_image(
            {
                "id": f"{TOPIC_ID}_src_{hid}",
                "topic_id": TOPIC_ID,
                "url": url,
                "source": ImageSource.SOURCE_ARTICLE.value,
                "image_type": ImageType.SOURCE.value,
                "photographer": "Graham Dunn",
                "photographer_url": "",
                "license": "Source Article",
                "keywords": ["Who What Wear", "Tom Bateman"],
                "order": i,
                "width": None,
                "height": None,
                "fetched_at": now,
            }
        )
        print(f"IMAGE_SAVED {i+1} {url[:100]}")

    log_cost_event(
        "TOPIC_IMAGE_STORE",
        success=True,
        topic_id=TOPIC_ID,
        count=len(images),
        mode="source_article_urls",
    )
    print(f"OPEN http://127.0.0.1:3000/topics/{TOPIC_ID}")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

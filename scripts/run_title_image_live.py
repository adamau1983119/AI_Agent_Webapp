"""Live title-image smoke: DeepSeek titles + Pillow overlay on WWW topic photo.

Usage (repo root):
  cd backend && python ../scripts/run_title_image_live.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

from dotenv import load_dotenv

load_dotenv(BACKEND / ".env")

TOPIC_ID = "www_tom_bateman_love_hypothesis_20260918"
OUT = ROOT / "docs" / "evidence" / "v8" / "title-image-live.jpg"


async def main() -> None:
    from app.database import connect_to_mongo, close_mongo_connection
    from app.schemas.alter_ego import ComposeRequest
    from app.services.compose_generate import generate_compose_part
    from app.services.images.jpeg_compress import compress_jpeg_bytes
    from app.services.images.title_image_overlay import render_title_jpeg
    from app.services.repositories.image_repository import ImageRepository
    from app.services.repositories.topic_repository import TopicRepository
    from app.utils.logger import log_cost_event
    import httpx

    await connect_to_mongo()
    try:
        topic = await TopicRepository().get_topic_by_id(TOPIC_ID)
        if not topic:
            raise SystemExit(f"topic_missing:{TOPIC_ID}")
        images = await ImageRepository().get_images_by_topic_id(TOPIC_ID)
        if not images:
            raise SystemExit("no_images")
        img = images[0]
        url = (img.get("url") or "").strip()
        title = topic.get("original_title") or topic.get("title") or TOPIC_ID
        fact = (topic.get("summary_flash") or topic.get("description") or title)[:1500]

        req = ComposeRequest(
            platform="facebook",
            style="casual",
            max_chars=500,
            part="title",
            language="zh-TW",
            topic_id=TOPIC_ID,
            topic_title=title,
            context_summary=fact,
            domain="fashion",
            preserve_snippets=[],
            revision_intent="",
            base_body="",
        )
        pack = await generate_compose_part(
            user_id="script-title-image",
            request=req,
            part="title",
            max_chars=500,
            lang="zh-TW",
            fact=fact,
            overlay="",
        )
        headings = [h for h in (pack.get("titles") or []) if str(h).strip()]
        if not headings:
            raise SystemExit(f"no_titles:{pack}")
        heading = str(headings[0]).strip()
        log_cost_event(
            "TITLE_IMAGE_LIVE_DEEPSEEK",
            success=True,
            titles=len(headings),
            heading=heading[:60],
        )

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            res = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; AlterEgo/1.0)"},
            )
            res.raise_for_status()
            raw = res.content
        jpeg = render_title_jpeg(raw, heading, "a")
        data, _, _ = compress_jpeg_bytes(jpeg)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_bytes(data)
        log_cost_event(
            "TITLE_IMAGE_LIVE_RENDER",
            success=True,
            image_id=img.get("id") or img.get("_id"),
            out_bytes=len(data),
            path=str(OUT),
        )
        print(f"OK headings={headings!r}")
        print(f"OK wrote {OUT} bytes={len(data)}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())

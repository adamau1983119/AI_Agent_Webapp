"""
單張公共主題卡組裝（Flash 骨 · DeepL 皮 · 不走 _translate_title）
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from app.models.topic import Category, Status
from app.services.public_feed.deepl_title import translate_public_title
from app.services.public_feed.public_feed_repository import PublicFeedRepository
from app.services.summarization.summary_flash_service import generate_summary_flash

logger = logging.getLogger(__name__)


async def build_and_save_public_topic(
    candidate: Dict[str, Any],
    repo: PublicFeedRepository,
    window_hours: int,
) -> bool:
    link = candidate["link"]
    if await repo.link_exists_in_window(link, window_hours):
        return False

    title_en = candidate["title"]
    category: Category = candidate["category"]
    snippet = candidate.get("snippet") or title_en

    summary = await generate_summary_flash(
        title_en,
        raw_text=snippet,
        topic_id="public_feed_pending",
    )
    title_zh = await translate_public_title(title_en, "zh-TW")
    title_ja = await translate_public_title(title_en, "ja")

    topic_id = f"pubfeed_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()
    doc: Dict[str, Any] = {
        "id": topic_id,
        "title": title_en,
        "original_title": title_en,
        "category": category.value if hasattr(category, "value") else category,
        "status": Status.CONFIRMED.value,
        "source": candidate["source_name"],
        "source_lang": "en",
        "display_language": "en",
        "titles_i18n": {"zh-TW": title_zh, "ja": title_ja},
        "summary_flash": summary,
        "description": summary[:200],
        "preview_images": candidate.get("preview_images") or [],
        "sources": [{
            "type": "rss",
            "name": candidate["source_name"],
            "url": link,
            "title": title_en,
            "fetched_at": now,
            "verified": True,
            "language": "en",
        }],
        "created_at": now,
        "generated_at": now,
        "updated_at": now,
    }
    await repo.insert_public_topic(doc)
    logger.info("public_feed 入庫: %s (%s)", topic_id, title_en[:40])
    return True

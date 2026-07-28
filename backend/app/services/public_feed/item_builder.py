"""
單張公共主題卡組裝（Flash 骨 · DeepL 皮 · 不走 _translate_title）
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from app.models.topic import Category, Status
from app.models.topic_translation import TranslationType
from app.services.public_feed.deepl_title import (
    translate_public_summary_with_meta,
    translate_public_title_with_meta,
)
from app.services.public_feed.public_feed_repository import PublicFeedRepository
from app.services.public_feed.source_country import infer_source_country
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
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
    title_zh, provider_zh = await translate_public_title_with_meta(title_en, "zh-TW")
    title_ja, provider_ja = await translate_public_title_with_meta(title_en, "ja")
    en_hint = f"{title_en}. {snippet}".strip()
    summary_zh, provider_sum_zh = await translate_public_summary_with_meta(
        summary, "zh-TW", en_hint=en_hint
    )
    summary_ja, provider_sum_ja = await translate_public_summary_with_meta(
        summary, "ja", en_hint=en_hint
    )
    summary_en, provider_sum_en = await translate_public_summary_with_meta(
        summary, "en", en_hint=en_hint
    )

    topic_id = f"pubfeed_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow()
    feed_url = candidate.get("feed_url") or ""
    source_country = infer_source_country(feed_url, candidate["source_name"])
    doc: Dict[str, Any] = {
        "id": topic_id,
        "title": title_en,
        "original_title": title_en,
        "category": category.value if hasattr(category, "value") else category,
        "status": Status.CONFIRMED.value,
        "source": candidate["source_name"],
        "source_lang": "en",
        "source_country": source_country,
        "is_trend_alert": False,
        "public_feed_flag": True,
        "display_language": "en",
        "titles_i18n": {"zh-TW": title_zh, "ja": title_ja},
        "summary_flash": summary,
        "summary_i18n": {
            "zh-TW": summary_zh,
            "ja": summary_ja,
            "en": summary_en,
        },
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

    trans_repo = TopicTranslationRepository()
    await trans_repo.ensure_indexes()
    for lang, title_t, summary_t, provider in (
        ("zh-TW", title_zh, summary_zh, provider_sum_zh or provider_zh),
        ("ja", title_ja, summary_ja, provider_sum_ja or provider_ja),
        ("en", title_en, summary_en, provider_sum_en),
    ):
        await trans_repo.upsert_translation({
            "topic_id": topic_id,
            "lang": lang,
            "type": TranslationType.STANDARD,
            "cached_title": title_t[:200],
            "cached_content": (summary_t or "")[:400] or None,
            "provider": provider,
        })

    logger.info("public_feed 入庫: %s (%s)", topic_id, title_en[:40])
    return True

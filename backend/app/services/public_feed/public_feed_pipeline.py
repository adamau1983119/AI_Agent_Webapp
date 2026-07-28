"""
v7 Discover 公共主題牆 8h 批次管線
"""
import logging
from typing import Any, Dict

from app.config import settings
from app.utils.logger import log_cost_event
from app.services.public_feed.item_builder import build_and_save_public_topic
from app.services.public_feed.public_feed_cache import refresh_feed_cache
from app.services.public_feed.public_feed_repository import PublicFeedRepository
from app.services.public_feed.rss_fetcher import collect_rss_candidates

logger = logging.getLogger(__name__)


async def run_public_feed_batch() -> Dict[str, Any]:
    batch_size = int(settings.safe_batch_size)
    window_hours = int(settings.PUBLIC_FEED_WINDOW_HOURS)
    if settings.ENVIRONMENT == "development":
        log_cost_event(
            "PUBLIC_FEED_DEV_CAP",
            environment=settings.ENVIRONMENT,
            safe_batch_size=batch_size,
            configured_batch=int(settings.PUBLIC_FEED_BATCH_SIZE),
        )
    repo = PublicFeedRepository()
    await repo.ensure_indexes()

    candidates = await collect_rss_candidates(batch_size)
    stats: Dict[str, Any] = {
        "candidates": len(candidates),
        "inserted": 0,
        "skipped_duplicate": 0,
        "safe_batch_size": batch_size,
    }

    for item in candidates:
        if stats["inserted"] >= batch_size:
            break
        saved = await build_and_save_public_topic(item, repo, window_hours)
        if saved:
            stats["inserted"] += 1
        else:
            stats["skipped_duplicate"] += 1

    cleanup = await repo.cleanup()
    stats["cleanup"] = cleanup

    topics = await repo.list_in_window(
        window_hours,
        limit=int(settings.PUBLIC_FEED_MAX_CARDS),
    )
    await refresh_feed_cache(topics)
    stats["in_window"] = len(topics)
    logger.info("public_feed_batch 完成: %s", stats)
    return stats

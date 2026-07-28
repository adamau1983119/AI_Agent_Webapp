"""
Discover 公共主題 Mongo 查詢與清理
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from app.config import settings
from app.services.repositories.topic_repository import TopicRepository

logger = logging.getLogger(__name__)


class PublicFeedRepository:
    def __init__(self):
        self._repo = TopicRepository()

    async def ensure_indexes(self) -> None:
        col = await self._repo._get_collection()
        await col.create_index(
            [("public_feed_flag", 1), ("created_at", -1)],
            name="public_feed_created_at",
        )

    async def link_exists_in_window(self, link: str, window_hours: int) -> bool:
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        return await self._repo.exists({
            "public_feed_flag": True,
            "created_at": {"$gte": cutoff},
            "sources.url": link,
        })

    async def insert_public_topic(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        doc["public_feed_flag"] = True
        return await self._repo.create_topic(doc)

    async def list_in_window(self, window_hours: int, limit: int) -> List[Dict[str, Any]]:
        cutoff = datetime.utcnow() - timedelta(hours=window_hours)
        return await self._repo.find_many(
            {"public_feed_flag": True, "created_at": {"$gte": cutoff}},
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def cleanup(self) -> Dict[str, int]:
        window = int(settings.PUBLIC_FEED_WINDOW_HOURS)
        max_cards = int(settings.PUBLIC_FEED_MAX_CARDS)
        cutoff = datetime.utcnow() - timedelta(hours=window)
        col = await self._repo._get_collection()
        old = await col.delete_many({
            "public_feed_flag": True,
            "created_at": {"$lt": cutoff},
        })
        remaining = await self._repo.count({"public_feed_flag": True})
        trimmed = 0
        if remaining > max_cards:
            excess = remaining - max_cards
            oldest = await self._repo.find_many(
                {"public_feed_flag": True},
                limit=excess,
                sort=[("created_at", 1)],
            )
            ids = [t["id"] for t in oldest if t.get("id")]
            if ids:
                res = await col.delete_many({"id": {"$in": ids}})
                trimmed = res.deleted_count
        stats = {"deleted_expired": old.deleted_count, "trimmed": trimmed}
        logger.info("public_feed cleanup: %s", stats)
        return stats

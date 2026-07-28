"""
topic_translations Repository（Motor CRUD + upsert）
"""
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class TopicTranslationRepository(BaseRepository):
    def __init__(self, db=None):
        super().__init__("topic_translations", db=db)
        self._indexes_ready = False

    async def ensure_indexes(self) -> None:
        if self._indexes_ready:
            return
        try:
            col = await self._get_collection()
            await col.create_index(
                [("topic_id", 1), ("lang", 1), ("type", 1)],
                unique=True,
                name="uniq_topic_lang_type",
            )
            self._indexes_ready = True
            logger.info("topic_translations 唯一索引已確保")
        except Exception as e:
            logger.warning("topic_translations 索引: %s", e)
            self._indexes_ready = True

    async def get_translation(
        self, topic_id: str, lang: str, trans_type: str
    ) -> Optional[Dict[str, Any]]:
        await self.ensure_indexes()
        return await self.find_one(
            {"topic_id": topic_id, "lang": lang, "type": trans_type}
        )

    async def upsert_translation(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        await self.ensure_indexes()
        now = datetime.utcnow()
        key = {
            "topic_id": doc["topic_id"],
            "lang": doc["lang"],
            "type": doc["type"],
        }
        payload = {**doc, "updated_at": now}
        col = await self._get_collection()
        await col.update_one(
            key,
            {"$set": payload, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        return await self.find_one(key)

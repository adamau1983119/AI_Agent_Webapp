"""
user_feedback_logs — Alter Ego 週 batch 輸入（AE-2）
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.services.repositories.base_repository import BaseRepository


class UserFeedbackRepository(BaseRepository):
    def __init__(self, db=None):
        super().__init__("user_feedback_logs", db=db)

    async def insert_feedback(
        self,
        *,
        user_id: str,
        action: str,
        topic_id: Optional[str] = None,
        dna_version_id: Optional[str] = None,
        comment: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        doc = {
            "user_id": user_id,
            "action": action,
            "topic_id": topic_id,
            "dna_version_id": dna_version_id,
            "comment": (comment or "")[:500],
            "meta": meta or {},
            "created_at": datetime.utcnow(),
        }
        created = await self.create(doc)
        return str(created.get("_id", ""))

    async def list_recent_for_user(
        self, user_id: str, *, days: int = 7, limit: int = 40
    ) -> List[Dict[str, Any]]:
        since = datetime.utcnow() - timedelta(days=days)
        collection = await self._get_collection()
        cursor = (
            collection.find({"user_id": user_id, "created_at": {"$gte": since}})
            .sort("created_at", -1)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)

    async def distinct_user_ids_since(self, days: int = 7) -> List[str]:
        since = datetime.utcnow() - timedelta(days=days)
        collection = await self._get_collection()
        return await collection.distinct("user_id", {"created_at": {"$gte": since}})

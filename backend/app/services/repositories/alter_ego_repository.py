"""
Alter Ego DNA repository（Mongo）
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from app.services.repositories.base_repository import BaseRepository


class AlterEgoDnaRepository(BaseRepository):
    def __init__(self, db=None):
        super().__init__("alter_ego_dna", db=db)

    async def get_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"user_id": user_id})

    async def upsert_active(
        self,
        user_id: str,
        dna_json: Dict[str, Any],
        reason: str = "extract",
    ) -> str:
        version_id = uuid.uuid4().hex
        now = datetime.utcnow()
        doc = {
            "user_id": user_id,
            "dna_json": dna_json,
            "dna_status": "active",
            "current_dna_version_id": version_id,
            "updated_at": now,
        }
        existing = await self.get_by_user(user_id)
        if existing:
            collection = await self._get_collection()
            await collection.update_one({"user_id": user_id}, {"$set": doc})
        else:
            doc["created_at"] = now
            await self.create(doc)

        snap_repo = AlterEgoDnaSnapshotRepository(self._db)
        await snap_repo.insert_snapshot(
            user_id=user_id,
            snapshot_id=version_id,
            dna_json=dna_json,
            reason=reason,
        )
        return version_id

    async def upsert_skipped(self, user_id: str) -> None:
        now = datetime.utcnow()
        existing = await self.get_by_user(user_id)
        if existing:
            collection = await self._get_collection()
            await collection.update_one(
                {"user_id": user_id},
                {"$set": {"dna_status": "skipped", "updated_at": now}},
            )
            return
        await self.create(
            {
                "user_id": user_id,
                "dna_status": "skipped",
                "created_at": now,
                "updated_at": now,
            }
        )

    async def rollback_to_snapshot(self, user_id: str, snapshot_id: str) -> str:
        snap_repo = AlterEgoDnaSnapshotRepository(self._db)
        snap = await snap_repo.get_for_user(user_id, snapshot_id)
        if not snap or not snap.get("dna_json"):
            raise ValueError("snapshot_not_found")
        return await self.upsert_active(
            user_id=user_id,
            dna_json=snap["dna_json"],
            reason="rollback",
        )


class AlterEgoDnaSnapshotRepository(BaseRepository):
    def __init__(self, db=None):
        super().__init__("alter_ego_dna_snapshots", db=db)

    async def insert_snapshot(
        self,
        user_id: str,
        snapshot_id: str,
        dna_json: Dict[str, Any],
        reason: str,
    ) -> None:
        await self.create(
            {
                "snapshot_id": snapshot_id,
                "user_id": user_id,
                "dna_json": dna_json,
                "reason": reason,
                "created_at": datetime.utcnow(),
            }
        )

    async def get_for_user(self, user_id: str, snapshot_id: str) -> Optional[Dict[str, Any]]:
        return await self.find_one({"user_id": user_id, "snapshot_id": snapshot_id})

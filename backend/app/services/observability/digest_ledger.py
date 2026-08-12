"""每日基本檢查寄信帳本（Mongo）— 可稽核、重啟後仍知今日是否已寄。"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger("observability.digest_ledger")
_COLL = "ops_digest_ledger"


async def _coll():
    from app.database import get_database

    db = await get_database()
    if db is None:
        return None
    return db[_COLL]


async def was_digest_sent(day_hkt: str) -> bool:
    """今日是否已有成功寄出紀錄（跨重啟）。"""
    try:
        coll = await _coll()
        if coll is None:
            return False
        doc = await coll.find_one({"day_hkt": day_hkt, "status": "digest_sent"})
        return doc is not None
    except Exception as exc:  # noqa: BLE001
        logger.warning("digest_ledger was_sent failed: %s", exc)
        return False


async def record_digest_attempt(payload: dict[str, Any]) -> None:
    """寫入一筆嘗試（成功／失敗都記）。"""
    try:
        coll = await _coll()
        if coll is None:
            return
        doc = {
            **payload,
            "recorded_at": datetime.utcnow(),
        }
        await coll.insert_one(doc)
    except Exception as exc:  # noqa: BLE001
        logger.warning("digest_ledger record failed: %s", exc)


async def latest_digest_summary() -> Optional[dict[str, Any]]:
    """供 /health 一眼看正式域最近寄信狀態。"""
    try:
        coll = await _coll()
        if coll is None:
            return None
        doc = await coll.find_one(sort=[("recorded_at", -1)])
        if not doc:
            return None
        return {
            "day_hkt": doc.get("day_hkt"),
            "status": doc.get("status"),
            "title": doc.get("title"),
            "traffic_light": doc.get("traffic_light"),
            "recorded_at": (
                doc["recorded_at"].isoformat() + "Z"
                if isinstance(doc.get("recorded_at"), datetime)
                else doc.get("recorded_at")
            ),
            "source": doc.get("source"),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("digest_ledger latest failed: %s", exc)
        return None

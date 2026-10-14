"""分析次數。不扣點。建立成功才把該頻道次數歸零；刪頻道不重算。"""
import logging
from typing import Any, Dict

from app.database import get_database
from app.services.automation.topic_day_hkt import today_hkt_str
from app.services.channel_assist_policy import decide_quota

logger = logging.getLogger(__name__)


async def consume_analysis(user_id: str) -> Dict[str, Any]:
    today = today_hkt_str()
    db = await get_database()
    users = db["users"]
    doc = await users.find_one({"id": user_id}, {"channel_assist_quota": 1})
    stored = (doc or {}).get("channel_assist_quota") or {}
    decision = decide_quota(
        pending=int(stored.get("pending") or 0),
        day_count=int(stored.get("day_count") or 0),
        stored_day=stored.get("day"),
        today=today,
    )
    if not decision["allowed"]:
        return decision
    await users.update_one(
        {"id": user_id},
        {"$set": {
            "channel_assist_quota.pending": decision["pending"],
            "channel_assist_quota.day": decision["day"],
            "channel_assist_quota.day_count": decision["day_count"],
        }},
    )
    return decision


async def reset_pending_on_create(user_id: str) -> None:
    """只清尚未建立成功的已用次數。每日次數保留。"""
    try:
        db = await get_database()
        await db["users"].update_one(
            {"id": user_id},
            {"$set": {"channel_assist_quota.pending": 0}},
        )
    except Exception as exc:
        logger.warning("建立成功後未清分析次數 user=%s err=%s", user_id, exc)

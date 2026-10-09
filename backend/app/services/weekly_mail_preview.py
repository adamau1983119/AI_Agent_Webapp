"""週報名單。只組 JSON，不寄信。"""
from __future__ import annotations

import hmac
import os
from datetime import datetime, timedelta
from typing import Any, Optional

from app.config_module import settings
from app.database import get_database
from app.services.credit_ledger_service import credit_ledger_service
from app.services.weekly_mail_rules import topic_title, weekly_eligible
from app.services.weekly_mail_token import create_unsubscribe_token
from app.utils.ui_language import allowed_language


def _card(doc: dict, language: str, kind: str) -> dict:
    topic_id = doc.get("id") or ""
    base = settings.FRONTEND_URL.rstrip("/")
    return {
        "id": topic_id,
        "title": topic_title(doc, language),
        "url": f"{base}/topics/{topic_id}",
        "kind": kind,
    }


async def _popular_ids(db) -> list[str]:
    since = datetime.utcnow() - timedelta(days=7)
    rows = await db["interactions"].aggregate([
        {"$match": {"action": "view", "created_at": {"$gte": since}}},
        {"$group": {"_id": "$topic_id", "views": {"$sum": 1}}},
        {"$sort": {"views": -1}},
        {"$limit": 3},
    ]).to_list(3)
    return [row["_id"] for row in rows if row.get("_id")]


async def _topics_by_ids(db, ids: list[str]) -> list[dict]:
    if not ids:
        return []
    docs = await db["topics"].find(
        {"id": {"$in": ids}, "hidden": {"$ne": True}, "status": {"$ne": "deleted"}},
        {"_id": 0, "id": 1, "title": 1, "original_title": 1, "titles_i18n": 1},
    ).to_list(len(ids))
    order = {topic_id: index for index, topic_id in enumerate(ids)}
    docs.sort(key=lambda doc: order.get(doc.get("id"), 99))
    return docs


async def _new_topics(db) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=7)
    return await db["topics"].find(
        {
            "hidden": {"$ne": True},
            "status": {"$ne": "deleted"},
            "created_at": {"$gte": since},
        },
        {"_id": 0, "id": 1, "title": 1, "original_title": 1, "titles_i18n": 1},
    ).sort("created_at", -1).limit(3).to_list(3)


async def card_set(db) -> tuple[list[dict], str]:
    popular = await _topics_by_ids(db, await _popular_ids(db))
    if popular:
        return popular, "popular"
    return await _new_topics(db), "new"


def preview_token_ok(header: Optional[str]) -> bool:
    expected = os.getenv("WEEKLY_MAIL_PREVIEW_TOKEN", "").strip()
    if not expected or not header:
        return False
    return hmac.compare_digest(header.strip(), expected)


async def build_weekly_rows() -> dict[str, Any]:
    db = await get_database()
    docs, kind = await card_set(db)
    users = await db["users"].find(
        {
            "status": "active",
            "email_verified": True,
            "weekly_mail_opt_out": {"$ne": True},
            "email_deliverable": {"$ne": False},
        },
        {"_id": 0, "id": 1, "email": 1, "name": 1, "language": 1, "status": 1,
         "email_verified": 1, "weekly_mail_opt_out": 1, "email_deliverable": 1},
    ).to_list(5000)
    api = settings.BACKEND_URL.rstrip("/")
    rows = []
    for user in users:
        if not weekly_eligible(user):
            continue
        language = allowed_language(user.get("language")) or "zh-TW"
        token = create_unsubscribe_token(user["id"], user["email"])
        snapshot = await credit_ledger_service.get_wallet_snapshot(user["id"])
        rows.append({
            "email": str(user["email"]).lower(),
            "name": user.get("name") or "",
            "language": language,
            "credits": int(snapshot.get("balance") or 0),
            "card_kind": kind,
            "topics": [_card(doc, language, kind) for doc in docs],
            "unsubscribe_url": f"{api}/api/v1/weekly-mail/unsubscribe?token={token}",
            "list_unsubscribe": f"<{api}/api/v1/weekly-mail/unsubscribe?token={token}>",
        })
    return {"card_kind": kind, "count": len(rows), "rows": rows}

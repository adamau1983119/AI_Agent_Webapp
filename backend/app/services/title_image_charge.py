"""Charge 10 credits for a title-image download. Preview stays free."""
from __future__ import annotations

import secrets
from typing import Optional

from app.services.credit_ledger_service import credit_ledger_service

TITLE_IMAGE_DOWNLOAD_COST = 10


async def charge_title_image_download(user_id: str, topic_id: Optional[str]) -> int:
    await credit_ledger_service.ensure_initial_balance(user_id)
    key = f"title-image:{user_id}:{secrets.token_hex(8)}"
    return await credit_ledger_service.decr_credits(
        user_id,
        TITLE_IMAGE_DOWNLOAD_COST,
        action="title_image_download",
        idempotency_key=key,
        topic_id=(topic_id or "").strip() or None,
    )

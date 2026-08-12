"""
MyChannel API — feed / unlock（v7.1 · MC-2～MC-3）
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.jwt_auth import get_current_user, require_role
from app.models.user import UserRole
from app.schemas.my_channel import (
    AddCreditsRequest,
    AddCreditsResponse,
    ChannelTemplateItem,
    ChannelTemplatesResponse,
    MyChannelFeedCard,
    MyChannelFeedResponse,
    UnlockRequest,
    UnlockResponse,
)
from app.services.credit_ledger_service import InsufficientCreditsError, credit_ledger_service
from app.services.my_channel.channel_templates import load_channel_templates
from app.services.my_channel.my_channel_service import my_channel_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/my-channel", tags=["my-channel"])


@router.get("/feed", response_model=MyChannelFeedResponse)
async def get_my_channel_feed(
    lang: str = Query("zh-TW", description="zh-TW / en / ja"),
    current_user: dict = Depends(get_current_user),
):
    """免費層 feed（不含 source_url · MC-2）。"""
    user_id = current_user["id"]
    cards, balance, from_cache, rate_limited, has_channels = await my_channel_service.get_feed(
        user_id, lang
    )
    return MyChannelFeedResponse(
        data=[MyChannelFeedCard(**c) for c in cards],
        balance=balance,
        lang=lang,
        cached=from_cache,
        rate_limited=rate_limited,
        empty=len(cards) == 0,
        has_channels=has_channels,
    )


@router.get("/channel-templates", response_model=ChannelTemplatesResponse)
async def get_channel_templates(current_user: dict = Depends(get_current_user)):
    """無頻道用戶熱門模板（MC-6 · 靜態 JSON）。"""
    _ = current_user
    items = [ChannelTemplateItem(**row) for row in load_channel_templates()]
    return ChannelTemplatesResponse(data=items)


@router.post("/topics/{topic_id}/unlock", response_model=UnlockResponse)
async def unlock_topic(
    topic_id: str,
    body: UnlockRequest,
    lang: str = Query("zh-TW", description="UI 語言（zh-TW / en / ja）"),
    current_user: dict = Depends(get_current_user),
):
    """扣 1 點解鎖 URL + digest（MC-3 · 先扣點再回 body）。"""
    try:
        result = await my_channel_service.unlock_topic(
            current_user["id"],
            topic_id,
            body.idempotency_key,
            lang,
        )
        return UnlockResponse(**result)
    except InsufficientCreditsError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="insufficient_credits",
        ) from exc
    except ValueError as exc:
        code = str(exc)
        if code == "topic_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=code) from exc
        if code in ("topic_forbidden", "topic_missing_url"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from exc


admin_router = APIRouter(prefix="/admin/users", tags=["admin-users"])


@admin_router.post("/{user_id}/credits", response_model=AddCreditsResponse)
async def add_user_credits(
    user_id: str,
    body: AddCreditsRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN)),
):
    """管理員加點（MC-1 · PD-MC1-03）。"""
    balance = await credit_ledger_service.add_credits(
        user_id, body.amount, admin_id=current_user["id"]
    )
    return AddCreditsResponse(user_id=user_id, balance=balance, added=body.amount)

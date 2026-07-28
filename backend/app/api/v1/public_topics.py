"""
Discover 公共主題牆讀取 API（零 LLM · Redis → Mongo）
"""
import logging
from typing import List

from fastapi import APIRouter, Query

from app.config import settings
from app.schemas.public_feed import PublicFeedCard, PublicFeedResponse
from app.services.public_feed.feed_card_mapper import topics_to_feed_cards_async
from app.services.public_feed.public_feed_cache import get_cached_feed
from app.services.public_feed.public_feed_repository import PublicFeedRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public/topics", tags=["public-topics"])

_ALLOWED_LANGS = ("zh-TW", "ja", "en")


@router.get("/feed", response_model=PublicFeedResponse)
async def get_public_feed(
    lang: str = Query("zh-TW", description="zh-TW／ja／en"),
):
    if lang not in _ALLOWED_LANGS:
        lang = "zh-TW"

    cached = await get_cached_feed(lang)
    if cached is not None:
        cards = [PublicFeedCard(**c) for c in cached]
        return PublicFeedResponse(data=cards, lang=lang, cached=True, count=len(cards))

    repo = PublicFeedRepository()
    window = int(settings.PUBLIC_FEED_WINDOW_HOURS)
    limit = int(settings.PUBLIC_FEED_MAX_CARDS)
    topics = await repo.list_in_window(window, limit)
    raw_cards = await topics_to_feed_cards_async(topics, lang)
    cards = [PublicFeedCard(**c) for c in raw_cards]
    return PublicFeedResponse(data=cards, lang=lang, cached=False, count=len(cards))

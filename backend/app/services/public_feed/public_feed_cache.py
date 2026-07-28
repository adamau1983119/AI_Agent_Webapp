"""
Discover feed Redis 快取（TTL ≤36h）
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.cache_service import cache_service
from app.services.public_feed.feed_card_mapper import topics_to_feed_cards_async

logger = logging.getLogger(__name__)

_CACHE_PREFIX = "public_feed:feed:"
_FEED_LANGS = ("zh-TW", "ja", "en")


def _ttl_seconds() -> int:
    return int(settings.PUBLIC_FEED_WINDOW_HOURS) * 3600


def _cache_key(lang: str) -> str:
    return f"{_CACHE_PREFIX}{lang}"


async def get_cached_feed(lang: str) -> Optional[List[Dict[str, Any]]]:
    if not cache_service.enabled or not cache_service.redis_client:
        return None
    try:
        raw = await cache_service.redis_client.get(_cache_key(lang))
        if raw:
            return json.loads(raw)
    except Exception as e:
        logger.warning("public_feed cache read failed: %s", e)
    return None


async def set_cached_feed(lang: str, cards: List[Dict[str, Any]]) -> None:
    if not cache_service.enabled or not cache_service.redis_client:
        return
    try:
        await cache_service.redis_client.setex(
            _cache_key(lang),
            _ttl_seconds(),
            json.dumps(cards, default=str),
        )
    except Exception as e:
        logger.warning("public_feed cache write failed: %s", e)


async def refresh_feed_cache(topics: List[Dict[str, Any]]) -> None:
    for lang in _FEED_LANGS:
        cards = await topics_to_feed_cards_async(topics, lang)
        await set_cached_feed(lang, cards)
    logger.info("public_feed cache refreshed (%d topics)", len(topics))

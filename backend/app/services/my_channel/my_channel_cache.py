"""
MyChannel feed Redis 快取（MC-2 · MC-4 隔離 key）
"""
from __future__ import annotations

import json
import logging
import secrets
import time
from typing import Any, Dict, List, Optional

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

_CACHE_PREFIX = "my_channel:feed:"
_ASSEMBLE_PREFIX = "my_channel:assemble:"
_UNLOCK_RESULT_PREFIX = "my_channel:unlock_result:"
_FEED_TTL = 3600
_MAX_ASSEMBLES_24H = 3
_ASSEMBLE_WINDOW = 86400
_IDEMPOTENCY_TTL = 86400 * 7


def _feed_key(user_id: str, lang: str) -> str:
    return f"{_CACHE_PREFIX}{user_id}:{lang}"


def _assemble_key(user_id: str) -> str:
    return f"{_ASSEMBLE_PREFIX}{user_id}"


def _unlock_result_key(user_id: str, idempotency_key: str) -> str:
    return f"{_UNLOCK_RESULT_PREFIX}{user_id}:{idempotency_key}"


async def get_unlock_result(user_id: str, idempotency_key: str) -> Optional[Dict[str, Any]]:
    if not cache_service.enabled or not cache_service.redis_client:
        return None
    try:
        raw = await cache_service.redis_client.get(_unlock_result_key(user_id, idempotency_key))
        if raw:
            return json.loads(raw)
    except Exception as e:
        logger.warning("my_channel unlock cache read failed: %s", e)
    return None


async def set_unlock_result(user_id: str, idempotency_key: str, payload: Dict[str, Any]) -> None:
    if not cache_service.enabled or not cache_service.redis_client:
        return
    try:
        await cache_service.redis_client.setex(
            _unlock_result_key(user_id, idempotency_key),
            _IDEMPOTENCY_TTL,
            json.dumps(payload, default=str),
        )
    except Exception as e:
        logger.warning("my_channel unlock cache write failed: %s", e)


async def get_cached_feed(user_id: str, lang: str) -> Optional[List[Dict[str, Any]]]:
    if not cache_service.enabled or not cache_service.redis_client:
        return None
    try:
        raw = await cache_service.redis_client.get(_feed_key(user_id, lang))
        if raw:
            return json.loads(raw)
    except Exception as e:
        logger.warning("my_channel cache read failed: %s", e)
    return None


async def set_cached_feed(user_id: str, lang: str, cards: List[Dict[str, Any]]) -> None:
    if not cache_service.enabled or not cache_service.redis_client:
        return
    try:
        await cache_service.redis_client.setex(
            _feed_key(user_id, lang),
            _FEED_TTL,
            json.dumps(cards, default=str),
        )
    except Exception as e:
        logger.warning("my_channel cache write failed: %s", e)


async def can_assemble(user_id: str) -> bool:
    if not cache_service.enabled or not cache_service.redis_client:
        return True
    try:
        now = time.time()
        key = _assemble_key(user_id)
        await cache_service.redis_client.zremrangebyscore(key, "-inf", now - _ASSEMBLE_WINDOW)
        count = await cache_service.redis_client.zcard(key)
        return count < _MAX_ASSEMBLES_24H
    except Exception as e:
        logger.warning("my_channel assemble limit check failed: %s", e)
        return True


async def record_assemble(user_id: str) -> None:
    if not cache_service.enabled or not cache_service.redis_client:
        return
    try:
        now = time.time()
        key = _assemble_key(user_id)
        member = f"{now}:{secrets.token_hex(4)}"
        await cache_service.redis_client.zadd(key, {member: now})
        await cache_service.redis_client.expire(key, _ASSEMBLE_WINDOW + 60)
    except Exception as e:
        logger.warning("my_channel assemble record failed: %s", e)

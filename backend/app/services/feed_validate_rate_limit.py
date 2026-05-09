"""
POST /channels/feeds/validate、GET /channels/feeds/search 專用 per-IP 限流。
- 若應用已連上 Redis（cache_service），使用滑動視窗 + Lua，多 worker／多機共享。
- 否則回退行程內記憶體（單機開發）。
429 回應：{"detail": {"code": "<穩定代碼>"}}，供前端依 code 對應 i18n。
"""
from __future__ import annotations

import asyncio
import logging
import secrets
import time
from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import HTTPException, Request, status
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

FEED_VALIDATE_PER_MINUTE = 8
FEED_VALIDATE_PER_HOUR = 32
FEED_SEARCH_PER_MINUTE = 45

CODE_VALIDATE_MINUTE = "feed_validate_rate_limit_minute"
CODE_VALIDATE_HOUR = "feed_validate_rate_limit_hour"
CODE_SEARCH = "feed_search_rate_limit"

_lock = asyncio.Lock()
_history: Dict[str, List[float]] = defaultdict(list)

_search_lock = asyncio.Lock()
_search_history: Dict[str, List[float]] = defaultdict(list)

_LUA_VALIDATE = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local win_hour = tonumber(ARGV[2])
local win_min = tonumber(ARGV[3])
local lim_min = tonumber(ARGV[4])
local lim_hour = tonumber(ARGV[5])
local member = ARGV[6]
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - win_hour)
local hour_count = redis.call('ZCARD', key)
local min_count = redis.call('ZCOUNT', key, now - win_min, '+inf')
if min_count >= lim_min then
  return {0, 'm'}
end
if hour_count >= lim_hour then
  return {0, 'h'}
end
redis.call('ZADD', key, now, member)
redis.call('EXPIRE', key, win_hour + 10)
return {1, 'ok'}
"""

_LUA_SEARCH = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local win = tonumber(ARGV[2])
local lim = tonumber(ARGV[3])
local member = ARGV[4]
redis.call('ZREMRANGEBYSCORE', key, '-inf', now - win)
local c = redis.call('ZCARD', key)
if c >= lim then
  return 0
end
redis.call('ZADD', key, now, member)
redis.call('EXPIRE', key, win + 10)
return 1
"""


def _detail(code: str) -> dict:
    return {"code": code}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real = request.headers.get("X-Real-IP")
    if real:
        return real.strip()
    if request.client:
        return request.client.host
    return "unknown"


def _safe_ip_segment(ip: str) -> str:
    return ip.replace(":", "_").replace(" ", "_")[:200]


def _redis_client() -> Optional[Redis]:
    try:
        from app.services.cache_service import cache_service

        if cache_service.enabled and cache_service.redis_client:
            return cache_service.redis_client
    except Exception as e:  # pragma: no cover
        logger.debug("feed rate limit redis lookup: %s", e)
    return None


def _prune_validate(ip: str, now: float) -> None:
    hour_ago = now - 3600
    _history[ip] = [ts for ts in _history[ip] if ts > hour_ago]


async def _enforce_validate_memory(request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    async with _lock:
        _prune_validate(ip, now)
        minute_ago = now - 60
        hour_ago = now - 3600
        ts_list = _history[ip]
        in_minute = [t for t in ts_list if t > minute_ago]
        in_hour = [t for t in ts_list if t > hour_ago]
        if len(in_minute) >= FEED_VALIDATE_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_detail(CODE_VALIDATE_MINUTE),
                headers={"Retry-After": "60"},
            )
        if len(in_hour) >= FEED_VALIDATE_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_detail(CODE_VALIDATE_HOUR),
                headers={"Retry-After": "3600"},
            )
        ts_list.append(now)
        _history[ip] = ts_list


async def _enforce_validate_redis(redis: Redis, request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    key = f"rl:feed_validate:{_safe_ip_segment(ip)}"
    member = f"{now}:{secrets.token_hex(8)}"
    raw = await redis.eval(
        _LUA_VALIDATE,
        1,
        key,
        str(now),
        "3600",
        "60",
        str(FEED_VALIDATE_PER_MINUTE),
        str(FEED_VALIDATE_PER_HOUR),
        member,
    )
    if not raw or raw[0] != 1:
        kind = raw[1] if raw and len(raw) > 1 else "m"
        if kind == "h":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_detail(CODE_VALIDATE_HOUR),
                headers={"Retry-After": "3600"},
            )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_detail(CODE_VALIDATE_MINUTE),
            headers={"Retry-After": "60"},
        )


async def enforce_feed_validate_rate_limit(request: Request) -> None:
    redis = _redis_client()
    if redis:
        try:
            await _enforce_validate_redis(redis, request)
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Redis feed_validate rate limit failed, using memory: %s", e)
    await _enforce_validate_memory(request)


async def _enforce_search_memory(request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    async with _search_lock:
        minute_ago = now - 60
        _search_history[ip] = [t for t in _search_history[ip] if t > minute_ago]
        if len(_search_history[ip]) >= FEED_SEARCH_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_detail(CODE_SEARCH),
                headers={"Retry-After": "60"},
            )
        _search_history[ip].append(now)


async def _enforce_search_redis(redis: Redis, request: Request) -> None:
    ip = _client_ip(request)
    now = time.time()
    key = f"rl:feed_search:{_safe_ip_segment(ip)}"
    member = f"{now}:{secrets.token_hex(8)}"
    ok = await redis.eval(
        _LUA_SEARCH,
        1,
        key,
        str(now),
        "60",
        str(FEED_SEARCH_PER_MINUTE),
        member,
    )
    if ok != 1:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=_detail(CODE_SEARCH),
            headers={"Retry-After": "60"},
        )


async def enforce_feed_search_rate_limit(request: Request) -> None:
    redis = _redis_client()
    if redis:
        try:
            await _enforce_search_redis(redis, request)
            return
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Redis feed_search rate limit failed, using memory: %s", e)
    await _enforce_search_memory(request)

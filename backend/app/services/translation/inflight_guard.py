"""
防快取擊穿：per-key asyncio 鎖（v7 P2-13）
"""
import asyncio
from typing import Awaitable, Callable, Dict, TypeVar

T = TypeVar("T")
_inflight: Dict[str, asyncio.Lock] = {}


def translation_key(topic_id: str, lang: str, trans_type: str) -> str:
    return f"{topic_id}:{lang}:{trans_type}"


async def with_inflight(key: str, fn: Callable[[], Awaitable[T]]) -> T:
    """同一 key 併發僅一條路徑執行；finally 移除 in-flight 條目。"""
    lock = _inflight.setdefault(key, asyncio.Lock())
    async with lock:
        try:
            return await fn()
        finally:
            _inflight.pop(key, None)

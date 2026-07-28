"""
MyChannel feed 組裝與解鎖（MC-2～MC-3 · 零登入 collect）
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.credit_ledger_service import UNLOCK_COST, credit_ledger_service
from app.services.my_channel.my_channel_cache import (
    can_assemble,
    get_cached_feed,
    get_unlock_result,
    record_assemble,
    set_cached_feed,
    set_unlock_result,
)
from app.services.public_feed.feed_translation_loader import title_map_for_topics
from app.services.repositories.channel_repository import ChannelRepository
from app.services.repositories.topic_repository import TopicRepository

logger = logging.getLogger(__name__)

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_INTRO_MAX = 30
_DIGEST_MAX = 300
_ALLOWED_LANGS = ("zh-TW", "en", "ja")


def _has_valid_source_url(topic: Dict[str, Any]) -> bool:
    for src in topic.get("sources") or []:
        url = (src.get("url") or "").strip()
        if _URL_RE.match(url):
            return True
    return False


def _first_source_url(topic: Dict[str, Any]) -> Optional[str]:
    for src in topic.get("sources") or []:
        url = (src.get("url") or "").strip()
        if _URL_RE.match(url):
            return url
    return None


def _intro_text(topic: Dict[str, Any]) -> str:
    raw = (topic.get("description") or topic.get("summary_flash") or "").strip()
    if len(raw) <= _INTRO_MAX:
        return raw
    return raw[:_INTRO_MAX]


def _digest_text(topic: Dict[str, Any]) -> str:
    raw = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()
    if len(raw) <= _DIGEST_MAX:
        return raw
    return raw[:_DIGEST_MAX]


def _resolve_heading(topic: Dict[str, Any], lang: str, title_map: Dict[str, str]) -> str:
    tid = str(topic.get("id") or "")
    if tid and tid in title_map:
        return title_map[tid]
    titles = topic.get("titles_i18n") or {}
    return titles.get(lang) or topic.get("title") or ""


class MyChannelService:
    def __init__(self) -> None:
        self._channels = ChannelRepository()
        self._topics = TopicRepository()

    async def get_feed(
        self, user_id: str, lang: str
    ) -> Tuple[List[Dict[str, Any]], int, bool, bool, bool]:
        if lang not in _ALLOWED_LANGS:
            lang = "zh-TW"

        balance = await credit_ledger_service.ensure_initial_balance(user_id)
        channels = await self._channels.get_user_channels(user_id)
        has_channels = bool(channels)

        cached = await get_cached_feed(user_id, lang)
        if cached is not None:
            return cached, balance, True, False, has_channels

        if not await can_assemble(user_id):
            logger.info("my_channel assemble rate limited user=%s", user_id)
            return [], balance, False, True, has_channels

        cards = await self._assemble_cards(user_id, lang)
        await set_cached_feed(user_id, lang, cards)
        await record_assemble(user_id)
        return cards, balance, False, False, has_channels

    async def _assemble_cards(self, user_id: str, lang: str) -> List[Dict[str, Any]]:
        channels = await self._channels.get_user_channels(user_id)
        if not channels:
            return []

        seen: set[str] = set()
        candidates: List[Dict[str, Any]] = []

        for ch in channels:
            topics, _ = await self._topics.list_by_channel_id(
                ch["id"], user_id=user_id, limit=40, sort="generated_at", order="desc"
            )
            for topic in topics:
                tid = str(topic.get("id") or "")
                if not tid or tid in seen:
                    continue
                if not _has_valid_source_url(topic):
                    continue
                seen.add(tid)
                candidates.append(topic)

        def _sort_key(t: Dict[str, Any]) -> datetime:
            for field in ("generated_at", "created_at", "updated_at"):
                val = t.get(field)
                if isinstance(val, datetime):
                    return val
                if isinstance(val, str):
                    try:
                        return datetime.fromisoformat(val.replace("Z", "+00:00"))
                    except ValueError:
                        pass
            return datetime.min

        candidates.sort(key=_sort_key, reverse=True)
        candidates = candidates[:30]

        title_map = await title_map_for_topics(candidates, lang)
        cards: List[Dict[str, Any]] = []
        for topic in candidates:
            previews = topic.get("preview_images") or []
            cards.append(
                {
                    "id": topic["id"],
                    "heading": _resolve_heading(topic, lang, title_map),
                    "intro": _intro_text(topic),
                    "category": topic.get("category"),
                    "image_url": previews[0] if previews else None,
                }
            )
        return cards

    async def unlock_topic(
        self,
        user_id: str,
        topic_id: str,
        idempotency_key: str,
    ) -> Dict[str, Any]:
        cached = await get_unlock_result(user_id, idempotency_key)
        if cached:
            return cached

        topic = await self._topics.find_by_id(topic_id)
        if not topic:
            raise ValueError("topic_not_found")
        if str(topic.get("user_id") or "") != user_id:
            raise ValueError("topic_forbidden")

        source_url = _first_source_url(topic)
        if not source_url:
            raise ValueError("topic_missing_url")

        digest = _digest_text(topic)
        balance = await credit_ledger_service.decr_credits(
            user_id,
            UNLOCK_COST,
            action="unlock",
            idempotency_key=idempotency_key,
            topic_id=topic_id,
        )

        payload = {
            "topic_id": topic_id,
            "source_url": source_url,
            "digest_300": digest,
            "balance": balance,
        }
        await set_unlock_result(user_id, idempotency_key, payload)
        return payload


my_channel_service = MyChannelService()

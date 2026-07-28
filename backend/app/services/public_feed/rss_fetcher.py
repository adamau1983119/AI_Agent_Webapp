"""
Discover RSS 候選抓取（Feed Health 白名單 · 僅 RSS）
"""
import logging
from typing import Any, Dict, List, Tuple

import feedparser
import httpx

from app.config.feed_roles import get_all_feeds_for_category
from app.models.topic import Category
from app.services.automation.image_extractor import OriginalImageExtractor
from app.services.feed_health_service import FeedHealthService, SourceListType
from app.services.summarization.summary_flash_service import strip_html

logger = logging.getLogger(__name__)

_CATEGORIES = (Category.FASHION, Category.FOOD, Category.TREND)


def _entry_snippet(entry: Dict[str, Any]) -> str:
    if entry.get("content"):
        val = entry["content"]
        raw = val[0].get("value", "") if isinstance(val, list) else str(val)
    else:
        raw = entry.get("summary", "") or ""
    return strip_html(raw)


async def _feed_allowed(health: FeedHealthService, feed_url: str) -> bool:
    if await health.should_skip_feed(feed_url):
        return False
    list_type = await health.get_source_list_type(feed_url)
    if list_type == SourceListType.BLACKLIST:
        return False
    return list_type == SourceListType.WHITELIST or list_type == SourceListType.NORMAL


async def collect_rss_candidates(batch_size: int) -> List[Dict[str, Any]]:
    health = FeedHealthService()
    extractor = OriginalImageExtractor()
    candidates: List[Dict[str, Any]] = []
    feeds: List[Tuple[Category, str, str, float]] = []
    for cat in _CATEGORIES:
        for name, url, weight in get_all_feeds_for_category(cat):
            feeds.append((cat, name, url, weight))

    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        for category, source_name, feed_url, _ in feeds:
            if len(candidates) >= batch_size:
                break
            try:
                if not await _feed_allowed(health, feed_url):
                    continue
                resp = await client.get(feed_url)
                resp.raise_for_status()
                parsed = feedparser.parse(resp.text)
            except Exception as e:
                logger.warning("public_feed RSS 失敗 %s: %s", source_name, e)
                continue
            for entry in parsed.entries[:5]:
                if len(candidates) >= batch_size:
                    break
                title = (entry.get("title") or "").strip()
                link = (entry.get("link") or "").strip()
                if not title or not link:
                    continue
                previews = extractor.extract_from_entry(entry, source_name)
                candidates.append({
                    "title": title,
                    "link": link,
                    "source_name": source_name,
                    "feed_url": feed_url,
                    "category": category,
                    "snippet": _entry_snippet(entry),
                    "preview_images": previews[:3],
                })
    logger.info("public_feed RSS 候選: %d", len(candidates))
    return candidates

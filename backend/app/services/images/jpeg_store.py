"""Store compressed source JPEG beside the URL row. MD-M2 ≤150."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from bson.binary import Binary

from app.database import get_database

logger = logging.getLogger(__name__)

COLLECTION = "image_jpegs"
MAX_STORED = 200 * 1024


def http_image_url(value: Any) -> str:
    """RSS image fields are either a URL string or {url: ...}."""
    if isinstance(value, dict):
        value = value.get("url") or ""
    url = str(value or "").strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return ""


def split_source_image_id(image_id: str) -> Optional[Tuple[str, int]]:
    """`{topic_id}_source_{idx}` → topic id and index."""
    marker = "_source_"
    if marker not in (image_id or ""):
        return None
    topic_id, _, idx = image_id.rpartition(marker)
    if not topic_id or not idx.isdigit():
        return None
    return topic_id, int(idx)


def url_from_topic_sources(topic: Dict[str, Any], index: int) -> str:
    urls = []
    for source in topic.get("sources") or []:
        for item in source.get("images") or []:
            if isinstance(item, str) and item.strip():
                urls.append(item.strip())
            elif isinstance(item, dict) and item.get("url"):
                urls.append(str(item["url"]).strip())
    if index < 0 or index >= len(urls):
        return ""
    return urls[index]


async def load_stored_jpeg(image_id: str) -> Optional[bytes]:
    if not image_id:
        return None
    db = await get_database()
    doc = await db[COLLECTION].find_one({"id": image_id}, {"jpeg": 1})
    raw = (doc or {}).get("jpeg")
    if not raw:
        return None
    return bytes(raw)


async def save_stored_jpeg(image_id: str, data: bytes) -> None:
    if not image_id or not data or len(data) > MAX_STORED:
        return
    db = await get_database()
    await db[COLLECTION].update_one(
        {"id": image_id},
        {"$set": {"id": image_id, "jpeg": Binary(data), "bytes": len(data)}},
        upsert=True,
    )


async def persist_source_jpeg(image_id: str, url: str) -> bool:
    """Compress a remote source photo once and keep the JPEG. Failures stay URL-only."""
    url = http_image_url(url)
    if not image_id or not url:
        return False
    try:
        if await load_stored_jpeg(image_id):
            return True
        from app.services.images.jpeg_compress import fetch_and_compress

        data = await fetch_and_compress(url, tag="TOPIC_IMAGE_STORE")
        await save_stored_jpeg(image_id, data)
        return True
    except Exception as e:
        logger.warning("source jpeg store skipped id=%s: %s", image_id, e)
        return False


async def persist_topic_source_jpegs(topic_id: str, urls: list, limit: int = 4) -> int:
    """Store up to `limit` source photos for one topic. Ids match `{topic_id}_source_{idx}`."""
    kept = 0
    if not topic_id:
        return 0
    for idx, item in enumerate(list(urls or [])[:limit]):
        if await persist_source_jpeg(f"{topic_id}_source_{idx}", http_image_url(item)):
            kept += 1
    return kept

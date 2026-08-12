"""
DuckDuckGo 圖片服務（無需 API Key）
使用 ddgs 套件搜尋圖片（duckduckgo-search 後繼專案）。
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from app.models.image import ImageSource
from app.services.images.base import ImageServiceBase

logger = logging.getLogger(__name__)


class DuckDuckGoService(ImageServiceBase):
    """DuckDuckGo 圖片服務（無需 API Key）"""

    def __init__(self) -> None:
        logger.info("初始化 DuckDuckGo 圖片服務（無需 API Key）")

    async def search_images(
        self,
        keywords: str,
        page: int = 1,
        limit: int = 20,
        trace_id: str = "",
    ) -> List[Dict[str, Any]]:
        limit = min(max(limit, 1), 50)
        tag = f"[{trace_id}] " if trace_id else ""
        try:
            images = await asyncio.to_thread(self._search_sync, keywords, page, limit)
            logger.info(f"{tag}✅ DuckDuckGo 搜尋成功，找到 {len(images)} 張圖片")
            return images
        except Exception as e:
            logger.error(f"{tag}DuckDuckGo 搜尋失敗: {e}")
            raise

    def _search_sync(self, keywords: str, page: int, limit: int) -> List[Dict[str, Any]]:
        from ddgs import DDGS

        offset = max(0, (page - 1) * limit)
        fetch = min(offset + limit, 100)
        raw = list(DDGS().images(keywords, max_results=fetch))
        sliced = raw[offset : offset + limit]
        return [self._normalize(item, keywords) for item in sliced if item.get("image")]

    def _normalize(self, item: Dict[str, Any], keywords: str) -> Dict[str, Any]:
        url = item.get("image") or item.get("url") or ""
        title = item.get("title") or keywords
        return {
            "id": f"ddg_{abs(hash(url)) % 10000000}",
            "url": url,
            "thumbnail_url": item.get("thumbnail") or url,
            "width": int(item.get("width") or 0),
            "height": int(item.get("height") or 0),
            "title": title,
            "source": ImageSource.DUCKDUCKGO.value,
            "photographer": title.split(" - ")[0] if " - " in title else "",
            "photographer_url": "",
            "license": "Unknown",
            "keywords": [keywords],
        }

    async def get_image_info(self, image_id: str) -> Dict[str, Any]:
        return {
            "id": image_id,
            "url": "",
            "source": ImageSource.DUCKDUCKGO.value,
            "license": "Unknown",
        }

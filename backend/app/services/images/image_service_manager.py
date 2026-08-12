"""
圖片服務管理器
實現備援機制（Google Custom Search → Unsplash → Pexels → Pixabay）
"""
from typing import List, Dict, Any, Optional
import logging
from app.services.images.unsplash import UnsplashService
from app.services.images.pexels import PexelsService
from app.services.images.pixabay import PixabayService
from app.services.images.google_custom_search import GoogleCustomSearchService
from app.services.images.exceptions import ImageSearchError, ErrorCode
from app.models.image import ImageSource

logger = logging.getLogger(__name__)


class ImageServiceManager:
    """圖片服務管理器"""

    def __init__(self):
        self.google_custom_search = GoogleCustomSearchService()
        self.unsplash = UnsplashService()
        self.pexels = PexelsService()
        self.pixabay = PixabayService()

        # Google 為相片搜尋首選；圖庫 API 僅作備援
        self.services = [
            ("Google Custom Search", self.google_custom_search, ImageSource.GOOGLE_CUSTOM_SEARCH),
            ("Unsplash", self.unsplash, ImageSource.UNSPLASH),
            ("Pexels", self.pexels, ImageSource.PEXELS),
            ("Pixabay", self.pixabay, ImageSource.PIXABAY),
        ]

    async def search_images(
        self,
        keywords: str,
        source: Optional[ImageSource] = None,
        page: int = 1,
        limit: int = 20,
        trace_id: str = "",
    ) -> Dict[str, Any]:
        attempts: List[Dict] = []

        if source:
            service_map = {
                ImageSource.GOOGLE_CUSTOM_SEARCH: ("Google Custom Search", self.google_custom_search),
                ImageSource.UNSPLASH: ("Unsplash", self.unsplash),
                ImageSource.PEXELS: ("Pexels", self.pexels),
                ImageSource.PIXABAY: ("Pixabay", self.pixabay),
            }
            service_info = service_map.get(source)
            if not service_info:
                raise ImageSearchError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    source.value if source else "unknown",
                    f"不支援的圖片來源: {source.value if source else 'None'}",
                )
            service_name, service = service_info
            return await self._try_provider(
                service, service_name, source.value, keywords, page, limit, trace_id, attempts
            )

        for service_name, service, service_source in self.services:
            result = await self._try_provider(
                service, service_name, service_source.value, keywords, page, limit, trace_id, attempts
            )
            if result["items"]:
                return result

        logger.warning(
            f"[{trace_id}] 所有圖片來源皆無結果；請確認 Railway 已設定 "
            "GOOGLE_API_KEY 與 GOOGLE_SEARCH_ENGINE_ID"
        )
        return {
            "source": None,
            "items": [],
            "attempts": attempts,
        }

    async def _try_provider(
        self,
        service: Any,
        service_name: str,
        service_source: str,
        keywords: str,
        page: int,
        limit: int,
        trace_id: str,
        attempts: List[Dict],
    ) -> Dict[str, Any]:
        try:
            logger.info(f"[{trace_id}] 嘗試使用 {service_name} 搜尋圖片: keywords='{keywords}'")

            if hasattr(service, "search_images"):
                try:
                    images = await service.search_images(keywords, page, limit, trace_id=trace_id)
                except TypeError:
                    images = await service.search_images(keywords, page, limit)
            else:
                raise ImageSearchError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    service_source,
                    f"服務 {service_name} 不支援 search_images 方法",
                )

            if images:
                logger.info(f"[{trace_id}] ✅ {service_name} 搜尋成功: 找到 {len(images)} 張圖片")
                attempts.append({
                    "source": service_source,
                    "status": "success",
                    "count": len(images),
                })
                return {"source": service_source, "items": images, "attempts": attempts}

            logger.info(f"[{trace_id}] {service_name} 搜尋無結果")
            attempts.append({"source": service_source, "status": "no_results", "count": 0})
            return {"source": None, "items": [], "attempts": attempts}

        except ImageSearchError as e:
            logger.warning(f"[{trace_id}] {service_name} 搜尋失敗: {e.code} - {e.message}")
            attempts.append({
                "source": service_source,
                "status": "error",
                "code": e.code,
                "message": e.message,
                "details": e.details,
            })
            return {"source": None, "items": [], "attempts": attempts}
        except ValueError as e:
            logger.warning(f"[{trace_id}] {service_name} API Key 未設定，跳過")
            attempts.append({
                "source": service_source,
                "status": "unavailable",
                "message": "API Key 未設定",
            })
            return {"source": None, "items": [], "attempts": attempts}
        except Exception as e:
            logger.exception(f"[{trace_id}] {service_name} 發生未處理異常")
            attempts.append({
                "source": service_source,
                "status": "exception",
                "message": str(e),
                "exception_type": type(e).__name__,
            })
            return {"source": None, "items": [], "attempts": attempts}

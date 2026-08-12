"""
圖片服務管理器
提供統一的圖片搜尋介面（Google Custom Search 優先）
"""
from typing import List, Dict, Any, Optional
from app.services.images.unsplash import UnsplashService
from app.services.images.pexels import PexelsService
from app.services.images.pixabay import PixabayService
from app.services.images.google_custom_search import GoogleCustomSearchService
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """圖片服務管理器"""

    def __init__(self):
        self.google_custom_search = GoogleCustomSearchService()
        self.unsplash = UnsplashService()
        self.pexels = PexelsService()
        self.pixabay = PixabayService()

        self.services = [
            (self.google_custom_search, ImageSource.GOOGLE_CUSTOM_SEARCH),
            (self.unsplash, ImageSource.UNSPLASH),
            (self.pexels, ImageSource.PEXELS),
            (self.pixabay, ImageSource.PIXABAY),
        ]

    async def search_images(
        self,
        keywords: str,
        source: Optional[ImageSource] = None,
        page: int = 1,
        limit: int = 20,
        use_fallback: bool = True,
    ) -> List[Dict[str, Any]]:
        if source:
            service_map = {
                ImageSource.GOOGLE_CUSTOM_SEARCH: self.google_custom_search,
                ImageSource.UNSPLASH: self.unsplash,
                ImageSource.PEXELS: self.pexels,
                ImageSource.PIXABAY: self.pixabay,
            }
            service = service_map.get(source)
            if not service:
                raise ValueError(f"不支援的圖片來源: {source}")
            try:
                return await service.search_images(keywords, page, limit)
            except Exception as e:
                logger.error(f"{source.value} 搜尋失敗: {e}")
                if not use_fallback:
                    raise

        last_error = None
        for service, service_source in self.services:
            try:
                images = await service.search_images(keywords, page, limit)
                logger.info(f"使用 {service_source.value} 成功搜尋圖片")
                return images
            except ValueError as e:
                logger.warning(f"{service_source.value} API Key 未設定，跳過")
                continue
            except Exception as e:
                logger.warning(f"{service_source.value} 搜尋失敗: {e}")
                last_error = e
                continue

        if last_error:
            raise last_error
        raise ValueError(
            "圖片搜尋失敗：請設定 GOOGLE_API_KEY 與 GOOGLE_SEARCH_ENGINE_ID"
        )

    async def get_image_info(
        self,
        image_id: str,
        source: Optional[ImageSource] = None,
    ) -> Optional[Dict[str, Any]]:
        if not source:
            if image_id.startswith("google_"):
                source = ImageSource.GOOGLE_CUSTOM_SEARCH
            elif image_id.startswith("pexels_"):
                source = ImageSource.PEXELS
            elif image_id.startswith("pixabay_"):
                source = ImageSource.PIXABAY
            else:
                source = ImageSource.UNSPLASH

        service_map = {
            ImageSource.GOOGLE_CUSTOM_SEARCH: self.google_custom_search,
            ImageSource.UNSPLASH: self.unsplash,
            ImageSource.PEXELS: self.pexels,
            ImageSource.PIXABAY: self.pixabay,
        }

        service = service_map.get(source)
        if not service:
            raise ValueError(f"不支援的圖片來源: {source}")

        try:
            return await service.get_image_info(image_id)
        except Exception as e:
            logger.error(f"取得圖片詳情失敗: {e}")
            raise

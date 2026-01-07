"""
圖片服務管理器
實現備援機制（Unsplash → Pexels → Pixabay）
"""
from typing import List, Dict, Any, Optional
import logging
from app.services.images.unsplash import UnsplashService
from app.services.images.pexels import PexelsService
from app.services.images.pixabay import PixabayService
from app.services.images.duckduckgo import DuckDuckGoService
from app.services.images.google_custom_search import GoogleCustomSearchService
from app.models.image import ImageSource

logger = logging.getLogger(__name__)


class ImageServiceManager:
    """圖片服務管理器"""
    
    def __init__(self):
        self.unsplash = UnsplashService()
        self.pexels = PexelsService()
        self.pixabay = PixabayService()
        self.google_custom_search = GoogleCustomSearchService()  # Google Custom Search（需要 API Key）
        self.duckduckgo = DuckDuckGoService()  # 無需 API Key 的備援服務
        
        # 服務優先順序
        # 注意：Google Custom Search 放在 API 服務之後，DuckDuckGo 不放在這裡，作為最後備援
        self.services = [
            ("Unsplash", self.unsplash, ImageSource.UNSPLASH),
            ("Pexels", self.pexels, ImageSource.PEXELS),
            ("Pixabay", self.pixabay, ImageSource.PIXABAY),
            ("Google Custom Search", self.google_custom_search, ImageSource.GOOGLE_CUSTOM_SEARCH),  # Google（需要 API Key）
        ]
    
    async def search_images(
        self,
        keywords: str,
        source: Optional[ImageSource] = None,
        page: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片（帶備援機制）
        
        Args:
            keywords: 搜尋關鍵字
            source: 指定來源（如果為 None，則按優先順序嘗試）
            page: 頁碼
            limit: 每頁數量
            
        Returns:
            圖片列表
        """
        # 如果指定了來源，只使用該來源
        if source:
            service_map = {
                ImageSource.UNSPLASH: self.unsplash,
                ImageSource.PEXELS: self.pexels,
                ImageSource.PIXABAY: self.pixabay,
                ImageSource.GOOGLE_CUSTOM_SEARCH: self.google_custom_search,
                ImageSource.DUCKDUCKGO: self.duckduckgo,
            }
            
            service = service_map.get(source)
            if not service:
                raise ValueError(f"不支援的圖片來源: {source}")
            
            try:
                return await service.search_images(keywords, page, limit)
            except Exception as e:
                logger.error(f"{source.value} 搜尋失敗: {e}")
                raise
        
        # 否則按優先順序嘗試
        last_error = None
        for service_name, service, service_source in self.services:
            try:
                logger.info(f"嘗試使用 {service_name} 搜尋圖片...")
                images = await service.search_images(keywords, page, limit)
                logger.info(f"✅ {service_name} 搜尋成功，找到 {len(images)} 張圖片")
                return images
            except ValueError as e:
                # API Key 未設定，跳過
                logger.warning(f"{service_name} API Key 未設定，跳過")
                continue
            except Exception as e:
                logger.warning(f"{service_name} 搜尋失敗: {e}，嘗試下一個服務...")
                last_error = e
                continue
        
        # 所有 API 服務都失敗，嘗試使用 DuckDuckGo（不需要 API Key）
        logger.info("所有 API 服務都失敗或未設定 API Key，嘗試使用 DuckDuckGo（不需要 API Key）...")
        try:
            images = await self.duckduckgo.search_images(keywords, page, limit)
            if images and len(images) > 0:
                logger.info(f"✅ DuckDuckGo 搜尋成功，找到 {len(images)} 張圖片")
                return images
            else:
                logger.warning("DuckDuckGo 搜尋返回空結果")
                return []  # 返回空列表而不是拋出異常
        except Exception as e:
            logger.error(f"DuckDuckGo 搜尋也失敗: {e}", exc_info=True)
            # 即使 DuckDuckGo 也失敗，返回空列表而不是拋出異常
            # 這樣前端可以正常顯示，只是沒有圖片
            logger.warning("所有圖片服務都失敗，返回空列表")
            return []

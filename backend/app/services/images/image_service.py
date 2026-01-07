"""
圖片服務管理器
提供統一的圖片搜尋介面，支援多個來源和備援機制
"""
from typing import List, Dict, Any, Optional
from app.services.images.unsplash import UnsplashService
from app.services.images.pexels import PexelsService
from app.services.images.pixabay import PixabayService
from app.services.images.duckduckgo import DuckDuckGoService
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """圖片服務管理器"""
    
    def __init__(self):
        self.unsplash = UnsplashService()
        self.pexels = PexelsService()
        self.pixabay = PixabayService()
        self.duckduckgo = DuckDuckGoService()  # 無需 API Key 的備援服務
        
        # 服務優先順序
        self.services = [
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
        use_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片（支援備援機制）
        
        Args:
            keywords: 搜尋關鍵字
            source: 指定來源（如果為 None，按優先順序嘗試）
            page: 頁碼
            limit: 每頁數量
            use_fallback: 是否使用備援服務
            
        Returns:
            圖片列表
        """
        if source:
            # 使用指定來源
            service_map = {
                ImageSource.UNSPLASH: self.unsplash,
                ImageSource.PEXELS: self.pexels,
                ImageSource.PIXABAY: self.pixabay,
                ImageSource.DUCKDUCKGO: self.duckduckgo,
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
                # 繼續嘗試備援服務
        
        # 按優先順序嘗試各個服務
        last_error = None
        for service, service_source in self.services:
            try:
                images = await service.search_images(keywords, page, limit)
                logger.info(f"使用 {service_source.value} 成功搜尋圖片")
                return images
            except ValueError as e:
                # API Key 未設定，跳過此服務
                logger.warning(f"{service_source.value} API Key 未設定，跳過")
                continue
            except Exception as e:
                logger.warning(f"{service_source.value} 搜尋失敗: {e}")
                last_error = e
                continue
        
        # 所有 API 服務都失敗，嘗試使用 DuckDuckGo（不需要 API Key）
        if use_fallback:
            logger.info("所有 API 服務都失敗或未設定 API Key，嘗試使用 DuckDuckGo（不需要 API Key）...")
            try:
                images = await self.duckduckgo.search_images(keywords, page, limit)
                logger.info(f"✅ DuckDuckGo 搜尋成功，找到 {len(images)} 張圖片")
                return images
            except Exception as e:
                logger.error(f"DuckDuckGo 搜尋也失敗: {e}")
                if last_error:
                    raise last_error
                raise ValueError("所有圖片服務都失敗，包括不需要 API Key 的 DuckDuckGo")
        
        # 如果 use_fallback=False，則拋出錯誤
        if last_error:
            raise last_error
        raise ValueError("沒有可用的圖片服務（所有 API Key 都未設定）")
    
    async def get_image_info(
        self,
        image_id: str,
        source: Optional[ImageSource] = None
    ) -> Optional[Dict[str, Any]]:
        """
        取得圖片詳情
        
        Args:
            image_id: 圖片 ID
            source: 圖片來源（如果為 None，根據 ID 推斷）
            
        Returns:
            圖片資訊
        """
        # 根據 ID 推斷來源
        if not source:
            if image_id.startswith("pexels_"):
                source = ImageSource.PEXELS
            elif image_id.startswith("pixabay_"):
                source = ImageSource.PIXABAY
            else:
                source = ImageSource.UNSPLASH
        
        service_map = {
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

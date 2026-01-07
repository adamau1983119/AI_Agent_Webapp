"""
圖片服務管理器
實現備援機制（Unsplash → Pexels → Pixabay → Google Custom Search → DuckDuckGo）
"""
from typing import List, Dict, Any, Optional
import logging
from app.services.images.unsplash import UnsplashService
from app.services.images.pexels import PexelsService
from app.services.images.pixabay import PixabayService
from app.services.images.duckduckgo import DuckDuckGoService
from app.services.images.google_custom_search import GoogleCustomSearchService
from app.services.images.exceptions import ImageSearchError, ErrorCode
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
        limit: int = 20,
        trace_id: str = ""
    ) -> Dict[str, Any]:
        """
        搜尋圖片（帶備援機制）
        
        Args:
            keywords: 搜尋關鍵字
            source: 指定來源（如果為 None，則按優先順序嘗試）
            page: 頁碼
            limit: 每頁數量
            trace_id: 追蹤 ID
            
        Returns:
            包含 source、items 和 attempts 的字典
        """
        attempts = []
        
        # 如果指定了來源，只使用該來源
        if source:
            service_map = {
                ImageSource.UNSPLASH: ("Unsplash", self.unsplash),
                ImageSource.PEXELS: ("Pexels", self.pexels),
                ImageSource.PIXABAY: ("Pixabay", self.pixabay),
                ImageSource.GOOGLE_CUSTOM_SEARCH: ("Google Custom Search", self.google_custom_search),
                ImageSource.DUCKDUCKGO: ("DuckDuckGo", self.duckduckgo),
            }
            
            service_info = service_map.get(source)
            if not service_info:
                raise ImageSearchError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    source.value if source else "unknown",
                    f"不支援的圖片來源: {source.value if source else 'None'}"
                )
            
            service_name, service = service_info
            return await self._try_provider(service, service_name, source.value, keywords, page, limit, trace_id, attempts)
        
        # 否則按優先順序嘗試所有服務
        for service_name, service, service_source in self.services:
            result = await self._try_provider(service, service_name, service_source.value, keywords, page, limit, trace_id, attempts)
            if result["items"]:
                return result
        
        # 所有 API 服務都失敗，嘗試使用 DuckDuckGo（不需要 API Key）
        logger.info(f"[{trace_id}] 所有 API 服務都失敗或未設定 API Key，嘗試使用 DuckDuckGo（不需要 API Key）...")
        result = await self._try_provider(
            self.duckduckgo,
            "DuckDuckGo",
            ImageSource.DUCKDUCKGO.value,
            keywords,
            page,
            limit,
            trace_id,
            attempts
        )
        
        # 即使 DuckDuckGo 也失敗，返回包含 attempts 的結果
        return result
    
    async def _try_provider(
        self,
        service: Any,
        service_name: str,
        service_source: str,
        keywords: str,
        page: int,
        limit: int,
        trace_id: str,
        attempts: List[Dict]
    ) -> Dict[str, Any]:
        """嘗試使用單個服務提供者"""
        try:
            logger.info(f"[{trace_id}] 嘗試使用 {service_name} 搜尋圖片: keywords='{keywords}'")
            
            # 檢查服務是否有 search_images 方法且支援 trace_id
            if hasattr(service, 'search_images'):
                # 嘗試傳遞 trace_id（如果服務支援）
                try:
                    images = await service.search_images(keywords, page, limit, trace_id=trace_id)
                except TypeError:
                    # 如果服務不支援 trace_id 參數，使用舊的方式
                    images = await service.search_images(keywords, page, limit)
            else:
                raise ImageSearchError(
                    ErrorCode.SOURCE_UNAVAILABLE,
                    service_source,
                    f"服務 {service_name} 不支援 search_images 方法"
                )
            
            if images and len(images) > 0:
                logger.info(f"[{trace_id}] ✅ {service_name} 搜尋成功: 找到 {len(images)} 張圖片")
                attempts.append({
                    "source": service_source,
                    "status": "success",
                    "count": len(images)
                })
                return {
                    "source": service_source,
                    "items": images,
                    "attempts": attempts
                }
            else:
                logger.info(f"[{trace_id}] {service_name} 搜尋無結果")
                attempts.append({
                    "source": service_source,
                    "status": "no_results",
                    "count": 0
                })
                return {
                    "source": None,
                    "items": [],
                    "attempts": attempts
                }
                
        except ImageSearchError as e:
            logger.warning(f"[{trace_id}] {service_name} 搜尋失敗: {e.code} - {e.message}")
            attempts.append({
                "source": service_source,
                "status": "error",
                "code": e.code,
                "message": e.message,
                "details": e.details
            })
            return {
                "source": None,
                "items": [],
                "attempts": attempts
            }
        except ValueError as e:
            # API Key 未設定
            logger.warning(f"[{trace_id}] {service_name} API Key 未設定，跳過")
            attempts.append({
                "source": service_source,
                "status": "unavailable",
                "message": "API Key 未設定"
            })
            return {
                "source": None,
                "items": [],
                "attempts": attempts
            }
        except Exception as e:
            logger.exception(f"[{trace_id}] {service_name} 發生未處理異常")
            attempts.append({
                "source": service_source,
                "status": "exception",
                "message": str(e),
                "exception_type": type(e).__name__
            })
            return {
                "source": None,
                "items": [],
                "attempts": attempts
            }

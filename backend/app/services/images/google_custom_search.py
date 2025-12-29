"""
Google Custom Search 圖片服務（需要 API Key）
使用 Google Custom Search API 搜尋圖片
"""
import httpx
from typing import List, Dict, Any
from app.services.images.base import ImageServiceBase
from app.config import settings
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class GoogleCustomSearchService(ImageServiceBase):
    """Google Custom Search 圖片服務（需要 API Key）"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.search_engine_id = settings.GOOGLE_SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search API Key 或 Search Engine ID 未設定")
        else:
            logger.info("初始化 Google Custom Search 圖片服務")
    
    async def search_images(
        self,
        keywords: str,
        page: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片（使用 Google Custom Search API）
        
        Args:
            keywords: 搜尋關鍵字
            page: 頁碼（Google 限制每頁最多 10 張）
            limit: 每頁數量（最多 10）
            
        Returns:
            圖片列表
        """
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google Custom Search API Key 或 Search Engine ID 未設定")
        
        limit = min(limit, 10)  # Google 限制每頁最多 10 張
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": keywords,
                "searchType": "image",  # 只搜尋圖片
                "num": limit,
                "start": (page - 1) * limit + 1,  # Google 的 start 從 1 開始
                "safe": "active",  # 安全搜尋
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                items = data.get("items", [])
                
                # 轉換為統一格式
                result = []
                for item in items:
                    result.append({
                        "id": f"google_{item.get('link', '')[:50]}",
                        "url": item.get("link", ""),
                        "thumbnail_url": item.get("image", {}).get("thumbnailLink", item.get("link", "")),
                        "width": item.get("image", {}).get("width", 0),
                        "height": item.get("image", {}).get("height", 0),
                        "title": item.get("title", ""),
                        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
                        "photographer": item.get("displayLink", ""),
                        "photographer_url": item.get("image", {}).get("contextLink", ""),
                        "license": "Unknown",  # Google 不提供授權資訊
                        "keywords": [keywords],
                    })
                
                logger.info(f"✅ Google Custom Search 搜尋成功，找到 {len(result)} 張圖片")
                return result
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.error("Google Custom Search API 配額已用完或 API Key 無效")
            elif e.response.status_code == 429:
                logger.error("Google Custom Search API 請求過於頻繁")
            else:
                logger.error(f"Google Custom Search API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Google Custom Search API 時發生錯誤: {e}")
            raise
    
    async def get_image_info(self, image_id: str) -> Dict[str, Any]:
        """
        根據 ID 獲取圖片詳情
        
        Args:
            image_id: 圖片 ID（格式：google_xxx）
            
        Returns:
            圖片詳情
        """
        # Google Custom Search 不支援根據 ID 獲取圖片
        # 這裡返回一個基本結構
        return {
            "id": image_id,
            "url": "",
            "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
            "license": "Unknown",
        }


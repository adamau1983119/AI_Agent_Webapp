"""
Unsplash 圖片服務
"""
import httpx
from typing import List, Dict, Any, Optional
from app.services.images.base import ImageServiceBase
from app.config import settings
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class UnsplashService(ImageServiceBase):
    """Unsplash 服務"""
    
    def __init__(self):
        self.api_key = settings.UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"
    
    async def search_images(
        self,
        keywords: str,
        page: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片
        
        Args:
            keywords: 搜尋關鍵字
            page: 頁碼
            limit: 每頁數量（最大 30）
            
        Returns:
            圖片列表
        """
        if not self.api_key:
            raise ValueError("Unsplash API Key 未設定")
        
        limit = min(limit, 30)  # Unsplash 限制每頁最多 30 張
        
        headers = {
            "Authorization": f"Client-ID {self.api_key}"
        }
        
        params = {
            "query": keywords,
            "page": page,
            "per_page": limit,
            "orientation": "landscape"  # 橫向圖片
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                
                # 轉換為統一格式
                images = []
                for item in results:
                    images.append({
                        "id": item.get("id"),
                        "url": item["urls"].get("regular") or item["urls"].get("full"),
                        "thumbnail_url": item["urls"].get("thumb") or item["urls"].get("small"),
                        "source": ImageSource.UNSPLASH.value,
                        "photographer": item["user"].get("name", "Unknown"),
                        "photographer_url": item["user"].get("links", {}).get("html", ""),
                        "license": "Unsplash License",
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "description": item.get("description", ""),
                        "keywords": [tag.get("title", "") for tag in item.get("tags", [])]
                    })
                
                return images
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Unsplash API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Unsplash API 時發生錯誤: {e}")
            raise
    
    async def get_image_info(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        取得圖片詳情
        
        Args:
            image_id: 圖片 ID
            
        Returns:
            圖片資訊
        """
        if not self.api_key:
            raise ValueError("Unsplash API Key 未設定")
        
        headers = {
            "Authorization": f"Client-ID {self.api_key}"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/photos/{image_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                item = response.json()
                
                return {
                    "id": item.get("id"),
                    "url": item["urls"].get("regular") or item["urls"].get("full"),
                    "thumbnail_url": item["urls"].get("thumb") or item["urls"].get("small"),
                    "source": ImageSource.UNSPLASH.value,
                    "photographer": item["user"].get("name", "Unknown"),
                    "photographer_url": item["user"].get("links", {}).get("html", ""),
                    "license": "Unsplash License",
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "description": item.get("description", ""),
                    "keywords": [tag.get("title", "") for tag in item.get("tags", [])]
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Unsplash API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Unsplash API 時發生錯誤: {e}")
            raise

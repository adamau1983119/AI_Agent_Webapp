"""
Pixabay 圖片服務（備援）
"""
import httpx
from typing import List, Dict, Any, Optional
from app.services.images.base import ImageServiceBase
from app.config import settings
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class PixabayService(ImageServiceBase):
    """Pixabay 服務"""
    
    def __init__(self):
        self.api_key = settings.PIXABAY_API_KEY
        self.base_url = "https://pixabay.com/api"
    
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
            limit: 每頁數量（最大 200）
            
        Returns:
            圖片列表
        """
        if not self.api_key:
            raise ValueError("Pixabay API Key 未設定")
        
        limit = min(limit, 200)  # Pixabay 限制每頁最多 200 張
        
        params = {
            "key": self.api_key,
            "q": keywords,
            "page": page,
            "per_page": limit,
            "image_type": "photo",
            "orientation": "horizontal",
            "safesearch": "true"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("hits", [])
                
                # 轉換為統一格式
                images = []
                for item in results:
                    images.append({
                        "id": f"pixabay_{item.get('id')}",
                        "url": item.get("largeImageURL") or item.get("webformatURL"),
                        "thumbnail_url": item.get("previewURL") or item.get("webformatURL"),
                        "source": ImageSource.PIXABAY.value,
                        "photographer": item.get("user", "Unknown"),
                        "photographer_url": f"https://pixabay.com/users/{item.get('user', '')}-{item.get('user_id', '')}/",
                        "license": "Pixabay License",
                        "width": item.get("imageWidth"),
                        "height": item.get("imageHeight"),
                        "description": item.get("tags", ""),
                        "keywords": item.get("tags", "").split(", ") if item.get("tags") else []
                    })
                
                return images
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Pixabay API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Pixabay API 時發生錯誤: {e}")
            raise
    
    async def get_image_info(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        取得圖片詳情
        
        Args:
            image_id: 圖片 ID（格式：pixabay_123456）
            
        Returns:
            圖片資訊
        """
        # Pixabay 需要原始 ID
        if image_id.startswith("pixabay_"):
            image_id = image_id.replace("pixabay_", "")
        
        if not self.api_key:
            raise ValueError("Pixabay API Key 未設定")
        
        params = {
            "key": self.api_key,
            "id": image_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                hits = data.get("hits", [])
                
                if not hits:
                    return None
                
                item = hits[0]
                
                return {
                    "id": f"pixabay_{item.get('id')}",
                    "url": item.get("largeImageURL") or item.get("webformatURL"),
                    "thumbnail_url": item.get("previewURL"),
                    "source": ImageSource.PIXABAY.value,
                    "photographer": item.get("user", "Unknown"),
                    "photographer_url": f"https://pixabay.com/users/{item.get('user', '')}-{item.get('user_id', '')}/",
                    "license": "Pixabay License",
                    "width": item.get("imageWidth"),
                    "height": item.get("imageHeight"),
                    "description": item.get("tags", ""),
                    "keywords": item.get("tags", "").split(", ") if item.get("tags") else []
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Pixabay API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Pixabay API 時發生錯誤: {e}")
            raise

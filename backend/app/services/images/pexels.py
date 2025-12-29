"""
Pexels 圖片服務（備援）
"""
import httpx
from typing import List, Dict, Any, Optional
from app.services.images.base import ImageServiceBase
from app.config import settings
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class PexelsService(ImageServiceBase):
    """Pexels 服務"""
    
    def __init__(self):
        self.api_key = settings.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/v1"
    
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
            limit: 每頁數量（最大 80）
            
        Returns:
            圖片列表
        """
        if not self.api_key:
            raise ValueError("Pexels API Key 未設定")
        
        limit = min(limit, 80)  # Pexels 限制每頁最多 80 張
        
        headers = {
            "Authorization": self.api_key
        }
        
        params = {
            "query": keywords,
            "page": page,
            "per_page": limit,
            "orientation": "landscape"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                results = data.get("photos", [])
                
                # 轉換為統一格式
                images = []
                for item in results:
                    images.append({
                        "id": f"pexels_{item.get('id')}",
                        "url": item.get("src", {}).get("large") or item.get("src", {}).get("original"),
                        "thumbnail_url": item.get("src", {}).get("medium") or item.get("src", {}).get("small"),
                        "source": ImageSource.PEXELS.value,
                        "photographer": item.get("photographer", "Unknown"),
                        "photographer_url": item.get("photographer_url", ""),
                        "license": "Pexels License",
                        "width": item.get("width"),
                        "height": item.get("height"),
                        "description": "",
                        "keywords": []
                    })
                
                return images
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Pexels API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Pexels API 時發生錯誤: {e}")
            raise
    
    async def get_image_info(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        取得圖片詳情
        
        Args:
            image_id: 圖片 ID（格式：pexels_123456）
            
        Returns:
            圖片資訊
        """
        # Pexels 需要原始 ID
        if image_id.startswith("pexels_"):
            image_id = image_id.replace("pexels_", "")
        
        if not self.api_key:
            raise ValueError("Pexels API Key 未設定")
        
        headers = {
            "Authorization": self.api_key
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
                    "id": f"pexels_{item.get('id')}",
                    "url": item.get("src", {}).get("large") or item.get("src", {}).get("original"),
                    "thumbnail_url": item.get("src", {}).get("medium"),
                    "source": ImageSource.PEXELS.value,
                    "photographer": item.get("photographer", "Unknown"),
                    "photographer_url": item.get("photographer_url", ""),
                    "license": "Pexels License",
                    "width": item.get("width"),
                    "height": item.get("height"),
                    "description": "",
                    "keywords": []
                }
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error(f"Pexels API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"調用 Pexels API 時發生錯誤: {e}")
            raise

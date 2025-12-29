"""
圖片服務抽象層
定義圖片服務的通用介面
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ImageServiceBase(ABC):
    """圖片服務基礎類別"""
    
    @abstractmethod
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
            limit: 每頁數量
            
        Returns:
            圖片列表
        """
        pass
    
    @abstractmethod
    async def get_image_info(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        取得圖片詳情
        
        Args:
            image_id: 圖片 ID
            
        Returns:
            圖片資訊
        """
        pass

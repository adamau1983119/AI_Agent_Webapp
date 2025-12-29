"""
Image Repository
提供 Image 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class ImageRepository(BaseRepository):
    """Image Repository"""
    
    def __init__(self):
        super().__init__("images")
    
    async def create_image(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立 Image
        
        Args:
            image_data: Image 資料
            
        Returns:
            建立的 Image
        """
        # 確保時間戳記
        image_data.setdefault("fetched_at", datetime.utcnow())
        
        return await self.create(image_data)
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 ID 取得 Image
        
        Args:
            image_id: Image ID
            
        Returns:
            Image 資料
        """
        return await self.find_by_id(image_id)
    
    async def get_images_by_topic_id(
        self,
        topic_id: str,
        sort_by_order: bool = True
    ) -> List[Dict[str, Any]]:
        """
        根據 Topic ID 取得所有 Images
        
        Args:
            topic_id: Topic ID
            sort_by_order: 是否按 order 排序
            
        Returns:
            Images 列表
        """
        filter = {"topic_id": topic_id}
        sort = [("order", 1)] if sort_by_order else None
        
        return await self.find_many(filter, sort=sort, limit=100)
    
    async def update_image(
        self,
        image_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新 Image
        
        Args:
            image_id: Image ID
            update_data: 更新資料
            
        Returns:
            更新後的 Image
        """
        return await self.update_by_id(image_id, {"$set": update_data})
    
    async def delete_image(self, image_id: str) -> bool:
        """
        刪除 Image
        
        Args:
            image_id: Image ID
            
        Returns:
            是否成功
        """
        return await self.delete_by_id(image_id)
    
    async def reorder_images(
        self,
        topic_id: str,
        image_orders: List[Dict[str, int]]
    ) -> bool:
        """
        重新排序 Images
        
        Args:
            topic_id: Topic ID
            image_orders: 圖片排序列表 [{"image_id": "xxx", "order": 1}, ...]
            
        Returns:
            是否成功
        """
        collection = await self._get_collection()
        
        # 批次更新
        operations = []
        for item in image_orders:
            operations.append({
                "updateOne": {
                    "filter": {"id": item["image_id"], "topic_id": topic_id},
                    "update": {"$set": {"order": item["order"], "updated_at": datetime.utcnow()}}
                }
            })
        
        if operations:
            result = await collection.bulk_write(operations)
            return result.modified_count > 0
        
        return False
    
    async def count_by_topic_id(self, topic_id: str) -> int:
        """
        計算 Topic 的圖片數量
        
        Args:
            topic_id: Topic ID
            
        Returns:
            圖片數量
        """
        return await self.count({"topic_id": topic_id})

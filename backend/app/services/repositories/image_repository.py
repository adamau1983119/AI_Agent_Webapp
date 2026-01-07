"""
Image Repository
?ä? Image ??CRUD ?ä?
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
        å»ºç? Image
        
        Args:
            image_data: Image è³‡æ?
            
        Returns:
            å»ºç???Image
        """
        # ç¢ºä??‚é??³è?
        image_data.setdefault("fetched_at", datetime.utcnow())
        
        return await self.create(image_data)
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        ?¹æ? ID ?–å? Image
        
        Args:
            image_id: Image ID
            
        Returns:
            Image è³‡æ?
        """
        return await self.find_by_id(image_id)
    
    async def get_images_by_topic_id(
        self,
        topic_id: str,
        sort_by_order: bool = True
    ) -> List[Dict[str, Any]]:
        """
        ?¹æ? Topic ID ?–å??€??Images
        
        Args:
            topic_id: Topic ID
            sort_by_order: ?¯å¦??order ?’å?
            
        Returns:
            Images ?—è¡¨
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
        ?´æ–° Image
        
        Args:
            image_id: Image ID
            update_data: ?´æ–°è³‡æ?
            
        Returns:
            ?´æ–°å¾Œç? Image
        """
        return await self.update_by_id(image_id, {"$set": update_data})
    
    async def delete_image(self, image_id: str) -> bool:
        """
        ?ªé™¤ Image
        
        Args:
            image_id: Image ID
            
        Returns:
            ?¯å¦?å?
        """
        return await self.delete_by_id(image_id)
    
    async def reorder_images(
        self,
        topic_id: str,
        image_orders: List[Dict[str, int]]
    ) -> bool:
        """
        ?æ–°?’å? Images
        
        Args:
            topic_id: Topic ID
            image_orders: ?–ç??’å??—è¡¨ [{"image_id": "xxx", "order": 1}, ...]
            
        Returns:
            ?¯å¦?å?
        """
        collection = await self._get_collection()
        
        # ?¹æ¬¡?´æ–°
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
        è¨ˆç? Topic ?„å??‡æ•¸??
        
        Args:
            topic_id: Topic ID
            
        Returns:
            ?–ç??¸é?
        """
        return await self.count({"topic_id": topic_id})

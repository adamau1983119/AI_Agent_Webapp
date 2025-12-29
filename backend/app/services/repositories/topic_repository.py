"""
Topic Repository
提供 Topic 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.topic import Category, Status
import logging

logger = logging.getLogger(__name__)


class TopicRepository(BaseRepository):
    """Topic Repository"""
    
    def __init__(self):
        super().__init__("topics")
    
    async def create_topic(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立 Topic
        
        Args:
            topic_data: Topic 資料
            
        Returns:
            建立的 Topic
        """
        # 確保時間戳記
        now = datetime.utcnow()
        topic_data.setdefault("created_at", now)
        topic_data.setdefault("generated_at", now)
        topic_data.setdefault("updated_at", now)
        
        return await self.create(topic_data)
    
    async def get_topic_by_id(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 ID 取得 Topic
        
        Args:
            topic_id: Topic ID
            
        Returns:
            Topic 資料
        """
        return await self.find_by_id(topic_id)
    
    async def list_topics(
        self,
        category: Optional[Category] = None,
        status: Optional[Status] = None,
        date: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        sort: str = "generated_at",
        order: str = "desc"
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        列出 Topics
        
        Args:
            category: 分類篩選
            status: 狀態篩選
            date: 日期篩選（YYYY-MM-DD）
            search: 搜尋關鍵字（搜尋標題和來源）
            page: 頁碼
            limit: 每頁數量
            sort: 排序欄位
            order: 排序順序（asc/desc）
            
        Returns:
            (Topics 列表, 總數量)
        """
        # 建立查詢條件
        filter: Dict[str, Any] = {}
        
        if category:
            filter["category"] = category.value if hasattr(category, 'value') else category
        
        if status:
            filter["status"] = status.value if hasattr(status, 'value') else status
        
        if date:
            # 日期範圍：當天的 00:00:00 到 23:59:59
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = datetime(
                start_date.year,
                start_date.month,
                start_date.day,
                23, 59, 59, 999999
            )
            filter["generated_at"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        # 搜尋功能：搜尋標題和來源
        if search and search.strip():
            search_query = search.strip()
            # 使用 MongoDB 的正則表達式進行不區分大小寫的搜尋
            filter["$or"] = [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"source": {"$regex": search_query, "$options": "i"}},
            ]
        
        # 建立排序條件
        sort_order = -1 if order == "desc" else 1
        sort_list = [(sort, sort_order)]
        
        # 計算跳過數量
        skip = (page - 1) * limit
        
        # 查詢
        topics = await self.find_many(filter, skip=skip, limit=limit, sort=sort_list)
        total = await self.count(filter)
        
        return topics, total
    
    async def update_topic(
        self,
        topic_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新 Topic
        
        Args:
            topic_id: Topic ID
            update_data: 更新資料
            
        Returns:
            更新後的 Topic
        """
        return await self.update_by_id(topic_id, {"$set": update_data})
    
    async def update_topic_status(
        self,
        topic_id: str,
        status: Status
    ) -> Optional[Dict[str, Any]]:
        """
        更新 Topic 狀態
        
        Args:
            topic_id: Topic ID
            status: 新狀態
            
        Returns:
            更新後的 Topic
        """
        status_value = status.value if hasattr(status, 'value') else status
        return await self.update_by_id(
            topic_id,
            {"$set": {"status": status_value}}
        )
    
    async def delete_topic(self, topic_id: str) -> bool:
        """
        刪除 Topic（軟刪除：將狀態設為 deleted）
        
        Args:
            topic_id: Topic ID
            
        Returns:
            是否成功
        """
        result = await self.update_by_id(
            topic_id,
            {"$set": {"status": Status.DELETED.value}}
        )
        return result is not None
    
    async def hard_delete_topic(self, topic_id: str) -> bool:
        """
        硬刪除 Topic（從資料庫中完全刪除）
        
        Args:
            topic_id: Topic ID
            
        Returns:
            是否成功
        """
        return await self.delete_by_id(topic_id)

"""
Interaction Repository
提供 Interaction 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.interaction import InteractionAction
import logging

logger = logging.getLogger(__name__)


class InteractionRepository(BaseRepository):
    """Interaction Repository"""
    
    def __init__(self):
        super().__init__("interactions")
    
    async def create_interaction(
        self,
        user_id: str,
        topic_id: str,
        action: InteractionAction,
        article_id: Optional[str] = None,
        photo_id: Optional[str] = None,
        script_id: Optional[str] = None,
        duration: Optional[int] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        建立互動記錄
        
        Args:
            user_id: 顧客 ID
            topic_id: 主題 ID
            action: 互動類型
            article_id: 文章 ID（可選）
            photo_id: 照片 ID（可選）
            script_id: 劇本 ID（可選）
            duration: 停留時間（秒）
            category: 主題分類
            
        Returns:
            建立的互動記錄
        """
        interaction_data = {
            "id": f"interaction_{datetime.utcnow().timestamp()}_{user_id}",
            "user_id": user_id,
            "topic_id": topic_id,
            "article_id": article_id,
            "photo_id": photo_id,
            "script_id": script_id,
            "action": action.value if hasattr(action, 'value') else action,
            "duration": duration,
            "category": category,
            "created_at": datetime.utcnow()
        }
        
        return await self.create(interaction_data)
    
    async def get_interactions_by_user(
        self,
        user_id: str,
        action: Optional[InteractionAction] = None,
        category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        查詢顧客的互動記錄
        
        Args:
            user_id: 顧客 ID
            action: 互動類型（可選）
            category: 主題分類（可選）
            start_date: 開始日期（可選）
            end_date: 結束日期（可選）
            page: 頁碼
            limit: 每頁數量
            
        Returns:
            (互動記錄列表, 總數)
        """
        query = {"user_id": user_id}
        
        if action:
            query["action"] = action.value if hasattr(action, 'value') else action
        
        if category:
            query["category"] = category
        
        if start_date:
            query["created_at"] = {"$gte": start_date}
        
        if end_date:
            if "created_at" in query:
                query["created_at"]["$lte"] = end_date
            else:
                query["created_at"] = {"$lte": end_date}
        
        skip = (page - 1) * limit
        
        # 查詢總數
        total = await self.collection.count_documents(query)
        
        # 查詢數據
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        interactions = await cursor.to_list(length=limit)
        
        # 移除 MongoDB 的 _id
        for interaction in interactions:
            interaction.pop("_id", None)
        
        return interactions, total
    
    async def get_interaction_stats(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        取得顧客的互動統計數據
        
        Args:
            user_id: 顧客 ID
            
        Returns:
            統計數據
        """
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$action",
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": None,
                "total_likes": {
                    "$sum": {"$cond": [{"$eq": ["$_id", "like"]}, "$count", 0]}
                },
                "total_dislikes": {
                    "$sum": {"$cond": [{"$eq": ["$_id", "dislike"]}, "$count", 0]}
                },
                "total_edits": {
                    "$sum": {"$cond": [{"$eq": ["$_id", "edit"]}, "$count", 0]}
                },
                "total_replaces": {
                    "$sum": {"$cond": [{"$eq": ["$_id", "replace"]}, "$count", 0]}
                },
                "total_views": {
                    "$sum": {"$cond": [{"$eq": ["$_id", "view"]}, "$count", 0]}
                },
                "avg_view_time": {
                    "$avg": {
                        "$cond": [
                            {"$eq": ["$_id", "view"]},
                            "$duration",
                            None
                        ]
                    }
                }
            }},
            {"$project": {
                "_id": 0,
                "total_likes": {"$ifNull": ["$total_likes", 0]},
                "total_dislikes": {"$ifNull": ["$total_dislikes", 0]},
                "total_edits": {"$ifNull": ["$total_edits", 0]},
                "total_replaces": {"$ifNull": ["$total_replaces", 0]},
                "total_views": {"$ifNull": ["$total_views", 0]},
                "avg_view_time": {"$ifNull": ["$avg_view_time", 0]}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        
        if result:
            stats = result[0]
        else:
            stats = {
                "total_likes": 0,
                "total_dislikes": 0,
                "total_edits": 0,
                "total_replaces": 0,
                "total_views": 0,
                "avg_view_time": 0
            }
        
        # 計算分類分佈
        category_pipeline = [
            {"$match": {"user_id": user_id, "category": {"$exists": True}}},
            {"$group": {
                "_id": "$category",
                "likes": {
                    "$sum": {"$cond": [{"$eq": ["$action", "like"]}, 1, 0]}
                },
                "dislikes": {
                    "$sum": {"$cond": [{"$eq": ["$action", "dislike"]}, 1, 0]}
                }
            }}
        ]
        
        category_result = await self.collection.aggregate(category_pipeline).to_list(length=None)
        category_distribution = {
            cat["_id"]: {
                "likes": cat.get("likes", 0),
                "dislikes": cat.get("dislikes", 0)
            }
            for cat in category_result
        }
        
        stats["category_distribution"] = category_distribution
        
        return stats


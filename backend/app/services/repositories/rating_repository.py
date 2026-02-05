"""
Rating Repository
Phase 4: AI 個人化
提供 Rating 的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.rating import RatingValue, RatingReason
import logging
import secrets

logger = logging.getLogger(__name__)


class RatingRepository(BaseRepository):
    """Rating Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("ratings", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            await collection.create_index("user_id")
            await collection.create_index("content_id")
            await collection.create_index("topic_id")
            await collection.create_index([("user_id", 1), ("content_id", 1)], unique=True)
            await collection.create_index("created_at")
            await collection.create_index("value")
            
            self._indexes_created = True
            logger.info("Rating 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def create_rating(
        self,
        user_id: str,
        rating_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        建立評分
        
        Args:
            user_id: 用戶 ID
            rating_data: 評分資料
            
        Returns:
            建立的評分
        """
        await self.ensure_indexes()
        
        now = datetime.utcnow()
        rating_id = f"rating_{secrets.token_urlsafe(12)}"
        
        document = {
            "id": rating_id,
            "user_id": user_id,
            **rating_data,
            "created_at": now,
        }
        
        return await self.create(document)
    
    async def get_user_rating_for_content(
        self,
        user_id: str,
        content_id: str
    ) -> Optional[Dict[str, Any]]:
        """取得用戶對特定內容的評分"""
        await self.ensure_indexes()
        return await self.find_one({
            "user_id": user_id,
            "content_id": content_id
        })
    
    async def update_rating(
        self,
        user_id: str,
        content_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新評分"""
        collection = await self._get_collection()
        return await collection.find_one_and_update(
            {"user_id": user_id, "content_id": content_id},
            {"$set": update_data},
            return_document=True
        )
    
    async def get_user_ratings(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """取得用戶的評分歷史"""
        await self.ensure_indexes()
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit
        )
    
    async def count_user_ratings(self, user_id: str) -> int:
        """計算用戶的評分數量"""
        return await self.count({"user_id": user_id})
    
    async def get_user_rating_stats(self, user_id: str) -> Dict[str, Any]:
        """取得用戶的評分統計"""
        await self.ensure_indexes()
        collection = await self._get_collection()
        
        # 基本統計
        total = await self.count({"user_id": user_id})
        positive = await self.count({"user_id": user_id, "value": RatingValue.LIKE.value})
        negative = await self.count({"user_id": user_id, "value": RatingValue.DISLIKE.value})
        
        positive_ratio = positive / total if total > 0 else 0
        
        # 按原因統計
        reason_pipeline = [
            {"$match": {"user_id": user_id}},
            {"$unwind": "$reasons"},
            {"$group": {
                "_id": {"value": "$value", "reason": "$reasons"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        like_reasons = []
        dislike_reasons = []
        
        async for doc in collection.aggregate(reason_pipeline):
            item = {"reason": doc["_id"]["reason"], "count": doc["count"]}
            if doc["_id"]["value"] == RatingValue.LIKE.value:
                like_reasons.append(item)
            else:
                dislike_reasons.append(item)
        
        # 按格式統計
        format_pipeline = [
            {"$match": {"user_id": user_id, "content_format": {"$ne": None}}},
            {"$group": {
                "_id": {"format": "$content_format", "value": "$value"},
                "count": {"$sum": 1}
            }}
        ]
        
        ratings_by_format = {}
        async for doc in collection.aggregate(format_pipeline):
            fmt = doc["_id"]["format"]
            if fmt not in ratings_by_format:
                ratings_by_format[fmt] = {"like": 0, "dislike": 0}
            if doc["_id"]["value"] == RatingValue.LIKE.value:
                ratings_by_format[fmt]["like"] = doc["count"]
            else:
                ratings_by_format[fmt]["dislike"] = doc["count"]
        
        # 按類別統計
        category_pipeline = [
            {"$match": {"user_id": user_id, "topic_category": {"$ne": None}}},
            {"$group": {
                "_id": {"category": "$topic_category", "value": "$value"},
                "count": {"$sum": 1}
            }}
        ]
        
        ratings_by_category = {}
        async for doc in collection.aggregate(category_pipeline):
            cat = doc["_id"]["category"]
            if cat not in ratings_by_category:
                ratings_by_category[cat] = {"like": 0, "dislike": 0}
            if doc["_id"]["value"] == RatingValue.LIKE.value:
                ratings_by_category[cat]["like"] = doc["count"]
            else:
                ratings_by_category[cat]["dislike"] = doc["count"]
        
        return {
            "total_ratings": total,
            "positive_ratings": positive,
            "negative_ratings": negative,
            "positive_ratio": round(positive_ratio, 3),
            "top_like_reasons": like_reasons[:5],
            "top_dislike_reasons": dislike_reasons[:5],
            "ratings_by_format": ratings_by_format,
            "ratings_by_category": ratings_by_category
        }
    
    async def get_recent_ratings_for_analysis(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """取得最近的評分用於風格分析"""
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", -1)],
            limit=limit
        )
    
    async def delete_user_ratings(self, user_id: str) -> int:
        """刪除用戶的所有評分（用於重置）"""
        collection = await self._get_collection()
        result = await collection.delete_many({"user_id": user_id})
        return result.deleted_count


"""
Recommendation Repository
提供 Recommendation 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.topic import Category
import logging

logger = logging.getLogger(__name__)


class RecommendationRepository(BaseRepository):
    """Recommendation Repository"""
    
    def __init__(self):
        super().__init__("recommendations")
    
    async def create_recommendation(
        self,
        user_id: str,
        category: Category,
        keyword: str,
        confidence_score: float,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        建立推薦記錄
        
        Args:
            user_id: 顧客 ID
            category: 主題分類
            keyword: 推薦關鍵字
            confidence_score: 推薦信心分數
            reason: 推薦原因
            
        Returns:
            建立的推薦記錄
        """
        recommendation_data = {
            "id": f"recommendation_{datetime.utcnow().timestamp()}_{user_id}",
            "user_id": user_id,
            "category": category.value if hasattr(category, 'value') else category,
            "keyword": keyword,
            "confidence_score": confidence_score,
            "reason": reason,
            "generated_at": datetime.utcnow(),
            "interaction_result": None,
            "effectiveness": None
        }
        
        return await self.create(recommendation_data)
    
    async def get_recommendations_by_user(
        self,
        user_id: str,
        category: Optional[Category] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        取得顧客的推薦列表
        
        Args:
            user_id: 顧客 ID
            category: 主題分類（可選）
            limit: 返回數量
            
        Returns:
            推薦列表
        """
        query = {"user_id": user_id}
        
        if category:
            query["category"] = category.value if hasattr(category, 'value') else category
        
        cursor = self.collection.find(query).sort("confidence_score", -1).limit(limit)
        recommendations = await cursor.to_list(length=limit)
        
        # 移除 MongoDB 的 _id
        for recommendation in recommendations:
            recommendation.pop("_id", None)
        
        return recommendations
    
    async def get_recommendation_history(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        取得推薦歷史
        
        Args:
            user_id: 顧客 ID
            start_date: 開始日期（可選）
            end_date: 結束日期（可選）
            
        Returns:
            推薦歷史列表
        """
        query = {"user_id": user_id}
        
        if start_date or end_date:
            query["generated_at"] = {}
            if start_date:
                query["generated_at"]["$gte"] = start_date
            if end_date:
                query["generated_at"]["$lte"] = end_date
        
        cursor = self.collection.find(query).sort("generated_at", -1)
        recommendations = await cursor.to_list(length=None)
        
        # 移除 MongoDB 的 _id
        for recommendation in recommendations:
            recommendation.pop("_id", None)
        
        return recommendations
    
    async def update_recommendation_interaction(
        self,
        recommendation_id: str,
        interaction_result: Dict[str, Any],
        effectiveness: str
    ) -> Optional[Dict[str, Any]]:
        """
        更新推薦的互動結果
        
        Args:
            recommendation_id: 推薦 ID
            interaction_result: 互動結果
            effectiveness: 推薦效果
            
        Returns:
            更新後的推薦記錄
        """
        update_data = {
            "interaction_result": interaction_result,
            "effectiveness": effectiveness
        }
        
        return await self.update_by_id(recommendation_id, {"$set": update_data})


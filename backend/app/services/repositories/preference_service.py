"""
Preference Service
處理偏好模型的建立、更新和推薦生成
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math
import logging
from app.services.repositories.user_preferences_repository import UserPreferencesRepository
from app.services.repositories.interaction_repository import InteractionRepository
from app.services.repositories.recommendation_repository import RecommendationRepository
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category

logger = logging.getLogger(__name__)


class PreferenceService:
    """偏好服務"""
    
    def __init__(self):
        self.preferences_repo = UserPreferencesRepository()
        self.interaction_repo = InteractionRepository()
        self.recommendation_repo = RecommendationRepository()
        self.topic_repo = TopicRepository()
    
    async def get_preferences(self, user_id: str = "user_default") -> Dict[str, Any]:
        """
        取得偏好模型
        
        Args:
            user_id: 顧客 ID
            
        Returns:
            偏好模型
        """
        preferences = await self.preferences_repo.get_preferences(user_id)
        
        if not preferences:
            # 建立預設偏好
            preferences = await self.preferences_repo.create_default_preferences(user_id)
        
        return preferences
    
    async def update_preferences_from_interactions(
        self,
        user_id: str = "user_default"
    ) -> Dict[str, Any]:
        """
        根據互動數據更新偏好模型（專家建議：指數衰減權重）
        
        Args:
            user_id: 顧客 ID
            
        Returns:
            更新後的偏好模型
        """
        # 取得所有互動記錄
        interactions, _ = await self.interaction_repo.get_interactions_by_user(
            user_id=user_id,
            limit=1000  # 取得最近1000筆互動
        )
        
        if not interactions:
            return await self.get_preferences(user_id)
        
        # 取得首次互動時間
        first_interaction = min(interactions, key=lambda x: x.get("created_at", datetime.utcnow()))
        first_interaction_date = first_interaction.get("created_at", datetime.utcnow())
        
        # 初始化偏好模型
        category_scores = {
            "fashion": 0.0,
            "food": 0.0,
            "social": 0.0
        }
        
        style_preferences = {
            "article_style": "influencer",
            "photo_style": "mixed",
            "script_style": "fast_paced"
        }
        
        interaction_stats = {
            "total_likes": 0,
            "total_dislikes": 0,
            "total_edits": 0,
            "total_replaces": 0,
            "view_times": []
        }
        
        # 指數衰減參數（專家建議：α=0.7→0.3）
        initial_alpha = 0.7
        steady_alpha = 0.3
        decay_rate = 0.1  # 每天衰減10%
        
        # 分析互動數據
        for interaction in interactions:
            # 計算權重（指數衰減）
            days_since_first = (interaction.get("created_at", datetime.utcnow()) - first_interaction_date).days
            weight = initial_alpha * math.exp(-decay_rate * days_since_first)
            weight = max(weight, steady_alpha)  # 確保不低於穩態權重
            
            action = interaction.get("action")
            category = interaction.get("category", "fashion")
            
            # 更新分類分數
            if action == "like":
                category_scores[category] += 1.0 * weight
                interaction_stats["total_likes"] += 1
            elif action == "dislike":
                category_scores[category] -= 0.5 * weight
                interaction_stats["total_dislikes"] += 1
            elif action == "edit":
                interaction_stats["total_edits"] += 1
                # 分析修改模式，調整風格偏好（簡化版）
                # 實際應該分析修改內容
            elif action == "replace":
                interaction_stats["total_replaces"] += 1
                # 分析替換的照片類型，調整照片風格偏好（簡化版）
            elif action == "view":
                duration = interaction.get("duration", 0)
                if duration:
                    interaction_stats["view_times"].append(duration)
        
        # 計算平均停留時間
        avg_view_time = (
            sum(interaction_stats["view_times"]) / len(interaction_stats["view_times"])
            if interaction_stats["view_times"] else 0.0
        )
        
        # 正規化分類分數（轉換為0-1範圍）
        # 使用 min-max 正規化
        scores_list = list(category_scores.values())
        if scores_list:
            min_score = min(scores_list)
            max_score = max(scores_list)
            score_range = max_score - min_score if max_score != min_score else 1.0
            
            for category in category_scores:
                # Min-Max 正規化到 0-1
                if score_range > 0:
                    normalized = (category_scores[category] - min_score) / score_range
                else:
                    normalized = 0.5  # 如果所有分數相同，設為中間值
                category_scores[category] = max(0.0, min(1.0, normalized))
        
        # 更新偏好模型
        update_data = {
            "category_scores": category_scores,
            "style_preferences": style_preferences,
            "interaction_stats": {
                "total_likes": interaction_stats["total_likes"],
                "total_dislikes": interaction_stats["total_dislikes"],
                "total_edits": interaction_stats["total_edits"],
                "total_replaces": interaction_stats["total_replaces"],
                "avg_view_time": avg_view_time
            },
            "last_interaction": datetime.utcnow()
        }
        
        updated = await self.preferences_repo.update_preferences(user_id, update_data)
        return updated
    
    async def generate_recommendations(
        self,
        user_id: str,
        preferences: Dict[str, Any],
        category: Optional[Category] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        根據偏好模型生成推薦主題
        
        Args:
            user_id: 顧客 ID
            preferences: 偏好模型
            category: 主題分類（可選）
            limit: 返回數量
            
        Returns:
            推薦列表
        """
        recommendations = []
        
        # 取得候選主題（最近7天）
        start_date = datetime.utcnow() - timedelta(days=7)
        
        # 如果指定分類，只查詢該分類
        if category:
            categories = [category]
        else:
            # 根據偏好分數選擇分類
            category_scores = preferences.get("category_scores", {})
            categories = sorted(
                category_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:2]  # 選擇前2個偏好分類
            categories = [Category(cat[0]) for cat in categories]
        
        # 為每個分類生成推薦
        for cat in categories:
            # 取得該分類的主題
            topics, _ = await self.topic_repo.list_topics(
                category=cat,
                limit=20
            )
            
            for topic in topics:
                # 計算推薦分數
                score = await self._calculate_recommendation_score(
                    topic,
                    preferences
                )
                
                if score > 0.5:  # 只推薦分數 > 0.5 的主題
                    recommendation = await self.recommendation_repo.create_recommendation(
                        user_id=user_id,
                        category=cat,
                        keyword=topic.get("title", ""),
                        confidence_score=score,
                        reason=f"顧客偏好{cat.value}主題，推薦分數：{score:.2f}"
                    )
                    recommendations.append(recommendation)
        
        # 按分數排序並返回前N個
        recommendations.sort(key=lambda x: x.get("confidence_score", 0), reverse=True)
        return recommendations[:limit]
    
    async def _calculate_recommendation_score(
        self,
        topic: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> float:
        """
        計算推薦分數（0.0 - 1.0）
        
        Args:
            topic: 主題資料
            preferences: 偏好模型
            
        Returns:
            推薦分數
        """
        score = 0.5  # 基礎分數
        
        # 主題類別匹配（30%）
        category = topic.get("category", "fashion")
        category_scores = preferences.get("category_scores", {})
        category_score = category_scores.get(category, 0.0)
        score += category_score * 0.3
        
        # 來源偏好匹配（20%）
        source_preferences = preferences.get("source_preferences", {})
        topic_source = topic.get("source", "")
        preferred_sources = source_preferences.get(category, [])
        if topic_source in preferred_sources:
            score += 0.2
        
        # 時間衰減（新內容優先）
        generated_at = topic.get("generated_at", datetime.utcnow())
        if isinstance(generated_at, str):
            generated_at = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
        
        days_old = (datetime.utcnow() - generated_at.replace(tzinfo=None)).days
        time_decay = math.exp(-days_old / 7.0)  # 7天衰減
        score *= time_decay
        
        return min(1.0, max(0.0, score))


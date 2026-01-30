"""
StyleProfile Repository
Phase 4: AI 個人化
提供 StyleProfile 的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.style_profile import (
    LearningStage, PresetStyle, TonePreference, ContentPreference, TopicPreference,
    PRESET_STYLE_CONFIGS, get_learning_stage, calculate_confidence_score
)
import logging
import secrets

logger = logging.getLogger(__name__)


class StyleProfileRepository(BaseRepository):
    """StyleProfile Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("style_profiles", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # 用戶 ID 唯一索引
            await collection.create_index("user_id", unique=True)
            await collection.create_index("learning_stage")
            await collection.create_index("last_updated_at")
            
            self._indexes_created = True
            logger.info("StyleProfile 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def get_or_create(self, user_id: str) -> Dict[str, Any]:
        """
        取得或建立用戶的風格檔案
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            風格檔案
        """
        await self.ensure_indexes()
        
        # 嘗試取得現有檔案
        profile = await self.find_one({"user_id": user_id})
        
        if profile:
            return profile
        
        # 建立新檔案
        return await self.create_profile(user_id)
    
    async def create_profile(
        self,
        user_id: str,
        preset_style: PresetStyle = PresetStyle.CASUAL
    ) -> Dict[str, Any]:
        """建立新的風格檔案"""
        await self.ensure_indexes()
        
        now = datetime.utcnow()
        profile_id = f"style_{secrets.token_urlsafe(12)}"
        
        # 取得預設風格配置
        style_config = PRESET_STYLE_CONFIGS.get(preset_style, PRESET_STYLE_CONFIGS[PresetStyle.CASUAL])
        
        document = {
            "id": profile_id,
            "user_id": user_id,
            "preset_style": preset_style.value,
            "tone": style_config["tone"].model_dump(),
            "content": style_config["content"].model_dump(),
            "topics": TopicPreference().model_dump(),
            "learning_stage": LearningStage.COLD_START.value,
            "total_ratings": 0,
            "positive_ratings": 0,
            "negative_ratings": 0,
            "confidence_score": 0.0,
            "last_updated_at": now,
            "created_at": now,
        }
        
        return await self.create(document)
    
    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根據用戶 ID 取得風格檔案"""
        await self.ensure_indexes()
        return await self.find_one({"user_id": user_id})
    
    async def update_profile(
        self,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新風格檔案"""
        update_data["last_updated_at"] = datetime.utcnow()
        
        collection = await self._get_collection()
        result = await collection.find_one_and_update(
            {"user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    async def update_preset_style(
        self,
        user_id: str,
        preset_style: PresetStyle
    ) -> Optional[Dict[str, Any]]:
        """更新預設風格"""
        style_config = PRESET_STYLE_CONFIGS.get(preset_style)
        if not style_config:
            return None
        
        return await self.update_profile(user_id, {
            "preset_style": preset_style.value,
            "tone": style_config["tone"].model_dump(),
            "content": style_config["content"].model_dump(),
        })
    
    async def increment_ratings(
        self,
        user_id: str,
        is_positive: bool
    ) -> Optional[Dict[str, Any]]:
        """增加評分計數並更新學習階段"""
        collection = await self._get_collection()
        
        # 增加評分計數
        inc_field = "positive_ratings" if is_positive else "negative_ratings"
        
        result = await collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$inc": {
                    "total_ratings": 1,
                    inc_field: 1
                },
                "$set": {"last_updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        if result:
            # 更新學習階段和信心分數
            total = result["total_ratings"]
            positive = result["positive_ratings"]
            positive_ratio = positive / total if total > 0 else 0
            
            learning_stage = get_learning_stage(total)
            confidence = calculate_confidence_score(total, positive_ratio)
            
            return await self.update_profile(user_id, {
                "learning_stage": learning_stage.value,
                "confidence_score": confidence
            })
        
        return result
    
    async def update_tone_from_rating(
        self,
        user_id: str,
        rating_reasons: List[str],
        is_positive: bool
    ) -> Optional[Dict[str, Any]]:
        """
        根據評分原因更新語氣偏好
        
        這是風格學習的核心邏輯：
        - 如果用戶喜歡「專業」風格，增加 formal_score
        - 如果用戶不喜歡「太長」，減少 preferred_length
        """
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        
        tone = profile.get("tone", {})
        content = profile.get("content", {})
        
        # 根據原因調整偏好（每次調整 0.05）
        adjustment = 0.05 if is_positive else -0.05
        
        for reason in rating_reasons:
            if reason == "professional":
                tone["formal_score"] = max(0, min(1, tone.get("formal_score", 0.5) + adjustment))
            elif reason == "creative":
                tone["humor_score"] = max(0, min(1, tone.get("humor_score", 0.3) + adjustment))
            elif reason == "engaging":
                tone["emotion_score"] = max(0, min(1, tone.get("emotion_score", 0.5) + adjustment))
            elif reason == "tone_good":
                # 維持當前設定
                pass
            elif reason == "tone_bad":
                # 微調所有語氣分數向中間靠攏
                tone["formal_score"] = 0.9 * tone.get("formal_score", 0.5) + 0.1 * 0.5
            elif reason == "too_long":
                if content.get("preferred_length") == "long":
                    content["preferred_length"] = "medium"
                elif content.get("preferred_length") == "medium":
                    content["preferred_length"] = "short"
            elif reason == "too_short":
                if content.get("preferred_length") == "short":
                    content["preferred_length"] = "medium"
                elif content.get("preferred_length") == "medium":
                    content["preferred_length"] = "long"
        
        return await self.update_profile(user_id, {
            "tone": tone,
            "content": content
        })
    
    async def update_topic_preferences(
        self,
        user_id: str,
        topic_category: str,
        keywords: List[str],
        is_positive: bool
    ) -> Optional[Dict[str, Any]]:
        """更新主題偏好"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        
        topics = profile.get("topics", {})
        liked_topics = topics.get("liked_topics", [])
        disliked_topics = topics.get("disliked_topics", [])
        liked_keywords = topics.get("liked_keywords", [])
        disliked_keywords = topics.get("disliked_keywords", [])
        
        if is_positive:
            # 添加到喜歡列表
            if topic_category and topic_category not in liked_topics:
                liked_topics.append(topic_category)
            if topic_category in disliked_topics:
                disliked_topics.remove(topic_category)
            
            for kw in keywords[:5]:  # 最多添加 5 個
                if kw not in liked_keywords:
                    liked_keywords.append(kw)
                if kw in disliked_keywords:
                    disliked_keywords.remove(kw)
        else:
            # 添加到不喜歡列表
            if topic_category and topic_category not in disliked_topics:
                disliked_topics.append(topic_category)
            if topic_category in liked_topics:
                liked_topics.remove(topic_category)
            
            for kw in keywords[:5]:
                if kw not in disliked_keywords:
                    disliked_keywords.append(kw)
                if kw in liked_keywords:
                    liked_keywords.remove(kw)
        
        # 限制列表長度
        liked_topics = liked_topics[-20:]
        disliked_topics = disliked_topics[-20:]
        liked_keywords = liked_keywords[-50:]
        disliked_keywords = disliked_keywords[-50:]
        
        return await self.update_profile(user_id, {
            "topics": {
                "liked_topics": liked_topics,
                "disliked_topics": disliked_topics,
                "liked_keywords": liked_keywords,
                "disliked_keywords": disliked_keywords
            }
        })
    
    async def reset_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """重置風格檔案（保留預設風格）"""
        profile = await self.get_by_user_id(user_id)
        if not profile:
            return None
        
        preset_style = PresetStyle(profile.get("preset_style", PresetStyle.CASUAL.value))
        style_config = PRESET_STYLE_CONFIGS.get(preset_style, PRESET_STYLE_CONFIGS[PresetStyle.CASUAL])
        
        return await self.update_profile(user_id, {
            "tone": style_config["tone"].model_dump(),
            "content": style_config["content"].model_dump(),
            "topics": TopicPreference().model_dump(),
            "learning_stage": LearningStage.COLD_START.value,
            "total_ratings": 0,
            "positive_ratings": 0,
            "negative_ratings": 0,
            "confidence_score": 0.0,
        })
    
    async def get_stats(self) -> Dict[str, Any]:
        """取得統計資訊"""
        await self.ensure_indexes()
        collection = await self._get_collection()
        
        # 計算各階段數量
        pipeline = [
            {"$group": {
                "_id": "$learning_stage",
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence_score"}
            }}
        ]
        
        stage_stats = {}
        async for doc in collection.aggregate(pipeline):
            stage_stats[doc["_id"]] = {
                "count": doc["count"],
                "avg_confidence": round(doc["avg_confidence"], 3)
            }
        
        total = await self.count({})
        
        return {
            "total_profiles": total,
            "by_learning_stage": stage_stats
        }


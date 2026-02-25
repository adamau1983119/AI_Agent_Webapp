"""
靈感策劃偏好服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. 偏好異常檢測
2. 分級確認策略
3. 偏好管理
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.repositories.base_repository import BaseRepository
from app.database import get_database
import logging

logger = logging.getLogger(__name__)


# 分級確認策略配置
PREFERENCE_CONFIRMATION_LEVELS = {
    "high_frequency": {
        "preferences": ["format", "tone", "language", "region"],
        "strategy": "auto_apply",
        "confirmation_trigger": "anomaly",  # 僅在異常時提示
        "anomaly_threshold": 0.3  # 與歷史偏好差異 > 30% 時提示
    },
    "medium_frequency": {
        "preferences": ["output_length", "detail_depth"],
        "strategy": "silent_learning",
        "confirmation_trigger": "3_uses",  # 使用 3 次後提示確認
        "auto_apply_after": 5  # 5 次使用後自動套用
    },
    "low_frequency": {
        "preferences": ["module_preferences", "special_requirements"],
        "strategy": "always_confirm",
        "confirmation_trigger": "immediate"  # 立即確認
    }
}


class InspirationPreferenceRepository(BaseRepository):
    """靈感策劃偏好 Repository"""
    
    def __init__(self):
        super().__init__("user_inspiration_preferences")
    
    async def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """取得用戶偏好"""
        return await self.find_by_id(user_id)
    
    async def update_preferences(
        self,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新偏好"""
        update_data["updated_at"] = datetime.utcnow()
        return await self.update_by_id(user_id, {"$set": update_data}, upsert=True)
    
    async def create_default_preferences(self, user_id: str) -> Dict[str, Any]:
        """建立預設偏好"""
        default_data = {
            "id": user_id,
            "user_id": user_id,
            "preferences": {
                "default_format": "video_script",
                "default_tone": "casual",
                "preferred_regions": [],
                "preferred_languages": ["zh-TW"]
            },
            "usage_stats": {
                "total_sessions": 0,
                "most_used_format": "video_script",
                "most_used_tone": "casual",
                "last_used_at": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            },
            "status": "active",
            "confirmation_pending": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return await self.create(default_data)


class InspirationPreferenceService:
    """靈感策劃偏好服務"""
    
    def __init__(self):
        self.preference_repo = InspirationPreferenceRepository()
    
    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """取得用戶偏好"""
        preferences = await self.preference_repo.get_preferences(user_id)
        
        if not preferences:
            preferences = await self.preference_repo.create_default_preferences(user_id)
        
        return preferences
    
    def detect_preference_anomaly(
        self,
        user_id: str,
        new_preference: Dict[str, Any],
        preference_type: str
    ) -> bool:
        """
        檢測偏好異常（與歷史偏好差異過大）
        
        Args:
            user_id: 用戶 ID
            new_preference: 新偏好值
            preference_type: 偏好類型（format, tone, language, region 等）
            
        Returns:
            bool: 是否為異常
        """
        # 注意：此方法需要歷史偏好數據，目前為框架實現
        # 實際使用時需要從資料庫取得歷史偏好
        
        # 檢查是否為高頻偏好
        is_high_frequency = any(
            preference_type in level["preferences"]
            for level in PREFERENCE_CONFIRMATION_LEVELS.values()
            if level["strategy"] == "auto_apply"
        )
        
        if not is_high_frequency:
            return False  # 非高頻偏好，不需要異常檢測
        
        # 計算差異度（簡化版，實際需要從資料庫取得歷史數據）
        # similarity = self._calculate_similarity(historical, new_preference)
        
        # 如果相似度 < 70%，視為異常
        # return similarity < 0.7
        
        # 目前返回 False（等待歷史數據實現）
        return False
    
    def _calculate_similarity(
        self,
        historical: Any,
        new_value: Any
    ) -> float:
        """
        計算相似度（0.0 - 1.0）
        
        Args:
            historical: 歷史值
            new_value: 新值
            
        Returns:
            float: 相似度分數
        """
        if historical == new_value:
            return 1.0
        
        # 如果是字串，使用簡單比對
        if isinstance(historical, str) and isinstance(new_value, str):
            if historical == new_value:
                return 1.0
            # 簡單相似度計算（實際可以使用更複雜的算法）
            return 0.5
        
        # 如果是列表，計算交集比例
        if isinstance(historical, list) and isinstance(new_value, list):
            if not historical:
                return 0.0
            intersection = set(historical) & set(new_value)
            return len(intersection) / len(historical)
        
        return 0.0
    
    def get_preference_level(self, preference_type: str) -> str:
        """
        取得偏好類型的分級
        
        Returns:
            str: 'high_frequency' | 'medium_frequency' | 'low_frequency'
        """
        for level, config in PREFERENCE_CONFIRMATION_LEVELS.items():
            if preference_type in config["preferences"]:
                return level
        return "low_frequency"  # 預設為低頻
    
    async def should_confirm_preference(
        self,
        user_id: str,
        preference_type: str,
        new_value: Any,
        usage_count: int = 0
    ) -> Dict[str, Any]:
        """
        判斷是否需要用戶確認偏好
        
        Returns:
            Dict: {
                "should_confirm": bool,
                "level": str,
                "reason": str
            }
        """
        level = self.get_preference_level(preference_type)
        config = PREFERENCE_CONFIRMATION_LEVELS[level]
        
        # 高頻偏好：僅在異常時提示
        if level == "high_frequency":
            is_anomaly = self.detect_preference_anomaly(user_id, new_value, preference_type)
            return {
                "should_confirm": is_anomaly,
                "level": level,
                "reason": "anomaly" if is_anomaly else "auto_apply"
            }
        
        # 中頻偏好：使用 3 次後提示確認
        elif level == "medium_frequency":
            if usage_count >= config["auto_apply_after"]:
                return {
                    "should_confirm": False,
                    "level": level,
                    "reason": "auto_apply_after_threshold"
                }
            elif usage_count >= 3:
                return {
                    "should_confirm": True,
                    "level": level,
                    "reason": "3_uses_threshold"
                }
            else:
                return {
                    "should_confirm": False,
                    "level": level,
                    "reason": "silent_learning"
                }
        
        # 低頻偏好：立即確認
        else:
            return {
                "should_confirm": True,
                "level": level,
                "reason": "immediate"
            }
    
    async def update_preference_usage(
        self,
        user_id: str,
        preference_type: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        更新偏好使用統計
        
        Returns:
            Dict: 更新後的偏好數據
        """
        preferences = await self.get_preferences(user_id)
        
        # 更新使用統計
        usage_stats = preferences.get("usage_stats", {})
        usage_stats["total_sessions"] = usage_stats.get("total_sessions", 0) + 1
        usage_stats["last_used_at"] = datetime.utcnow()
        usage_stats["last_updated"] = datetime.utcnow()
        
        # 更新最常使用的格式/語氣
        if preference_type == "format":
            usage_stats["most_used_format"] = value
        elif preference_type == "tone":
            usage_stats["most_used_tone"] = value
        
        # 更新偏好
        prefs = preferences.get("preferences", {})
        if preference_type in ["format", "tone", "language", "region"]:
            prefs[f"default_{preference_type}"] = value
        
        update_data = {
            "preferences": prefs,
            "usage_stats": usage_stats
        }
        
        return await self.preference_repo.update_preferences(user_id, update_data)


# 建立全域實例
inspiration_preference_service = InspirationPreferenceService()


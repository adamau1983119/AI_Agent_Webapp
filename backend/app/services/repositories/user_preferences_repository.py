"""
UserPreferences Repository
提供 UserPreferences 的 CRUD 操作
"""
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class UserPreferencesRepository(BaseRepository):
    """UserPreferences Repository"""
    
    def __init__(self):
        super().__init__("user_preferences")
    
    async def get_preferences(self, user_id: str = "user_default") -> Optional[Dict[str, Any]]:
        """
        取得使用者偏好
        
        Args:
            user_id: 使用者 ID（預設為 user_default）
            
        Returns:
            使用者偏好資料
        """
        return await self.find_by_id(user_id)
    
    async def update_preferences(
        self,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新使用者偏好
        
        Args:
            user_id: 使用者 ID
            update_data: 更新資料
            
        Returns:
            更新後的偏好資料
        """
        # 添加更新時間
        update_data["updated_at"] = datetime.utcnow()
        
        return await self.update_by_id(user_id, {"$set": update_data}, upsert=True)
    
    async def create_default_preferences(
        self,
        user_id: str = "user_default"
    ) -> Dict[str, Any]:
        """
        建立預設使用者偏好
        
        Args:
            user_id: 使用者 ID
            
        Returns:
            建立的偏好資料
        """
        default_data = {
            "id": user_id,
            "fashion_weight": 0.5,
            "food_weight": 0.3,
            "trend_weight": 0.2,
            "keywords": [],
            "excluded_keywords": [],
            "source_preferences": {
                "fashion": [],
                "food": [],
                "trend": []
            },
            "updated_at": datetime.utcnow()
        }
        
        return await self.create(default_data)

"""
AuditLog Repository
提供 AuditLog 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.audit_log import Action, EntityType
import logging

logger = logging.getLogger(__name__)


class AuditLogRepository(BaseRepository):
    """AuditLog Repository"""
    
    def __init__(self):
        super().__init__("audit_logs")
    
    async def create_log(
        self,
        action: Action,
        entity_type: EntityType,
        topic_id: Optional[str] = None,
        user: str = "system",
        changes: Optional[Dict[str, Any]] = None,
        source: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        建立審計日誌
        
        Args:
            action: 操作類型
            entity_type: 實體類型
            topic_id: Topic ID（可選）
            user: 使用者
            changes: 變更內容
            source: 來源資訊
            
        Returns:
            建立的審計日誌
        """
        log_data = {
            "id": f"audit_{datetime.utcnow().timestamp()}",
            "topic_id": topic_id,
            "action": action.value if hasattr(action, 'value') else action,
            "entity_type": entity_type.value if hasattr(entity_type, 'value') else entity_type,
            "user": user,
            "timestamp": datetime.utcnow(),
            "changes": changes,
            "source": source
        }
        
        return await self.create(log_data)
    
    async def get_logs_by_topic_id(
        self,
        topic_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        根據 Topic ID 取得審計日誌
        
        Args:
            topic_id: Topic ID
            limit: 限制數量
            
        Returns:
            審計日誌列表
        """
        return await self.find_many(
            {"topic_id": topic_id},
            sort=[("timestamp", -1)],
            limit=limit
        )
    
    async def get_logs_by_action(
        self,
        action: Action,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        根據操作類型取得審計日誌
        
        Args:
            action: 操作類型
            limit: 限制數量
            
        Returns:
            審計日誌列表
        """
        action_value = action.value if hasattr(action, 'value') else action
        return await self.find_many(
            {"action": action_value},
            sort=[("timestamp", -1)],
            limit=limit
        )

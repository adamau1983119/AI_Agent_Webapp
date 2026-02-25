"""
靈感策劃對話服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. 對話狀態管理
2. 跨 Session 記憶
3. 過期機制（30 天）
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.services.repositories.base_repository import BaseRepository
import logging
import uuid

logger = logging.getLogger(__name__)


class InspirationConversationRepository(BaseRepository):
    """靈感策劃對話 Repository"""
    
    def __init__(self):
        super().__init__("inspiration_sessions")
    
    async def create_session(
        self,
        user_id: str,
        topic: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """建立新會話"""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
        
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "session_id": session_id,
            "conversation_id": conversation_id,
            "topic": topic,
            "preferences": preferences,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None
        }
        
        return await self.create(session_data)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """取得會話"""
        return await self.find_by_id(session_id)
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """取得用戶的所有會話（按時間倒序）"""
        return await self.find_many(
            filter={"user_id": user_id},
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_type: str = "question"
    ) -> Optional[Dict[str, Any]]:
        """添加訊息到會話"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        message = {
            "role": role,  # 'user' | 'assistant'
            "content": content,
            "type": message_type,  # 'question' | 'answer' | 'content'
            "timestamp": datetime.utcnow()
        }
        
        messages = session.get("messages", [])
        messages.append(message)
        
        update_data = {
            "messages": messages,
            "updated_at": datetime.utcnow()
        }
        
        return await self.update_by_id(session_id, {"$set": update_data})
    
    async def complete_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """標記會話為完成"""
        update_data = {
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        return await self.update_by_id(session_id, {"$set": update_data})
    
    async def cleanup_expired_sessions(self, days: int = 30) -> int:
        """清理過期會話（預設 30 天）"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        collection = await self._get_collection()
        result = await collection.delete_many({
            "created_at": {"$lt": cutoff_date}
        })
        
        return result.deleted_count


class InspirationConversationService:
    """靈感策劃對話服務"""
    
    def __init__(self):
        self.conversation_repo = InspirationConversationRepository()
    
    async def start_conversation(
        self,
        user_id: str,
        topic: str,
        language: str = "zh-TW"
    ) -> Dict[str, Any]:
        """
        開始新對話
        
        Args:
            user_id: 用戶 ID
            topic: 主題
            language: 語言
            
        Returns:
            會話資料（包含 session_id, conversation_id）
        """
        preferences = {
            "language": language,
            "format": None,
            "tone": None,
            "region": None
        }
        
        session = await self.conversation_repo.create_session(
            user_id=user_id,
            topic=topic,
            preferences=preferences
        )
        
        return session
    
    async def get_conversation_context(
        self,
        session_id: str,
        max_messages: int = 20
    ) -> List[Dict[str, Any]]:
        """
        取得對話上下文（用於 AI 生成）
        
        Args:
            session_id: 會話 ID
            max_messages: 最大訊息數
            
        Returns:
            訊息列表
        """
        session = await self.conversation_repo.get_session(session_id)
        if not session:
            return []
        
        messages = session.get("messages", [])
        return messages[-max_messages:]  # 返回最後 N 條訊息
    
    async def add_user_message(
        self,
        session_id: str,
        content: str
    ) -> Optional[Dict[str, Any]]:
        """添加用戶訊息"""
        return await self.conversation_repo.add_message(
            session_id=session_id,
            role="user",
            content=content,
            message_type="answer"
        )
    
    async def add_assistant_message(
        self,
        session_id: str,
        content: str,
        message_type: str = "question"
    ) -> Optional[Dict[str, Any]]:
        """添加助手訊息"""
        return await self.conversation_repo.add_message(
            session_id=session_id,
            role="assistant",
            content=content,
            message_type=message_type
        )
    
    async def get_user_conversation_history(
        self,
        user_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        取得用戶的對話歷史（跨 Session 記憶）
        
        Args:
            user_id: 用戶 ID
            limit: 返回數量
            
        Returns:
            會話列表
        """
        sessions = await self.conversation_repo.get_user_sessions(
            user_id=user_id,
            limit=limit
        )
        
        return sessions
    
    async def complete_conversation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """完成對話"""
        return await self.conversation_repo.complete_session(session_id)
    
    async def cleanup_expired(self, days: int = 30) -> int:
        """清理過期會話"""
        return await self.conversation_repo.cleanup_expired_sessions(days=days)


# 建立全域實例
inspiration_conversation_service = InspirationConversationService()


"""
User Repository
Phase 2: 會員系統
提供 User 的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.user import UserRole, UserStatus, Language
import logging
import secrets

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """User Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("users", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # 創建唯一索引
            await collection.create_index("email", unique=True)
            await collection.create_index("google_id", sparse=True)  # sparse: 只為有值的文檔建立索引
            await collection.create_index("created_at")
            await collection.create_index("status")
            await collection.create_index("role")
            
            self._indexes_created = True
            logger.info("User 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def create_user(
        self,
        user_data: Dict[str, Any],
        password_hash: str
    ) -> Dict[str, Any]:
        """
        建立 User
        
        Args:
            user_data: User 資料（不含密碼）
            password_hash: 密碼雜湊
            
        Returns:
            建立的 User
        """
        await self.ensure_indexes()
        
        now = datetime.utcnow()
        
        # 生成唯一 ID
        user_id = f"user_{secrets.token_urlsafe(16)}"
        
        document = {
            "id": user_id,
            **user_data,
            "password_hash": password_hash,
            "email_verified": False,
            "created_at": now,
            "updated_at": now,
            "status": user_data.get("status", UserStatus.ACTIVE.value),
            "role": user_data.get("role", UserRole.USER.value),
        }
        
        return await self.create(document)
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根據 ID 取得 User"""
        return await self.find_by_id(user_id, id_field="id")
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根據 Email 取得 User"""
        await self.ensure_indexes()
        return await self.find_one({"email": email.lower()})
    
    async def get_user_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """根據 Google ID 取得 User"""
        await self.ensure_indexes()
        return await self.find_one({"google_id": google_id})
    
    async def update_user(
        self,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新 User"""
        update_data["updated_at"] = datetime.utcnow()
        return await self.update_by_id(user_id, {"$set": update_data}, id_field="id")
    
    async def update_password(
        self,
        user_id: str,
        password_hash: str
    ) -> Optional[Dict[str, Any]]:
        """更新密碼"""
        return await self.update_user(user_id, {
            "password_hash": password_hash,
            "updated_at": datetime.utcnow()
        })
    
    async def verify_email(
        self,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """驗證 Email"""
        return await self.update_user(user_id, {
            "email_verified": True,
            "email_verified_at": datetime.utcnow()
        })
    
    async def update_last_login(self, user_id: str) -> Optional[Dict[str, Any]]:
        """更新最後登入時間"""
        return await self.update_user(user_id, {
            "last_login_at": datetime.utcnow()
        })
    
    async def count_users(self, status: Optional[UserStatus] = None) -> int:
        """計算用戶數量"""
        filter_query = {}
        if status:
            filter_query["status"] = status.value
        
        return await self.count(filter_query)
    
    async def count_active_users(self) -> int:
        """計算活躍用戶數量（狀態為 active）"""
        return await self.count_users(UserStatus.ACTIVE)
    
    async def list_users(
        self,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        列出 Users（管理員功能）
        
        Args:
            role: 角色篩選
            status: 狀態篩選
            page: 頁碼
            limit: 每頁數量
            
        Returns:
            (Users 列表, 總數量)
        """
        filter_query = {}
        if role:
            filter_query["role"] = role.value
        if status:
            filter_query["status"] = status.value
        
        skip = (page - 1) * limit
        sort_list = [("created_at", -1)]
        
        users = await self.find_many(filter_query, skip=skip, limit=limit, sort=sort_list)
        total = await self.count(filter_query)
        
        return users, total
    
    async def delete_user(self, user_id: str) -> bool:
        """
        刪除 User（軟刪除）
        
        Args:
            user_id: User ID
            
        Returns:
            是否成功
        """
        result = await self.update_user(user_id, {
            "status": UserStatus.DELETED.value,
            "deleted_at": datetime.utcnow()
        })
        return result is not None


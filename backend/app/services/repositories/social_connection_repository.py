"""
SocialConnection Repository
Phase 5: 分發與整合
提供社交平台連接的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.social_connection import SocialPlatform, ConnectionStatus
import logging
import secrets

logger = logging.getLogger(__name__)


class SocialConnectionRepository(BaseRepository):
    """SocialConnection Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("social_connections", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # 用戶 + 平台唯一索引
            await collection.create_index(
                [("user_id", 1), ("platform", 1)],
                unique=True
            )
            await collection.create_index("user_id")
            await collection.create_index("platform")
            await collection.create_index("status")
            await collection.create_index("token_expires_at")
            
            self._indexes_created = True
            logger.info("SocialConnection 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def create_connection(
        self,
        user_id: str,
        connection_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        建立或更新社交連接
        
        如果已存在相同平台的連接，會更新而不是建立新的
        """
        await self.ensure_indexes()
        
        platform = connection_data.get("platform")
        
        # 檢查是否已存在
        existing = await self.get_user_connection(user_id, platform)
        
        if existing:
            # 更新現有連接
            return await self.update_connection(user_id, platform, {
                **connection_data,
                "status": ConnectionStatus.CONNECTED.value,
                "updated_at": datetime.utcnow()
            })
        
        # 建立新連接
        now = datetime.utcnow()
        connection_id = f"conn_{secrets.token_urlsafe(12)}"
        
        document = {
            "id": connection_id,
            "user_id": user_id,
            **connection_data,
            "platform": platform if isinstance(platform, str) else platform.value,
            "status": ConnectionStatus.CONNECTED.value,
            "last_used_at": None,
            "created_at": now,
            "updated_at": now,
        }
        
        return await self.create(document)
    
    async def get_user_connection(
        self,
        user_id: str,
        platform: SocialPlatform
    ) -> Optional[Dict[str, Any]]:
        """取得用戶的特定平台連接"""
        await self.ensure_indexes()
        platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
        return await self.find_one({
            "user_id": user_id,
            "platform": platform_value
        })
    
    async def get_user_connections(
        self,
        user_id: str,
        include_disconnected: bool = False
    ) -> List[Dict[str, Any]]:
        """取得用戶的所有社交連接"""
        await self.ensure_indexes()
        
        filter_query = {"user_id": user_id}
        if not include_disconnected:
            filter_query["status"] = {"$in": [
                ConnectionStatus.CONNECTED.value,
                ConnectionStatus.EXPIRED.value
            ]}
        
        return await self.find_many(filter_query)
    
    async def update_connection(
        self,
        user_id: str,
        platform: SocialPlatform,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新社交連接"""
        platform_value = platform.value if isinstance(platform, SocialPlatform) else platform
        update_data["updated_at"] = datetime.utcnow()
        
        collection = await self._get_collection()
        return await collection.find_one_and_update(
            {"user_id": user_id, "platform": platform_value},
            {"$set": update_data},
            return_document=True
        )
    
    async def disconnect(
        self,
        user_id: str,
        platform: SocialPlatform
    ) -> bool:
        """斷開社交連接"""
        result = await self.update_connection(user_id, platform, {
            "status": ConnectionStatus.DISCONNECTED.value,
            "access_token": None,
            "refresh_token": None,
        })
        return result is not None
    
    async def update_last_used(
        self,
        user_id: str,
        platform: SocialPlatform
    ) -> Optional[Dict[str, Any]]:
        """更新最後使用時間"""
        return await self.update_connection(user_id, platform, {
            "last_used_at": datetime.utcnow()
        })
    
    async def update_token(
        self,
        user_id: str,
        platform: SocialPlatform,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """更新 Token"""
        update_data = {
            "access_token": access_token,
            "status": ConnectionStatus.CONNECTED.value,
        }
        if refresh_token:
            update_data["refresh_token"] = refresh_token
        if expires_at:
            update_data["token_expires_at"] = expires_at
        
        return await self.update_connection(user_id, platform, update_data)
    
    async def mark_expired(
        self,
        user_id: str,
        platform: SocialPlatform
    ) -> Optional[Dict[str, Any]]:
        """標記 Token 過期"""
        return await self.update_connection(user_id, platform, {
            "status": ConnectionStatus.EXPIRED.value
        })
    
    async def get_expiring_connections(
        self,
        hours_before_expiry: int = 24
    ) -> List[Dict[str, Any]]:
        """取得即將過期的連接"""
        await self.ensure_indexes()
        
        expiry_threshold = datetime.utcnow() + timedelta(hours=hours_before_expiry)
        
        return await self.find_many({
            "status": ConnectionStatus.CONNECTED.value,
            "token_expires_at": {"$lt": expiry_threshold, "$ne": None}
        })
    
    async def count_user_connections(self, user_id: str) -> int:
        """計算用戶的連接數量"""
        return await self.count({
            "user_id": user_id,
            "status": ConnectionStatus.CONNECTED.value
        })
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """取得連接統計"""
        await self.ensure_indexes()
        collection = await self._get_collection()
        
        # 按平台統計
        pipeline = [
            {"$group": {
                "_id": {"platform": "$platform", "status": "$status"},
                "count": {"$sum": 1}
            }}
        ]
        
        stats_by_platform = {}
        async for doc in collection.aggregate(pipeline):
            platform = doc["_id"]["platform"]
            status = doc["_id"]["status"]
            if platform not in stats_by_platform:
                stats_by_platform[platform] = {}
            stats_by_platform[platform][status] = doc["count"]
        
        total = await self.count({})
        connected = await self.count({"status": ConnectionStatus.CONNECTED.value})
        
        return {
            "total_connections": total,
            "connected": connected,
            "by_platform": stats_by_platform
        }


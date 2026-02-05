"""
Channel Repository
Phase 3: 內容功能
提供 Channel 的 CRUD 操作
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.repositories.base_repository import BaseRepository
from app.models.channel import ChannelStatus, ChannelCollectionStatus, ChannelCategory, ChannelRegion
import logging
import secrets

logger = logging.getLogger(__name__)

# 最大頻道數量
MAX_CHANNELS_PER_USER = 3


class ChannelRepository(BaseRepository):
    """Channel Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("channels", db=db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # 創建索引
            await collection.create_index("user_id")
            await collection.create_index([("user_id", 1), ("status", 1)])
            await collection.create_index("category")
            await collection.create_index("region")
            await collection.create_index("created_at")
            
            self._indexes_created = True
            logger.info("Channel 索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    async def create_channel(
        self,
        user_id: str,
        channel_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        建立 Channel
        
        Args:
            user_id: 用戶 ID
            channel_data: Channel 資料
            
        Returns:
            建立的 Channel，如果超過限制則返回 None
        """
        await self.ensure_indexes()
        
        # 檢查用戶頻道數量
        current_count = await self.count_user_channels(user_id)
        if current_count >= MAX_CHANNELS_PER_USER:
            logger.warning(f"用戶 {user_id} 已達頻道上限 ({MAX_CHANNELS_PER_USER})")
            return None
        
        now = datetime.utcnow()
        
        # 生成唯一 ID
        channel_id = f"channel_{secrets.token_urlsafe(12)}"
        
        document = {
            "id": channel_id,
            "user_id": user_id,
            **channel_data,
            "status": ChannelStatus.ACTIVE.value,
            "topic_count": 0,
            "last_collected_at": None,
            "collection_status": ChannelCollectionStatus.IDLE.value,
            "created_at": now,
            "updated_at": now,
        }
        
        return await self.create(document)
    
    async def get_channel_by_id(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """根據 ID 取得 Channel"""
        return await self.find_by_id(channel_id, id_field="id")
    
    async def get_user_channel(
        self,
        user_id: str,
        channel_id: str
    ) -> Optional[Dict[str, Any]]:
        """取得用戶的特定 Channel"""
        await self.ensure_indexes()
        return await self.find_one({
            "id": channel_id,
            "user_id": user_id,
            "status": {"$ne": ChannelStatus.DELETED.value}
        })
    
    async def get_user_channels(
        self,
        user_id: str,
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """
        取得用戶的所有 Channel
        
        Args:
            user_id: 用戶 ID
            include_deleted: 是否包含已刪除的頻道
            
        Returns:
            Channel 列表
        """
        await self.ensure_indexes()
        
        filter_query = {"user_id": user_id}
        if not include_deleted:
            filter_query["status"] = {"$ne": ChannelStatus.DELETED.value}
        
        return await self.find_many(
            filter_query,
            sort=[("created_at", -1)]
        )
    
    async def count_user_channels(
        self,
        user_id: str,
        include_deleted: bool = False
    ) -> int:
        """計算用戶的頻道數量"""
        filter_query = {"user_id": user_id}
        if not include_deleted:
            filter_query["status"] = {"$ne": ChannelStatus.DELETED.value}
        
        return await self.count(filter_query)
    
    async def update_channel(
        self,
        channel_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新 Channel"""
        update_data["updated_at"] = datetime.utcnow()
        return await self.update_by_id(channel_id, {"$set": update_data}, id_field="id")
    
    async def delete_channel(
        self,
        channel_id: str,
        user_id: str
    ) -> bool:
        """
        刪除 Channel（軟刪除）
        
        Args:
            channel_id: Channel ID
            user_id: 用戶 ID（確保只能刪除自己的頻道）
            
        Returns:
            是否成功
        """
        channel = await self.get_user_channel(user_id, channel_id)
        if not channel:
            return False
        
        result = await self.update_channel(channel_id, {
            "status": ChannelStatus.DELETED.value,
            "deleted_at": datetime.utcnow()
        })
        return result is not None
    
    async def update_collection_status(
        self,
        channel_id: str,
        status: ChannelCollectionStatus,
        topic_count: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        更新收集狀態
        
        Args:
            channel_id: Channel ID
            status: 收集狀態
            topic_count: 主題數量（可選）
            
        Returns:
            更新後的 Channel
        """
        update_data = {
            "collection_status": status.value,
            "updated_at": datetime.utcnow()
        }
        
        if status == ChannelCollectionStatus.COMPLETED:
            update_data["last_collected_at"] = datetime.utcnow()
        
        if topic_count is not None:
            update_data["topic_count"] = topic_count
        
        return await self.update_channel(channel_id, update_data)
    
    async def increment_topic_count(
        self,
        channel_id: str,
        count: int = 1
    ) -> Optional[Dict[str, Any]]:
        """增加主題數量"""
        return await self.update_by_id(
            channel_id,
            {
                "$inc": {"topic_count": count},
                "$set": {"updated_at": datetime.utcnow()}
            },
            id_field="id"
        )
    
    async def get_active_channels(self) -> List[Dict[str, Any]]:
        """取得所有活躍的頻道（用於排程收集）"""
        await self.ensure_indexes()
        return await self.find_many({
            "status": ChannelStatus.ACTIVE.value
        })
    
    async def get_channels_by_category(
        self,
        category: ChannelCategory
    ) -> List[Dict[str, Any]]:
        """取得特定類別的頻道"""
        await self.ensure_indexes()
        return await self.find_many({
            "category": category.value,
            "status": ChannelStatus.ACTIVE.value
        })
    
    async def get_channels_by_region(
        self,
        region: ChannelRegion
    ) -> List[Dict[str, Any]]:
        """取得特定地區的頻道"""
        await self.ensure_indexes()
        return await self.find_many({
            "region": region.value,
            "status": ChannelStatus.ACTIVE.value
        })
    
    async def get_stats(self) -> Dict[str, Any]:
        """取得頻道統計資訊"""
        await self.ensure_indexes()
        collection = await self._get_collection()
        
        # 計算各類別數量
        pipeline = [
            {"$match": {"status": {"$ne": ChannelStatus.DELETED.value}}},
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }}
        ]
        
        category_stats = {}
        async for doc in collection.aggregate(pipeline):
            category_stats[doc["_id"]] = doc["count"]
        
        # 計算總數
        total = await self.count({"status": {"$ne": ChannelStatus.DELETED.value}})
        
        return {
            "total_channels": total,
            "by_category": category_stats
        }


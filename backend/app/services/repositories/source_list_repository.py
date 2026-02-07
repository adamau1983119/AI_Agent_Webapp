"""
RSS 來源名單 Repository
Phase 1: 白名單/黑名單/灰名單持久化存儲
使用 MongoDB 存儲來源名單，支援新增/查詢/移除操作
"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SourceListRepository(BaseRepository):
    """RSS 來源名單 Repository"""
    
    def __init__(self, db: Optional[AsyncIOMotorDatabase] = None):
        super().__init__("rss_source_lists", db)
        self._indexes_created = False
    
    async def ensure_indexes(self):
        """確保索引存在"""
        if self._indexes_created:
            return
        
        try:
            collection = await self._get_collection()
            
            # feed_url + list_type 唯一索引
            await collection.create_index(
                [("feed_url", 1), ("list_type", 1)],
                unique=True
            )
            await collection.create_index("list_type")
            await collection.create_index("feed_url")
            await collection.create_index("created_at")
            
            self._indexes_created = True
            logger.info("RSS 來源名單索引創建完成")
        except Exception as e:
            logger.warning(f"創建索引時發生錯誤（可能已存在）: {e}")
            self._indexes_created = True
    
    # ============================================
    # 白名單操作
    # ============================================
    
    async def add_to_whitelist(self, feed_url: str, reason: str = "") -> bool:
        """
        加入白名單
        
        Args:
            feed_url: Feed URL
            reason: 加入原因
            
        Returns:
            是否成功
        """
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            
            # 先從黑名單和灰名單移除
            await collection.delete_many({
                "feed_url": feed_url,
                "list_type": {"$in": ["blacklist", "greylist"]}
            })
            
            # 添加到白名單（upsert）
            await collection.update_one(
                {"feed_url": feed_url, "list_type": "whitelist"},
                {
                    "$set": {
                        "feed_url": feed_url,
                        "list_type": "whitelist",
                        "reason": reason,
                        "updated_at": datetime.utcnow(),
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow(),
                    }
                },
                upsert=True
            )
            
            logger.info(f"已將 {feed_url} 加入白名單")
            return True
        except Exception as e:
            logger.error(f"加入白名單失敗: {e}")
            return False
    
    async def add_to_blacklist(self, feed_url: str, reason: str = "") -> bool:
        """
        加入黑名單
        
        Args:
            feed_url: Feed URL
            reason: 加入原因
            
        Returns:
            是否成功
        """
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            
            # 先從白名單和灰名單移除
            await collection.delete_many({
                "feed_url": feed_url,
                "list_type": {"$in": ["whitelist", "greylist"]}
            })
            
            # 添加到黑名單（upsert）
            await collection.update_one(
                {"feed_url": feed_url, "list_type": "blacklist"},
                {
                    "$set": {
                        "feed_url": feed_url,
                        "list_type": "blacklist",
                        "reason": reason,
                        "updated_at": datetime.utcnow(),
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow(),
                    }
                },
                upsert=True
            )
            
            logger.info(f"已將 {feed_url} 加入黑名單")
            return True
        except Exception as e:
            logger.error(f"加入黑名單失敗: {e}")
            return False
    
    async def add_to_greylist(self, feed_url: str, reason: str = "") -> bool:
        """
        加入灰名單
        
        Args:
            feed_url: Feed URL
            reason: 加入原因
            
        Returns:
            是否成功
        """
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            
            # 從白名單移除（黑名單優先級更高，不動）
            await collection.delete_many({
                "feed_url": feed_url,
                "list_type": "whitelist"
            })
            
            # 檢查是否在黑名單（黑名單優先級更高）
            in_blacklist = await collection.count_documents({
                "feed_url": feed_url,
                "list_type": "blacklist"
            })
            
            if in_blacklist > 0:
                logger.warning(f"{feed_url} 已在黑名單，不加入灰名單")
                return False
            
            # 添加到灰名單（upsert）
            await collection.update_one(
                {"feed_url": feed_url, "list_type": "greylist"},
                {
                    "$set": {
                        "feed_url": feed_url,
                        "list_type": "greylist",
                        "reason": reason,
                        "updated_at": datetime.utcnow(),
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow(),
                    }
                },
                upsert=True
            )
            
            logger.info(f"已將 {feed_url} 加入灰名單")
            return True
        except Exception as e:
            logger.error(f"加入灰名單失敗: {e}")
            return False
    
    # ============================================
    # 查詢操作
    # ============================================
    
    async def get_list_type(self, feed_url: str) -> str:
        """
        查詢來源的名單類型
        
        Args:
            feed_url: Feed URL
            
        Returns:
            名單類型: "whitelist", "blacklist", "greylist", "normal"
        """
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            
            result = await collection.find_one({"feed_url": feed_url})
            if result:
                return result.get("list_type", "normal")
            return "normal"
        except Exception as e:
            logger.warning(f"查詢來源名單類型失敗: {e}")
            return "normal"
    
    async def get_whitelist(self) -> List[Dict[str, Any]]:
        """取得白名單所有來源"""
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            cursor = collection.find({"list_type": "whitelist"}).sort("created_at", -1)
            results = await cursor.to_list(length=None)
            
            for r in results:
                if "_id" in r:
                    r["_id"] = str(r["_id"])
            
            return results
        except Exception as e:
            logger.error(f"取得白名單失敗: {e}")
            return []
    
    async def get_blacklist(self) -> List[Dict[str, Any]]:
        """取得黑名單所有來源"""
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            cursor = collection.find({"list_type": "blacklist"}).sort("created_at", -1)
            results = await cursor.to_list(length=None)
            
            for r in results:
                if "_id" in r:
                    r["_id"] = str(r["_id"])
            
            return results
        except Exception as e:
            logger.error(f"取得黑名單失敗: {e}")
            return []
    
    async def get_greylist(self) -> List[Dict[str, Any]]:
        """取得灰名單所有來源"""
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            cursor = collection.find({"list_type": "greylist"}).sort("created_at", -1)
            results = await cursor.to_list(length=None)
            
            for r in results:
                if "_id" in r:
                    r["_id"] = str(r["_id"])
            
            return results
        except Exception as e:
            logger.error(f"取得灰名單失敗: {e}")
            return []
    
    async def get_all_lists(self) -> Dict[str, List[Dict[str, Any]]]:
        """取得所有名單"""
        whitelist = await self.get_whitelist()
        blacklist = await self.get_blacklist()
        greylist = await self.get_greylist()
        
        return {
            "whitelist": whitelist,
            "blacklist": blacklist,
            "greylist": greylist,
            "summary": {
                "whitelist_count": len(whitelist),
                "blacklist_count": len(blacklist),
                "greylist_count": len(greylist),
            }
        }
    
    # ============================================
    # 移除操作
    # ============================================
    
    async def remove_from_list(self, feed_url: str, list_type: Optional[str] = None) -> bool:
        """
        從名單中移除來源
        
        Args:
            feed_url: Feed URL
            list_type: 指定名單類型（如果為 None，則從所有名單移除）
            
        Returns:
            是否成功
        """
        await self.ensure_indexes()
        
        try:
            collection = await self._get_collection()
            
            filter_query = {"feed_url": feed_url}
            if list_type:
                filter_query["list_type"] = list_type
            
            result = await collection.delete_many(filter_query)
            
            if result.deleted_count > 0:
                logger.info(f"已從名單移除 {feed_url} (list_type={list_type or 'all'})")
                return True
            return False
        except Exception as e:
            logger.error(f"從名單移除失敗: {e}")
            return False
    
    async def get_whitelist_urls(self) -> List[str]:
        """取得白名單的所有 URL"""
        items = await self.get_whitelist()
        return [item["feed_url"] for item in items]
    
    async def get_blacklist_urls(self) -> List[str]:
        """取得黑名單的所有 URL"""
        items = await self.get_blacklist()
        return [item["feed_url"] for item in items]
    
    async def get_greylist_urls(self) -> List[str]:
        """取得灰名單的所有 URL"""
        items = await self.get_greylist()
        return [item["feed_url"] for item in items]


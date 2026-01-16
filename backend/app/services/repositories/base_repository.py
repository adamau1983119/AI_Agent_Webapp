"""
基礎 Repository 類別
提供通用的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel
from bson import ObjectId
# 使用統一的 exceptions 模組，避免循環導入問題
from app.exceptions import ConnectionFailure
from app.database import get_database
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """基礎 Repository 類別"""
    
    def __init__(self, collection_name: str, db: Optional[AsyncIOMotorDatabase] = None):
        """
        初始化 Repository
        
        Args:
            collection_name: 集合名稱
            db: 可選的資料庫實例（如果提供，將使用此實例而不是全局變數）
        """
        self.collection_name = collection_name
        self._db: Optional[AsyncIOMotorDatabase] = db
        self._collection: Optional[AsyncIOMotorCollection] = None
    
    async def _get_collection(self) -> AsyncIOMotorCollection:
        """
        取得集合實例
        
        Raises:
            ConnectionFailure: 如果資料庫未連接
        """
        if self._collection is None:
            try:
                # 如果沒有提供資料庫實例，嘗試從全局獲取（向後兼容）
                if self._db is None:
                    self._db = await get_database()
                self._collection = self._db[self.collection_name]
            except ConnectionFailure as e:
                logger.error(f"資料庫未連接，無法取得集合 {self.collection_name}: {e}")
                raise
        return self._collection
    
    async def create(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立文件
        
        Args:
            document: 文件資料
            
        Returns:
            建立的文件（包含 _id）
        """
        collection = await self._get_collection()
        result = await collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """
        根據 ID 查詢文件
        
        Args:
            id: 文件 ID
            
        Returns:
            文件資料，如果不存在則返回 None
        """
        collection = await self._get_collection()
        return await collection.find_one({"id": id})
    
    async def find_one(self, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        查詢單一文件
        
        Args:
            filter: 查詢條件
            
        Returns:
            文件資料，如果不存在則返回 None
        """
        collection = await self._get_collection()
        return await collection.find_one(filter)
    
    async def find_many(
        self,
        filter: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 10,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        查詢多個文件
        
        Args:
            filter: 查詢條件
            skip: 跳過數量
            limit: 限制數量
            sort: 排序條件
            
        Returns:
            文件列表
        """
        collection = await self._get_collection()
        cursor = collection.find(filter or {})
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count(self, filter: Optional[Dict[str, Any]] = None) -> int:
        """
        計算文件數量
        
        Args:
            filter: 查詢條件
            
        Returns:
            文件數量
        """
        collection = await self._get_collection()
        return await collection.count_documents(filter or {})
    
    async def update_by_id(
        self,
        id: str,
        update: Dict[str, Any],
        upsert: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        根據 ID 更新文件
        
        Args:
            id: 文件 ID
            update: 更新資料
            upsert: 如果不存在是否建立
            
        Returns:
            更新後的文件，如果不存在則返回 None
        """
        collection = await self._get_collection()
        
        # 添加更新時間
        update["$set"] = update.get("$set", {})
        update["$set"]["updated_at"] = datetime.utcnow()
        
        result = await collection.update_one(
            {"id": id},
            update,
            upsert=upsert
        )
        
        if result.modified_count > 0 or result.upserted_id:
            return await self.find_by_id(id)
        return None
    
    async def delete_by_id(self, id: str) -> bool:
        """
        根據 ID 刪除文件
        
        Args:
            id: 文件 ID
            
        Returns:
            是否刪除成功
        """
        collection = await self._get_collection()
        result = await collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def exists(self, filter: Dict[str, Any]) -> bool:
        """
        檢查文件是否存在
        
        Args:
            filter: 查詢條件
            
        Returns:
            是否存在
        """
        collection = await self._get_collection()
        count = await collection.count_documents(filter, limit=1)
        return count > 0

"""
Content Repository
提供 Content 的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)


class ContentRepository(BaseRepository):
    """Content Repository"""
    
    def __init__(self):
        super().__init__("contents")
    
    async def create_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立 Content
        
        Args:
            content_data: Content 資料
            
        Returns:
            建立的 Content
        """
        # 確保時間戳記和版本
        now = datetime.utcnow()
        content_data.setdefault("version", 1)
        content_data.setdefault("generated_at", now)
        content_data.setdefault("updated_at", now)
        content_data.setdefault("versions", [])
        
        return await self.create(content_data)
    
    async def get_content_by_topic_id(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 Topic ID 取得 Content
        
        Args:
            topic_id: Topic ID
            
        Returns:
            Content 資料
        """
        return await self.find_one({"topic_id": topic_id})
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 ID 取得 Content
        
        Args:
            content_id: Content ID
            
        Returns:
            Content 資料
        """
        return await self.find_by_id(content_id)
    
    async def update_content(
        self,
        content_id: str,
        update_data: Dict[str, Any],
        create_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        更新 Content
        
        Args:
            content_id: Content ID
            update_data: 更新資料
            create_version: 是否建立版本記錄
            
        Returns:
            更新後的 Content
        """
        collection = await self._get_collection()
        
        # 準備更新操作
        update_ops = {}
        
        if create_version:
            # 取得當前內容
            current = await self.find_by_id(content_id)
            if current:
                # 建立版本記錄
                version_data = {
                    "version": current.get("version", 1),
                    "type": "edited",
                    "article": current.get("article"),
                    "script": current.get("script"),
                    "edited_at": datetime.utcnow()
                }
                
                # 增加版本號
                new_version = current.get("version", 1) + 1
                update_data["version"] = new_version
                
                # 添加到版本歷史（使用 $push）
                update_ops["$push"] = {"versions": version_data}
        
        # 設定更新資料（使用 $set）
        update_ops["$set"] = update_data
        update_ops["$set"]["updated_at"] = datetime.utcnow()
        
        # 執行更新
        result = await collection.update_one(
            {"id": content_id},
            update_ops
        )
        
        if result.modified_count > 0:
            return await self.find_by_id(content_id)
        return None
    
    async def update_content_by_topic_id(
        self,
        topic_id: str,
        update_data: Dict[str, Any],
        create_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        根據 Topic ID 更新 Content
        
        Args:
            topic_id: Topic ID
            update_data: 更新資料
            create_version: 是否建立版本記錄
            
        Returns:
            更新後的 Content
        """
        content = await self.get_content_by_topic_id(topic_id)
        if not content:
            return None
        
        return await self.update_content(content["id"], update_data, create_version)
    
    async def get_content_versions(self, topic_id: str) -> List[Dict[str, Any]]:
        """
        取得 Content 版本歷史
        
        Args:
            topic_id: Topic ID
            
        Returns:
            版本列表
        """
        content = await self.get_content_by_topic_id(topic_id)
        if not content:
            return []
        
        return content.get("versions", [])
    
    async def delete_content(self, content_id: str) -> bool:
        """
        刪除 Content
        
        Args:
            content_id: Content ID
            
        Returns:
            是否成功
        """
        return await self.delete_by_id(content_id)

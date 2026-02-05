"""
Photo Repository (Phase 6)
提供 Photo 索引的 CRUD 操作
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.photo import Photo, PhotoSource, PhotoType
import logging

logger = logging.getLogger(__name__)


class PhotoRepository(BaseRepository):
    """
    Photo Repository (Phase 6)
    
    提供：
    - 照片索引的 CRUD 操作
    - 根據關鍵字查找照片
    - 根據文章 ID 獲取照片
    - 批量操作
    """
    
    def __init__(self, db=None):
        super().__init__("photos", db=db)
    
    # ============================================
    # 創建操作
    # ============================================
    
    async def create_photo(self, photo: Photo) -> Dict[str, Any]:
        """
        創建照片索引
        
        Args:
            photo: Photo 模型實例
            
        Returns:
            創建的照片字典
        """
        photo_dict = photo.model_dump()
        photo_dict.setdefault("created_at", datetime.utcnow())
        
        # 確保 photo_id 存在
        if not photo_dict.get("photo_id"):
            photo_dict["photo_id"] = photo.photo_id
        
        logger.info(f"Creating photo index: {photo_dict.get('photo_id')}")
        
        return await self.create(photo_dict)
    
    async def create_photo_from_dict(self, photo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        從字典創建照片索引
        
        Args:
            photo_data: 照片資料字典
            
        Returns:
            創建的照片字典
        """
        photo_data.setdefault("created_at", datetime.utcnow())
        photo_data.setdefault("keywords", [])
        
        return await self.create(photo_data)
    
    async def create_many(self, photos: List[Dict[str, Any]]) -> List[str]:
        """
        批量創建照片索引
        
        Args:
            photos: 照片列表
            
        Returns:
            創建的照片 ID 列表
        """
        if not photos:
            return []
        
        collection = await self._get_collection()
        now = datetime.utcnow()
        
        # 確保每張照片有時間戳和 keywords
        for photo in photos:
            photo.setdefault("created_at", now)
            photo.setdefault("keywords", [])
        
        result = await collection.insert_many(photos)
        logger.info(f"Created {len(result.inserted_ids)} photo indexes")
        
        return [str(id) for id in result.inserted_ids]
    
    async def upsert_photo(self, photo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        創建或更新照片索引（根據 photo_id）
        
        Args:
            photo_data: 照片資料
            
        Returns:
            照片字典
        """
        collection = await self._get_collection()
        photo_id = photo_data.get("photo_id")
        
        if not photo_id:
            raise ValueError("photo_id is required")
        
        photo_data["updated_at"] = datetime.utcnow()
        
        await collection.update_one(
            {"photo_id": photo_id},
            {"$set": photo_data},
            upsert=True
        )
        
        return await self.get_by_photo_id(photo_id)
    
    # ============================================
    # 查詢操作
    # ============================================
    
    async def get_by_photo_id(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 photo_id 獲取照片
        
        Args:
            photo_id: 照片 ID
            
        Returns:
            照片字典或 None
        """
        collection = await self._get_collection()
        return await collection.find_one({"photo_id": photo_id})
    
    async def get_by_article_id(
        self,
        article_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        根據文章 ID 獲取照片（原文照片）
        
        Args:
            article_id: 文章 ID
            limit: 數量限制
            
        Returns:
            照片列表
        """
        collection = await self._get_collection()
        cursor = collection.find({
            "article_id": article_id
        }).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    async def find_by_keywords(
        self,
        keywords: List[str],
        limit: int = 10,
        exclude_article_id: Optional[str] = None,
        min_quality_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        根據關鍵字查找照片
        
        Args:
            keywords: 關鍵字列表
            limit: 數量限制
            exclude_article_id: 排除的文章 ID（用於排除原文照片）
            min_quality_score: 最低質量分數
            
        Returns:
            照片列表（按匹配度排序）
        """
        if not keywords:
            return []
        
        collection = await self._get_collection()
        
        # 構建查詢條件
        match_query: Dict[str, Any] = {
            "keywords": {"$in": keywords},
            "quality_score": {"$gte": min_quality_score}
        }
        
        if exclude_article_id:
            match_query["article_id"] = {"$ne": exclude_article_id}
        
        # 使用聚合計算匹配度
        pipeline = [
            {"$match": match_query},
            {
                "$addFields": {
                    "match_count": {
                        "$size": {
                            "$setIntersection": ["$keywords", keywords]
                        }
                    }
                }
            },
            {"$sort": {"match_count": -1, "quality_score": -1}},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)
    
    async def find_by_source(
        self,
        source: PhotoSource,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        根據來源查找照片
        
        Args:
            source: 照片來源
            limit: 數量限制
            
        Returns:
            照片列表
        """
        source_value = source.value if hasattr(source, 'value') else source
        
        return await self.find_many(
            filter={"source": source_value},
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def find_original_photos(
        self,
        limit: int = 20,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        查找原文照片（有 article_id 的照片）
        
        Args:
            limit: 數量限制
            category: 分類篩選（需要關聯查詢）
            
        Returns:
            照片列表
        """
        filter_query: Dict[str, Any] = {
            "article_id": {"$ne": None},
            "photo_type": PhotoType.ORIGINAL.value
        }
        
        return await self.find_many(
            filter=filter_query,
            limit=limit,
            sort=[("created_at", -1)]
        )
    
    async def search_photos(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜尋照片（在 keywords 和 caption 中搜尋）
        
        Args:
            query: 搜尋關鍵字
            limit: 數量限制
            
        Returns:
            照片列表
        """
        if not query or not query.strip():
            return []
        
        collection = await self._get_collection()
        
        cursor = collection.find({
            "$or": [
                {"keywords": {"$regex": query, "$options": "i"}},
                {"caption": {"$regex": query, "$options": "i"}},
                {"alt_text": {"$regex": query, "$options": "i"}}
            ]
        }).sort("quality_score", -1).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    # ============================================
    # 更新操作
    # ============================================
    
    async def update_photo(
        self,
        photo_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新照片索引
        
        Args:
            photo_id: 照片 ID
            update_data: 更新資料
            
        Returns:
            更新後的照片或 None
        """
        collection = await self._get_collection()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.find_one_and_update(
            {"photo_id": photo_id},
            {"$set": update_data},
            return_document=True
        )
        
        return result
    
    async def add_keywords(
        self,
        photo_id: str,
        keywords: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        添加關鍵字（不重複）
        
        Args:
            photo_id: 照片 ID
            keywords: 要添加的關鍵字
            
        Returns:
            更新後的照片或 None
        """
        collection = await self._get_collection()
        
        result = await collection.find_one_and_update(
            {"photo_id": photo_id},
            {
                "$addToSet": {"keywords": {"$each": keywords}},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        return result
    
    async def update_quality_score(
        self,
        photo_id: str,
        quality_score: float
    ) -> Optional[Dict[str, Any]]:
        """
        更新質量分數
        
        Args:
            photo_id: 照片 ID
            quality_score: 新的質量分數
            
        Returns:
            更新後的照片或 None
        """
        return await self.update_photo(photo_id, {"quality_score": quality_score})
    
    async def increment_match_count(self, photo_id: str) -> Optional[Dict[str, Any]]:
        """
        增加匹配計數
        
        Args:
            photo_id: 照片 ID
            
        Returns:
            更新後的照片或 None
        """
        collection = await self._get_collection()
        
        result = await collection.find_one_and_update(
            {"photo_id": photo_id},
            {
                "$inc": {"match_count": 1},
                "$set": {"last_matched_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        return result
    
    # ============================================
    # 刪除操作
    # ============================================
    
    async def delete_photo(self, photo_id: str) -> bool:
        """
        刪除照片索引
        
        Args:
            photo_id: 照片 ID
            
        Returns:
            是否成功
        """
        collection = await self._get_collection()
        result = await collection.delete_one({"photo_id": photo_id})
        return result.deleted_count > 0
    
    async def delete_by_article_id(self, article_id: str) -> int:
        """
        刪除文章的所有照片索引
        
        Args:
            article_id: 文章 ID
            
        Returns:
            刪除的數量
        """
        collection = await self._get_collection()
        result = await collection.delete_many({"article_id": article_id})
        logger.info(f"Deleted {result.deleted_count} photos for article {article_id}")
        return result.deleted_count
    
    # ============================================
    # 統計操作
    # ============================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        獲取照片統計
        
        Returns:
            統計資料
        """
        collection = await self._get_collection()
        
        pipeline = [
            {
                "$group": {
                    "_id": "$source",
                    "count": {"$sum": 1},
                    "avg_quality": {"$avg": "$quality_score"},
                    "total_matches": {"$sum": "$match_count"}
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        by_source = await cursor.to_list(length=20)
        
        total = await self.count({})
        original_count = await self.count({"article_id": {"$ne": None}})
        
        return {
            "total": total,
            "original_photos": original_count,
            "external_photos": total - original_count,
            "by_source": {r["_id"]: r for r in by_source}
        }
    
    async def get_keywords_stats(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        獲取關鍵字統計（最常用的關鍵字）
        
        Args:
            limit: 數量限制
            
        Returns:
            關鍵字統計列表
        """
        collection = await self._get_collection()
        
        pipeline = [
            {"$unwind": "$keywords"},
            {
                "$group": {
                    "_id": "$keywords",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)
    
    # ============================================
    # 索引管理
    # ============================================
    
    async def ensure_indexes(self) -> None:
        """
        確保索引存在
        """
        collection = await self._get_collection()
        
        # photo_id 唯一索引
        await collection.create_index("photo_id", unique=True)
        
        # keywords 索引（用於匹配查詢）
        await collection.create_index("keywords")
        
        # article_id 索引（用於查找原文照片）
        await collection.create_index("article_id")
        
        # 複合索引（用於排序查詢）
        await collection.create_index([
            ("quality_score", -1),
            ("created_at", -1)
        ])
        
        logger.info("Photo indexes ensured")


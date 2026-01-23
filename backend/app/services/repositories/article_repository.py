"""
Article Repository (Phase 6)
提供 Article 的 CRUD 操作和聚合查詢
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.services.repositories.base_repository import BaseRepository
from app.models.article import (
    Article,
    ArticleCategory,
    ArticleStatus,
    ArticleImages,
    ImagePreview,
    ImageMatched,
)
import logging

logger = logging.getLogger(__name__)


class ArticleRepository(BaseRepository):
    """
    Article Repository (Phase 6)
    
    提供：
    - 基本 CRUD 操作
    - 按分類查詢
    - 聚合查詢獲取匹配圖片
    - 與舊 topics Collection 的兼容
    """
    
    def __init__(self, db=None):
        super().__init__("articles", db=db)
    
    # ============================================
    # 創建操作
    # ============================================
    
    async def create_article(self, article: Article) -> Dict[str, Any]:
        """
        創建文章
        
        Args:
            article: Article 模型實例
            
        Returns:
            創建的文章字典
        """
        # 確保時間戳
        now = datetime.utcnow()
        article_dict = article.model_dump()
        article_dict.setdefault("collected_at", now)
        article_dict.setdefault("updated_at", now)
        
        # 確保 article_id 存在
        if not article_dict.get("article_id"):
            article_dict["article_id"] = article.article_id
        
        logger.info(f"Creating article: {article_dict.get('article_id')} - {article_dict.get('title', '')[:50]}")
        
        return await self.create(article_dict)
    
    async def create_article_from_dict(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        從字典創建文章
        
        Args:
            article_data: 文章資料字典
            
        Returns:
            創建的文章字典
        """
        # 確保時間戳
        now = datetime.utcnow()
        article_data.setdefault("collected_at", now)
        article_data.setdefault("updated_at", now)
        
        # 確保 images 結構
        if "images" not in article_data:
            article_data["images"] = {"preview": [], "matched": []}
        
        return await self.create(article_data)
    
    async def create_many(self, articles: List[Dict[str, Any]]) -> List[str]:
        """
        批量創建文章
        
        Args:
            articles: 文章列表
            
        Returns:
            創建的文章 ID 列表
        """
        if not articles:
            return []
        
        collection = await self._get_collection()
        now = datetime.utcnow()
        
        # 確保每篇文章有時間戳
        for article in articles:
            article.setdefault("collected_at", now)
            article.setdefault("updated_at", now)
            if "images" not in article:
                article["images"] = {"preview": [], "matched": []}
        
        result = await collection.insert_many(articles)
        logger.info(f"Created {len(result.inserted_ids)} articles")
        
        return [str(id) for id in result.inserted_ids]
    
    # ============================================
    # 查詢操作
    # ============================================
    
    async def get_by_id(self, article_id: str) -> Optional[Dict[str, Any]]:
        """
        根據 article_id 獲取文章
        
        Args:
            article_id: 文章 ID
            
        Returns:
            文章字典或 None
        """
        collection = await self._get_collection()
        return await collection.find_one({"article_id": article_id})
    
    async def get_by_legacy_id(self, legacy_topic_id: str) -> Optional[Dict[str, Any]]:
        """
        根據舊的 topic_id 獲取文章（向後兼容）
        
        Args:
            legacy_topic_id: 舊的 topic ID
            
        Returns:
            文章字典或 None
        """
        collection = await self._get_collection()
        return await collection.find_one({"legacy_topic_id": legacy_topic_id})
    
    async def get_by_category(
        self,
        category: ArticleCategory,
        status: Optional[ArticleStatus] = None,
        limit: int = 10,
        skip: int = 0,
        sort_by: str = "collected_at",
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """
        根據分類獲取文章
        
        Args:
            category: 文章分類
            status: 狀態篩選（可選）
            limit: 數量限制
            skip: 跳過數量
            sort_by: 排序欄位
            sort_order: 排序順序（1=升序，-1=降序）
            
        Returns:
            文章列表
        """
        filter_query: Dict[str, Any] = {
            "category": category.value if hasattr(category, 'value') else category
        }
        
        if status:
            filter_query["status"] = status.value if hasattr(status, 'value') else status
        
        return await self.find_many(
            filter=filter_query,
            skip=skip,
            limit=limit,
            sort=[(sort_by, sort_order)]
        )
    
    async def list_articles(
        self,
        category: Optional[ArticleCategory] = None,
        status: Optional[ArticleStatus] = None,
        date: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        sort: str = "collected_at",
        order: str = "desc"
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        列出文章（帶分頁和篩選）
        
        Args:
            category: 分類篩選
            status: 狀態篩選
            date: 日期篩選（YYYY-MM-DD）
            search: 搜尋關鍵字
            page: 頁碼
            limit: 每頁數量
            sort: 排序欄位
            order: 排序順序（asc/desc）
            
        Returns:
            (文章列表, 總數量)
        """
        filter_query: Dict[str, Any] = {}
        
        if category:
            filter_query["category"] = category.value if hasattr(category, 'value') else category
        
        if status:
            filter_query["status"] = status.value if hasattr(status, 'value') else status
        
        if date:
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = datetime(
                start_date.year,
                start_date.month,
                start_date.day,
                23, 59, 59, 999999
            )
            filter_query["collected_at"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        if search and search.strip():
            search_query = search.strip()
            filter_query["$or"] = [
                {"title": {"$regex": search_query, "$options": "i"}},
                {"source": {"$regex": search_query, "$options": "i"}},
                {"hashtags": {"$regex": search_query, "$options": "i"}},
            ]
        
        sort_order = -1 if order == "desc" else 1
        sort_list = [(sort, sort_order)]
        skip = (page - 1) * limit
        
        articles = await self.find_many(filter_query, skip=skip, limit=limit, sort=sort_list)
        total = await self.count(filter_query)
        
        return articles, total
    
    async def get_by_hashtags(
        self,
        hashtags: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        根據 hashtags 獲取相關文章
        
        Args:
            hashtags: hashtag 列表
            limit: 數量限制
            
        Returns:
            文章列表
        """
        if not hashtags:
            return []
        
        collection = await self._get_collection()
        cursor = collection.find({
            "hashtags": {"$in": hashtags}
        }).limit(limit)
        
        return await cursor.to_list(length=limit)
    
    # ============================================
    # 更新操作
    # ============================================
    
    async def update_article(
        self,
        article_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新文章
        
        Args:
            article_id: 文章 ID
            update_data: 更新資料
            
        Returns:
            更新後的文章或 None
        """
        collection = await self._get_collection()
        update_data["updated_at"] = datetime.utcnow()
        
        result = await collection.find_one_and_update(
            {"article_id": article_id},
            {"$set": update_data},
            return_document=True
        )
        
        return result
    
    async def update_hashtags(
        self,
        article_id: str,
        hashtags: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        更新文章的 hashtags
        
        Args:
            article_id: 文章 ID
            hashtags: 新的 hashtags
            
        Returns:
            更新後的文章或 None
        """
        return await self.update_article(article_id, {"hashtags": hashtags})
    
    async def update_matched_images(
        self,
        article_id: str,
        matched_images: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        更新文章的匹配圖片
        
        Args:
            article_id: 文章 ID
            matched_images: 匹配圖片列表
            
        Returns:
            更新後的文章或 None
        """
        return await self.update_article(
            article_id,
            {"images.matched": matched_images}
        )
    
    async def add_preview_image(
        self,
        article_id: str,
        preview_image: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        添加預覽圖片
        
        Args:
            article_id: 文章 ID
            preview_image: 預覽圖片資料
            
        Returns:
            更新後的文章或 None
        """
        collection = await self._get_collection()
        
        result = await collection.find_one_and_update(
            {"article_id": article_id},
            {
                "$push": {"images.preview": preview_image},
                "$set": {"updated_at": datetime.utcnow()}
            },
            return_document=True
        )
        
        return result
    
    async def update_status(
        self,
        article_id: str,
        status: ArticleStatus
    ) -> Optional[Dict[str, Any]]:
        """
        更新文章狀態
        
        Args:
            article_id: 文章 ID
            status: 新狀態
            
        Returns:
            更新後的文章或 None
        """
        status_value = status.value if hasattr(status, 'value') else status
        return await self.update_article(article_id, {"status": status_value})
    
    # ============================================
    # 刪除操作
    # ============================================
    
    async def delete_article(self, article_id: str) -> bool:
        """
        軟刪除文章（設為 deleted 狀態）
        
        Args:
            article_id: 文章 ID
            
        Returns:
            是否成功
        """
        result = await self.update_status(article_id, ArticleStatus.DELETED)
        return result is not None
    
    async def hard_delete_article(self, article_id: str) -> bool:
        """
        硬刪除文章
        
        Args:
            article_id: 文章 ID
            
        Returns:
            是否成功
        """
        collection = await self._get_collection()
        result = await collection.delete_one({"article_id": article_id})
        return result.deleted_count > 0
    
    # ============================================
    # 聚合查詢
    # ============================================
    
    async def get_with_matched_images(
        self,
        article_id: str,
        photo_collection_name: str = "photos",
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        獲取文章及其匹配圖片（MongoDB 聚合查詢）
        
        Args:
            article_id: 文章 ID
            photo_collection_name: 照片集合名稱
            limit: 匹配圖片數量限制
            
        Returns:
            包含匹配圖片的文章或 None
        """
        collection = await self._get_collection()
        
        pipeline = [
            # 1. 匹配文章
            {"$match": {"article_id": article_id}},
            
            # 2. 查找原文照片的索引資訊
            {
                "$lookup": {
                    "from": photo_collection_name,
                    "localField": "images.preview.photo_id",
                    "foreignField": "photo_id",
                    "as": "photo_index"
                }
            },
            
            # 3. 合併 hashtags + photo_index.keywords
            {
                "$addFields": {
                    "all_keywords": {
                        "$setUnion": [
                            {"$ifNull": ["$hashtags", []]},
                            {
                                "$reduce": {
                                    "input": {"$ifNull": ["$photo_index.keywords", []]},
                                    "initialValue": [],
                                    "in": {"$concatArrays": ["$$value", "$$this"]}
                                }
                            }
                        ]
                    }
                }
            },
            
            # 4. 查找匹配的照片
            {
                "$lookup": {
                    "from": photo_collection_name,
                    "let": {"keywords": "$all_keywords", "aid": "$article_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$gt": [
                                        {"$size": {
                                            "$setIntersection": [
                                                {"$ifNull": ["$keywords", []]},
                                                "$$keywords"
                                            ]
                                        }},
                                        0
                                    ]
                                }
                            }
                        },
                        # 計算匹配分數
                        {
                            "$addFields": {
                                "match_count": {
                                    "$size": {
                                        "$setIntersection": [
                                            {"$ifNull": ["$keywords", []]},
                                            "$$keywords"
                                        ]
                                    }
                                },
                                "is_original": {
                                    "$eq": ["$article_id", "$$aid"]
                                }
                            }
                        },
                        # 計算最終分數
                        {
                            "$addFields": {
                                "score": {
                                    "$add": [
                                        {"$multiply": ["$match_count", 0.2]},
                                        {"$cond": ["$is_original", 0.5, 0]}
                                    ]
                                }
                            }
                        },
                        # 排序
                        {"$sort": {"score": -1}},
                        # 限制數量
                        {"$limit": limit}
                    ],
                    "as": "matched_photos"
                }
            },
            
            # 5. 格式化輸出
            {
                "$addFields": {
                    "images.matched": {
                        "$map": {
                            "input": "$matched_photos",
                            "as": "photo",
                            "in": {
                                "photo_id": "$$photo.photo_id",
                                "url": "$$photo.source_url",
                                "thumbnail_url": "$$photo.thumbnail_url",
                                "keywords": "$$photo.keywords",
                                "score": "$$photo.score",
                                "source": "$$photo.source_name",
                                "is_original": "$$photo.is_original"
                            }
                        }
                    }
                }
            },
            
            # 6. 移除臨時欄位
            {
                "$project": {
                    "photo_index": 0,
                    "matched_photos": 0,
                    "all_keywords": 0
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=1)
        
        return results[0] if results else None
    
    async def get_articles_stats(
        self,
        category: Optional[ArticleCategory] = None
    ) -> Dict[str, Any]:
        """
        獲取文章統計
        
        Args:
            category: 分類篩選（可選）
            
        Returns:
            統計資料
        """
        collection = await self._get_collection()
        
        match_stage = {}
        if category:
            match_stage["category"] = category.value if hasattr(category, 'value') else category
        
        pipeline = [
            {"$match": match_stage} if match_stage else {"$match": {}},
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1},
                    "avg_score": {"$avg": "$score"},
                    "with_images": {
                        "$sum": {
                            "$cond": [
                                {"$gt": [{"$size": {"$ifNull": ["$images.preview", []]}}, 0]},
                                1,
                                0
                            ]
                        }
                    }
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=10)
        
        return {
            "by_category": {r["_id"]: r for r in results},
            "total": sum(r["count"] for r in results)
        }


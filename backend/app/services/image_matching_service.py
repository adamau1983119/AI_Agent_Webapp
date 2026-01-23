"""
ImageMatchingService (Phase 6.6)
圖片匹配服務：使用 MongoDB 聚合查詢匹配圖片
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.repositories.article_repository import ArticleRepository
from app.services.repositories.photo_repository import PhotoRepository
import logging

logger = logging.getLogger(__name__)


class ImageMatchingService:
    """
    圖片匹配服務 (Phase 6.6)
    
    功能：
    1. 使用 MongoDB 聚合查詢匹配圖片
    2. 計算匹配分數
    3. 更新文章的匹配圖片
    4. 批量匹配
    """
    
    # 分數權重
    KEYWORD_WEIGHT = 0.4
    ORIGINAL_BONUS = 0.3
    QUALITY_WEIGHT = 0.2
    DIVERSITY_WEIGHT = 0.1
    
    def __init__(self, db=None):
        self.article_repo = ArticleRepository(db=db)
        self.photo_repo = PhotoRepository(db=db)
        self._db = db
    
    async def get_matched_images(
        self,
        article_id: str,
        limit: int = 10,
        include_original: bool = True
    ) -> List[Dict[str, Any]]:
        """
        獲取文章的匹配圖片
        
        Args:
            article_id: 文章 ID
            limit: 圖片數量限制
            include_original: 是否包含原文照片
            
        Returns:
            匹配圖片列表
        """
        # 1. 獲取文章
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            logger.warning(f"Article not found: {article_id}")
            return []
        
        # 2. 獲取關鍵字
        hashtags = article.get("hashtags", [])
        
        # 從原文照片獲取額外關鍵字
        preview_images = article.get("images", {}).get("preview", [])
        preview_photo_ids = [img.get("photo_id") for img in preview_images if img.get("photo_id")]
        
        # 查詢原文照片的關鍵字
        additional_keywords = []
        for photo_id in preview_photo_ids:
            photo = await self.photo_repo.get_by_photo_id(photo_id)
            if photo and photo.get("keywords"):
                additional_keywords.extend(photo["keywords"])
        
        # 合併關鍵字
        all_keywords = list(set(hashtags + additional_keywords))
        
        if not all_keywords:
            logger.warning(f"No keywords for article: {article_id}")
            return []
        
        # 3. 使用聚合查詢匹配圖片
        matched = await self._match_by_aggregation(
            article_id=article_id,
            keywords=all_keywords,
            limit=limit,
            include_original=include_original
        )
        
        return matched
    
    async def _match_by_aggregation(
        self,
        article_id: str,
        keywords: List[str],
        limit: int = 10,
        include_original: bool = True
    ) -> List[Dict[str, Any]]:
        """
        使用 MongoDB 聚合查詢匹配圖片
        
        Args:
            article_id: 文章 ID
            keywords: 關鍵字列表
            limit: 數量限制
            include_original: 是否包含原文照片
            
        Returns:
            匹配圖片列表
        """
        collection = await self.photo_repo._get_collection()
        
        # 構建匹配條件
        match_stage: Dict[str, Any] = {
            "keywords": {"$in": keywords}
        }
        
        if not include_original:
            # 排除原文照片
            match_stage["article_id"] = {"$ne": article_id}
        
        pipeline = [
            # 1. 匹配有相關關鍵字的照片
            {"$match": match_stage},
            
            # 2. 計算匹配數量
            {
                "$addFields": {
                    "match_count": {
                        "$size": {
                            "$setIntersection": [
                                {"$ifNull": ["$keywords", []]},
                                keywords
                            ]
                        }
                    },
                    "is_original": {
                        "$eq": ["$article_id", article_id]
                    }
                }
            },
            
            # 3. 計算分數
            {
                "$addFields": {
                    "score": {
                        "$add": [
                            # 關鍵字匹配分數
                            {
                                "$multiply": [
                                    {"$divide": ["$match_count", len(keywords)]},
                                    self.KEYWORD_WEIGHT
                                ]
                            },
                            # 原文照片加分
                            {
                                "$cond": [
                                    "$is_original",
                                    self.ORIGINAL_BONUS,
                                    0
                                ]
                            },
                            # 質量分數
                            {
                                "$multiply": [
                                    {"$ifNull": ["$quality_score", 0.5]},
                                    self.QUALITY_WEIGHT
                                ]
                            }
                        ]
                    }
                }
            },
            
            # 4. 排序
            {"$sort": {"score": -1, "match_count": -1}},
            
            # 5. 限制數量
            {"$limit": limit},
            
            # 6. 格式化輸出
            {
                "$project": {
                    "_id": 0,
                    "photo_id": 1,
                    "url": "$source_url",
                    "thumbnail_url": 1,
                    "keywords": 1,
                    "score": {"$round": ["$score", 3]},
                    "source": "$source_name",
                    "is_original": 1,
                    "width": 1,
                    "height": 1
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        # 添加多樣性加分
        results = self._apply_diversity_bonus(results)
        
        return results
    
    def _apply_diversity_bonus(
        self,
        images: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        應用多樣性加分
        
        不同來源的圖片獲得加分
        """
        if not images:
            return images
        
        seen_sources = set()
        
        for img in images:
            source = img.get("source", "unknown")
            
            if source not in seen_sources:
                # 新來源加分
                img["score"] = round(img.get("score", 0) + self.DIVERSITY_WEIGHT, 3)
                seen_sources.add(source)
        
        # 重新排序
        images.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return images
    
    def _calculate_score(
        self,
        photo: Dict[str, Any],
        keywords: List[str],
        article_id: str
    ) -> float:
        """
        計算匹配分數
        
        公式：Score = 0.4K + 0.3O + 0.2Q + 0.1D
        - K: 關鍵字匹配率
        - O: 原文照片加分
        - Q: 質量分數
        - D: 多樣性加分
        """
        score = 0.0
        
        # 關鍵字匹配率
        photo_keywords = set(photo.get("keywords", []))
        match_count = len(photo_keywords.intersection(keywords))
        keyword_score = match_count / len(keywords) if keywords else 0
        score += keyword_score * self.KEYWORD_WEIGHT
        
        # 原文照片加分
        if photo.get("article_id") == article_id:
            score += self.ORIGINAL_BONUS
        
        # 質量分數
        quality = photo.get("quality_score", 0.5)
        score += quality * self.QUALITY_WEIGHT
        
        return round(score, 3)
    
    async def update_matched_images(
        self,
        article_id: str,
        limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        更新文章的匹配圖片
        
        Args:
            article_id: 文章 ID
            limit: 圖片數量限制
            
        Returns:
            更新後的文章或 None
        """
        # 獲取匹配圖片
        matched = await self.get_matched_images(article_id, limit=limit)
        
        if not matched:
            logger.info(f"No matched images for article: {article_id}")
            return None
        
        # 更新文章
        result = await self.article_repo.update_matched_images(article_id, matched)
        
        # 更新照片的匹配計數
        for img in matched:
            photo_id = img.get("photo_id")
            if photo_id:
                await self.photo_repo.increment_match_count(photo_id)
        
        logger.info(f"Updated {len(matched)} matched images for article: {article_id}")
        return result
    
    async def batch_match(
        self,
        article_ids: Optional[List[str]] = None,
        category: Optional[str] = None,
        limit_per_article: int = 10
    ) -> Dict[str, Any]:
        """
        批量匹配圖片
        
        Args:
            article_ids: 文章 ID 列表（如果為 None，則匹配所有）
            category: 分類篩選
            limit_per_article: 每篇文章的圖片數量
            
        Returns:
            匹配結果統計
        """
        stats = {
            "total": 0,
            "matched": 0,
            "failed": 0,
            "total_images": 0
        }
        
        # 獲取文章列表
        if article_ids:
            articles = []
            for aid in article_ids:
                article = await self.article_repo.get_by_id(aid)
                if article:
                    articles.append(article)
        else:
            # 獲取所有需要匹配的文章
            filter_query = {}
            if category:
                filter_query["category"] = category
            
            articles, _ = await self.article_repo.list_articles(
                category=category,
                limit=1000
            )
        
        stats["total"] = len(articles)
        
        for article in articles:
            article_id = article.get("article_id")
            try:
                result = await self.update_matched_images(
                    article_id,
                    limit=limit_per_article
                )
                
                if result:
                    stats["matched"] += 1
                    matched_count = len(result.get("images", {}).get("matched", []))
                    stats["total_images"] += matched_count
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                stats["failed"] += 1
                logger.error(f"Failed to match images for article {article_id}: {e}")
        
        logger.info(f"Batch match complete: {stats}")
        return stats
    
    async def refresh_article_images(
        self,
        article_id: str,
        force: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        刷新文章的匹配圖片
        
        Args:
            article_id: 文章 ID
            force: 是否強制刷新（即使已有匹配圖片）
            
        Returns:
            更新後的文章或 None
        """
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            return None
        
        # 檢查是否需要刷新
        existing_matched = article.get("images", {}).get("matched", [])
        if existing_matched and not force:
            logger.info(f"Article {article_id} already has matched images, skipping")
            return article
        
        return await self.update_matched_images(article_id)


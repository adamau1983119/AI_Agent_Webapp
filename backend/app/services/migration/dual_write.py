"""
DualWriteService (Phase 6.3)
雙寫機制：同時寫入 articles 和 topics Collection
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.services.repositories.article_repository import ArticleRepository
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.photo_repository import PhotoRepository
from app.models.article import (
    Article,
    ArticleCategory,
    ArticleStatus,
    ArticleImages,
    ImagePreview,
)
from app.models.topic import Topic, Category, Status
import logging

logger = logging.getLogger(__name__)


class DualWriteService:
    """
    雙寫服務 (Phase 6.3)
    
    功能：
    1. 同時寫入 articles 和 topics Collection
    2. 單筆/批量遷移 topics → articles
    3. 回滾機制
    4. 數據一致性檢查
    """
    
    def __init__(self, db=None):
        self.article_repo = ArticleRepository(db=db)
        self.topic_repo = TopicRepository(db=db)
        self.photo_repo = PhotoRepository(db=db)
        self._db = db
    
    # ============================================
    # 雙寫操作
    # ============================================
    
    async def write_article(
        self,
        article: Article,
        write_to_topics: bool = True
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        """
        雙寫：同時寫入 articles 和 topics
        
        Args:
            article: Article 模型實例
            write_to_topics: 是否同時寫入 topics（用於向後兼容）
            
        Returns:
            (article_doc, topic_doc) - topic_doc 可能為 None
        """
        article_doc = None
        topic_doc = None
        
        try:
            # 1. 寫入 articles Collection
            article_doc = await self.article_repo.create_article(article)
            logger.info(f"Created article: {article.article_id}")
            
            # 2. 同時寫入 topics Collection（向後兼容）
            if write_to_topics:
                topic_data = article.to_legacy_topic()
                topic_doc = await self.topic_repo.create_topic(topic_data)
                
                # 更新 article 的 legacy_topic_id
                if topic_doc and topic_doc.get("_id"):
                    await self.article_repo.update_article(
                        article.article_id,
                        {"legacy_topic_id": str(topic_doc["_id"])}
                    )
                
                logger.info(f"Created legacy topic for article: {article.article_id}")
            
            return article_doc, topic_doc
            
        except Exception as e:
            # 回滾：如果 article 已創建但 topic 失敗，刪除 article
            logger.error(f"Dual write failed: {e}")
            if article_doc and not topic_doc and write_to_topics:
                await self._rollback_article(article.article_id)
            raise
    
    async def write_many_articles(
        self,
        articles: List[Article],
        write_to_topics: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        批量雙寫
        
        Args:
            articles: Article 列表
            write_to_topics: 是否同時寫入 topics
            
        Returns:
            (article_docs, topic_docs)
        """
        article_docs = []
        topic_docs = []
        
        for article in articles:
            try:
                article_doc, topic_doc = await self.write_article(
                    article, 
                    write_to_topics=write_to_topics
                )
                article_docs.append(article_doc)
                if topic_doc:
                    topic_docs.append(topic_doc)
            except Exception as e:
                logger.error(f"Failed to write article {article.article_id}: {e}")
                continue
        
        return article_docs, topic_docs
    
    # ============================================
    # 遷移操作
    # ============================================
    
    async def migrate_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        遷移單個 topic 到 articles
        
        Args:
            topic_id: Topic ID
            
        Returns:
            創建的 Article 或 None
        """
        # 1. 獲取 topic
        topic_doc = await self.topic_repo.get_topic_by_id(topic_id)
        if not topic_doc:
            logger.warning(f"Topic not found: {topic_id}")
            return None
        
        # 2. 檢查是否已遷移
        existing = await self.article_repo.get_by_legacy_id(str(topic_doc.get("_id")))
        if existing:
            logger.info(f"Topic already migrated: {topic_id}")
            return existing
        
        # 3. 轉換為 Article
        article = Article.from_legacy_topic(topic_doc)
        
        # 4. 寫入 articles（不再寫入 topics，因為已存在）
        article_doc = await self.article_repo.create_article(article)
        
        # 5. 創建照片索引
        await self._create_photo_indexes(article)
        
        logger.info(f"Migrated topic {topic_id} to article {article.article_id}")
        return article_doc
    
    async def migrate_batch(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        批量遷移 topics
        
        Args:
            category: 分類篩選（可選）
            limit: 每批數量
            skip: 跳過數量
            
        Returns:
            遷移結果統計
        """
        stats = {
            "total": 0,
            "migrated": 0,
            "skipped": 0,
            "failed": 0,
            "errors": []
        }
        
        # 獲取 topics
        filter_query = {}
        if category:
            filter_query["category"] = category
        
        topics, total = await self.topic_repo.list_topics(
            category=Category(category) if category else None,
            page=1,
            limit=limit
        )
        
        stats["total"] = len(topics)
        
        for topic in topics:
            topic_id = topic.get("id")
            try:
                # 檢查是否已遷移
                existing = await self.article_repo.get_by_legacy_id(str(topic.get("_id")))
                if existing:
                    stats["skipped"] += 1
                    continue
                
                # 遷移
                result = await self.migrate_topic(topic_id)
                if result:
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                stats["failed"] += 1
                stats["errors"].append({
                    "topic_id": topic_id,
                    "error": str(e)
                })
                logger.error(f"Failed to migrate topic {topic_id}: {e}")
        
        logger.info(f"Migration batch complete: {stats}")
        return stats
    
    async def migrate_all(
        self,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        遷移所有 topics
        
        Args:
            batch_size: 每批數量
            
        Returns:
            總遷移結果
        """
        total_stats = {
            "total": 0,
            "migrated": 0,
            "skipped": 0,
            "failed": 0,
            "batches": 0
        }
        
        skip = 0
        while True:
            batch_stats = await self.migrate_batch(limit=batch_size, skip=skip)
            
            total_stats["total"] += batch_stats["total"]
            total_stats["migrated"] += batch_stats["migrated"]
            total_stats["skipped"] += batch_stats["skipped"]
            total_stats["failed"] += batch_stats["failed"]
            total_stats["batches"] += 1
            
            if batch_stats["total"] < batch_size:
                break
            
            skip += batch_size
        
        logger.info(f"Full migration complete: {total_stats}")
        return total_stats
    
    # ============================================
    # 回滾操作
    # ============================================
    
    async def _rollback_article(self, article_id: str) -> bool:
        """
        回滾：刪除 article
        
        Args:
            article_id: Article ID
            
        Returns:
            是否成功
        """
        try:
            await self.article_repo.hard_delete_article(article_id)
            logger.info(f"Rolled back article: {article_id}")
            return True
        except Exception as e:
            logger.error(f"Rollback failed for article {article_id}: {e}")
            return False
    
    async def rollback_migration(
        self,
        article_id: str
    ) -> bool:
        """
        回滾遷移：刪除 article 和相關照片索引
        
        Args:
            article_id: Article ID
            
        Returns:
            是否成功
        """
        try:
            # 刪除照片索引
            await self.photo_repo.delete_by_article_id(article_id)
            
            # 刪除 article
            await self.article_repo.hard_delete_article(article_id)
            
            logger.info(f"Rolled back migration for article: {article_id}")
            return True
        except Exception as e:
            logger.error(f"Rollback migration failed: {e}")
            return False
    
    # ============================================
    # 輔助方法
    # ============================================
    
    async def _create_photo_indexes(self, article: Article) -> List[str]:
        """
        為文章創建照片索引
        
        Args:
            article: Article 實例
            
        Returns:
            創建的 photo_id 列表
        """
        photo_ids = []
        
        for preview in article.images.preview:
            photo_data = {
                "photo_id": preview.photo_id,
                "source_url": preview.url,
                "thumbnail_url": preview.thumbnail_url,
                "caption": preview.caption,
                "article_id": article.article_id,
                "keywords": article.hashtags.copy() if article.hashtags else [],
                "source_name": article.source,
                "photo_type": "original",
                "width": preview.width,
                "height": preview.height,
            }
            
            try:
                await self.photo_repo.upsert_photo(photo_data)
                photo_ids.append(preview.photo_id)
            except Exception as e:
                logger.error(f"Failed to create photo index {preview.photo_id}: {e}")
        
        return photo_ids
    
    async def check_consistency(
        self,
        article_id: str
    ) -> Dict[str, Any]:
        """
        檢查數據一致性
        
        Args:
            article_id: Article ID
            
        Returns:
            一致性檢查結果
        """
        result = {
            "article_id": article_id,
            "article_exists": False,
            "topic_exists": False,
            "photos_count": 0,
            "consistent": False,
            "issues": []
        }
        
        # 檢查 article
        article = await self.article_repo.get_by_id(article_id)
        result["article_exists"] = article is not None
        
        if article:
            # 檢查 topic
            legacy_id = article.get("legacy_topic_id")
            if legacy_id:
                topic = await self.topic_repo.find_one({"_id": legacy_id})
                result["topic_exists"] = topic is not None
            
            # 檢查 photos
            photos = await self.photo_repo.get_by_article_id(article_id)
            result["photos_count"] = len(photos)
            
            # 檢查一致性
            preview_count = len(article.get("images", {}).get("preview", []))
            if result["photos_count"] != preview_count:
                result["issues"].append(
                    f"Photo count mismatch: {result['photos_count']} vs {preview_count}"
                )
        
        result["consistent"] = len(result["issues"]) == 0
        return result
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        獲取遷移狀態
        
        Returns:
            遷移狀態統計
        """
        # 統計 topics
        topics_count = await self.topic_repo.count({})
        
        # 統計 articles
        articles_count = await self.article_repo.count({})
        
        # 統計已遷移（有 legacy_topic_id 的 articles）
        migrated_count = await self.article_repo.count({
            "legacy_topic_id": {"$ne": None}
        })
        
        return {
            "topics_total": topics_count,
            "articles_total": articles_count,
            "migrated": migrated_count,
            "pending": topics_count - migrated_count,
            "migration_progress": (migrated_count / topics_count * 100) if topics_count > 0 else 100
        }


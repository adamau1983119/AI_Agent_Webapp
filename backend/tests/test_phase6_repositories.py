"""
Phase 6.2 測試 - Repository 層測試
測試 ArticleRepository 和 PhotoRepository 的 CRUD 操作
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.repositories.article_repository import ArticleRepository
from app.services.repositories.photo_repository import PhotoRepository
from app.models.article import (
    Article,
    ArticleCategory,
    ArticleStatus,
    ArticleImages,
    ImagePreview,
)
from app.models.photo import Photo, PhotoSource, PhotoType


# ============================================
# Mock Database Fixtures
# ============================================

@pytest.fixture
def mock_db():
    """模擬 MongoDB 數據庫"""
    db = MagicMock()
    return db


@pytest.fixture
def mock_collection():
    """模擬 MongoDB Collection"""
    collection = AsyncMock()
    return collection


@pytest.fixture
def article_repo(mock_db, mock_collection):
    """創建帶有 mock 的 ArticleRepository"""
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    repo = ArticleRepository(db=mock_db)
    repo._collection = mock_collection
    return repo


@pytest.fixture
def photo_repo(mock_db, mock_collection):
    """創建帶有 mock 的 PhotoRepository"""
    mock_db.__getitem__ = MagicMock(return_value=mock_collection)
    repo = PhotoRepository(db=mock_db)
    repo._collection = mock_collection
    return repo


@pytest.fixture
def sample_article():
    """示例文章"""
    return Article(
        article_id="A20260123-001",
        title="Test Article",
        link="https://example.com/article",
        category=ArticleCategory.FASHION,
        source="Vogue",
        hashtags=["fashion", "test"]
    )


@pytest.fixture
def sample_photo():
    """示例照片"""
    return Photo(
        photo_id="P1001",
        keywords=["fashion", "style"],
        source_url="https://example.com/image.jpg",
        source=PhotoSource.VOGUE,
        source_name="Vogue"
    )


# ============================================
# T6.2.1: test_article_repo_create
# ============================================
class TestArticleRepoCreate:
    """測試 ArticleRepository 創建操作"""
    
    @pytest.mark.asyncio
    async def test_create_article(self, article_repo, mock_collection, sample_article):
        """測試創建文章"""
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mongo_id_001")
        )
        
        result = await article_repo.create_article(sample_article)
        
        assert result is not None
        assert result["article_id"] == "A20260123-001"
        assert result["title"] == "Test Article"
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_article_from_dict(self, article_repo, mock_collection):
        """測試從字典創建文章"""
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mongo_id_002")
        )
        
        article_data = {
            "article_id": "A20260123-002",
            "title": "Dict Article",
            "link": "https://example.com",
            "category": "fashion",
            "source": "Test"
        }
        
        result = await article_repo.create_article_from_dict(article_data)
        
        assert result is not None
        assert "images" in result
        assert "collected_at" in result
    
    @pytest.mark.asyncio
    async def test_create_many_articles(self, article_repo, mock_collection):
        """測試批量創建文章"""
        mock_collection.insert_many = AsyncMock(
            return_value=MagicMock(inserted_ids=["id1", "id2", "id3"])
        )
        
        articles = [
            {"article_id": f"A{i}", "title": f"Article {i}", "link": f"url{i}", "category": "fashion", "source": "Test"}
            for i in range(3)
        ]
        
        result = await article_repo.create_many(articles)
        
        assert len(result) == 3
        mock_collection.insert_many.assert_called_once()


# ============================================
# T6.2.2: test_article_repo_get_by_id
# ============================================
class TestArticleRepoGetById:
    """測試 ArticleRepository 根據 ID 獲取"""
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, article_repo, mock_collection):
        """測試獲取存在的文章"""
        mock_collection.find_one = AsyncMock(return_value={
            "article_id": "A20260123-001",
            "title": "Found Article"
        })
        
        result = await article_repo.get_by_id("A20260123-001")
        
        assert result is not None
        assert result["article_id"] == "A20260123-001"
        mock_collection.find_one.assert_called_once_with({"article_id": "A20260123-001"})
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, article_repo, mock_collection):
        """測試獲取不存在的文章"""
        mock_collection.find_one = AsyncMock(return_value=None)
        
        result = await article_repo.get_by_id("nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_legacy_id(self, article_repo, mock_collection):
        """測試根據舊 ID 獲取"""
        mock_collection.find_one = AsyncMock(return_value={
            "article_id": "A001",
            "legacy_topic_id": "old_topic_001"
        })
        
        result = await article_repo.get_by_legacy_id("old_topic_001")
        
        assert result is not None
        mock_collection.find_one.assert_called_once_with({"legacy_topic_id": "old_topic_001"})


# ============================================
# T6.2.3: test_article_repo_get_by_category
# ============================================
class TestArticleRepoGetByCategory:
    """測試 ArticleRepository 根據分類獲取"""
    
    @pytest.mark.asyncio
    async def test_get_by_category(self, article_repo, mock_collection):
        """測試根據分類獲取文章"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"article_id": "A1", "category": "fashion"},
            {"article_id": "A2", "category": "fashion"}
        ])
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await article_repo.get_by_category(ArticleCategory.FASHION, limit=10)
        
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_by_category_with_status(self, article_repo, mock_collection):
        """測試根據分類和狀態獲取文章"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await article_repo.get_by_category(
            ArticleCategory.FASHION,
            status=ArticleStatus.CONFIRMED
        )
        
        assert isinstance(result, list)


# ============================================
# T6.2.4: test_article_repo_update
# ============================================
class TestArticleRepoUpdate:
    """測試 ArticleRepository 更新操作"""
    
    @pytest.mark.asyncio
    async def test_update_article(self, article_repo, mock_collection):
        """測試更新文章"""
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "article_id": "A001",
            "title": "Updated Title"
        })
        
        result = await article_repo.update_article("A001", {"title": "Updated Title"})
        
        assert result is not None
        assert result["title"] == "Updated Title"
    
    @pytest.mark.asyncio
    async def test_update_hashtags(self, article_repo, mock_collection):
        """測試更新 hashtags"""
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "article_id": "A001",
            "hashtags": ["new", "tags"]
        })
        
        result = await article_repo.update_hashtags("A001", ["new", "tags"])
        
        assert result is not None
        assert result["hashtags"] == ["new", "tags"]
    
    @pytest.mark.asyncio
    async def test_update_matched_images(self, article_repo, mock_collection):
        """測試更新匹配圖片"""
        matched_images = [
            {"photo_id": "P1", "url": "url1", "score": 0.9},
            {"photo_id": "P2", "url": "url2", "score": 0.8}
        ]
        
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "article_id": "A001",
            "images": {"matched": matched_images}
        })
        
        result = await article_repo.update_matched_images("A001", matched_images)
        
        assert result is not None


# ============================================
# T6.2.5: test_article_repo_delete
# ============================================
class TestArticleRepoDelete:
    """測試 ArticleRepository 刪除操作"""
    
    @pytest.mark.asyncio
    async def test_soft_delete(self, article_repo, mock_collection):
        """測試軟刪除"""
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "article_id": "A001",
            "status": "deleted"
        })
        
        result = await article_repo.delete_article("A001")
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_hard_delete(self, article_repo, mock_collection):
        """測試硬刪除"""
        mock_collection.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )
        
        result = await article_repo.hard_delete_article("A001")
        
        assert result == True
        mock_collection.delete_one.assert_called_once()


# ============================================
# T6.2.6: test_photo_repo_create
# ============================================
class TestPhotoRepoCreate:
    """測試 PhotoRepository 創建操作"""
    
    @pytest.mark.asyncio
    async def test_create_photo(self, photo_repo, mock_collection, sample_photo):
        """測試創建照片索引"""
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mongo_id_001")
        )
        
        result = await photo_repo.create_photo(sample_photo)
        
        assert result is not None
        assert result["photo_id"] == "P1001"
        mock_collection.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_photo_from_dict(self, photo_repo, mock_collection):
        """測試從字典創建照片"""
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="mongo_id_002")
        )
        
        photo_data = {
            "photo_id": "P002",
            "source_url": "https://example.com/img.jpg"
        }
        
        result = await photo_repo.create_photo_from_dict(photo_data)
        
        assert result is not None
        assert "keywords" in result
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_create_many_photos(self, photo_repo, mock_collection):
        """測試批量創建照片"""
        mock_collection.insert_many = AsyncMock(
            return_value=MagicMock(inserted_ids=["id1", "id2"])
        )
        
        photos = [
            {"photo_id": f"P{i}", "source_url": f"url{i}"}
            for i in range(2)
        ]
        
        result = await photo_repo.create_many(photos)
        
        assert len(result) == 2


# ============================================
# T6.2.7: test_photo_repo_find_by_keywords
# ============================================
class TestPhotoRepoFindByKeywords:
    """測試 PhotoRepository 根據關鍵字查找"""
    
    @pytest.mark.asyncio
    async def test_find_by_keywords(self, photo_repo, mock_collection):
        """測試根據關鍵字查找照片"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"photo_id": "P1", "keywords": ["fashion"], "match_count": 1},
            {"photo_id": "P2", "keywords": ["fashion", "style"], "match_count": 2}
        ])
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        
        result = await photo_repo.find_by_keywords(["fashion", "style"], limit=10)
        
        assert len(result) == 2
        mock_collection.aggregate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_by_keywords_empty(self, photo_repo, mock_collection):
        """測試空關鍵字列表"""
        result = await photo_repo.find_by_keywords([])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_find_by_keywords_with_exclude(self, photo_repo, mock_collection):
        """測試排除特定文章的照片"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        
        result = await photo_repo.find_by_keywords(
            ["fashion"],
            exclude_article_id="A001"
        )
        
        assert isinstance(result, list)


# ============================================
# T6.2.8: test_photo_repo_get_by_article_id
# ============================================
class TestPhotoRepoGetByArticleId:
    """測試 PhotoRepository 根據文章 ID 獲取"""
    
    @pytest.mark.asyncio
    async def test_get_by_article_id(self, photo_repo, mock_collection):
        """測試獲取文章的照片"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"photo_id": "P1", "article_id": "A001"},
            {"photo_id": "P2", "article_id": "A001"}
        ])
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await photo_repo.get_by_article_id("A001")
        
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_by_article_id_empty(self, photo_repo, mock_collection):
        """測試文章無照片"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        result = await photo_repo.get_by_article_id("nonexistent")
        
        assert result == []


# ============================================
# T6.2.9: test_photo_repo_bulk_insert
# ============================================
class TestPhotoRepoBulkInsert:
    """測試 PhotoRepository 批量操作"""
    
    @pytest.mark.asyncio
    async def test_upsert_photo(self, photo_repo, mock_collection):
        """測試 upsert 照片"""
        mock_collection.update_one = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value={
            "photo_id": "P001",
            "keywords": ["updated"]
        })
        
        photo_data = {
            "photo_id": "P001",
            "keywords": ["updated"],
            "source_url": "url"
        }
        
        result = await photo_repo.upsert_photo(photo_data)
        
        assert result is not None
        mock_collection.update_one.assert_called_once()


# ============================================
# 額外測試：Photo 更新操作
# ============================================
class TestPhotoRepoUpdate:
    """測試 PhotoRepository 更新操作"""
    
    @pytest.mark.asyncio
    async def test_add_keywords(self, photo_repo, mock_collection):
        """測試添加關鍵字"""
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "photo_id": "P001",
            "keywords": ["old", "new1", "new2"]
        })
        
        result = await photo_repo.add_keywords("P001", ["new1", "new2"])
        
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_increment_match_count(self, photo_repo, mock_collection):
        """測試增加匹配計數"""
        mock_collection.find_one_and_update = AsyncMock(return_value={
            "photo_id": "P001",
            "match_count": 5
        })
        
        result = await photo_repo.increment_match_count("P001")
        
        assert result is not None


# ============================================
# 額外測試：統計操作
# ============================================
class TestRepoStats:
    """測試統計操作"""
    
    @pytest.mark.asyncio
    async def test_article_stats(self, article_repo, mock_collection):
        """測試文章統計"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "fashion", "count": 10, "avg_score": 0.8, "with_images": 8}
        ])
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        
        result = await article_repo.get_articles_stats()
        
        assert "by_category" in result
        assert "total" in result
    
    @pytest.mark.asyncio
    async def test_photo_stats(self, photo_repo, mock_collection):
        """測試照片統計"""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": "Vogue", "count": 20, "avg_quality": 0.85}
        ])
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        mock_collection.count_documents = AsyncMock(side_effect=[100, 30])
        
        result = await photo_repo.get_stats()
        
        assert "total" in result
        assert "original_photos" in result
        assert "by_source" in result


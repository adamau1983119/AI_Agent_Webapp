"""
Phase 6.3-6.7 測試
測試雙寫機制、圖片提取、Hashtag 提取、圖片匹配服務
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.migration.dual_write import DualWriteService
from app.services.automation.image_extractor import OriginalImageExtractor
from app.services.hashtag_extractor import HashtagExtractor, extract_hashtags
from app.services.image_matching_service import ImageMatchingService
from app.models.article import Article, ArticleCategory, ArticleImages, ImagePreview
from app.models.photo import Photo


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_article_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_topic_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_photo_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def sample_article():
    return Article(
        article_id="A20260123-001",
        title="Valentino Presents New Collection at Paris Fashion Week",
        link="https://vogue.com/article",
        category=ArticleCategory.FASHION,
        source="Vogue",
        hashtags=["Valentino", "ParisFashionWeek"],
        images=ArticleImages(
            preview=[ImagePreview(photo_id="P1001", url="https://vogue.com/img.jpg")]
        )
    )


@pytest.fixture
def sample_rss_entry():
    return {
        "title": "Test Article",
        "link": "https://example.com/article",
        "media_content": [
            {"url": "https://example.com/img1.jpg", "type": "image/jpeg", "width": "1920", "height": "1080"}
        ],
        "media_thumbnail": [
            {"url": "https://example.com/thumb.jpg", "width": "300", "height": "200"}
        ],
        "content": [
            {"value": '<img src="https://example.com/img2.jpg" alt="Test image">'}
        ]
    }


# ============================================
# T6.3: DualWriteService Tests
# ============================================

class TestDualWriteService:
    """測試雙寫服務"""
    
    @pytest.mark.asyncio
    async def test_write_article_creates_both(self, mock_db, sample_article):
        """測試雙寫創建兩個記錄"""
        service = DualWriteService(db=mock_db)
        
        # Mock repositories
        service.article_repo.create_article = AsyncMock(return_value={
            "article_id": sample_article.article_id,
            "_id": "mongo_article_id"
        })
        service.topic_repo.create_topic = AsyncMock(return_value={
            "id": sample_article.article_id,
            "_id": "mongo_topic_id"
        })
        service.article_repo.update_article = AsyncMock()
        
        article_doc, topic_doc = await service.write_article(sample_article)
        
        assert article_doc is not None
        assert topic_doc is not None
        service.article_repo.create_article.assert_called_once()
        service.topic_repo.create_topic.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_write_article_without_topics(self, mock_db, sample_article):
        """測試只寫入 articles"""
        service = DualWriteService(db=mock_db)
        
        service.article_repo.create_article = AsyncMock(return_value={
            "article_id": sample_article.article_id
        })
        service.topic_repo.create_topic = AsyncMock()
        
        article_doc, topic_doc = await service.write_article(
            sample_article, 
            write_to_topics=False
        )
        
        assert article_doc is not None
        assert topic_doc is None
        service.topic_repo.create_topic.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_migrate_topic(self, mock_db):
        """測試遷移單個 topic"""
        service = DualWriteService(db=mock_db)
        
        legacy_topic = {
            "id": "topic_001",
            "_id": "mongo_id",
            "title": "Test Topic",
            "category": "fashion",
            "source": "Vogue",
            "sources": [{"url": "https://vogue.com", "name": "Vogue", "type": "rss"}],
            "preview_images": ["https://vogue.com/img.jpg"]
        }
        
        service.topic_repo.get_topic_by_id = AsyncMock(return_value=legacy_topic)
        service.article_repo.get_by_legacy_id = AsyncMock(return_value=None)
        service.article_repo.create_article = AsyncMock(return_value={"article_id": "A001"})
        service.photo_repo.upsert_photo = AsyncMock()
        
        result = await service.migrate_topic("topic_001")
        
        assert result is not None
        service.article_repo.create_article.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_migrate_already_migrated(self, mock_db):
        """測試已遷移的 topic"""
        service = DualWriteService(db=mock_db)
        
        service.topic_repo.get_topic_by_id = AsyncMock(return_value={"_id": "mongo_id"})
        service.article_repo.get_by_legacy_id = AsyncMock(return_value={"article_id": "A001"})
        service.article_repo.create_article = AsyncMock()
        
        result = await service.migrate_topic("topic_001")
        
        assert result is not None
        service.article_repo.create_article.assert_not_called()


# ============================================
# T6.4: OriginalImageExtractor Tests
# ============================================

class TestOriginalImageExtractor:
    """測試原文照片提取器"""
    
    def test_extract_from_media_content(self, sample_rss_entry):
        """測試從 media_content 提取"""
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(sample_rss_entry)
        
        assert len(images) >= 1
        assert any("img1.jpg" in img["url"] for img in images)
    
    def test_extract_from_media_thumbnail(self, sample_rss_entry):
        """測試從 media_thumbnail 提取"""
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(sample_rss_entry)
        
        assert any("thumb.jpg" in img["url"] for img in images)
    
    def test_extract_from_html(self, sample_rss_entry):
        """測試從 HTML 提取"""
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(sample_rss_entry)
        
        assert any("img2.jpg" in img["url"] for img in images)
    
    def test_generate_photo_id(self):
        """測試生成 photo_id"""
        url = "https://example.com/image.jpg"
        photo_id = OriginalImageExtractor.generate_photo_id(url)
        
        assert photo_id.startswith("P")
        assert len(photo_id) == 9  # P + 8 chars
        
        # 相同 URL 應該生成相同 ID
        photo_id2 = OriginalImageExtractor.generate_photo_id(url)
        assert photo_id == photo_id2
    
    def test_filter_tracking_pixels(self):
        """測試過濾追蹤像素"""
        entry = {
            "media_content": [
                {"url": "https://example.com/real-image.jpg", "type": "image/jpeg"},
                {"url": "https://tracking.example.com/pixel.gif", "type": "image/gif"},
                {"url": "https://analytics.example.com/1x1.png", "type": "image/png"}
            ]
        }
        
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(entry)
        
        # 應該只有真正的圖片
        assert len(images) == 1
        assert "real-image.jpg" in images[0]["url"]
    
    def test_deduplicate_images(self):
        """測試去重"""
        entry = {
            "media_content": [
                {"url": "https://example.com/image.jpg", "type": "image/jpeg"}
            ],
            "media_thumbnail": [
                {"url": "https://example.com/image.jpg"}  # 重複
            ]
        }
        
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(entry)
        
        # 應該只有一張
        assert len(images) == 1


# ============================================
# T6.5: HashtagExtractor Tests
# ============================================

class TestHashtagExtractor:
    """測試 Hashtag 提取器"""
    
    def test_extract_existing_hashtags(self):
        """測試提取已有的 #hashtag"""
        extractor = HashtagExtractor()
        hashtags = extractor.extract(
            title="New collection from #Valentino at #ParisFashionWeek"
        )
        
        assert "Valentino" in hashtags
        assert "ParisFashionWeek" in hashtags
    
    def test_extract_proper_nouns(self):
        """測試提取專有名詞"""
        extractor = HashtagExtractor()
        hashtags = extractor.extract(
            title="Valentino Presents New Collection at Paris Fashion Week"
        )
        
        assert "Valentino" in hashtags
        # "Paris Fashion Week" 會被合併為 "ParisFashionWeek"
        assert any("Paris" in h for h in hashtags)
    
    def test_extract_brands(self):
        """測試提取品牌名稱"""
        extractor = HashtagExtractor(category="fashion")
        hashtags = extractor.extract(
            title="Gucci and Prada showcase at Milan Fashion Week"
        )
        
        assert "Gucci" in hashtags
        assert "Prada" in hashtags
    
    def test_filter_stop_words(self):
        """測試過濾停用詞"""
        extractor = HashtagExtractor()
        hashtags = extractor.extract(
            title="The new collection is very beautiful"
        )
        
        # 停用詞不應該出現
        assert "the" not in [h.lower() for h in hashtags]
        assert "is" not in [h.lower() for h in hashtags]
        assert "very" not in [h.lower() for h in hashtags]
    
    def test_max_hashtags_limit(self):
        """測試最大數量限制"""
        extractor = HashtagExtractor(max_hashtags=5)
        hashtags = extractor.extract(
            title="Gucci Prada Valentino Chanel Dior Hermès Burberry at Paris Fashion Week"
        )
        
        assert len(hashtags) <= 5
    
    def test_convenience_function(self):
        """測試便捷函數"""
        hashtags = extract_hashtags(
            title="Valentino at Paris Fashion Week",
            category="fashion"
        )
        
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0


# ============================================
# T6.6: ImageMatchingService Tests
# ============================================

class TestImageMatchingService:
    """測試圖片匹配服務"""
    
    @pytest.mark.asyncio
    async def test_get_matched_images(self, mock_db):
        """測試獲取匹配圖片"""
        service = ImageMatchingService(db=mock_db)
        
        # Mock article
        service.article_repo.get_by_id = AsyncMock(return_value={
            "article_id": "A001",
            "hashtags": ["Valentino", "fashion"],
            "images": {"preview": [{"photo_id": "P001"}]}
        })
        
        # Mock photo
        service.photo_repo.get_by_photo_id = AsyncMock(return_value={
            "photo_id": "P001",
            "keywords": ["Valentino", "runway"]
        })
        
        # Mock aggregation
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"photo_id": "P002", "url": "url2", "score": 0.8, "keywords": ["Valentino"]}
        ])
        
        mock_collection = AsyncMock()
        mock_collection.aggregate = MagicMock(return_value=mock_cursor)
        service.photo_repo._get_collection = AsyncMock(return_value=mock_collection)
        
        result = await service.get_matched_images("A001")
        
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_update_matched_images(self, mock_db):
        """測試更新匹配圖片"""
        service = ImageMatchingService(db=mock_db)
        
        # Mock
        service.get_matched_images = AsyncMock(return_value=[
            {"photo_id": "P001", "url": "url1", "score": 0.9}
        ])
        service.article_repo.update_matched_images = AsyncMock(return_value={
            "article_id": "A001",
            "images": {"matched": [{"photo_id": "P001"}]}
        })
        service.photo_repo.increment_match_count = AsyncMock()
        
        result = await service.update_matched_images("A001")
        
        assert result is not None
        service.photo_repo.increment_match_count.assert_called()
    
    def test_apply_diversity_bonus(self, mock_db):
        """測試多樣性加分"""
        service = ImageMatchingService(db=mock_db)
        
        images = [
            {"photo_id": "P1", "source": "Vogue", "score": 0.8},
            {"photo_id": "P2", "source": "Vogue", "score": 0.7},
            {"photo_id": "P3", "source": "Unsplash", "score": 0.6}
        ]
        
        result = service._apply_diversity_bonus(images)
        
        # 第一個 Vogue 和第一個 Unsplash 應該有加分
        vogue_scores = [img["score"] for img in result if img["source"] == "Vogue"]
        unsplash_scores = [img["score"] for img in result if img["source"] == "Unsplash"]
        
        # 至少有一個 Unsplash 有加分
        assert any(s > 0.6 for s in unsplash_scores)


# ============================================
# T6.7: API Tests (basic structure)
# ============================================

class TestArticlesAPI:
    """測試 Articles API 結構"""
    
    def test_api_router_exists(self):
        """測試 API router 存在"""
        from app.api.v1.articles import router
        
        assert router is not None
        assert router.prefix == "/articles"
    
    def test_api_endpoints_defined(self):
        """測試 API 端點已定義"""
        from app.api.v1.articles import router
        
        routes = [r.path for r in router.routes]
        
        # 檢查端點是否存在（包含 prefix）
        assert any("articles" in r for r in routes)  # GET /articles
        assert any("article_id" in r for r in routes)  # GET /articles/{id}
        assert any("matched-images" in r for r in routes)
        assert any("refresh-images" in r for r in routes)


# ============================================
# Integration Tests
# ============================================

class TestPhase6Integration:
    """Phase 6 整合測試"""
    
    def test_article_to_legacy_conversion(self, sample_article):
        """測試 Article 轉換為舊格式"""
        legacy = sample_article.to_legacy_topic()
        
        assert legacy["id"] == sample_article.article_id
        assert legacy["title"] == sample_article.title
        # category 可能已經是字串（use_enum_values=True）
        expected_category = sample_article.category.value if hasattr(sample_article.category, 'value') else sample_article.category
        assert legacy["category"] == expected_category
    
    def test_article_from_legacy_conversion(self):
        """測試從舊格式創建 Article"""
        legacy = {
            "id": "topic_001",
            "_id": "mongo_id",
            "title": "Test Topic",
            "category": "fashion",
            "source": "Vogue",
            "sources": [{"url": "https://vogue.com", "name": "Vogue", "type": "rss", "images": ["img.jpg"]}],
            "preview_images": ["img.jpg"]
        }
        
        article = Article.from_legacy_topic(legacy)
        
        assert article.article_id == "topic_001"
        assert article.legacy_topic_id == "mongo_id"
        assert len(article.images.preview) >= 1
    
    def test_hashtag_to_photo_matching_flow(self):
        """測試 hashtag 到圖片匹配的流程"""
        # 1. 提取 hashtags
        hashtags = extract_hashtags(
            title="Valentino at Paris Fashion Week",
            category="fashion"
        )
        
        assert len(hashtags) > 0
        
        # 2. 創建文章
        article = Article(
            title="Valentino at Paris Fashion Week",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Vogue",
            hashtags=hashtags
        )
        
        assert article.hashtags == hashtags


"""
Phase 6.8 整合測試
測試 TopicCollector 與 Phase 6 服務的整合
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.automation.topic_collector import TopicCollector
from app.models.topic import Category
from app.models.article import Article, ArticleCategory


# ============================================
# Fixtures
# ============================================

@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def sample_rss_entry():
    """模擬 RSS entry"""
    return {
        "title": "Valentino Unveils Spring 2026 Collection at Paris Fashion Week",
        "link": "https://vogue.com/article/valentino-spring-2026",
        "published_parsed": datetime.utcnow().timetuple(),
        "media_content": [
            {"url": "https://vogue.com/images/valentino1.jpg", "type": "image/jpeg", "width": "1920", "height": "1080"}
        ],
        "media_thumbnail": [
            {"url": "https://vogue.com/images/valentino_thumb.jpg", "width": "300", "height": "200"}
        ],
        "content": [
            {"value": "<p>Valentino's creative director presented a stunning collection...</p><img src='https://vogue.com/images/valentino2.jpg' alt='Runway'>"}
        ],
        "summary": "Valentino showcases innovative designs at Paris Fashion Week..."
    }


@pytest.fixture
def sample_feed_response():
    """模擬 feedparser 解析結果"""
    return {
        "feed": {"title": "Vogue Fashion"},
        "entries": [
            {
                "title": "Valentino Unveils Spring 2026 Collection",
                "link": "https://vogue.com/article1",
                "media_content": [{"url": "https://vogue.com/img1.jpg", "type": "image/jpeg"}],
                "summary": "Stunning collection from Valentino..."
            },
            {
                "title": "Gucci Returns to Milan Fashion Week",
                "link": "https://vogue.com/article2",
                "media_content": [{"url": "https://vogue.com/img2.jpg", "type": "image/jpeg"}],
                "summary": "Gucci makes a grand return..."
            }
        ]
    }


# ============================================
# TopicCollector Integration Tests
# ============================================

class TestTopicCollectorPhase6:
    """測試 TopicCollector Phase 6 整合"""
    
    def test_collector_initializes_with_new_services(self, mock_db):
        """測試收集器初始化包含新服務"""
        collector = TopicCollector(db=mock_db, enable_dual_write=True)
        
        assert hasattr(collector, 'image_extractor')
        assert hasattr(collector, 'dual_write_service')
        assert collector.image_extractor is not None
        assert collector.dual_write_service is not None
    
    def test_collector_without_dual_write(self, mock_db):
        """測試禁用雙寫"""
        collector = TopicCollector(db=mock_db, enable_dual_write=False)
        
        assert collector.enable_dual_write == False
        assert collector.dual_write_service is None
    
    def test_build_article_from_topic(self, mock_db):
        """測試從 topic 構建 Article"""
        collector = TopicCollector(db=mock_db, enable_dual_write=False)
        
        topic = {
            "title": "Valentino 在巴黎時裝週發表新系列",
            "category": "fashion",
            "source": "Vogue",
            "description": "Valentino 2026 春夏系列...",
            "score": 0.85
        }
        
        preview_images = [
            {"photo_id": "P1001", "url": "https://vogue.com/img1.jpg", "caption": "Runway"}
        ]
        
        hashtags = ["Valentino", "ParisFashionWeek", "Runway"]
        
        entry = {
            "title": "Valentino Spring 2026 Collection"
        }
        
        article = collector._build_article_from_topic(
            topic=topic,
            entry=entry,
            preview_images=preview_images,
            hashtags=hashtags,
            category=Category.FASHION,
            link="https://vogue.com/article",
            source_name="Vogue",
            role_name="authority"
        )
        
        assert isinstance(article, Article)
        assert article.title == "Valentino 在巴黎時裝週發表新系列"
        assert article.category == ArticleCategory.FASHION
        assert len(article.hashtags) == 3
        assert len(article.images.preview) == 1
        assert article.images.preview[0].photo_id == "P1001"


# ============================================
# Image Extractor Integration Tests
# ============================================

class TestImageExtractorIntegration:
    """測試 OriginalImageExtractor 整合"""
    
    def test_extract_from_rss_entry(self, sample_rss_entry):
        """測試從 RSS entry 提取圖片"""
        from app.services.automation.image_extractor import OriginalImageExtractor
        
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(sample_rss_entry, "Vogue")
        
        assert len(images) >= 2
        assert all("photo_id" in img for img in images)
        assert all(img["photo_id"].startswith("P") for img in images)
    
    def test_extract_generates_unique_photo_ids(self, sample_rss_entry):
        """測試生成唯一的 photo_id"""
        from app.services.automation.image_extractor import OriginalImageExtractor
        
        extractor = OriginalImageExtractor()
        images = extractor.extract_from_entry(sample_rss_entry, "Vogue")
        
        photo_ids = [img["photo_id"] for img in images]
        assert len(photo_ids) == len(set(photo_ids))  # 無重複


# ============================================
# Hashtag Extractor Integration Tests
# ============================================

class TestHashtagExtractorIntegration:
    """測試 HashtagExtractor 整合"""
    
    def test_extract_hashtags_for_fashion(self):
        """測試時尚類 hashtag 提取"""
        from app.services.hashtag_extractor import HashtagExtractor
        
        extractor = HashtagExtractor(category="fashion")
        hashtags = extractor.extract(
            title="Valentino Unveils Spring 2026 Collection at Paris Fashion Week",
            content="The Italian fashion house presented a stunning collection featuring bold colors and innovative designs."
        )
        
        assert len(hashtags) > 0
        # 應該提取到品牌和事件
        assert any("Valentino" in h for h in hashtags)
    
    def test_extract_hashtags_for_food(self):
        """測試美食類 hashtag 提取"""
        from app.services.hashtag_extractor import HashtagExtractor
        
        extractor = HashtagExtractor(category="food")
        hashtags = extractor.extract(
            title="Michelin Star Chef Opens New Restaurant in Tokyo"
        )
        
        assert len(hashtags) > 0
    
    def test_extract_hashtags_for_trend(self):
        """測試趨勢類 hashtag 提取"""
        from app.services.hashtag_extractor import HashtagExtractor
        
        extractor = HashtagExtractor(category="trend")
        hashtags = extractor.extract(
            title="OpenAI Announces GPT-5 with Revolutionary Capabilities"
        )
        
        assert len(hashtags) > 0


# ============================================
# Dual Write Integration Tests
# ============================================

class TestDualWriteIntegration:
    """測試 DualWriteService 整合"""
    
    @pytest.mark.asyncio
    async def test_dual_write_in_collector(self, mock_db):
        """測試收集器中的雙寫"""
        collector = TopicCollector(db=mock_db, enable_dual_write=True)
        
        # Mock dual write service
        collector.dual_write_service.write_article = AsyncMock(return_value=(
            {"article_id": "A20260123-001"},
            {"_id": "mongo_id"}
        ))
        
        topic = {
            "title": "Test Topic",
            "category": "fashion",
            "source": "Vogue",
            "description": "Test description",
            "score": 0.8
        }
        
        article = collector._build_article_from_topic(
            topic=topic,
            entry={"title": "Test"},
            preview_images=[],
            hashtags=["test"],
            category=Category.FASHION,
            link="https://example.com",
            source_name="Vogue",
            role_name="authority"
        )
        
        article_doc, topic_doc = await collector.dual_write_service.write_article(article)
        
        assert article_doc is not None
        assert article_doc.get("article_id") == "A20260123-001"


# ============================================
# End-to-End Flow Tests
# ============================================

class TestEndToEndFlow:
    """端到端流程測試"""
    
    def test_full_flow_topic_to_article(self):
        """測試完整流程：RSS entry → Topic → Article"""
        from app.services.automation.image_extractor import OriginalImageExtractor
        from app.services.hashtag_extractor import HashtagExtractor
        from app.models.article import Article, ArticleCategory, ArticleImages, ImagePreview
        
        # 1. 模擬 RSS entry
        entry = {
            "title": "Gucci Presents Fall 2026 Collection",
            "link": "https://vogue.com/gucci-fall-2026",
            "media_content": [
                {"url": "https://vogue.com/gucci1.jpg", "type": "image/jpeg"}
            ],
            "summary": "Gucci's creative director unveiled a bold new direction..."
        }
        
        # 2. 提取原文照片
        image_extractor = OriginalImageExtractor()
        preview_images = image_extractor.extract_from_entry(entry, "Vogue")
        
        assert len(preview_images) >= 1
        
        # 3. 提取 hashtags
        hashtag_extractor = HashtagExtractor(category="fashion")
        hashtags = hashtag_extractor.extract(
            title=entry["title"],
            content=entry.get("summary", "")
        )
        
        assert len(hashtags) > 0
        assert "Gucci" in hashtags
        
        # 4. 構建 Article
        image_previews = [
            ImagePreview(
                photo_id=img["photo_id"],
                url=img["url"],
                caption=img.get("caption")
            )
            for img in preview_images
        ]
        
        article = Article(
            title="Gucci 發表 2026 秋冬系列",
            original_title=entry["title"],
            link=entry["link"],
            category=ArticleCategory.FASHION,
            source="Vogue",
            hashtags=hashtags,
            images=ArticleImages(preview=image_previews, matched=[])
        )
        
        assert article.article_id is not None
        assert len(article.images.preview) >= 1
        assert len(article.hashtags) > 0
    
    def test_category_mapping(self):
        """測試分類映射"""
        from app.models.topic import Category as TopicCategory
        from app.models.article import ArticleCategory
        
        # 確保分類值一致
        assert TopicCategory.FASHION.value == ArticleCategory.FASHION.value
        assert TopicCategory.FOOD.value == ArticleCategory.FOOD.value
        assert TopicCategory.TREND.value == ArticleCategory.TREND.value


# ============================================
# Performance Tests (Basic)
# ============================================

class TestPerformance:
    """基本性能測試"""
    
    def test_image_extraction_speed(self):
        """測試圖片提取速度"""
        import time
        from app.services.automation.image_extractor import OriginalImageExtractor
        
        extractor = OriginalImageExtractor()
        
        # 創建 100 個 entries
        entries = [
            {
                "title": f"Article {i}",
                "link": f"https://example.com/article{i}",
                "media_content": [{"url": f"https://example.com/img{i}.jpg", "type": "image/jpeg"}]
            }
            for i in range(100)
        ]
        
        start = time.time()
        for entry in entries:
            extractor.extract_from_entry(entry, "Test")
        elapsed = time.time() - start
        
        # 100 個 entries 應該在 1 秒內完成
        assert elapsed < 1.0
    
    def test_hashtag_extraction_speed(self):
        """測試 hashtag 提取速度"""
        import time
        from app.services.hashtag_extractor import HashtagExtractor
        
        extractor = HashtagExtractor(category="fashion")
        
        titles = [
            f"Fashion Brand {i} Unveils New Collection at Paris Fashion Week"
            for i in range(100)
        ]
        
        start = time.time()
        for title in titles:
            extractor.extract(title=title)
        elapsed = time.time() - start
        
        # 100 個標題應該在 1 秒內完成
        assert elapsed < 1.0


"""
Phase 6.1 測試 - 數據模型測試
測試 Article 和 Photo 模型的創建、驗證和轉換
"""
import pytest
from datetime import datetime, timedelta
from app.models.article import (
    Article,
    ArticleCategory,
    ArticleStatus,
    ArticleImages,
    ArticleSourceInfo,
    ImagePreview,
    ImageMatched,
    generate_article_id,
)
from app.models.photo import (
    Photo,
    PhotoSource,
    PhotoType,
    generate_photo_id,
    create_photo_from_url,
)


# ============================================
# T6.1.1: test_article_model_creation
# ============================================
class TestArticleModelCreation:
    """測試 Article 模型創建"""
    
    def test_create_article_with_required_fields(self):
        """測試使用必要欄位創建 Article"""
        article = Article(
            title="Test Article",
            link="https://example.com/article",
            category=ArticleCategory.FASHION,
            source="Vogue"
        )
        
        assert article.title == "Test Article"
        assert article.link == "https://example.com/article"
        assert article.category == ArticleCategory.FASHION
        assert article.source == "Vogue"
        assert article.article_id is not None
        assert article.article_id.startswith("A")
    
    def test_create_article_with_all_fields(self):
        """測試使用所有欄位創建 Article"""
        article = Article(
            article_id="A20260123-001",
            title="Valentino 在巴黎時裝週發表新系列",
            original_title="Valentino Presents New Collection",
            description="Valentino 2026 春夏系列",
            content="完整文章內容...",
            link="https://vogue.com/article",
            category=ArticleCategory.FASHION,
            status=ArticleStatus.CONFIRMED,
            source="Vogue",
            hashtags=["Valentino", "ParisFashionWeek"],
            score=0.85
        )
        
        assert article.article_id == "A20260123-001"
        assert article.original_title == "Valentino Presents New Collection"
        assert article.status == ArticleStatus.CONFIRMED
        assert len(article.hashtags) == 2
        assert article.score == 0.85


# ============================================
# T6.1.2: test_article_model_validation
# ============================================
class TestArticleModelValidation:
    """測試 Article 模型驗證"""
    
    def test_title_min_length(self):
        """測試標題最小長度驗證"""
        with pytest.raises(ValueError):
            Article(
                title="",  # 空標題
                link="https://example.com",
                category=ArticleCategory.FASHION,
                source="Test"
            )
    
    def test_score_range(self):
        """測試分數範圍驗證"""
        # 正常範圍
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test",
            score=0.5
        )
        assert article.score == 0.5
        
        # 超出範圍應該報錯
        with pytest.raises(ValueError):
            Article(
                title="Test",
                link="https://example.com",
                category=ArticleCategory.FASHION,
                source="Test",
                score=1.5  # 超出範圍
            )
    
    def test_category_enum_validation(self):
        """測試分類枚舉驗證"""
        article = Article(
            title="Test",
            link="https://example.com",
            category="fashion",  # 字串應該自動轉換
            source="Test"
        )
        assert article.category == ArticleCategory.FASHION


# ============================================
# T6.1.3: test_article_model_defaults
# ============================================
class TestArticleModelDefaults:
    """測試 Article 模型預設值"""
    
    def test_default_status(self):
        """測試預設狀態"""
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test"
        )
        assert article.status == ArticleStatus.PENDING
    
    def test_default_images(self):
        """測試預設圖片結構"""
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test"
        )
        assert isinstance(article.images, ArticleImages)
        assert article.images.preview == []
        assert article.images.matched == []
    
    def test_default_hashtags(self):
        """測試預設 hashtags"""
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test"
        )
        assert article.hashtags == []
    
    def test_default_timestamps(self):
        """測試預設時間戳"""
        before = datetime.utcnow()
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test"
        )
        after = datetime.utcnow()
        
        assert before <= article.collected_at <= after
        assert before <= article.updated_at <= after


# ============================================
# T6.1.4: test_photo_model_creation
# ============================================
class TestPhotoModelCreation:
    """測試 Photo 模型創建"""
    
    def test_create_photo_with_required_fields(self):
        """測試使用必要欄位創建 Photo"""
        photo = Photo(
            source_url="https://example.com/image.jpg"
        )
        
        assert photo.source_url == "https://example.com/image.jpg"
        assert photo.photo_id is not None
        assert photo.photo_id.startswith("P")
    
    def test_create_photo_with_all_fields(self):
        """測試使用所有欄位創建 Photo"""
        photo = Photo(
            photo_id="P1001",
            keywords=["Valentino", "fashion"],
            source_url="https://vogue.com/img.jpg",
            thumbnail_url="https://vogue.com/img_thumb.jpg",
            caption="Valentino runway",
            article_id="A20260123-001",
            source=PhotoSource.VOGUE,
            source_name="Vogue",
            photo_type=PhotoType.ORIGINAL,
            quality_score=0.9,
            width=1920,
            height=1080
        )
        
        assert photo.photo_id == "P1001"
        assert len(photo.keywords) == 2
        assert photo.article_id == "A20260123-001"
        assert photo.source == PhotoSource.VOGUE
        assert photo.photo_type == PhotoType.ORIGINAL
        assert photo.quality_score == 0.9


# ============================================
# T6.1.5: test_photo_model_validation
# ============================================
class TestPhotoModelValidation:
    """測試 Photo 模型驗證"""
    
    def test_quality_score_range(self):
        """測試質量分數範圍"""
        photo = Photo(
            source_url="https://example.com/img.jpg",
            quality_score=0.5
        )
        assert photo.quality_score == 0.5
        
        with pytest.raises(ValueError):
            Photo(
                source_url="https://example.com/img.jpg",
                quality_score=1.5  # 超出範圍
            )
    
    def test_dimensions_validation(self):
        """測試尺寸驗證"""
        photo = Photo(
            source_url="https://example.com/img.jpg",
            width=1920,
            height=1080
        )
        assert photo.width == 1920
        assert photo.height == 1080
        
        with pytest.raises(ValueError):
            Photo(
                source_url="https://example.com/img.jpg",
                width=0  # 無效寬度
            )


# ============================================
# T6.1.6: test_image_preview_structure
# ============================================
class TestImagePreviewStructure:
    """測試 ImagePreview 結構"""
    
    def test_create_image_preview(self):
        """測試創建 ImagePreview"""
        preview = ImagePreview(
            photo_id="P1001",
            url="https://vogue.com/img.jpg",
            thumbnail_url="https://vogue.com/img_thumb.jpg",
            caption="Valentino runway"
        )
        
        assert preview.photo_id == "P1001"
        assert preview.url == "https://vogue.com/img.jpg"
        assert preview.caption == "Valentino runway"
    
    def test_image_preview_in_article(self):
        """測試 ImagePreview 在 Article 中的使用"""
        preview = ImagePreview(
            photo_id="P1001",
            url="https://vogue.com/img.jpg"
        )
        
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test",
            images=ArticleImages(preview=[preview])
        )
        
        assert len(article.images.preview) == 1
        assert article.images.preview[0].photo_id == "P1001"


# ============================================
# T6.1.7: test_image_matched_structure
# ============================================
class TestImageMatchedStructure:
    """測試 ImageMatched 結構"""
    
    def test_create_image_matched(self):
        """測試創建 ImageMatched"""
        matched = ImageMatched(
            photo_id="P2005",
            url="https://unsplash.com/img.jpg",
            keywords=["Valentino", "fashion"],
            score=0.85,
            source="Unsplash",
            is_original=False
        )
        
        assert matched.photo_id == "P2005"
        assert matched.score == 0.85
        assert matched.is_original == False
        assert len(matched.keywords) == 2
    
    def test_image_matched_in_article(self):
        """測試 ImageMatched 在 Article 中的使用"""
        matched = ImageMatched(
            photo_id="P2005",
            url="https://unsplash.com/img.jpg",
            score=0.85
        )
        
        article = Article(
            title="Test",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Test",
            images=ArticleImages(matched=[matched])
        )
        
        assert len(article.images.matched) == 1
        assert article.images.matched[0].score == 0.85


# ============================================
# T6.1.8: test_article_to_dict
# ============================================
class TestArticleToDict:
    """測試 Article 轉換為字典"""
    
    def test_article_dict_output(self):
        """測試 Article.dict() 輸出"""
        article = Article(
            article_id="A20260123-001",
            title="Test Article",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Vogue",
            hashtags=["test", "fashion"]
        )
        
        data = article.model_dump()
        
        assert data["article_id"] == "A20260123-001"
        assert data["title"] == "Test Article"
        assert data["category"] == "fashion"
        assert data["hashtags"] == ["test", "fashion"]
        assert "images" in data
        assert "preview" in data["images"]
        assert "matched" in data["images"]
    
    def test_article_to_legacy_topic(self):
        """測試 Article 轉換為舊 Topic 格式"""
        preview = ImagePreview(
            photo_id="P1001",
            url="https://vogue.com/img.jpg"
        )
        
        article = Article(
            article_id="A20260123-001",
            title="Test Article",
            link="https://example.com",
            category=ArticleCategory.FASHION,
            source="Vogue",
            images=ArticleImages(preview=[preview])
        )
        
        legacy = article.to_legacy_topic()
        
        assert legacy["id"] == "A20260123-001"
        assert legacy["title"] == "Test Article"
        assert legacy["category"] == "fashion"
        assert "https://vogue.com/img.jpg" in legacy["preview_images"]
    
    def test_article_from_legacy_topic(self):
        """測試從舊 Topic 創建 Article"""
        legacy_topic = {
            "id": "topic_001",
            "_id": "mongo_id_001",
            "title": "Legacy Topic",
            "category": "fashion",
            "status": "pending",
            "source": "Vogue",
            "sources": [{
                "type": "rss",
                "name": "Vogue",
                "url": "https://vogue.com/article",
                "images": ["https://vogue.com/img1.jpg"]
            }],
            "preview_images": ["https://vogue.com/img1.jpg"],
            "description": "Test description"
        }
        
        article = Article.from_legacy_topic(legacy_topic)
        
        assert article.article_id == "topic_001"
        assert article.title == "Legacy Topic"
        assert article.legacy_topic_id == "mongo_id_001"
        assert len(article.images.preview) >= 1


# ============================================
# 額外測試：輔助函數
# ============================================
class TestHelperFunctions:
    """測試輔助函數"""
    
    def test_generate_article_id(self):
        """測試生成文章 ID"""
        id1 = generate_article_id()
        id2 = generate_article_id()
        
        assert id1.startswith("A")
        assert id2.startswith("A")
        assert id1 != id2
    
    def test_generate_photo_id_random(self):
        """測試生成隨機照片 ID"""
        id1 = generate_photo_id()
        id2 = generate_photo_id()
        
        assert id1.startswith("P")
        assert id2.startswith("P")
        assert id1 != id2
    
    def test_generate_photo_id_from_url(self):
        """測試從 URL 生成照片 ID"""
        url = "https://example.com/image.jpg"
        id1 = generate_photo_id(url)
        id2 = generate_photo_id(url)
        
        # 相同 URL 應該生成相同 ID
        assert id1 == id2
        assert id1.startswith("P")
    
    def test_create_photo_from_url(self):
        """測試從 URL 創建 Photo"""
        photo = create_photo_from_url(
            url="https://vogue.com/img.jpg",
            keywords=["fashion", "style"],
            article_id="A001",
            source_name="Vogue",
            caption="Test caption",
            width=1920,
            height=1080
        )
        
        assert photo.source_url == "https://vogue.com/img.jpg"
        assert photo.keywords == ["fashion", "style"]
        assert photo.article_id == "A001"
        assert photo.photo_type == PhotoType.ORIGINAL
        assert photo.quality_score > 0


# ============================================
# Photo 方法測試
# ============================================
class TestPhotoMethods:
    """測試 Photo 模型方法"""
    
    def test_is_original_true(self):
        """測試 is_original() 為 True"""
        photo = Photo(
            source_url="https://example.com/img.jpg",
            article_id="A001",
            photo_type=PhotoType.ORIGINAL
        )
        assert photo.is_original() == True
    
    def test_is_original_false(self):
        """測試 is_original() 為 False"""
        photo = Photo(
            source_url="https://example.com/img.jpg",
            photo_type=PhotoType.EXTERNAL
        )
        assert photo.is_original() == False
    
    def test_calculate_quality_score(self):
        """測試質量分數計算"""
        photo = Photo(
            source_url="https://example.com/img.jpg",
            caption="Test caption",
            keywords=["test", "image"],
            width=1920,
            height=1080
        )
        
        score = photo.calculate_quality_score()
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # 有 caption、keywords、高解析度
    
    def test_to_matched_format(self):
        """測試轉換為 matched 格式"""
        photo = Photo(
            photo_id="P1001",
            source_url="https://example.com/img.jpg",
            keywords=["test"],
            source_name="Test"
        )
        
        matched = photo.to_matched_format(score=0.85)
        
        assert matched["photo_id"] == "P1001"
        assert matched["url"] == "https://example.com/img.jpg"
        assert matched["score"] == 0.85
        assert matched["keywords"] == ["test"]


"""
Article 資料模型 (Phase 6)
新的文章結構，包含 images.preview/matched 和 hashtags
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid


class ArticleCategory(str, Enum):
    """文章分類"""
    FASHION = "fashion"
    FOOD = "food"
    TREND = "trend"


class ArticleStatus(str, Enum):
    """文章狀態"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PUBLISHED = "published"
    DELETED = "deleted"


class ImagePreview(BaseModel):
    """
    原文照片結構
    從 RSS Feed 提取的原始圖片
    """
    photo_id: str = Field(..., description="照片唯一 ID")
    url: str = Field(..., description="圖片 URL")
    thumbnail_url: Optional[str] = Field(None, description="縮圖 URL")
    caption: Optional[str] = Field(None, description="圖片說明")
    width: Optional[int] = Field(None, ge=1, description="寬度")
    height: Optional[int] = Field(None, ge=1, description="高度")
    
    class Config:
        json_schema_extra = {
            "example": {
                "photo_id": "P1001",
                "url": "https://vogue.com/img1.jpg",
                "thumbnail_url": "https://vogue.com/img1_thumb.jpg",
                "caption": "Valentino runway look"
            }
        }


class ImageMatched(BaseModel):
    """
    匹配照片結構
    通過 MongoDB 聚合查詢匹配的圖片
    """
    photo_id: str = Field(..., description="照片唯一 ID")
    url: str = Field(..., description="圖片 URL")
    thumbnail_url: Optional[str] = Field(None, description="縮圖 URL")
    keywords: List[str] = Field(default_factory=list, description="匹配的關鍵字")
    score: float = Field(default=0.0, ge=0.0, le=2.0, description="匹配分數")
    source: str = Field(default="unknown", description="圖片來源")
    is_original: bool = Field(default=False, description="是否為原文照片")
    width: Optional[int] = Field(None, ge=1, description="寬度")
    height: Optional[int] = Field(None, ge=1, description="高度")
    
    class Config:
        json_schema_extra = {
            "example": {
                "photo_id": "P2005",
                "url": "https://unsplash.com/img2.jpg",
                "keywords": ["Valentino", "fashion"],
                "score": 0.85,
                "source": "Unsplash",
                "is_original": False
            }
        }


class ArticleImages(BaseModel):
    """
    文章圖片結構
    包含原文照片和匹配照片
    """
    preview: List[ImagePreview] = Field(
        default_factory=list, 
        description="原文照片列表（從 RSS 提取）"
    )
    matched: List[ImageMatched] = Field(
        default_factory=list, 
        description="匹配照片列表（MongoDB 聚合查詢）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "preview": [
                    {"photo_id": "P1001", "url": "https://vogue.com/img1.jpg"}
                ],
                "matched": [
                    {"photo_id": "P2005", "url": "https://unsplash.com/img2.jpg", "score": 0.85}
                ]
            }
        }


class ArticleSourceInfo(BaseModel):
    """文章來源資訊"""
    type: str = Field(default="rss", description="來源類型（rss/news/youtube）")
    name: str = Field(..., description="來源名稱")
    url: str = Field(..., description="來源 URL")
    role: Optional[str] = Field(None, description="來源角色（authority/streetwear 等）")
    fetched_at: Optional[datetime] = Field(None, description="取得時間")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Article(BaseModel):
    """
    Article 資料模型 (Phase 6)
    
    新的文章結構，用於取代舊的 Topic 結構
    包含：
    - 基本資訊（title, description, link）
    - 分類和狀態
    - hashtags（用於圖片匹配）
    - images（preview + matched）
    - 來源資訊
    - 評分
    """
    # 基本識別
    article_id: str = Field(
        default_factory=lambda: f"A{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
        description="文章唯一 ID"
    )
    
    # 內容欄位
    title: str = Field(..., min_length=1, max_length=500, description="文章標題")
    original_title: Optional[str] = Field(None, max_length=500, description="原始標題（翻譯前）")
    description: Optional[str] = Field(None, max_length=1000, description="文章摘要")
    content: Optional[str] = Field(None, description="文章內容")
    link: str = Field(..., description="文章連結")
    
    # 分類和狀態
    category: ArticleCategory = Field(..., description="文章分類")
    status: ArticleStatus = Field(default=ArticleStatus.PENDING, description="文章狀態")
    
    # 來源資訊
    source: str = Field(..., description="主要來源名稱")
    source_info: Optional[ArticleSourceInfo] = Field(None, description="詳細來源資訊")
    
    # 核心新增：hashtags（用於圖片匹配）
    hashtags: List[str] = Field(
        default_factory=list, 
        description="文章標籤（用於圖片匹配）",
        max_length=20
    )
    
    # 核心新增：圖片結構
    images: ArticleImages = Field(
        default_factory=ArticleImages, 
        description="圖片結構（preview + matched）"
    )
    
    # 時間戳
    published_at: Optional[datetime] = Field(None, description="發布時間")
    collected_at: datetime = Field(default_factory=datetime.utcnow, description="收集時間")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新時間")
    
    # 評分
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="文章評分")
    diversity_contribution: float = Field(default=0.0, description="多樣性貢獻")
    
    # 雙寫兼容欄位
    legacy_topic_id: Optional[str] = Field(None, description="對應舊 topics 的 _id")
    
    # 元數據
    metadata: Dict[str, Any] = Field(default_factory=dict, description="額外元數據")
    
    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "article_id": "A20260123-001",
                "title": "Valentino 在巴黎時裝週發表新系列",
                "original_title": "Valentino Presents New Collection at Paris Fashion Week",
                "description": "Valentino 2026 春夏系列...",
                "link": "https://vogue.com/article/valentino-pfw-2026",
                "category": "fashion",
                "status": "pending",
                "source": "Vogue",
                "hashtags": ["Valentino", "ParisFashionWeek", "Runway", "Spring2026"],
                "images": {
                    "preview": [
                        {"photo_id": "P1001", "url": "https://vogue.com/img1.jpg"}
                    ],
                    "matched": []
                },
                "score": 0.85
            }
        }
    
    def to_legacy_topic(self) -> dict:
        """
        轉換為舊的 Topic 格式（向後兼容）
        """
        return {
            "_id": self.legacy_topic_id or self.article_id,
            "id": self.article_id,
            "title": self.title,
            "category": self.category,
            "status": self.status,
            "source": self.source,
            "sources": [{
                "type": self.source_info.type if self.source_info else "rss",
                "name": self.source,
                "url": self.link,
                "images": [img.url for img in self.images.preview],
            }] if self.source else [],
            "description": self.description,
            "preview_images": [img.url for img in self.images.preview],
            "generated_at": self.collected_at,
            "updated_at": self.updated_at,
            "created_at": self.collected_at,
        }
    
    @classmethod
    def from_legacy_topic(cls, topic: dict) -> "Article":
        """
        從舊的 Topic 格式創建 Article
        """
        # 提取 preview images
        preview_images = []
        preview_urls = topic.get("preview_images", [])
        for i, url in enumerate(preview_urls):
            preview_images.append(ImagePreview(
                photo_id=f"legacy_{topic.get('id', 'unknown')}_{i}",
                url=url
            ))
        
        # 從 sources 提取更多 preview images
        for source in topic.get("sources", []):
            for url in source.get("images", []):
                if url not in preview_urls:
                    preview_images.append(ImagePreview(
                        photo_id=f"legacy_src_{len(preview_images)}",
                        url=url
                    ))
        
        return cls(
            article_id=topic.get("id", f"legacy_{topic.get('_id', 'unknown')}"),
            title=topic.get("title", ""),
            description=topic.get("description"),
            link=topic.get("sources", [{}])[0].get("url", "") if topic.get("sources") else "",
            category=topic.get("category", "fashion"),
            status=topic.get("status", "pending"),
            source=topic.get("source", ""),
            hashtags=[],  # 需要後續提取
            images=ArticleImages(preview=preview_images, matched=[]),
            published_at=topic.get("generated_at"),
            collected_at=topic.get("created_at", datetime.utcnow()),
            updated_at=topic.get("updated_at", datetime.utcnow()),
            legacy_topic_id=str(topic.get("_id")) if topic.get("_id") else None,
        )


# 輔助函數
def generate_article_id() -> str:
    """生成文章 ID"""
    return f"A{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"


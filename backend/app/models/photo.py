"""
Photo 資料模型 (Phase 6)
照片索引結構，用於 MongoDB 聚合查詢匹配
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import hashlib


class PhotoSource(str, Enum):
    """照片來源"""
    # 原文來源
    VOGUE = "Vogue"
    ELLE = "Elle"
    HYPEBEAST = "Hypebeast"
    WWD = "WWD"
    BOF = "Business of Fashion"
    EATER = "Eater"
    BON_APPETIT = "Bon Appetit"
    TECHCRUNCH = "TechCrunch"
    THE_VERGE = "The Verge"
    WIRED = "Wired"
    # 外部圖庫
    UNSPLASH = "Unsplash"
    PEXELS = "Pexels"
    PIXABAY = "Pixabay"
    DUCKDUCKGO = "DuckDuckGo"
    GOOGLE = "Google"
    # 其他
    UNKNOWN = "unknown"


class PhotoType(str, Enum):
    """照片類型"""
    ORIGINAL = "original"  # 原文照片（從文章提取）
    EXTERNAL = "external"  # 外部照片（從圖庫搜尋）
    USER = "user"          # 用戶上傳


class Photo(BaseModel):
    """
    Photo 資料模型 (Phase 6)
    
    照片索引結構，用於：
    1. 存儲從 RSS 提取的原文照片
    2. 存儲從外部圖庫搜尋的照片
    3. 支援 MongoDB 聚合查詢進行圖片匹配
    
    核心欄位：
    - photo_id: 唯一 ID
    - keywords: 關鍵字列表（用於匹配）
    - article_id: 關聯文章（原文照片才有）
    """
    # 唯一識別
    photo_id: str = Field(
        default_factory=lambda: f"P{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}",
        description="照片唯一 ID"
    )
    
    # 核心欄位：關鍵字（用於聚合查詢匹配）
    keywords: List[str] = Field(
        default_factory=list, 
        description="關鍵字列表（用於匹配）",
        max_length=30
    )
    
    # 圖片 URL
    source_url: str = Field(..., description="原圖 URL")
    thumbnail_url: Optional[str] = Field(None, description="縮圖 URL")
    
    # 圖片資訊
    caption: Optional[str] = Field(None, max_length=500, description="圖片說明/標題")
    alt_text: Optional[str] = Field(None, max_length=300, description="替代文字")
    
    # 關聯文章（原文照片才有）
    article_id: Optional[str] = Field(
        None, 
        description="關聯文章 ID（原文照片才有，外部照片為 None）"
    )
    
    # 來源資訊
    source: PhotoSource = Field(default=PhotoSource.UNKNOWN, description="照片來源")
    source_name: str = Field(default="unknown", description="來源名稱（字串）")
    photo_type: PhotoType = Field(default=PhotoType.EXTERNAL, description="照片類型")
    
    # 圖片質量
    quality_score: float = Field(
        default=0.5, 
        ge=0.0, 
        le=1.0, 
        description="圖片質量分數"
    )
    width: Optional[int] = Field(None, ge=1, description="寬度")
    height: Optional[int] = Field(None, ge=1, description="高度")
    
    # 攝影師資訊（外部圖庫）
    photographer: Optional[str] = Field(None, description="攝影師名稱")
    photographer_url: Optional[str] = Field(None, description="攝影師連結")
    license: Optional[str] = Field(None, description="授權類型")
    
    # 時間戳
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建立時間")
    
    # 統計
    match_count: int = Field(default=0, ge=0, description="被匹配次數")
    last_matched_at: Optional[datetime] = Field(None, description="最後匹配時間")
    
    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "photo_id": "P1001",
                "keywords": ["Valentino", "Paris Fashion Week", "runway"],
                "source_url": "https://vogue.com/img1.jpg",
                "thumbnail_url": "https://vogue.com/img1_thumb.jpg",
                "caption": "Valentino Spring 2026 Collection",
                "article_id": "A20260123-001",
                "source": "Vogue",
                "photo_type": "original",
                "quality_score": 0.9,
                "width": 1920,
                "height": 1080
            }
        }
    
    def is_original(self) -> bool:
        """是否為原文照片"""
        return self.article_id is not None and self.photo_type == PhotoType.ORIGINAL
    
    def calculate_quality_score(self) -> float:
        """
        計算圖片質量分數
        
        基於：
        - 解析度
        - 是否有 caption
        - 是否有關鍵字
        """
        score = 0.3  # 基礎分
        
        # 解析度加分
        if self.width and self.height:
            max_dim = max(self.width, self.height)
            if max_dim >= 1920:
                score += 0.3
            elif max_dim >= 1200:
                score += 0.2
            elif max_dim >= 800:
                score += 0.1
        
        # caption 加分
        if self.caption:
            score += 0.2
        
        # keywords 加分
        if self.keywords:
            keyword_bonus = min(len(self.keywords) * 0.05, 0.2)
            score += keyword_bonus
        
        return min(score, 1.0)
    
    def update_quality_score(self) -> None:
        """更新質量分數"""
        self.quality_score = self.calculate_quality_score()
    
    def to_matched_format(self, score: float = 0.0) -> dict:
        """
        轉換為 ImageMatched 格式
        
        Args:
            score: 匹配分數
            
        Returns:
            ImageMatched 格式的字典
        """
        return {
            "photo_id": self.photo_id,
            "url": self.source_url,
            "thumbnail_url": self.thumbnail_url,
            "keywords": self.keywords,
            "score": score,
            "source": self.source_name,
            "is_original": self.is_original(),
            "width": self.width,
            "height": self.height,
        }


# 輔助函數
def generate_photo_id(url: Optional[str] = None) -> str:
    """
    生成照片 ID
    
    Args:
        url: 可選的圖片 URL（用於生成確定性 ID）
        
    Returns:
        照片 ID
    """
    if url:
        # 基於 URL 生成確定性 ID
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"P{url_hash}"
    else:
        # 生成隨機 ID
        return f"P{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"


def create_photo_from_url(
    url: str,
    keywords: List[str] = None,
    article_id: Optional[str] = None,
    source_name: str = "unknown",
    caption: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> Photo:
    """
    從 URL 創建 Photo 對象
    
    Args:
        url: 圖片 URL
        keywords: 關鍵字列表
        article_id: 關聯文章 ID
        source_name: 來源名稱
        caption: 圖片說明
        width: 寬度
        height: 高度
        
    Returns:
        Photo 對象
    """
    # 確定照片類型
    photo_type = PhotoType.ORIGINAL if article_id else PhotoType.EXTERNAL
    
    # 確定來源
    source = PhotoSource.UNKNOWN
    source_lower = source_name.lower()
    for ps in PhotoSource:
        if ps.value.lower() in source_lower or source_lower in ps.value.lower():
            source = ps
            break
    
    photo = Photo(
        photo_id=generate_photo_id(url),
        keywords=keywords or [],
        source_url=url,
        caption=caption,
        article_id=article_id,
        source=source,
        source_name=source_name,
        photo_type=photo_type,
        width=width,
        height=height,
    )
    
    # 計算並更新質量分數
    photo.update_quality_score()
    
    return photo


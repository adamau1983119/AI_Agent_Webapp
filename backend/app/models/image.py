"""
Image 資料模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from enum import Enum


class ImageSource(str, Enum):
    """圖片來源"""
    UNSPLASH = "Unsplash"
    PEXELS = "Pexels"
    PIXABAY = "Pixabay"
    DUCKDUCKGO = "DuckDuckGo"  # 無需 API Key 的圖片搜尋
    GOOGLE_CUSTOM_SEARCH = "Google Custom Search"  # Google Custom Search API（需要 API Key）
    SOURCE_ARTICLE = "Source Article"  # 原文圖片


class ImageType(str, Enum):
    """圖片類型"""
    SOURCE = "source"  # 原文圖片
    MATCHED = "matched"  # 匹配的圖片


class Image(BaseModel):
    """Image 資料模型"""
    id: str = Field(..., description="圖片唯一識別碼")
    topic_id: str = Field(..., description="主題 ID")
    url: str = Field(..., description="圖片 URL")
    source: ImageSource = Field(..., description="圖片來源")
    image_type: ImageType = Field(default=ImageType.MATCHED, description="圖片類型（source=原文圖片，matched=匹配圖片）")
    photographer: Optional[str] = Field(None, description="攝影師名稱")
    photographer_url: Optional[str] = Field(None, description="攝影師連結")
    license: str = Field(..., description="授權類型")
    keywords: List[str] = Field(default_factory=list, description="關鍵字")
    order: int = Field(default=0, ge=0, description="排序")
    width: Optional[int] = Field(None, ge=1, description="寬度")
    height: Optional[int] = Field(None, ge=1, description="高度")
    fetched_at: datetime = Field(default_factory=datetime.utcnow, description="取得時間")

    model_config = ConfigDict(use_enum_values=True)

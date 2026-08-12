"""
Topic Schemas
用於 Topic API 的請求和回應模型
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.topic import Category, Status, SourceInfo
from app.schemas.content import ContentResponse
from app.schemas.image import ImageResponse
from app.schemas.common import PaginationResponse


class TopicBase(BaseModel):
    """Topic 基礎模型"""
    title: str = Field(..., min_length=1, max_length=200, description="主題標題")
    category: Category = Field(..., description="主題分類")
    source: str = Field(..., min_length=1, description="主要來源")


class TopicCreate(TopicBase):
    """建立 Topic 請求"""
    sources: Optional[List[SourceInfo]] = Field(None, description="資料來源列表")


class TopicUpdate(BaseModel):
    """更新 Topic 請求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="主題標題")
    category: Optional[Category] = Field(None, description="主題分類")
    status: Optional[Status] = Field(None, description="主題狀態")
    source: Optional[str] = Field(None, min_length=1, description="主要來源")
    sources: Optional[List[SourceInfo]] = Field(None, description="資料來源列表")


class TopicStatusUpdate(BaseModel):
    """更新 Topic 狀態請求"""
    status: Status = Field(..., description="主題狀態")


class TopicResponse(BaseModel):
    """Topic 回應模型（列表用）"""
    id: str = Field(..., description="主題唯一識別碼")
    title: str = Field(..., description="主題標題")
    category: Category = Field(..., description="主題分類")
    status: Status = Field(..., description="主題狀態")
    source: str = Field(..., description="主要來源")
    generated_at: datetime = Field(..., description="生成時間")
    updated_at: datetime = Field(..., description="更新時間")
    image_count: Optional[int] = Field(None, description="圖片數量")
    word_count: Optional[int] = Field(None, description="字數")
    # 階段 1 新增欄位
    preview_images: Optional[List[str]] = Field(None, description="預覽圖片 URL 列表")
    is_expanded: bool = Field(default=False, description="是否已展開")
    description: Optional[str] = Field(None, description="主題內容摘要（約30字）")
    summary_flash: Optional[str] = Field(None, description="Flash 提煉摘要（v7 事實源）")
    # Phase 7: 多語言支援
    display_language: Optional[str] = Field(None, description="標題/摘要的顯示語言（zh-TW/en/ja）")
    original_title: Optional[str] = Field(None, description="原始標題（來源語言）")
    titles_i18n: Optional[Dict[str, str]] = Field(
        None, description="多語言標題快取（zh-TW/en/ja）"
    )
    description_i18n: Optional[Dict[str, str]] = Field(
        None, description="多語言摘要快取（zh-TW/en/ja）"
    )
    title_script_mismatch: Optional[bool] = Field(
        None,
        description="標題文字腳本是否與 display_language 不一致（前端可省略自行檢測）",
    )
    content_locale: Optional[str] = Field(
        None, description="本次回應 title/description 所屬語言（ui_lang 解析後）"
    )
    locale_resolved: Optional[bool] = Field(
        None, description="title+description 成套是否已符合請求語言"
    )

    model_config = ConfigDict(from_attributes=True)


class TopicTranslateDisplayRequest(BaseModel):
    """譯為目前語言請求"""
    target_language: Optional[str] = Field(
        None, description="目標語言（zh-TW/en/ja）；省略則由前端帶入介面語言"
    )
    translation_type: Optional[str] = Field(
        "standard_translation",
        description="standard_translation（DeepL）| kol_style（Flash 按需）",
    )


class TopicTranslateDisplayResponse(BaseModel):
    """譯為目前語言回應"""
    topic_id: str
    title: str
    description: Optional[str] = None
    target_language: str
    display_language: str
    original_title: Optional[str] = None
    cached: bool = False
    titles_i18n: Optional[Dict[str, str]] = None
    description_i18n: Optional[Dict[str, str]] = None


class TopicDetailResponse(BaseModel):
    """Topic 詳情回應模型"""
    id: str = Field(..., description="主題唯一識別碼")
    title: str = Field(..., description="主題標題")
    category: Category = Field(..., description="主題分類")
    status: Status = Field(..., description="主題狀態")
    source: str = Field(..., description="主要來源")
    sources: List[SourceInfo] = Field(..., description="資料來源列表")
    generated_at: datetime = Field(..., description="生成時間")
    updated_at: datetime = Field(..., description="更新時間")
    created_at: datetime = Field(..., description="建立時間")
    content: Optional[ContentResponse] = Field(None, description="內容資訊")
    images: List[ImageResponse] = Field(default_factory=list, description="圖片列表")
    # 階段 1 新增欄位
    preview_images: Optional[List[str]] = Field(None, description="預覽圖片 URL 列表")
    is_expanded: bool = Field(default=False, description="是否已展開")
    generation_config: Optional[Dict[str, Any]] = Field(None, description="生成配置")
    description: Optional[str] = Field(None, description="主題內容摘要（約30字）")
    summary_flash: Optional[str] = Field(None, description="Flash 提煉摘要（v7 事實源）")
    # Phase 7: 多語言支援
    display_language: Optional[str] = Field(None, description="標題/摘要的顯示語言（zh-TW/en/ja）")
    original_title: Optional[str] = Field(None, description="原始標題（來源語言）")
    titles_i18n: Optional[Dict[str, str]] = Field(None, description="多語言標題快取")
    description_i18n: Optional[Dict[str, str]] = Field(None, description="多語言摘要快取")
    title_script_mismatch: Optional[bool] = Field(
        None, description="標題腳本與 display_language 不一致"
    )
    content_locale: Optional[str] = Field(None, description="本次回應 title/description 所屬語言")
    locale_resolved: Optional[bool] = Field(None, description="成套是否已符合請求語言")

    model_config = ConfigDict(from_attributes=True)


class TopicListResponse(BaseModel):
    """Topic 列表回應"""
    data: List[TopicResponse] = Field(..., description="主題列表")
    pagination: PaginationResponse = Field(..., description="分頁資訊")

"""
Topic Schemas
用於 Topic API 的請求和回應模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
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

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopicListResponse(BaseModel):
    """Topic 列表回應"""
    data: List[TopicResponse] = Field(..., description="主題列表")
    pagination: PaginationResponse = Field(..., description="分頁資訊")

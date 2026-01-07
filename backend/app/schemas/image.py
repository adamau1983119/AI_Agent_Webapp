"""
Image Schemas
用於 Image API 的請求和回應模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.image import ImageSource
from app.schemas.common import PaginationResponse


class ImageBase(BaseModel):
    """Image 基礎模型"""
    url: str = Field(..., description="圖片 URL")
    source: ImageSource = Field(..., description="圖片來源")
    photographer: Optional[str] = Field(None, description="攝影師名稱")
    photographer_url: Optional[str] = Field(None, description="攝影師連結")
    license: str = Field(..., description="授權類型")
    keywords: Optional[List[str]] = Field(None, description="關鍵字")
    order: int = Field(default=0, ge=0, description="排序")
    width: Optional[int] = Field(None, ge=1, description="寬度")
    height: Optional[int] = Field(None, ge=1, description="高度")


class ImageCreate(ImageBase):
    """建立 Image 請求"""
    topic_id: str = Field(..., description="主題 ID")


class ImageUpdate(BaseModel):
    """更新 Image 請求"""
    url: Optional[str] = Field(None, description="圖片 URL")
    source: Optional[ImageSource] = Field(None, description="圖片來源")
    photographer: Optional[str] = Field(None, description="攝影師名稱")
    photographer_url: Optional[str] = Field(None, description="攝影師連結")
    license: Optional[str] = Field(None, description="授權類型")
    keywords: Optional[List[str]] = Field(None, description="關鍵字")
    order: Optional[int] = Field(None, ge=0, description="排序")


class ImageResponse(BaseModel):
    """Image 回應模型"""
    id: str = Field(..., description="圖片唯一識別碼")
    topic_id: str = Field(..., description="主題 ID")
    url: str = Field(..., description="圖片 URL")
    source: ImageSource = Field(..., description="圖片來源")
    photographer: Optional[str] = Field(None, description="攝影師名稱")
    photographer_url: Optional[str] = Field(None, description="攝影師連結")
    license: str = Field(..., description="授權類型")
    keywords: List[str] = Field(default_factory=list, description="關鍵字")
    order: int = Field(..., description="排序")
    width: Optional[int] = Field(None, description="寬度")
    height: Optional[int] = Field(None, description="高度")
    fetched_at: datetime = Field(..., description="取得時間")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageSearchAttempt(BaseModel):
    """圖片搜尋嘗試記錄"""
    source: str = Field(..., description="圖片來源")
    status: str = Field(..., description="狀態：success, no_results, error, unavailable, exception")
    count: Optional[int] = Field(None, description="結果數量（成功時）")
    code: Optional[str] = Field(None, description="錯誤代碼（錯誤時）")
    message: Optional[str] = Field(None, description="錯誤訊息（錯誤時）")
    details: Optional[dict] = Field(None, description="額外詳情")
    exception_type: Optional[str] = Field(None, description="異常類型（異常時）")


class ImageSearchResponse(BaseModel):
    """圖片搜尋回應"""
    data: List[ImageResponse] = Field(..., description="圖片列表")
    pagination: PaginationResponse = Field(..., description="分頁資訊")
    source: Optional[str] = Field(None, description="最終使用的圖片來源")
    attempts: List[ImageSearchAttempt] = Field(default_factory=list, description="搜尋嘗試記錄")
    trace_id: Optional[str] = Field(None, description="追蹤 ID")


class ImageListResponse(BaseModel):
    """圖片列表回應"""
    data: List[ImageResponse] = Field(..., description="圖片列表")


class ImageReorderItem(BaseModel):
    """圖片排序項目"""
    image_id: str = Field(..., description="圖片 ID")
    order: int = Field(..., ge=0, description="新排序")


class ImageReorderRequest(BaseModel):
    """圖片重新排序請求"""
    image_orders: List[ImageReorderItem] = Field(..., description="圖片排序列表")

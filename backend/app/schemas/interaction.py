"""
Interaction Schemas
用於 Interaction API 的請求和回應模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.interaction import InteractionAction
from app.schemas.common import PaginationResponse


class InteractionCreate(BaseModel):
    """建立 Interaction 請求"""
    user_id: str = Field(..., description="顧客 ID")
    topic_id: str = Field(..., description="主題 ID")
    article_id: Optional[str] = Field(None, description="文章 ID（可選）")
    photo_id: Optional[str] = Field(None, description="照片 ID（可選）")
    script_id: Optional[str] = Field(None, description="劇本 ID（可選）")
    action: InteractionAction = Field(..., description="互動類型")
    duration: Optional[int] = Field(None, ge=0, description="停留時間（秒）")


class InteractionResponse(BaseModel):
    """Interaction 回應模型"""
    id: str = Field(..., description="互動唯一識別碼")
    user_id: str = Field(..., description="顧客 ID")
    topic_id: str = Field(..., description="主題 ID")
    article_id: Optional[str] = Field(None, description="文章 ID")
    photo_id: Optional[str] = Field(None, description="照片 ID")
    script_id: Optional[str] = Field(None, description="劇本 ID")
    action: InteractionAction = Field(..., description="互動類型")
    duration: Optional[int] = Field(None, description="停留時間（秒）")
    category: Optional[str] = Field(None, description="主題分類")
    created_at: datetime = Field(..., description="建立時間")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class InteractionListResponse(BaseModel):
    """互動列表回應"""
    user_id: str = Field(..., description="顧客 ID")
    interactions: List[InteractionResponse] = Field(..., description="互動記錄列表")
    pagination: PaginationResponse = Field(..., description="分頁資訊")


class InteractionStatsResponse(BaseModel):
    """互動統計回應"""
    user_id: str = Field(..., description="顧客 ID")
    stats: dict = Field(..., description="統計數據")


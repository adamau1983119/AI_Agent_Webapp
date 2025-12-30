"""
Interaction 資料模型
用於追蹤顧客互動行為
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class InteractionAction(str, Enum):
    """互動類型"""
    LIKE = "like"
    DISLIKE = "dislike"
    EDIT = "edit"
    REPLACE = "replace"
    VIEW = "view"


class Interaction(BaseModel):
    """Interaction 資料模型"""
    id: str = Field(..., description="互動唯一識別碼")
    user_id: str = Field(..., description="顧客 ID")
    topic_id: str = Field(..., description="主題 ID")
    article_id: Optional[str] = Field(None, description="文章 ID（可選）")
    photo_id: Optional[str] = Field(None, description="照片 ID（可選）")
    script_id: Optional[str] = Field(None, description="劇本 ID（可選）")
    action: InteractionAction = Field(..., description="互動類型")
    duration: Optional[int] = Field(None, ge=0, description="停留時間（秒）")
    category: Optional[str] = Field(None, description="主題分類")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建立時間")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


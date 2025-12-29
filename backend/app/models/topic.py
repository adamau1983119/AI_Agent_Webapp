"""
Topic 資料模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Category(str, Enum):
    """主題分類"""
    FASHION = "fashion"
    FOOD = "food"
    TREND = "trend"


class Status(str, Enum):
    """主題狀態"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DELETED = "deleted"


class SourceInfo(BaseModel):
    """資料來源資訊"""
    type: str = Field(..., description="來源類型（news/youtube/rss）")
    name: str = Field(..., description="來源名稱")
    url: str = Field(..., description="來源 URL")
    title: Optional[str] = Field(None, description="來源標題（可選，預設使用 name）")
    fetched_at: Optional[datetime] = Field(None, description="取得時間（可選）")
    verified: bool = Field(default=True, description="是否驗證")
    verified_at: Optional[str] = Field(None, description="驗證時間（可選）")
    reliability: Optional[str] = Field(None, description="可靠性（可選）")
    keywords: Optional[List[str]] = Field(None, description="關鍵字列表（可選）")
    
    def __init__(self, **data):
        # 如果沒有 title，使用 name
        if 'title' not in data or not data.get('title'):
            data['title'] = data.get('name', '')
        # 如果沒有 fetched_at，使用 verified_at
        if 'fetched_at' not in data or not data.get('fetched_at'):
            if 'verified_at' in data and data.get('verified_at'):
                from datetime import datetime
                try:
                    if isinstance(data['verified_at'], str):
                        data['fetched_at'] = datetime.fromisoformat(data['verified_at'].replace('Z', '+00:00'))
                    else:
                        data['fetched_at'] = data['verified_at']
                except:
                    pass
        super().__init__(**data)


class Topic(BaseModel):
    """Topic 資料模型"""
    id: str = Field(..., description="主題唯一識別碼")
    title: str = Field(..., min_length=1, max_length=200, description="主題標題")
    category: Category = Field(..., description="主題分類")
    status: Status = Field(default=Status.PENDING, description="主題狀態")
    source: str = Field(..., min_length=1, description="主要來源")
    sources: List[SourceInfo] = Field(default_factory=list, description="資料來源列表")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成時間")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新時間")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建立時間")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

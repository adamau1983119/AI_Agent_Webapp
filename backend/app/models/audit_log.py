"""
AuditLog 資料模型
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    """操作類型"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class EntityType(str, Enum):
    """實體類型"""
    TOPIC = "topic"
    CONTENT = "content"
    IMAGE = "image"
    USER_PREFERENCES = "user_preferences"


class SourceInfo(BaseModel):
    """來源資訊"""
    type: str = Field(..., description="來源類型（crawler/manual/system）")
    url: Optional[str] = Field(None, description="來源 URL")
    crawled_at: Optional[datetime] = Field(None, description="爬取時間")


class Changes(BaseModel):
    """變更內容"""
    before: Optional[Dict[str, Any]] = Field(None, description="變更前資料")
    after: Optional[Dict[str, Any]] = Field(None, description="變更後資料")


class AuditLog(BaseModel):
    """AuditLog 資料模型"""
    id: str = Field(..., description="審計日誌唯一識別碼")
    topic_id: Optional[str] = Field(None, description="主題 ID")
    action: Action = Field(..., description="操作類型")
    entity_type: EntityType = Field(..., description="實體類型")
    user: str = Field(default="system", description="使用者")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="時間戳記")
    changes: Optional[Changes] = Field(None, description="變更內容")
    source: Optional[SourceInfo] = Field(None, description="來源資訊")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True

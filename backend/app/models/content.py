"""
Content 資料模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContentVersion(BaseModel):
    """內容版本資訊"""
    version: int = Field(..., description="版本號")
    type: str = Field(..., description="版本類型（generated/edited）")
    article: Optional[str] = Field(None, description="短文內容")
    script: Optional[str] = Field(None, description="腳本內容")
    generated_at: datetime = Field(..., description="生成時間")
    edited_at: Optional[datetime] = Field(None, description="編輯時間")
    score: Optional[int] = Field(None, ge=0, le=100, description="品質評分")
    changes: Optional[List[str]] = Field(None, description="變更說明")


class Content(BaseModel):
    """Content 資料模型"""
    id: str = Field(..., description="內容唯一識別碼")
    topic_id: str = Field(..., description="主題 ID")
    article: Optional[str] = Field(None, description="短文內容")
    script: Optional[str] = Field(None, description="腳本內容")
    word_count: int = Field(default=0, ge=0, description="字數")
    estimated_duration: int = Field(default=0, ge=0, description="預計時長（秒）")
    model_used: str = Field(default="qwen-turbo", description="使用的 AI 模型")
    prompt_version: str = Field(default="v1.0", description="Prompt 版本")
    version: int = Field(default=1, ge=1, description="內容版本")
    versions: List[ContentVersion] = Field(default_factory=list, description="版本歷史")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成時間")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新時間")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

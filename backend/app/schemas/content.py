"""
Content Schemas
用於 Content API 的請求和回應模型
"""
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    """Content 基礎模型"""
    article: Optional[str] = Field(None, description="短文內容")
    script: Optional[str] = Field(None, description="腳本內容")


class ContentCreate(ContentBase):
    """建立 Content 請求"""
    topic_id: str = Field(..., description="主題 ID")
    model_used: str = Field(default="qwen-turbo", description="使用的 AI 模型")
    prompt_version: str = Field(default="v1.0", description="Prompt 版本")


class ContentUpdate(ContentBase):
    """更新 Content 請求"""
    pass


class GenerateContentRequest(BaseModel):
    """生成內容請求"""
    type: Literal["article", "script", "both"] = Field(
        default="both",
        description="生成類型"
    )
    article_length: int = Field(default=500, ge=100, le=2000, description="短文長度（字）")
    script_duration: int = Field(default=30, ge=10, le=120, description="腳本時長（秒）")


class ContentVersionResponse(BaseModel):
    """內容版本回應"""
    version: int = Field(..., description="版本號")
    type: str = Field(..., description="版本類型")
    article: Optional[str] = Field(None, description="短文內容")
    script: Optional[str] = Field(None, description="腳本內容")
    generated_at: Optional[datetime] = Field(None, description="生成時間")
    edited_at: Optional[datetime] = Field(None, description="編輯時間")
    score: Optional[int] = Field(None, description="品質評分")
    changes: Optional[list[str]] = Field(None, description="變更說明")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentResponse(BaseModel):
    """Content 回應模型"""
    id: str = Field(..., description="內容唯一識別碼")
    topic_id: str = Field(..., description="主題 ID")
    article: Optional[str] = Field(None, description="短文內容")
    script: Optional[str] = Field(None, description="腳本內容")
    word_count: int = Field(..., description="字數")
    estimated_duration: int = Field(..., description="預計時長（秒）")
    model_used: str = Field(..., description="使用的 AI 模型")
    prompt_version: str = Field(..., description="Prompt 版本")
    version: int = Field(..., description="內容版本")
    generated_at: datetime = Field(..., description="生成時間")
    updated_at: datetime = Field(..., description="更新時間")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentVersionsResponse(BaseModel):
    """內容版本歷史回應"""
    data: list[ContentVersionResponse] = Field(..., description="版本列表")

"""
topic_translations Collection 模型（v7 D1）
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TranslationType:
    STANDARD = "standard_translation"
    KOL = "kol_style"


class TranslationProvider:
    DEEPL = "deepl"
    FLASH = "deepseek_flash"
    FALLBACK = "fallback"


class TopicTranslation(BaseModel):
    topic_id: str = Field(..., description="關聯 topics.id")
    lang: str = Field(..., description="zh-TW | en | ja")
    type: str = Field(..., description="standard_translation | kol_style")
    cached_title: str = Field(..., description="翻譯後標題")
    cached_content: Optional[str] = Field(None, description="翻譯後摘要／內容")
    provider: str = Field(..., description="deepl | deepseek_flash | fallback")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

"""
Discover 公共主題牆 API Schema
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PublicFeedCard(BaseModel):
    id: str
    title: str
    description: str = ""
    summary_flash: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_lang: str = "en"
    created_at: Optional[datetime] = None


class PublicFeedResponse(BaseModel):
    data: List[PublicFeedCard] = Field(default_factory=list)
    lang: str
    cached: bool = False
    count: int = 0

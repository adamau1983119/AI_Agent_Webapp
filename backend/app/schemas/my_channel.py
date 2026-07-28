"""
MyChannel API schemas（MC-2～MC-5）
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class MyChannelFeedCard(BaseModel):
    id: str
    heading: str
    intro: str = Field(..., max_length=30)
    category: Optional[str] = None
    image_url: Optional[str] = None


class MyChannelFeedResponse(BaseModel):
    data: List[MyChannelFeedCard]
    balance: int
    lang: str
    cached: bool = False
    rate_limited: bool = False
    empty: bool = False
    has_channels: bool = False


class ChannelTemplateItem(BaseModel):
    id: str
    category: str
    region: str
    name_key: str
    desc_key: str
    suggested_name: str


class ChannelTemplatesResponse(BaseModel):
    data: List[ChannelTemplateItem]


class UnlockResponse(BaseModel):
    topic_id: str
    source_url: str
    digest_300: str = Field(..., max_length=300)
    balance: int


class UnlockRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=64)


class AddCreditsRequest(BaseModel):
    amount: int = Field(..., gt=0, le=1000)


class AddCreditsResponse(BaseModel):
    user_id: str
    balance: int
    added: int

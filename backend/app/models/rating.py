"""
Rating 評分模型
Phase 4: AI 個人化
用於記錄用戶對生成內容的評分
"""
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class RatingValue(str, Enum):
    """評分值"""
    LIKE = "like"        # 👍 喜歡
    DISLIKE = "dislike"  # 👎 不喜歡


class RatingReason(str, Enum):
    """評分原因"""
    # 喜歡的原因
    TONE_GOOD = "tone_good"              # 語氣很好
    CONTENT_RELEVANT = "content_relevant" # 內容相關
    CREATIVE = "creative"                # 有創意
    PROFESSIONAL = "professional"        # 很專業
    ENGAGING = "engaging"                # 很吸引人
    LENGTH_PERFECT = "length_perfect"    # 長度剛好
    
    # 不喜歡的原因
    TONE_BAD = "tone_bad"                # 語氣不對
    CONTENT_IRRELEVANT = "content_irrelevant"  # 內容不相關
    TOO_GENERIC = "too_generic"          # 太普通
    TOO_LONG = "too_long"                # 太長
    TOO_SHORT = "too_short"              # 太短
    BORING = "boring"                    # 無聊
    INACCURATE = "inaccurate"            # 不準確
    
    # 通用
    OTHER = "other"                      # 其他


# ============================================
# Rating Schema
# ============================================

class RatingCreate(BaseModel):
    """建立評分"""
    content_id: str = Field(..., description="內容 ID")
    topic_id: str = Field(..., description="主題 ID")
    value: RatingValue = Field(..., description="評分值 (like/dislike)")
    reasons: List[RatingReason] = Field(default=[], description="評分原因（可多選）")
    comment: Optional[str] = Field(None, max_length=500, description="額外評論")
    
    # 內容元數據（用於分析）
    content_format: Optional[str] = Field(None, description="內容格式")
    content_length: Optional[int] = Field(None, description="內容長度")
    topic_category: Optional[str] = Field(None, description="主題類別")


class RatingResponse(BaseModel):
    """評分回應"""
    id: str
    user_id: str
    content_id: str
    topic_id: str
    value: RatingValue
    reasons: List[RatingReason]
    comment: Optional[str]
    content_format: Optional[str]
    content_length: Optional[int]
    topic_category: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingStats(BaseModel):
    """評分統計"""
    total_ratings: int
    positive_ratings: int
    negative_ratings: int
    positive_ratio: float
    
    # 按原因分類
    top_like_reasons: List[dict]   # [{"reason": "...", "count": N}]
    top_dislike_reasons: List[dict]
    
    # 按格式分類
    ratings_by_format: dict  # {"full_article": {"like": N, "dislike": N}, ...}
    
    # 按類別分類
    ratings_by_category: dict  # {"fashion": {"like": N, "dislike": N}, ...}


class UserRatingHistory(BaseModel):
    """用戶評分歷史"""
    user_id: str
    ratings: List[RatingResponse]
    total: int
    page: int
    limit: int


# ============================================
# 評分原因標籤
# ============================================

RATING_REASON_LABELS = {
    # 喜歡
    RatingReason.TONE_GOOD: {"label": "語氣很好", "sentiment": "positive"},
    RatingReason.CONTENT_RELEVANT: {"label": "內容相關", "sentiment": "positive"},
    RatingReason.CREATIVE: {"label": "有創意", "sentiment": "positive"},
    RatingReason.PROFESSIONAL: {"label": "很專業", "sentiment": "positive"},
    RatingReason.ENGAGING: {"label": "很吸引人", "sentiment": "positive"},
    RatingReason.LENGTH_PERFECT: {"label": "長度剛好", "sentiment": "positive"},
    
    # 不喜歡
    RatingReason.TONE_BAD: {"label": "語氣不對", "sentiment": "negative"},
    RatingReason.CONTENT_IRRELEVANT: {"label": "內容不相關", "sentiment": "negative"},
    RatingReason.TOO_GENERIC: {"label": "太普通", "sentiment": "negative"},
    RatingReason.TOO_LONG: {"label": "太長", "sentiment": "negative"},
    RatingReason.TOO_SHORT: {"label": "太短", "sentiment": "negative"},
    RatingReason.BORING: {"label": "無聊", "sentiment": "negative"},
    RatingReason.INACCURATE: {"label": "不準確", "sentiment": "negative"},
    
    RatingReason.OTHER: {"label": "其他", "sentiment": "neutral"},
}


def get_positive_reasons() -> List[RatingReason]:
    """取得正面評分原因"""
    return [
        RatingReason.TONE_GOOD,
        RatingReason.CONTENT_RELEVANT,
        RatingReason.CREATIVE,
        RatingReason.PROFESSIONAL,
        RatingReason.ENGAGING,
        RatingReason.LENGTH_PERFECT,
    ]


def get_negative_reasons() -> List[RatingReason]:
    """取得負面評分原因"""
    return [
        RatingReason.TONE_BAD,
        RatingReason.CONTENT_IRRELEVANT,
        RatingReason.TOO_GENERIC,
        RatingReason.TOO_LONG,
        RatingReason.TOO_SHORT,
        RatingReason.BORING,
        RatingReason.INACCURATE,
    ]


"""
StyleProfile 風格檔案模型
Phase 4: AI 個人化
用於記錄用戶的內容風格偏好
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class LearningStage(str, Enum):
    """學習階段"""
    COLD_START = "cold_start"    # 冷啟動（0-20 評分）
    LEARNING = "learning"        # 學習中（20-100 評分）
    MATURE = "mature"            # 成熟（100+ 評分）


class PresetStyle(str, Enum):
    """預設風格"""
    PROFESSIONAL = "professional"    # 專業正式
    CASUAL = "casual"                # 輕鬆隨性
    HUMOROUS = "humorous"            # 幽默風趣
    INSPIRING = "inspiring"          # 激勵人心
    STORYTELLING = "storytelling"    # 故事敘述


class OutputFormat(str, Enum):
    """輸出格式"""
    FULL_ARTICLE = "full_article"    # 完整文章（300-500 字）
    SOCIAL_POST = "social_post"      # 社交貼文（100-150 字）
    CAPTION = "caption"              # Caption（50 字 + Hashtags）
    SCRIPT = "script"                # 腳本（分段式）


# ============================================
# 風格偏好子模型
# ============================================

class TonePreference(BaseModel):
    """語氣偏好"""
    formal_score: float = Field(default=0.5, ge=0, le=1, description="正式程度 (0=隨性, 1=正式)")
    humor_score: float = Field(default=0.3, ge=0, le=1, description="幽默程度")
    emotion_score: float = Field(default=0.5, ge=0, le=1, description="情感程度")
    directness_score: float = Field(default=0.5, ge=0, le=1, description="直接程度")


class ContentPreference(BaseModel):
    """內容偏好"""
    preferred_length: str = Field(default="medium", description="偏好長度 (short/medium/long)")
    use_emoji: bool = Field(default=True, description="使用表情符號")
    use_hashtags: bool = Field(default=True, description="使用 Hashtags")
    preferred_hashtag_count: int = Field(default=5, ge=0, le=30, description="偏好 Hashtag 數量")


class TopicPreference(BaseModel):
    """主題偏好"""
    liked_topics: List[str] = Field(default=[], description="喜歡的主題")
    disliked_topics: List[str] = Field(default=[], description="不喜歡的主題")
    liked_keywords: List[str] = Field(default=[], description="喜歡的關鍵字")
    disliked_keywords: List[str] = Field(default=[], description="不喜歡的關鍵字")


# ============================================
# StyleProfile 主模型
# ============================================

class StyleProfileBase(BaseModel):
    """風格檔案基礎"""
    preset_style: PresetStyle = Field(default=PresetStyle.CASUAL, description="預設風格")
    tone: TonePreference = Field(default_factory=TonePreference, description="語氣偏好")
    content: ContentPreference = Field(default_factory=ContentPreference, description="內容偏好")
    topics: TopicPreference = Field(default_factory=TopicPreference, description="主題偏好")


class StyleProfileCreate(BaseModel):
    """建立風格檔案"""
    preset_style: PresetStyle = PresetStyle.CASUAL


class StyleProfileUpdate(BaseModel):
    """更新風格檔案"""
    preset_style: Optional[PresetStyle] = None
    tone: Optional[TonePreference] = None
    content: Optional[ContentPreference] = None
    topics: Optional[TopicPreference] = None


class StyleProfileResponse(StyleProfileBase):
    """風格檔案回應"""
    id: str
    user_id: str
    learning_stage: LearningStage = LearningStage.COLD_START
    total_ratings: int = 0
    positive_ratings: int = 0
    negative_ratings: int = 0
    confidence_score: float = 0.0
    last_updated_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class StyleProfileStats(BaseModel):
    """風格檔案統計"""
    user_id: str
    learning_stage: LearningStage
    total_ratings: int
    positive_ratio: float
    confidence_score: float
    top_liked_topics: List[str]
    top_disliked_topics: List[str]
    tone_summary: Dict[str, float]


# ============================================
# 預設風格定義
# ============================================

PRESET_STYLE_CONFIGS: Dict[PresetStyle, Dict[str, Any]] = {
    PresetStyle.PROFESSIONAL: {
        "name": "專業正式",
        "description": "適合商業、財經、科技等專業內容",
        "tone": TonePreference(
            formal_score=0.9,
            humor_score=0.1,
            emotion_score=0.3,
            directness_score=0.8
        ),
        "content": ContentPreference(
            preferred_length="long",
            use_emoji=False,
            use_hashtags=True,
            preferred_hashtag_count=3
        ),
        "prompt_hints": [
            "使用專業術語",
            "引用數據和統計",
            "保持客觀中立",
            "結構清晰有條理"
        ]
    },
    PresetStyle.CASUAL: {
        "name": "輕鬆隨性",
        "description": "適合生活、旅遊、美食等日常內容",
        "tone": TonePreference(
            formal_score=0.3,
            humor_score=0.5,
            emotion_score=0.6,
            directness_score=0.5
        ),
        "content": ContentPreference(
            preferred_length="medium",
            use_emoji=True,
            use_hashtags=True,
            preferred_hashtag_count=5
        ),
        "prompt_hints": [
            "使用口語化表達",
            "加入個人感受",
            "輕鬆有趣的語氣",
            "適當使用表情符號"
        ]
    },
    PresetStyle.HUMOROUS: {
        "name": "幽默風趣",
        "description": "適合娛樂、趣聞、創意內容",
        "tone": TonePreference(
            formal_score=0.1,
            humor_score=0.9,
            emotion_score=0.7,
            directness_score=0.4
        ),
        "content": ContentPreference(
            preferred_length="short",
            use_emoji=True,
            use_hashtags=True,
            preferred_hashtag_count=8
        ),
        "prompt_hints": [
            "加入雙關語或諧音梗",
            "使用誇張修辭",
            "創造意外轉折",
            "讓讀者會心一笑"
        ]
    },
    PresetStyle.INSPIRING: {
        "name": "激勵人心",
        "description": "適合勵志、成長、心靈雞湯內容",
        "tone": TonePreference(
            formal_score=0.5,
            humor_score=0.2,
            emotion_score=0.9,
            directness_score=0.6
        ),
        "content": ContentPreference(
            preferred_length="medium",
            use_emoji=True,
            use_hashtags=True,
            preferred_hashtag_count=5
        ),
        "prompt_hints": [
            "傳遞正能量",
            "使用激勵性語句",
            "分享成功經驗",
            "引發讀者共鳴"
        ]
    },
    PresetStyle.STORYTELLING: {
        "name": "故事敘述",
        "description": "適合分享經歷、教學、深度內容",
        "tone": TonePreference(
            formal_score=0.4,
            humor_score=0.3,
            emotion_score=0.7,
            directness_score=0.5
        ),
        "content": ContentPreference(
            preferred_length="long",
            use_emoji=True,
            use_hashtags=True,
            preferred_hashtag_count=4
        ),
        "prompt_hints": [
            "使用故事結構",
            "描繪場景細節",
            "建立情感連結",
            "有開頭、發展、結尾"
        ]
    }
}


# ============================================
# 輸出格式定義
# ============================================

OUTPUT_FORMAT_CONFIGS: Dict[OutputFormat, Dict[str, Any]] = {
    OutputFormat.FULL_ARTICLE: {
        "name": "完整文章",
        "description": "300-500 字的完整文章",
        "min_length": 300,
        "max_length": 500,
        "structure": ["開頭引言", "主體內容", "結尾總結"],
        "hashtag_count": 3,
    },
    OutputFormat.SOCIAL_POST: {
        "name": "社交貼文",
        "description": "100-150 字的社交媒體貼文",
        "min_length": 100,
        "max_length": 150,
        "structure": ["吸睛開頭", "核心訊息", "行動呼籲"],
        "hashtag_count": 5,
    },
    OutputFormat.CAPTION: {
        "name": "Caption",
        "description": "50 字內 + Hashtags",
        "min_length": 20,
        "max_length": 50,
        "structure": ["精簡內容"],
        "hashtag_count": 10,
    },
    OutputFormat.SCRIPT: {
        "name": "腳本",
        "description": "分段式影片/Podcast 腳本",
        "min_length": 200,
        "max_length": 400,
        "structure": ["Hook", "介紹", "主體1", "主體2", "總結", "CTA"],
        "hashtag_count": 5,
    },
}


def get_learning_stage(total_ratings: int) -> LearningStage:
    """根據評分數量判斷學習階段"""
    if total_ratings < 20:
        return LearningStage.COLD_START
    elif total_ratings < 100:
        return LearningStage.LEARNING
    else:
        return LearningStage.MATURE


def calculate_confidence_score(
    total_ratings: int,
    positive_ratio: float,
    consistency_score: float = 0.5
) -> float:
    """
    計算信心分數
    
    公式：confidence = 0.4 * quantity_factor + 0.3 * positive_ratio + 0.3 * consistency
    
    Args:
        total_ratings: 總評分數
        positive_ratio: 正面評分比例
        consistency_score: 一致性分數
        
    Returns:
        信心分數 (0-1)
    """
    # 數量因子：評分越多，信心越高（最大 100 個達到滿分）
    quantity_factor = min(total_ratings / 100, 1.0)
    
    # 計算信心分數
    confidence = (
        0.4 * quantity_factor +
        0.3 * positive_ratio +
        0.3 * consistency_score
    )
    
    return round(confidence, 3)


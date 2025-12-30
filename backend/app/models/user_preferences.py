"""
UserPreferences 資料模型
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class SourcePreferences(BaseModel):
    """來源偏好設定"""
    fashion: List[str] = Field(default_factory=list, description="時尚來源偏好")
    food: List[str] = Field(default_factory=list, description="美食來源偏好")
    trend: List[str] = Field(default_factory=list, description="社會趨勢來源偏好")


class StylePreferences(BaseModel):
    """風格偏好設定"""
    article_style: str = Field(default="influencer", description="文章風格（influencer/formal/academic）")
    photo_style: str = Field(default="mixed", description="照片風格（close_up/panoramic/mixed）")
    script_style: str = Field(default="fast_paced", description="劇本風格（fast_paced/narrative/humorous）")


class InteractionStats(BaseModel):
    """互動統計"""
    total_likes: int = Field(default=0, description="喜歡次數")
    total_dislikes: int = Field(default=0, description="不喜歡次數")
    total_edits: int = Field(default=0, description="修改次數")
    total_replaces: int = Field(default=0, description="替換次數")
    avg_view_time: float = Field(default=0.0, description="平均停留時間（秒）")


class CategoryScores(BaseModel):
    """分類分數"""
    fashion: float = Field(default=0.0, description="時尚分數")
    food: float = Field(default=0.0, description="美食分數")
    social: float = Field(default=0.0, description="社會趨勢分數")


class UserPreferences(BaseModel):
    """UserPreferences 資料模型（擴充版）"""
    id: str = Field(default="user_default", description="使用者 ID（單一使用者）")
    
    # 舊版權重（保留向後兼容）
    fashion_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="時尚權重")
    food_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="美食權重")
    trend_weight: float = Field(default=0.2, ge=0.0, le=1.0, description="社會趨勢權重")
    
    # 新版偏好模型（專家建議）
    category_scores: Optional[CategoryScores] = Field(
        default_factory=lambda: CategoryScores(),
        description="分類分數（根據互動計算）"
    )
    style_preferences: Optional[StylePreferences] = Field(
        default_factory=lambda: StylePreferences(),
        description="風格偏好"
    )
    interaction_stats: Optional[InteractionStats] = Field(
        default_factory=lambda: InteractionStats(),
        description="互動統計"
    )
    
    keywords: List[str] = Field(default_factory=list, description="偏好關鍵字")
    excluded_keywords: List[str] = Field(default_factory=list, description="排除關鍵字")
    source_preferences: SourcePreferences = Field(
        default_factory=SourcePreferences,
        description="來源偏好"
    )
    last_interaction: Optional[datetime] = Field(None, description="最後互動時間")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    @model_validator(mode='after')
    def validate_weights_sum(self):
        """驗證權重總和為 1.0"""
        total = self.fashion_weight + self.food_weight + self.trend_weight
        if abs(total - 1.0) > 0.01:  # 允許小數點誤差
            raise ValueError(f'權重總和必須為 1.0，當前總和為 {total:.2f}')
        return self

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

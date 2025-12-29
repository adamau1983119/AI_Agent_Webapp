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


class UserPreferences(BaseModel):
    """UserPreferences 資料模型"""
    id: str = Field(default="user_default", description="使用者 ID（單一使用者）")
    fashion_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="時尚權重")
    food_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="美食權重")
    trend_weight: float = Field(default=0.2, ge=0.0, le=1.0, description="社會趨勢權重")
    keywords: List[str] = Field(default_factory=list, description="偏好關鍵字")
    excluded_keywords: List[str] = Field(default_factory=list, description="排除關鍵字")
    source_preferences: SourcePreferences = Field(
        default_factory=SourcePreferences,
        description="來源偏好"
    )
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

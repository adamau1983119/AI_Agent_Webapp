"""
UserPreferences Schemas
用於 UserPreferences API 的請求和回應模型
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from app.models.user_preferences import SourcePreferences


class UserPreferencesUpdate(BaseModel):
    """更新 UserPreferences 請求"""
    fashion_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="時尚權重")
    food_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="美食權重")
    trend_weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="社會趨勢權重")
    keywords: Optional[List[str]] = Field(None, description="偏好關鍵字")
    excluded_keywords: Optional[List[str]] = Field(None, description="排除關鍵字")
    source_preferences: Optional[SourcePreferences] = Field(None, description="來源偏好")

    @model_validator(mode='after')
    def validate_weights_sum(self):
        """驗證權重總和為 1.0（如果所有權重都已提供）"""
        # 只驗證所有權重都已提供的情況
        if all(w is not None for w in [self.fashion_weight, self.food_weight, self.trend_weight]):
            total = self.fashion_weight + self.food_weight + self.trend_weight
            if abs(total - 1.0) > 0.01:  # 允許小數點誤差
                raise ValueError(f'權重總和必須為 1.0，當前總和為 {total:.2f}')
        return self


class UserPreferencesResponse(BaseModel):
    """UserPreferences 回應模型"""
    id: str = Field(..., description="使用者 ID")
    fashion_weight: float = Field(..., description="時尚權重")
    food_weight: float = Field(..., description="美食權重")
    trend_weight: float = Field(..., description="社會趨勢權重")
    keywords: List[str] = Field(..., description="偏好關鍵字")
    excluded_keywords: List[str] = Field(..., description="排除關鍵字")
    source_preferences: SourcePreferences = Field(..., description="來源偏好")
    updated_at: Optional[datetime] = Field(None, description="更新時間")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

"""
Recommendation Schemas
用於 Recommendation API 的請求和回應模型
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.topic import Category


class RecommendationResponse(BaseModel):
    """Recommendation 回應模型"""
    id: str = Field(..., description="推薦唯一識別碼")
    user_id: str = Field(..., description="顧客 ID")
    category: Category = Field(..., description="主題分類")
    keyword: str = Field(..., description="推薦關鍵字")
    confidence_score: float = Field(..., description="推薦信心分數")
    reason: Optional[str] = Field(None, description="推薦原因")
    generated_at: datetime = Field(..., description="生成時間")
    interaction_result: Optional[Dict[str, Any]] = Field(None, description="互動結果")
    effectiveness: Optional[str] = Field(None, description="推薦效果")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RecommendationListResponse(BaseModel):
    """推薦列表回應"""
    user_id: str = Field(..., description="顧客 ID")
    recommendations: List[RecommendationResponse] = Field(..., description="推薦列表")


class RecommendationHistoryResponse(BaseModel):
    """推薦歷史回應"""
    user_id: str = Field(..., description="顧客 ID")
    history: List[RecommendationResponse] = Field(..., description="推薦歷史")


"""
Recommendation 資料模型
用於儲存推薦結果
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.topic import Category


class Recommendation(BaseModel):
    """Recommendation 資料模型"""
    id: str = Field(..., description="推薦唯一識別碼")
    user_id: str = Field(..., description="顧客 ID")
    category: Category = Field(..., description="主題分類")
    keyword: str = Field(..., description="推薦關鍵字")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="推薦信心分數")
    reason: Optional[str] = Field(None, description="推薦原因")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成時間")
    interaction_result: Optional[Dict[str, Any]] = Field(None, description="互動結果")
    effectiveness: Optional[str] = Field(None, description="推薦效果（high/medium/low）")

    class Config:
        """Pydantic 配置"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


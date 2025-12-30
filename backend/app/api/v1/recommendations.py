"""
Recommendations API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendationListResponse,
    RecommendationHistoryResponse,
)
from app.services.repositories.recommendation_repository import RecommendationRepository
from app.services.repositories.preference_service import PreferenceService
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Repository 和 Service 實例
recommendation_repo = RecommendationRepository()
preference_service = PreferenceService()
topic_repo = TopicRepository()


def _convert_to_response(recommendation_doc: dict) -> RecommendationResponse:
    """將 MongoDB 文檔轉換為 RecommendationResponse"""
    recommendation_doc.pop("_id", None)
    return RecommendationResponse(**recommendation_doc)


@router.get("/{user_id}", response_model=RecommendationListResponse)
async def get_recommendations(
    user_id: str = Path(..., description="顧客 ID"),
    category: Optional[Category] = Query(None, description="主題分類"),
    limit: int = Query(5, ge=1, le=20, description="返回數量")
):
    """
    根據偏好模型生成推薦主題
    """
    try:
        # 先更新偏好模型（根據最新互動數據）
        await preference_service.update_preferences_from_interactions(user_id)
        
        # 取得偏好模型
        preferences = await preference_service.get_preferences(user_id)
        
        # 計算推薦分數並生成推薦
        recommendations = await preference_service.generate_recommendations(
            user_id=user_id,
            preferences=preferences,
            category=category,
            limit=limit
        )
        
        # 轉換為回應格式
        recommendation_responses = [
            _convert_to_response(rec) for rec in recommendations
        ]
        
        return RecommendationListResponse(
            user_id=user_id,
            recommendations=recommendation_responses
        )
    except Exception as e:
        logger.error(f"取得推薦失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/history", response_model=RecommendationHistoryResponse)
async def get_recommendation_history(
    user_id: str = Path(..., description="顧客 ID"),
    start_date: Optional[str] = Query(None, description="開始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="結束日期（YYYY-MM-DD）")
):
    """
    查詢推薦歷史和效果
    """
    try:
        # 轉換日期字串
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # 查詢推薦歷史
        history = await recommendation_repo.get_recommendation_history(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt
        )
        
        # 轉換為回應格式
        history_responses = [
            _convert_to_response(rec) for rec in history
        ]
        
        return RecommendationHistoryResponse(
            user_id=user_id,
            history=history_responses
        )
    except Exception as e:
        logger.error(f"查詢推薦歷史失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


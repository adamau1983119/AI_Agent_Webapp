"""
評分 API 端點
Phase 4: AI 個人化
提供評分提交和查詢功能
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.rating import (
    RatingCreate, RatingResponse, RatingStats, RatingValue, RatingReason,
    RATING_REASON_LABELS, get_positive_reasons, get_negative_reasons
)
from app.services.style_learning_service import style_learning_service
from app.middleware.jwt_auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ratings", tags=["ratings"])


@router.post("", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
async def submit_rating(
    rating_data: RatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    提交評分
    
    - **content_id**: 內容 ID（必須）
    - **topic_id**: 主題 ID（必須）
    - **value**: 評分值（like/dislike）
    - **reasons**: 評分原因（可多選）
    - **comment**: 額外評論（可選）
    
    評分會自動更新用戶的風格檔案
    """
    rating, error = await style_learning_service.submit_rating(
        user_id=current_user["id"],
        rating_data=rating_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return RatingResponse(**rating)


@router.get("/reasons")
async def get_rating_reasons(
    rating_type: Optional[str] = Query(None, description="評分類型 (like/dislike)")
):
    """
    取得評分原因選項
    
    - **rating_type**: 可選，篩選特定類型的原因
    """
    if rating_type == "like":
        reasons = get_positive_reasons()
    elif rating_type == "dislike":
        reasons = get_negative_reasons()
    else:
        reasons = list(RatingReason)
    
    return {
        "reasons": [
            {
                "value": r.value,
                "label": RATING_REASON_LABELS[r]["label"],
                "sentiment": RATING_REASON_LABELS[r]["sentiment"]
            }
            for r in reasons
        ]
    }


@router.get("/stats", response_model=RatingStats)
async def get_my_rating_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的評分統計
    
    返回：
    - 總評分數
    - 正/負評分比例
    - 按原因分類統計
    - 按內容格式分類統計
    - 按主題類別分類統計
    """
    stats = await style_learning_service.get_rating_stats(current_user["id"])
    return RatingStats(**stats)


@router.get("/history")
async def get_my_rating_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的評分歷史
    
    支援分頁
    """
    result = await style_learning_service.get_rating_history(
        user_id=current_user["id"],
        page=page,
        limit=limit
    )
    
    return result


@router.get("/content/{content_id}")
async def get_my_rating_for_content(
    content_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取得我對特定內容的評分
    """
    from app.services.repositories.rating_repository import RatingRepository
    repo = RatingRepository()
    
    rating = await repo.get_user_rating_for_content(
        current_user["id"],
        content_id
    )
    
    if not rating:
        return {"rated": False}
    
    return {
        "rated": True,
        "rating": RatingResponse(**rating)
    }


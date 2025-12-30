"""
Interactions API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionListResponse,
    InteractionStatsResponse,
)
from app.services.repositories.interaction_repository import InteractionRepository
from app.services.repositories.topic_repository import TopicRepository
from app.models.interaction import InteractionAction
from app.models.topic import Category
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interactions", tags=["interactions"])

# Repository 實例
interaction_repo = InteractionRepository()
topic_repo = TopicRepository()


def _convert_to_response(interaction_doc: dict) -> InteractionResponse:
    """將 MongoDB 文檔轉換為 InteractionResponse"""
    interaction_doc.pop("_id", None)
    return InteractionResponse(**interaction_doc)


@router.post("", response_model=InteractionResponse)
async def create_interaction(interaction_data: InteractionCreate):
    """
    記錄互動
    """
    try:
        # 取得主題資訊以獲取分類
        topic = await topic_repo.get_topic_by_id(interaction_data.topic_id)
        category = topic.get("category") if topic else None
        
        # 建立互動記錄
        created = await interaction_repo.create_interaction(
            user_id=interaction_data.user_id,
            topic_id=interaction_data.topic_id,
            action=interaction_data.action,
            article_id=interaction_data.article_id,
            photo_id=interaction_data.photo_id,
            script_id=interaction_data.script_id,
            duration=interaction_data.duration,
            category=category
        )
        
        return _convert_to_response(created)
    except Exception as e:
        logger.error(f"記錄互動失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=InteractionListResponse)
async def get_user_interactions(
    user_id: str = Path(..., description="顧客 ID"),
    action: Optional[InteractionAction] = Query(None, description="互動類型"),
    category: Optional[Category] = Query(None, description="主題分類"),
    start_date: Optional[str] = Query(None, description="開始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="結束日期（YYYY-MM-DD）"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=100, description="每頁數量")
):
    """
    查詢顧客的所有互動記錄
    """
    try:
        # 轉換日期字串
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        # 查詢互動記錄
        interactions, total = await interaction_repo.get_interactions_by_user(
            user_id=user_id,
            action=action,
            category=category.value if category else None,
            start_date=start_dt,
            end_date=end_dt,
            page=page,
            limit=limit
        )
        
        # 轉換為回應格式
        interaction_responses = [
            _convert_to_response(interaction) for interaction in interactions
        ]
        
        from app.schemas.common import PaginationResponse
        pagination = PaginationResponse.create(page, limit, total)
        
        return InteractionListResponse(
            user_id=user_id,
            interactions=interaction_responses,
            pagination=pagination
        )
    except Exception as e:
        logger.error(f"查詢互動記錄失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/stats", response_model=InteractionStatsResponse)
async def get_interaction_stats(
    user_id: str = Path(..., description="顧客 ID")
):
    """
    取得顧客的互動統計數據
    """
    try:
        stats = await interaction_repo.get_interaction_stats(user_id)
        
        return InteractionStatsResponse(
            user_id=user_id,
            stats=stats
        )
    except Exception as e:
        logger.error(f"取得互動統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


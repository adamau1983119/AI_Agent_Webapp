"""
Feed 健康監控 API
提供 RSS Feed 健康狀態查詢和管理端點
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from app.services.feed_health_service import FeedHealthService
from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.services.scoring_service import DiversityScorer
from app.models.topic import Category

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feeds", tags=["Feed Health"])

# 初始化服務
health_repo = FeedHealthRepository()
health_service = FeedHealthService(health_repo)
diversity_scorer = DiversityScorer()


# ========== Response Schemas ==========

class FeedHealthResponse(BaseModel):
    """單一 Feed 健康狀態"""
    feed_url: str
    source_name: Optional[str] = None
    health_score: int
    health_status: str
    reliability_score: float
    is_paused: bool
    checked_at: datetime


class CategoryHealthResponse(BaseModel):
    """分類健康狀態"""
    category: str
    total_feeds: int
    healthy_feeds: int
    paused_feeds: int
    average_health_score: float
    overall_status: str
    generated_at: datetime


class StatsResponse(BaseModel):
    """統計摘要"""
    last_hour: dict
    last_24_hours: dict
    feeds: dict
    generated_at: datetime


class DiversityReportResponse(BaseModel):
    """多樣性報告"""
    score: float
    total_topics: int
    unique_sources: int
    source_distribution: dict
    status: str
    passed: bool


# ========== API Endpoints ==========

@router.get("/health", summary="獲取所有 Feed 健康狀態")
async def get_all_feeds_health():
    """
    獲取所有分類的 Feed 健康狀態
    
    Returns:
        所有分類的健康狀態報告
    """
    try:
        result = await health_service.get_all_categories_health()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"獲取健康狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{category}", summary="獲取分類的 Feed 健康狀態")
async def get_category_feeds_health(category: str):
    """
    獲取指定分類的 Feed 健康狀態
    
    Args:
        category: 分類名稱 (fashion, food, trend)
        
    Returns:
        分類的健康狀態報告
    """
    try:
        # 驗證分類
        category_enum = None
        for cat in Category:
            if cat.value.lower() == category.lower():
                category_enum = cat
                break
        
        if not category_enum:
            from app.utils.i18n import get_error_message, get_user_language
            language = get_user_language(request=request)
            raise HTTPException(
                status_code=400,
                detail=get_error_message("feed.invalid_category", language)
            )
        
        result = await health_service.get_category_health(category_enum)
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取分類健康狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="獲取統計摘要")
async def get_feeds_stats():
    """
    獲取 Feed 請求的統計摘要
    
    Returns:
        統計摘要（過去 1 小時、24 小時的請求統計）
    """
    try:
        result = await health_service.get_stats_summary()
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"獲取統計失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problematic", summary="獲取有問題的 Feed 列表")
async def get_problematic_feeds(
    threshold: float = Query(0.7, ge=0, le=1, description="可靠度閾值")
):
    """
    獲取可靠度低於閾值的 Feed 列表
    
    Args:
        threshold: 可靠度閾值 (0-1)，低於此值視為有問題
        
    Returns:
        問題 Feed 列表
    """
    try:
        result = await health_service.get_problematic_feeds(threshold)
        return {
            "success": True,
            "data": {
                "threshold": threshold,
                "count": len(result),
                "feeds": result
            }
        }
    except Exception as e:
        logger.error(f"獲取問題 Feed 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feed-health", summary="獲取單一 Feed 健康狀態")
async def get_single_feed_health(
    feed_url: str = Query(..., description="Feed URL")
):
    """
    獲取單一 Feed 的詳細健康狀態
    
    Args:
        feed_url: Feed URL
        
    Returns:
        Feed 健康狀態詳情
    """
    try:
        result = await health_service.get_feed_health(feed_url)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"獲取 Feed 健康狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diversity-report", summary="獲取多樣性報告")
async def get_diversity_report(
    category: Optional[str] = Query(None, description="分類過濾 (fashion, food, trend)")
):
    """
    獲取內容來源多樣性報告
    
    這個報告顯示最近收集的主題是否來自多樣化的來源。
    多樣性分數 >= 0.6 為通過標準。
    
    Args:
        category: 可選的分類過濾
        
    Returns:
        多樣性報告
    """
    try:
        # 這裡需要從資料庫獲取最近的主題
        # 暫時返回模擬數據，實際實現需要整合 TopicRepository
        from app.services.repositories.topic_repository import TopicRepository
        topic_repo = TopicRepository()
        
        # 獲取最近的主題
        filter_params = {}
        if category:
            filter_params["category"] = category
        
        topics, total = await topic_repo.list_topics(
            category=Category(category) if category else None,
            limit=30
        )
        
        # 計算多樣性
        report = diversity_scorer.get_diversity_report(topics)
        
        return {
            "success": True,
            "data": {
                "category": category or "all",
                "report": report
            }
        }
    except Exception as e:
        logger.error(f"獲取多樣性報告失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause", summary="手動暫停 Feed")
async def pause_feed(
    feed_url: str = Query(..., description="Feed URL"),
    reason: str = Query("Manual pause", description="暫停原因")
):
    """
    手動暫停指定的 Feed
    
    暫停的 Feed 在收集主題時會被跳過。
    
    Args:
        feed_url: Feed URL
        reason: 暫停原因
        
    Returns:
        操作結果
    """
    try:
        # 通過記錄多次失敗來觸發暫停機制
        for _ in range(3):
            await health_repo.record_failure(feed_url, f"Manual pause: {reason}")
        
        return {
            "success": True,
            "message": f"Feed 已暫停: {feed_url}",
            "data": {
                "feed_url": feed_url,
                "reason": reason,
                "is_paused": True
            }
        }
    except Exception as e:
        logger.error(f"暫停 Feed 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", summary="恢復 Feed")
async def resume_feed(
    feed_url: str = Query(..., description="Feed URL")
):
    """
    恢復被暫停的 Feed
    
    通過記錄一次成功來重置失敗計數。
    
    Args:
        feed_url: Feed URL
        
    Returns:
        操作結果
    """
    try:
        # 記錄一次成功來重置狀態
        await health_repo.record_success(feed_url, "Manual resume")
        
        is_still_paused = await health_repo.is_paused(feed_url)
        
        return {
            "success": True,
            "message": f"Feed 恢復請求已處理: {feed_url}",
            "data": {
                "feed_url": feed_url,
                "is_paused": is_still_paused
            }
        }
    except Exception as e:
        logger.error(f"恢復 Feed 失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


"""
Feed 健康監控 API v4.0
提供 RSS Feed 健康狀態查詢、來源名單管理端點

Phase 1 完成：
- 1.3.1 白名單 CRUD API
- 1.3.2 黑名單 CRUD API
- 1.3.9 管理員專用健康報告端點
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from pydantic import BaseModel
from datetime import datetime

from app.services.feed_health_service import FeedHealthService, SourceListType
from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.services.repositories.source_list_repository import SourceListRepository
from app.services.scoring_service import DiversityScorer
from app.models.topic import Category
from app.models.user import UserRole
from app.middleware.jwt_auth import jwt_auth, get_current_user, require_role

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feeds", tags=["Feed Health"])

# 初始化服務
health_repo = FeedHealthRepository()
source_list_repo = SourceListRepository()
health_service = FeedHealthService(health_repo, source_list_repo)
diversity_scorer = DiversityScorer()


# ========== Request Schemas ==========

class SourceListRequest(BaseModel):
    """來源名單操作請求"""
    feed_url: str
    reason: str = ""


class SourceListRemoveRequest(BaseModel):
    """來源名單移除請求"""
    feed_url: str


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


# ========== 1.3.1 白名單管理 API ==========

@router.get("/whitelist", summary="查詢白名單")
async def get_whitelist(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    查詢白名單所有來源（管理員專用）
    """
    try:
        whitelist = await health_service.get_whitelist()
        return {
            "success": True,
            "data": {
                "count": len(whitelist),
                "items": whitelist
            }
        }
    except Exception as e:
        logger.error(f"查詢白名單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whitelist", summary="新增白名單來源")
async def add_to_whitelist(
    request_data: SourceListRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    將來源加入白名單（管理員專用）
    
    白名單來源不會被 Level 3-4 自動停用
    """
    try:
        success = await health_service.add_to_whitelist(
            request_data.feed_url,
            request_data.reason
        )
        
        if success:
            return {
                "success": True,
                "message": f"已將 {request_data.feed_url} 加入白名單",
                "data": {"feed_url": request_data.feed_url, "list_type": "whitelist"}
            }
        else:
            return {
                "success": False,
                "message": f"{request_data.feed_url} 已在白名單中"
            }
    except Exception as e:
        logger.error(f"加入白名單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/whitelist", summary="從白名單移除")
async def remove_from_whitelist(
    feed_url: str = Query(..., description="Feed URL"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    從白名單移除來源（管理員專用）
    """
    try:
        success = await source_list_repo.remove_from_list(feed_url, "whitelist")
        health_service._invalidate_cache()
        
        return {
            "success": success,
            "message": f"已從白名單移除 {feed_url}" if success else f"{feed_url} 不在白名單中"
        }
    except Exception as e:
        logger.error(f"從白名單移除失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 1.3.2 黑名單管理 API ==========

@router.get("/blacklist", summary="查詢黑名單")
async def get_blacklist(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    查詢黑名單所有來源（管理員專用）
    """
    try:
        blacklist = await health_service.get_blacklist()
        return {
            "success": True,
            "data": {
                "count": len(blacklist),
                "items": blacklist
            }
        }
    except Exception as e:
        logger.error(f"查詢黑名單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blacklist", summary="新增黑名單來源")
async def add_to_blacklist(
    request_data: SourceListRequest,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    將來源加入黑名單（管理員專用）
    
    黑名單來源永遠不會被使用
    """
    try:
        success = await health_service.add_to_blacklist(
            request_data.feed_url,
            request_data.reason
        )
        
        if success:
            return {
                "success": True,
                "message": f"已將 {request_data.feed_url} 加入黑名單",
                "data": {"feed_url": request_data.feed_url, "list_type": "blacklist"}
            }
        else:
            return {
                "success": False,
                "message": f"{request_data.feed_url} 已在黑名單中"
            }
    except Exception as e:
        logger.error(f"加入黑名單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/blacklist", summary="從黑名單移除")
async def remove_from_blacklist(
    feed_url: str = Query(..., description="Feed URL"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    從黑名單移除來源（管理員專用）
    """
    try:
        success = await source_list_repo.remove_from_list(feed_url, "blacklist")
        health_service._invalidate_cache()
        
        return {
            "success": success,
            "message": f"已從黑名單移除 {feed_url}" if success else f"{feed_url} 不在黑名單中"
        }
    except Exception as e:
        logger.error(f"從黑名單移除失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 來源名單總覽 ==========

@router.get("/source-lists", summary="查詢所有名單")
async def get_all_source_lists(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    查詢所有來源名單（白名單 + 黑名單 + 灰名單）（管理員專用）
    """
    try:
        all_lists = await health_service.get_all_lists()
        return {
            "success": True,
            "data": all_lists
        }
    except Exception as e:
        logger.error(f"查詢名單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/source-lists", summary="從所有名單移除")
async def remove_from_all_lists(
    feed_url: str = Query(..., description="Feed URL"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    從所有名單移除來源（管理員專用）
    """
    try:
        success = await health_service.remove_from_lists(feed_url)
        return {
            "success": success,
            "message": f"已從所有名單移除 {feed_url}" if success else f"{feed_url} 不在任何名單中"
        }
    except Exception as e:
        logger.error(f"從名單移除失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== 1.3.9 管理員健康報告 API ==========

@router.get("/health", summary="獲取所有 Feed 健康狀態（管理員）")
async def get_all_feeds_health(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取所有分類的 Feed 健康狀態（管理員專用）
    
    包含：
    - 各分類健康狀態
    - 動態角色分配
    - 多樣性門檻
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


@router.get("/health/{category}", summary="獲取分類的 Feed 健康狀態（管理員）")
async def get_category_feeds_health(
    category: str,
    request: Request,
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取指定分類的 Feed 健康狀態（管理員專用）
    """
    try:
        category_enum = None
        for cat in Category:
            if cat.value.lower() == category.lower():
                category_enum = cat
                break
        
        if not category_enum:
            raise HTTPException(
                status_code=400,
                detail=f"無效的分類: {category}。有效值: fashion, food, trend"
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


@router.get("/stats", summary="獲取統計摘要（管理員）")
async def get_feeds_stats(
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取 Feed 請求的統計摘要（管理員專用）
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


@router.get("/problematic", summary="獲取有問題的 Feed 列表（管理員）")
async def get_problematic_feeds(
    threshold: float = Query(0.7, ge=0, le=1, description="可靠度閾值"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取可靠度低於閾值的 Feed 列表（管理員專用）
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


@router.get("/feed-health", summary="獲取單一 Feed 健康狀態（管理員）")
async def get_single_feed_health(
    feed_url: str = Query(..., description="Feed URL"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取單一 Feed 的詳細健康狀態（管理員專用）
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


@router.get("/diversity-report", summary="獲取多樣性報告（管理員）")
async def get_diversity_report(
    category: Optional[str] = Query(None, description="分類過濾 (fashion, food, trend)"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    獲取內容來源多樣性報告（管理員專用）
    
    包含各分類獨立的多樣性門檻：
    - Fashion: 0.65
    - Food: 0.55
    - Trend: 0.75
    """
    try:
        from app.services.repositories.topic_repository import TopicRepository
        topic_repo = TopicRepository()
        
        topics, total = await topic_repo.list_topics(
            category=Category(category) if category else None,
            limit=30
        )
        
        report = diversity_scorer.get_diversity_report(topics)
        
        # 添加各分類門檻資訊
        diversity_check = None
        if category:
            diversity_check = health_service.check_diversity(category, report["score"])
        
        return {
            "success": True,
            "data": {
                "category": category or "all",
                "report": report,
                "diversity_check": diversity_check,
                "thresholds": {
                    "fashion": health_service.get_diversity_threshold("fashion"),
                    "food": health_service.get_diversity_threshold("food"),
                    "trend": health_service.get_diversity_threshold("trend"),
                }
            }
        }
    except Exception as e:
        logger.error(f"獲取多樣性報告失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause", summary="手動暫停 Feed（管理員）")
async def pause_feed(
    feed_url: str = Query(..., description="Feed URL"),
    reason: str = Query("Manual pause", description="暫停原因"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    手動暫停指定的 Feed（管理員專用）
    """
    try:
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


@router.post("/resume", summary="恢復 Feed（管理員）")
async def resume_feed(
    feed_url: str = Query(..., description="Feed URL"),
    current_user: dict = Depends(require_role(UserRole.ADMIN))
):
    """
    恢復被暫停的 Feed（管理員專用）
    """
    try:
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

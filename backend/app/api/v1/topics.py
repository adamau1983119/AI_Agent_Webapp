"""
Topics API 端點
"""
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, Path, Header
from app.schemas.topic import (
    TopicCreate,
    TopicUpdate,
    TopicStatusUpdate,
    TopicResponse,
    TopicDetailResponse,
    TopicListResponse,
)
from app.schemas.common import PaginationResponse, ErrorResponse
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.services.search_service import SearchService, UserRole
from app.models.topic import Category, Status
from app.database import check_connection_from_request, get_database_from_request
from fastapi import Request
from app.config import settings
# 使用統一的 exceptions 模組，避免循環導入問題
from app.exceptions import ConnectionFailure
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topics", tags=["topics"])

# Repository 實例
topic_repo = TopicRepository()
content_repo = ContentRepository()
image_repo = ImageRepository()


def get_user_role_from_request(request: Request) -> UserRole:
    """
    從請求中獲取用戶角色
    
    Args:
        request: FastAPI 請求對象
        
    Returns:
        用戶角色（預設為 guest）
    """
    # 嘗試從 header 中獲取角色
    role_header = request.headers.get("X-User-Role", "").lower()
    
    # 驗證角色是否有效
    try:
        return UserRole(role_header) if role_header else UserRole.GUEST
    except ValueError:
        # 如果角色無效，預設為 guest
        return UserRole.GUEST


def _convert_to_response(topic_doc: dict) -> TopicResponse:
    """將 MongoDB 文檔轉換為 TopicResponse"""
    # 移除 MongoDB 的 _id
    topic_doc.pop("_id", None)
    return TopicResponse(**topic_doc)


@router.get("", response_model=TopicListResponse)
async def list_topics(
    request: Request,
    category: Optional[Category] = Query(None, description="分類篩選"),
    status: Optional[Status] = Query(None, description="狀態篩選"),
    date: Optional[str] = Query(None, description="日期篩選（YYYY-MM-DD）"),
    search: Optional[str] = Query(None, description="搜尋關鍵字（搜尋標題和來源）"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(10, ge=1, le=100, description="每頁數量"),
    sort: str = Query("generated_at", description="排序欄位"),
    order: str = Query("desc", description="排序順序（asc/desc）")
):
    """
    取得主題列表
    
    支援篩選、搜尋、分頁和排序
    """
    try:
        # 檢查資料庫連接狀態（從 app.state）
        is_connected, reason = await check_connection_from_request(request)
        if not is_connected:
            # 在開發環境中，資料庫未連接時返回空列表
            if settings.ENVIRONMENT == "development":
                logger.warning(f"資料庫未連接 ({reason})，返回空主題列表（開發環境）")
                pagination = PaginationResponse.create(page, limit, 0)
                return TopicListResponse(
                    data=[],
                    pagination=pagination
                )
            else:
                # 生產環境必須有資料庫連接
                raise HTTPException(
                    status_code=503,
                    detail=f"資料庫服務暫時不可用: {reason}"
                )
        
        # 從 app.state 獲取資料庫實例並傳遞給 repository
        db = get_database_from_request(request)
        topic_repo = TopicRepository(db=db) if db is not None else TopicRepository()
        
        topics, total = await topic_repo.list_topics(
            category=category,
            status=status,
            date=date,
            search=search,
            page=page,
            limit=limit,
            sort=sort,
            order=order
        )
        
        # 轉換為回應格式
        topic_responses = []
        for topic in topics:
            try:
                # 取得圖片數量和字數（如果查詢失敗，使用默認值）
                try:
                    image_count = await image_repo.count_by_topic_id(topic["id"])
                except Exception as e:
                    logger.warning(f"取得主題 {topic['id']} 的圖片數量失敗: {e}")
                    image_count = 0
                
                try:
                    content = await content_repo.get_content_by_topic_id(topic["id"])
                    word_count = content.get("word_count", 0) if content else 0
                except Exception as e:
                    logger.warning(f"取得主題 {topic['id']} 的內容失敗: {e}")
                    word_count = 0
                
                topic["image_count"] = image_count
                topic["word_count"] = word_count
                topic_responses.append(_convert_to_response(topic))
            except Exception as e:
                logger.warning(f"處理主題 {topic.get('id', 'unknown')} 時發生錯誤: {e}")
                # 即使處理單個主題失敗，也繼續處理其他主題
                # 使用默認值
                topic["image_count"] = 0
                topic["word_count"] = 0
                try:
                    topic_responses.append(_convert_to_response(topic))
                except Exception as e2:
                    logger.error(f"無法轉換主題 {topic.get('id', 'unknown')} 為回應格式: {e2}")
                    continue
        
        pagination = PaginationResponse.create(page, limit, total)
        
        return TopicListResponse(
            data=topic_responses,
            pagination=pagination
        )
    except ConnectionFailure as e:
        logger.error(f"資料庫連接失敗: {e}")
        if settings.ENVIRONMENT == "development":
            # 開發環境返回空列表
            pagination = PaginationResponse.create(page, limit, 0)
            return TopicListResponse(
                data=[],
                pagination=pagination
            )
        else:
            raise HTTPException(
                status_code=503,
                detail="資料庫服務暫時不可用，請稍後再試"
            )
    except Exception as e:
        logger.error(f"取得主題列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{topic_id}", response_model=TopicDetailResponse)
async def get_topic_detail(topic_id: str = Path(..., description="主題 ID")):
    """
    取得主題詳情
    
    包含內容和圖片資訊
    """
    try:
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 取得內容
        content = await content_repo.get_content_by_topic_id(topic_id)
        content_response = None
        if content:
            try:
                from app.schemas.content import ContentResponse
                from app.api.v1.contents import _convert_to_response
                content_response = _convert_to_response(content)
            except Exception as e:
                logger.warning(f"轉換內容資料失敗，跳過: {e}, content keys: {list(content.keys()) if isinstance(content, dict) else 'not dict'}")
                content_response = None
        
        # 取得圖片列表
        images = await image_repo.get_images_by_topic_id(topic_id)
        from app.schemas.image import ImageResponse
        image_responses = []
        for image in images:
            try:
                image.pop("_id", None)
                # 確保所有必需欄位都存在
                if "keywords" not in image or image["keywords"] is None:
                    image["keywords"] = []
                if "order" not in image:
                    image["order"] = 0
                if "license" not in image or not image.get("license"):
                    image["license"] = "Unknown"
                image_responses.append(ImageResponse(**image))
            except Exception as e:
                logger.warning(f"處理圖片資料失敗，跳過: {e}, image keys: {list(image.keys()) if isinstance(image, dict) else 'not dict'}")
                continue
        
        # 轉換為回應格式
        topic.pop("_id", None)
        
        # 確保所有必需欄位都存在
        required_fields = ["id", "title", "category", "status", "source", "generated_at", "updated_at"]
        for field in required_fields:
            if field not in topic:
                logger.error(f"主題 {topic_id} 缺少必需欄位: {field}, topic keys: {list(topic.keys())}")
                raise HTTPException(
                    status_code=500,
                    detail=f"主題資料不完整，缺少欄位: {field}"
                )
        
        # 確保有 created_at（如果沒有，使用 generated_at）
        if "created_at" not in topic or not topic.get("created_at"):
            topic["created_at"] = topic.get("generated_at", datetime.utcnow())
        
        # 處理 sources 資料，確保符合 SourceInfo 模型
        if "sources" in topic and topic["sources"]:
            from app.models.topic import SourceInfo
            processed_sources = []
            for source in topic["sources"]:
                try:
                    # 確保有 title（如果沒有，使用 name）
                    if "title" not in source or not source.get("title"):
                        source["title"] = source.get("name", "")
                    # 確保有 fetched_at（如果沒有，使用 verified_at）
                    if "fetched_at" not in source or not source.get("fetched_at"):
                        if "verified_at" in source and source.get("verified_at"):
                            from datetime import datetime
                            try:
                                verified_at = source["verified_at"]
                                if isinstance(verified_at, str):
                                    source["fetched_at"] = datetime.fromisoformat(verified_at.replace('Z', '+00:00'))
                                else:
                                    source["fetched_at"] = verified_at
                            except:
                                from datetime import datetime
                                source["fetched_at"] = datetime.utcnow()
                        else:
                            from datetime import datetime
                            source["fetched_at"] = datetime.utcnow()
                    processed_sources.append(SourceInfo(**source))
                except Exception as e:
                    logger.warning(f"處理 source 資料失敗，跳過: {e}")
                    continue
            topic["sources"] = processed_sources
        else:
            # 如果沒有 sources，使用空列表
            topic["sources"] = []
        
        try:
            # 確保 category 和 status 是正確的類型
            if isinstance(topic.get("category"), str):
                from app.models.topic import Category
                try:
                    topic["category"] = Category(topic["category"])
                except:
                    logger.warning(f"無法轉換 category: {topic.get('category')}")
            
            if isinstance(topic.get("status"), str):
                from app.models.topic import Status
                try:
                    topic["status"] = Status(topic["status"])
                except:
                    logger.warning(f"無法轉換 status: {topic.get('status')}")
            
            response = TopicDetailResponse(
                **topic,
                content=content_response,
                images=image_responses
            )
            return response
        except Exception as e:
            logger.error(f"建立 TopicDetailResponse 失敗: {e}")
            logger.error(f"Topic 資料: {topic}")
            logger.error(f"Topic keys: {list(topic.keys())}")
            logger.error(f"Topic values: {[(k, type(v).__name__) for k, v in topic.items()]}")
            logger.error(f"Content response: {content_response}")
            logger.error(f"Image responses count: {len(image_responses)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(
                status_code=500,
                detail=f"建立主題詳情回應失敗: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得主題詳情失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: str = Path(..., description="主題 ID"),
    update_data: TopicUpdate = ...
):
    """
    更新主題
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 準備更新資料（只包含提供的欄位）
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 更新主題
        updated = await topic_repo.update_topic(topic_id, update_dict)
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="更新主題失敗"
            )
        
        updated.pop("_id", None)
        return _convert_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新主題失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{topic_id}/status", response_model=TopicResponse)
async def update_topic_status(
    topic_id: str = Path(..., description="主題 ID"),
    status_update: TopicStatusUpdate = ...
):
    """
    更新主題狀態
    """
    try:
        updated = await topic_repo.update_topic_status(
            topic_id,
            status_update.status
        )
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        updated.pop("_id", None)
        return _convert_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新主題狀態失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/all")
async def delete_all_topics(request: Request):
    """
    批量刪除所有主題（硬刪除）- 僅用於開發/測試環境
    """
    try:
        db = get_database_from_request(request)
        if db is None:
            raise HTTPException(
                status_code=400,
                detail="資料庫未連接，無法刪除主題"
            )
        
        collection = db["topics"]
        
        # 獲取刪除前的數量
        count_before = await collection.count_documents({})
        
        # 硬刪除所有主題
        result = await collection.delete_many({})
        deleted_count = result.deleted_count
        
        logger.info(f"✅ 已刪除所有主題，共 {deleted_count} 個")
        
        return {
            "message": f"已刪除所有主題",
            "deleted_count": deleted_count,
            "count_before": count_before
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除所有主題失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/today")
async def delete_today_topics(request: Request):
    """
    批量刪除今日生成的主題（硬刪除）
    """
    try:
        db = get_database_from_request(request)
        if db is None:
            raise HTTPException(
                status_code=400,
                detail="資料庫未連接，無法刪除主題"
            )
        
        # 獲取今日日期（UTC）
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # 查詢今日主題
        collection = db["topics"]
        filter_query = {
            "generated_at": {
                "$gte": today_start,
                "$lte": today_end
            }
        }
        
        # 獲取要刪除的主題 ID 列表（用於日誌）
        today_topics = await collection.find(filter_query).to_list(length=None)
        topic_ids = [t.get("id") for t in today_topics if t.get("id")]
        
        # 硬刪除今日主題
        result = await collection.delete_many(filter_query)
        deleted_count = result.deleted_count
        
        logger.info(f"✅ 已刪除 {deleted_count} 個今日主題")
        if topic_ids:
            logger.info(f"   刪除的主題 ID: {topic_ids[:10]}...")  # 只顯示前10個
        
        return {
            "message": f"已刪除 {deleted_count} 個今日主題",
            "deleted_count": deleted_count,
            "topic_ids": topic_ids
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除今日主題失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}")
async def delete_topic(topic_id: str = Path(..., description="主題 ID")):
    """
    刪除主題（軟刪除）
    """
    try:
        success = await topic_repo.delete_topic(topic_id)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        return {
            "message": "主題已刪除",
            "data": {"id": topic_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除主題失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 搜尋 API 端點 ====================

@router.get("/search")
async def search_topics(
    request: Request,
    query: str = Query(..., min_length=2, max_length=100, description="搜尋關鍵字（2-100字元）"),
    category: Optional[Category] = Query(None, description="分類篩選（fashion/food/trend）"),
    page: int = Query(1, ge=1, le=100, description="頁碼（1-100）"),
    limit: int = Query(10, ge=1, le=50, description="每頁數量（1-50）"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="用戶角色（guest/user/premium/admin）")
):
    """
    搜尋主題（中文全文搜尋）
    
    支援中文關鍵字搜尋主題標題、摘要、內容。
    根據用戶角色過濾結果欄位。
    
    - **guest**: 只能查看標題和摘要
    - **user**: 可查看標題、摘要、來源 URL、預覽圖片
    - **premium**: 可查看所有欄位
    - **admin**: 可查看所有欄位（包括 metadata）
    """
    try:
        # 檢查資料庫連接狀態
        is_connected, reason = await check_connection_from_request(request)
        if not is_connected:
            if settings.ENVIRONMENT == "development":
                logger.warning(f"資料庫未連接 ({reason})，返回空搜尋結果（開發環境）")
                return {
                    "source": "db",
                    "results": [],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": 0,
                        "pages": 0
                    }
                }
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"資料庫服務暫時不可用: {reason}"
                )
        
        # 獲取用戶角色
        role = UserRole.GUEST
        if x_user_role:
            try:
                role = UserRole(x_user_role.lower())
            except ValueError:
                logger.warning(f"無效的用戶角色: {x_user_role}，使用預設角色 guest")
        else:
            # 嘗試從請求中獲取角色
            role = get_user_role_from_request(request)
        
        # 從 app.state 獲取資料庫實例
        db = get_database_from_request(request)
        search_service = SearchService(db=db)
        
        # 執行搜尋
        result = await search_service.search_topics(
            query=query,
            category=category,
            page=page,
            limit=limit,
            role=role
        )
        
        logger.info(f"搜尋: '{query}' by role {role.value}, found {result['pagination']['total']} results")
        
        return result
        
    except ValueError as e:
        # 輸入驗證錯誤
        logger.warning(f"搜尋請求驗證失敗: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionFailure as e:
        logger.error(f"資料庫連接失敗: {e}")
        if settings.ENVIRONMENT == "development":
            return {
                "source": "db",
                "results": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": 0,
                    "pages": 0
                }
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="資料庫服務暫時不可用，請稍後再試"
            )
    except Exception as e:
        logger.error(f"搜尋主題失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜尋失敗: {str(e)}")


@router.get("/search/check")
async def check_url_exists(
    request: Request,
    url: str = Query(..., description="原文 URL")
):
    """
    檢查原文 URL 是否已收錄
    
    用於檢查某篇原文是否已經被系統收錄。
    """
    try:
        # 檢查資料庫連接狀態
        is_connected, reason = await check_connection_from_request(request)
        if not is_connected:
            if settings.ENVIRONMENT == "development":
                return {"exists": False, "topic": None}
            else:
                raise HTTPException(
                    status_code=503,
                    detail=f"資料庫服務暫時不可用: {reason}"
                )
        
        # 從 app.state 獲取資料庫實例
        db = get_database_from_request(request)
        search_service = SearchService(db=db)
        
        # 檢查 URL
        result = await search_service.check_url_exists(url)
        
        return result
        
    except ConnectionFailure as e:
        logger.error(f"資料庫連接失敗: {e}")
        if settings.ENVIRONMENT == "development":
            return {"exists": False, "topic": None}
        else:
            raise HTTPException(
                status_code=503,
                detail="資料庫服務暫時不可用，請稍後再試"
            )
    except Exception as e:
        logger.error(f"檢查 URL 是否存在失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"檢查失敗: {str(e)}")


@router.get("/search/hot-queries")
async def get_hot_queries(
    limit: int = Query(10, ge=1, le=50, description="返回數量（1-50）")
):
    """
    取得熱門查詢列表
    
    返回最熱門的搜尋關鍵字及其查詢次數。
    """
    try:
        from app.services.cache_service import cache_service
        
        queries = await cache_service.get_hot_queries(limit=limit)
        
        return {
            "queries": queries
        }
    except Exception as e:
        logger.error(f"獲取熱門查詢失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"獲取熱門查詢失敗: {str(e)}")


@router.delete("/search/cache")
async def clear_search_cache(
    pattern: str = Query("search:*", description="快取 key 模式（預設清除所有搜尋快取）"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role", description="用戶角色（必須為 admin）")
):
    """
    清除搜尋快取（僅管理員）
    
    用於手動清除快取，支援模式匹配。
    預設清除所有搜尋快取（search:*）。
    """
    try:
        # 檢查權限（必須是管理員）
        role = UserRole.GUEST
        if x_user_role:
            try:
                role = UserRole(x_user_role.lower())
            except ValueError:
                pass
        
        if role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="無權限清除快取（需要管理員權限）"
            )
        
        from app.services.cache_service import cache_service
        
        deleted_count = await cache_service.clear_cache(pattern=pattern)
        
        return {
            "deleted": deleted_count,
            "message": f"已清除 {deleted_count} 個快取項目"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清除快取失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"清除快取失敗: {str(e)}")


@router.get("/search/health")
async def search_health_check():
    """
    檢查搜尋服務健康狀態
    
    返回 Redis、Elasticsearch、MongoDB 的連接狀態。
    """
    try:
        from app.services.cache_service import cache_service
        from app.services.elasticsearch_service import es_service
        from app.database import check_connection
        
        health_status = {}
        
        # 檢查 Redis
        if cache_service.enabled and cache_service.redis_client:
            try:
                await cache_service.redis_client.ping()
                health_status["redis"] = "ok"
            except Exception as e:
                health_status["redis"] = f"error: {str(e)}"
        else:
            health_status["redis"] = "disabled"
        
        # 檢查 Elasticsearch
        if es_service.enabled:
            es_health = await es_service.health_check()
            health_status["elasticsearch"] = es_health.get("status", "unknown")
        else:
            health_status["elasticsearch"] = "disabled"
        
        # 檢查 MongoDB
        try:
            is_connected, reason = await check_connection()
            if is_connected:
                health_status["mongodb"] = "ok"
            else:
                health_status["mongodb"] = f"error: {reason}"
        except Exception as e:
            health_status["mongodb"] = f"error: {str(e)}"
        
        return health_status
    except Exception as e:
        logger.error(f"健康檢查失敗: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"健康檢查失敗: {str(e)}")

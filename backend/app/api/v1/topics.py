"""
Topics API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
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
from app.models.topic import Category, Status
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topics", tags=["topics"])

# Repository 實例
topic_repo = TopicRepository()
content_repo = ContentRepository()
image_repo = ImageRepository()


def _convert_to_response(topic_doc: dict) -> TopicResponse:
    """將 MongoDB 文檔轉換為 TopicResponse"""
    # 移除 MongoDB 的 _id
    topic_doc.pop("_id", None)
    return TopicResponse(**topic_doc)


@router.get("", response_model=TopicListResponse)
async def list_topics(
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

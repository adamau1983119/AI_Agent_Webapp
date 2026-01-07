"""
Images API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body
from app.schemas.image import (
    ImageCreate,
    ImageUpdate,
    ImageResponse,
    ImageListResponse,
    ImageSearchResponse,
    ImageReorderRequest,
)
from app.services.repositories.image_repository import ImageRepository
from app.services.repositories.topic_repository import TopicRepository
from app.models.image import ImageSource
from app.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])

# Repository 實例
image_repo = ImageRepository()
topic_repo = TopicRepository()


def _convert_to_response(image_doc: dict) -> ImageResponse:
    """將 MongoDB 文檔轉換為 ImageResponse"""
    from datetime import datetime
    
    # 保存 _id（如果需要）
    mongo_id = image_doc.pop("_id", None)
    
    # 確保 id 欄位存在（如果沒有，使用 MongoDB 的 _id）
    if "id" not in image_doc:
        if mongo_id:
            image_doc["id"] = str(mongo_id)
        else:
            raise ValueError("Image document must have either 'id' or '_id' field")
    
    # 確保所有必需欄位都存在
    if "keywords" not in image_doc or image_doc["keywords"] is None:
        image_doc["keywords"] = []
    
    if "order" not in image_doc:
        image_doc["order"] = 0
    
    if "license" not in image_doc or not image_doc.get("license"):
        image_doc["license"] = "Unknown"
    
    if "fetched_at" not in image_doc:
        image_doc["fetched_at"] = datetime.utcnow()
    
    # 確保 source 是正確的類型
    if isinstance(image_doc.get("source"), str):
        from app.models.image import ImageSource
        try:
            image_doc["source"] = ImageSource(image_doc["source"])
        except:
            logger.warning(f"無法轉換 source: {image_doc.get('source')}")
    
    return ImageResponse(**image_doc)


@router.get("/search", response_model=ImageSearchResponse)
async def search_images(
    keywords: str = Query(..., description="搜尋關鍵字"),
    source: Optional[ImageSource] = Query(None, description="圖片來源（可選，預設自動選擇）"),
    page: int = Query(1, ge=1, description="頁碼"),
    limit: int = Query(20, ge=1, le=30, description="每頁數量")
):
    """
    搜尋圖片
    
    支援多個圖片來源（Unsplash/Pexels/Pixabay/Google Custom Search），自動備援
    如果所有 API Key 都未設定，會自動使用 DuckDuckGo
    """
    import uuid
    from app.services.images.image_service_manager import ImageServiceManager
    from app.services.images.exceptions import ImageSearchError
    from app.schemas.common import PaginationResponse
    from app.schemas.image import ImageResponse, ImageSearchAttempt
    
    # 生成 trace_id
    trace_id = str(uuid.uuid4())[:8]
    logger.info(f"[{trace_id}] 圖片搜尋請求: keywords='{keywords}', source={source}, page={page}, limit={limit}")
    
    try:
        image_service = ImageServiceManager()
        
        # 搜尋圖片（返回包含 source、items 和 attempts 的字典）
        result = await image_service.search_images(
            keywords=keywords,
            source=source,
            page=page,
            limit=limit,
            trace_id=trace_id
        )
        
        # 轉換為回應格式
        image_responses = []
        for img in result.get("items", []):
            # 確保所有必需欄位都存在
            img_id = img.get("id", "")
            if not img_id:
                img_id = f"temp_{abs(hash(img.get('url', '')))}"
            
            img_source = img.get("source", ImageSource.UNSPLASH.value)
            if isinstance(img_source, str):
                try:
                    img_source = ImageSource(img_source)
                except ValueError:
                    img_source = ImageSource.UNSPLASH
            
            img_license = img.get("license", "")
            if not img_license:
                img_license = "Unknown"
            
            img_keywords = img.get("keywords", [])
            if not img_keywords:
                img_keywords = []
            elif isinstance(img_keywords, str):
                img_keywords = [img_keywords]
            
            image_responses.append(ImageResponse(
                id=img_id,
                topic_id="",  # 搜尋結果沒有 topic_id
                url=img.get("url", ""),
                source=img_source,
                photographer=img.get("photographer"),
                photographer_url=img.get("photographer_url"),
                license=img_license,
                keywords=img_keywords,
                order=0,
                width=img.get("width"),
                height=img.get("height"),
                fetched_at=datetime.utcnow()
            ))
        
        # 轉換 attempts
        attempts = []
        for attempt in result.get("attempts", []):
            attempts.append(ImageSearchAttempt(
                source=attempt.get("source", "unknown"),
                status=attempt.get("status", "unknown"),
                count=attempt.get("count"),
                code=attempt.get("code"),
                message=attempt.get("message"),
                details=attempt.get("details"),
                exception_type=attempt.get("exception_type")
            ))
        
        # 注意：實際 API 可能不提供總數，這裡使用估算
        total = len(image_responses) * page if image_responses else 0
        
        return ImageSearchResponse(
            data=image_responses,
            pagination=PaginationResponse.create(page, limit, total),
            source=result.get("source"),
            attempts=attempts,
            trace_id=trace_id
        )
        
    except ImageSearchError as e:
        logger.warning(f"[{trace_id}] 圖片搜尋錯誤: {e.code} - {e.message}")
        # 返回 200，但包含錯誤資訊
        attempts = [ImageSearchAttempt(
            source=e.source,
            status="error",
            code=e.code,
            message=e.message,
            details=e.details
        )]
        return ImageSearchResponse(
            data=[],
            pagination=PaginationResponse.create(page, limit, 0),
            source=None,
            attempts=attempts,
            trace_id=trace_id
        )
    except ValueError as e:
        logger.warning(f"[{trace_id}] 圖片搜尋參數錯誤: {e}")
        return ImageSearchResponse(
            data=[],
            pagination=PaginationResponse.create(page, limit, 0),
            source=None,
            attempts=[],
            trace_id=trace_id
        )
    except Exception as e:
        logger.exception(f"[{trace_id}] 圖片搜尋發生未處理異常")
        # 即使發生未處理異常，也返回 200 而不是 500，但包含錯誤資訊
        # 這樣前端可以正常顯示錯誤訊息
        error_message = str(e) if getattr(settings, 'DEBUG', False) else "伺服器內部錯誤"
        attempts = [ImageSearchAttempt(
            source="unknown",
            status="exception",
            message=error_message,
            exception_type=type(e).__name__
        )]
        return ImageSearchResponse(
            data=[],
            pagination=PaginationResponse.create(page, limit, 0),
            source=None,
            attempts=attempts,
            trace_id=trace_id
        )


@router.get("/{topic_id}", response_model=ImageListResponse)
async def get_topic_images(topic_id: str = Path(..., description="主題 ID")):
    """
    取得主題圖片列表
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        images = await image_repo.get_images_by_topic_id(topic_id)
        
        image_responses = []
        for image in images:
            image_responses.append(_convert_to_response(image))
        
        return ImageListResponse(data=image_responses)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取得圖片列表失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}", response_model=ImageResponse)
async def create_image(
    topic_id: str = Path(..., description="主題 ID"),
    image_data: ImageCreate = ...
):
    """
    新增圖片
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 準備圖片資料
        image_dict = image_data.model_dump()
        image_dict["topic_id"] = topic_id
        image_dict["id"] = f"image_{topic_id}_{datetime.utcnow().timestamp()}"
        
        # 建立圖片
        created = await image_repo.create_image(image_dict)
        
        return _convert_to_response(created)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"新增圖片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}/{image_id}", response_model=ImageResponse)
async def update_image(
    topic_id: str = Path(..., description="主題 ID"),
    image_id: str = Path(..., description="圖片 ID"),
    update_data: ImageUpdate = ...
):
    """
    替換圖片
    """
    try:
        # 檢查圖片是否存在
        image = await image_repo.get_image_by_id(image_id)
        if not image or image.get("topic_id") != topic_id:
            raise HTTPException(
                status_code=404,
                detail=f"圖片不存在: {image_id}"
            )
        
        # 準備更新資料
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # 更新圖片
        updated = await image_repo.update_image(image_id, update_dict)
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="更新圖片失敗"
            )
        
        return _convert_to_response(updated)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新圖片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{topic_id}/{image_id}")
async def delete_image(
    topic_id: str = Path(..., description="主題 ID"),
    image_id: str = Path(..., description="圖片 ID")
):
    """
    刪除圖片
    """
    try:
        # 檢查圖片是否存在
        image = await image_repo.get_image_by_id(image_id)
        if not image or image.get("topic_id") != topic_id:
            raise HTTPException(
                status_code=404,
                detail=f"圖片不存在: {image_id}"
            )
        
        success = await image_repo.delete_image(image_id)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="刪除圖片失敗"
            )
        
        return {
            "message": "圖片已刪除",
            "data": {"id": image_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刪除圖片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{topic_id}/reorder")
async def reorder_images(
    topic_id: str = Path(..., description="主題 ID"),
    reorder_data: ImageReorderRequest = ...
):
    """
    重新排序圖片
    """
    try:
        # 檢查主題是否存在
        topic = await topic_repo.get_topic_by_id(topic_id)
        if not topic:
            raise HTTPException(
                status_code=404,
                detail=f"主題不存在: {topic_id}"
            )
        
        # 準備排序資料
        image_orders = [
            {"image_id": item.image_id, "order": item.order}
            for item in reorder_data.image_orders
        ]
        
        # 重新排序
        success = await image_repo.reorder_images(topic_id, image_orders)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="重新排序失敗"
            )
        
        return {
            "message": "圖片排序已更新",
            "data": {"topic_id": topic_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新排序圖片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{topic_id}/match", response_model=ImageListResponse)
async def match_photos_for_topic(
    topic_id: str = Path(..., description="主題 ID"),
    min_count: int = Query(default=8, ge=1, le=20, description="最少照片數量")
):
    """
    根據文章內容匹配照片（分層閾值檢查）
    """
    try:
        from app.services.images.enhanced_photo_matcher import EnhancedPhotoMatcher
        from app.services.repositories.content_repository import ContentRepository
        
        photo_matcher = EnhancedPhotoMatcher()
        content_repo = ContentRepository()
        
        # 取得文章內容
        content = await content_repo.get_content_by_topic_id(topic_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"主題內容不存在: {topic_id}"
            )
        
        article_text = content.get("article", "")
        
        # 匹配照片
        match_result = await photo_matcher.match_photos_with_layers(
            article_text=article_text,
            topic_id=topic_id,
            min_count=min_count
        )
        
        # 保存匹配的照片到資料庫
        matched_photos = match_result.get("matched_photos", [])
        saved_images = []
        
        existing_images = await image_repo.get_images_by_topic_id(topic_id)
        max_order = max([img.get("order", 0) for img in existing_images]) if existing_images else -1
        
        for idx, photo in enumerate(matched_photos):
            try:
                image_data = {
                    "id": photo.get("id", f"img_{topic_id}_{idx}"),
                    "topic_id": topic_id,
                    "url": photo.get("url", ""),
                    "source": photo.get("source", ImageSource.UNSPLASH.value),
                    "photographer": photo.get("photographer"),
                    "photographer_url": photo.get("photographer_url"),
                    "license": photo.get("license", "Unknown"),
                    "keywords": photo.get("keywords", []),
                    "order": max_order + idx + 1,
                    "width": photo.get("width"),
                    "height": photo.get("height"),
                    "fetched_at": datetime.utcnow(),
                    "match_score": photo.get("overall_score", 0.0),
                    "matches_item": photo.get("matches_item")
                }
                
                created = await image_repo.create_image(image_data)
                saved_images.append(_convert_to_response(created))
            except Exception as e:
                logger.warning(f"保存照片失敗: {e}")
                continue
        
        return ImageListResponse(data=saved_images)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"匹配照片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-match")
async def validate_photo_match(
    topic_id: str = Body(..., description="主題 ID"),
    article_id: Optional[str] = Body(None, description="文章 ID")
):
    """
    驗證照片與文字匹配度
    """
    try:
        from app.services.images.enhanced_photo_matcher import EnhancedPhotoMatcher
        from app.services.repositories.content_repository import ContentRepository
        
        photo_matcher = EnhancedPhotoMatcher()
        content_repo = ContentRepository()
        
        # 取得文章內容
        content = await content_repo.get_content_by_topic_id(topic_id)
        if not content:
            raise HTTPException(
                status_code=404,
                detail=f"主題內容不存在: {topic_id}"
            )
        
        article_text = content.get("article", "")
        
        # 取得照片
        images = await image_repo.get_images_by_topic_id(topic_id)
        
        # 驗證匹配
        validation_results = []
        core_features = photo_matcher._extract_core_features(article_text)
        
        for image in images:
            photo_dict = {
                "url": image.get("url", ""),
                "description": "",
                "keywords": image.get("keywords", [])
            }
            
            core_match_score = photo_matcher._calculate_core_match_score(core_features, photo_dict)
            
            mentioned_item = None
            for feature in core_features:
                if feature.lower() in str(image.get("keywords", [])).lower():
                    mentioned_item = feature
                    break
            
            validation_results.append({
                "mentioned_item": mentioned_item or "未提及",
                "has_matching_photo": core_match_score >= 0.85,
                "photo_id": image.get("id"),
                "match_score": core_match_score
            })
        
        overall_match = all(result["has_matching_photo"] for result in validation_results if result["mentioned_item"] != "未提及")
        
        return {
            "topic_id": topic_id,
            "validation_results": validation_results,
            "overall_match": overall_match,
            "warnings": [
                result["mentioned_item"] for result in validation_results
                if not result["has_matching_photo"] and result["mentioned_item"] != "未提及"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"驗證照片匹配失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))
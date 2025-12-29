"""
Images API 端點
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
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
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])

# Repository 實例
image_repo = ImageRepository()
topic_repo = TopicRepository()


def _convert_to_response(image_doc: dict) -> ImageResponse:
    """將 MongoDB 文檔轉換為 ImageResponse"""
    image_doc.pop("_id", None)
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
    
    支援多個圖片來源（Unsplash/Pexels/Pixabay），自動備援
    """
    try:
        from app.services.images.image_service import ImageService
        from app.schemas.common import PaginationResponse
        
        image_service = ImageService()
        
        # 搜尋圖片（如果所有 API Key 都未設定，會自動使用 DuckDuckGo）
        try:
            images = await image_service.search_images(
                keywords=keywords,
                source=source,
                page=page,
                limit=limit,
                use_fallback=True
            )
        except ValueError as e:
            # 如果所有服務都失敗，嘗試直接使用 DuckDuckGo
            if "沒有可用的圖片服務" in str(e) or "所有圖片服務都失敗" in str(e):
                logger.warning(f"圖片搜尋失敗: {e}，嘗試使用 DuckDuckGo...")
                from app.services.images.duckduckgo import DuckDuckGoService
                duckduckgo = DuckDuckGoService()
                images = await duckduckgo.search_images(keywords, page, limit)
            else:
                raise
        
        # 轉換為回應格式
        from app.schemas.image import ImageResponse
        image_responses = []
        for img in images:
            # 建立臨時 ID（如果沒有）
            if "id" not in img:
                img["id"] = f"temp_{hash(img.get('url', ''))}"
            
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
        
        # 注意：實際 API 可能不提供總數，這裡使用估算
        total = len(images) * page if images else 0
        
        return ImageSearchResponse(
            data=image_responses,
            pagination=PaginationResponse.create(page, limit, total)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"搜尋圖片失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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

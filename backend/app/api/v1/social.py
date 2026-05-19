"""
社交平台 API 端點
Phase 5: 分發與整合
提供帳號連接和內容發布功能
"""
from typing import Optional, List, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from app.models.social_connection import (
    SocialPlatform, SocialConnectionResponse, SocialConnectionListResponse,
    PublishRequest, PublishResponse, PublishHistoryResponse,
    PLATFORM_CONFIGS, optimize_content_for_platform
)
from app.services.distribution_service import distribution_service
from app.config_module import settings
from app.middleware.jwt_auth import get_current_user
from app.utils.i18n import get_error_message, get_user_language
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/social", tags=["social"])


def _social_connect_redirect(query: str) -> str:
    """OAuth 回跳至前端（非後端 8000）"""
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}/social-connect?{query}"


# ============================================
# 帳號連接管理
# ============================================

@router.get("/connections", response_model=SocialConnectionListResponse)
async def get_my_connections(
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的社交平台連接
    """
    connections = await distribution_service.get_user_connections(current_user["id"])
    
    # 移除敏感資訊
    safe_connections = []
    for conn in connections:
        safe_conn = {k: v for k, v in conn.items() if k not in ["access_token", "refresh_token"]}
        safe_connections.append(SocialConnectionResponse(**safe_conn))
    
    return SocialConnectionListResponse(
        connections=safe_connections,
        total=len(safe_connections)
    )


@router.get("/platforms")
async def get_available_platforms():
    """
    取得可用的社交平台列表
    """
    platforms = []
    for platform, config in PLATFORM_CONFIGS.items():
        platforms.append({
            "value": platform.value,
            "name": config["name"],
            "icon": config["icon"],
            "max_caption_length": config["max_caption_length"],
            "max_hashtags": config["max_hashtags"],
            "image_required": config["image_required"],
            "note": config.get("note"),
        })
    
    return {"platforms": platforms}


@router.delete("/connections/{platform}")
async def disconnect_platform(
    platform: SocialPlatform,
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """
    斷開平台連接
    """
    language = get_user_language(user=current_user, request=request)
    success, error = await distribution_service.disconnect_platform(
        current_user["id"],
        platform,
        language
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 斷開 {platform.value}")
    
    return {"message": f"已斷開 {PLATFORM_CONFIGS[platform]['name']} 連接"}


# ============================================
# Meta OAuth (Instagram + Facebook + Threads)
# ============================================

@router.get("/meta/connect")
async def connect_meta(
    target: Literal["facebook", "instagram"] = Query(
        "facebook",
        description="連線目標：facebook 僅粉專 scope；instagram 另含 IG business scope",
    ),
    current_user: dict = Depends(get_current_user),
):
    """
    連接 Meta 平台（Facebook 或 Instagram 分開授權）
    
    返回授權 URL，前端需要跳轉到此 URL
    """
    state = f"{current_user['id']}:{secrets.token_urlsafe(16)}:{target}"
    oauth_url = distribution_service.get_meta_oauth_url(state, target)
    platforms = ["facebook"] if target == "facebook" else ["instagram"]

    return {
        "oauth_url": oauth_url,
        "state": state,
        "target": target,
        "platforms": platforms,
    }


@router.get("/meta/callback")
async def meta_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...)
):
    """
    Meta OAuth 回調
    
    處理授權完成後的回調
    """
    try:
        parts = state.split(":")
        if len(parts) < 2:
            language = get_user_language(request=request)
            raise HTTPException(status_code=400, detail=get_error_message("social.invalid_state", language))

        user_id = parts[0]
        target = parts[2] if len(parts) >= 3 else "facebook"
        if target not in ("facebook", "instagram"):
            target = "facebook"

        language = get_user_language(request=request)
        result, error = await distribution_service.handle_meta_callback(
            user_id, code, target=target, language=language
        )
        
        if error:
            return RedirectResponse(
                url=_social_connect_redirect(f"error={error}"),
                status_code=302,
            )
        
        return RedirectResponse(
            url=_social_connect_redirect("success=true"),
            status_code=302,
        )
        
    except Exception as e:
        logger.error(f"Meta callback error: {e}")
        return RedirectResponse(
            url=_social_connect_redirect("error=callback_failed"),
            status_code=302,
        )


# ============================================
# TikTok OAuth
# ============================================

@router.get("/tiktok/connect")
async def connect_tiktok(
    current_user: dict = Depends(get_current_user)
):
    """
    連接 TikTok
    """
    state = f"{current_user['id']}:{secrets.token_urlsafe(16)}"
    oauth_url = distribution_service.get_tiktok_oauth_url(state)
    
    return {
        "oauth_url": oauth_url,
        "state": state,
        "platforms": ["tiktok"]
    }


@router.get("/tiktok/callback")
async def tiktok_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...)
):
    """
    TikTok OAuth 回調
    """
    parts = state.split(":")
    if len(parts) != 2:
        return RedirectResponse(url=_social_connect_redirect("error=invalid_state"), status_code=302)
    
    user_id = parts[0]
    
    language = get_user_language(request=request)
    result, error = await distribution_service.handle_tiktok_callback(user_id, code, language)
    
    if error:
        return RedirectResponse(url=_social_connect_redirect(f"error={error}"), status_code=302)

    return RedirectResponse(url=_social_connect_redirect("success=true"), status_code=302)


# ============================================
# 內容發布
# ============================================

@router.post("/publish", response_model=PublishResponse)
async def publish_content(
    request: PublishRequest,
    current_user: dict = Depends(get_current_user),
    http_request: Request = None
):
    """
    發布內容到社交平台
    
    - **content_id**: 內容 ID
    - **content**: 要發布的內容
    - **platforms**: 目標平台列表
    - **hashtags**: Hashtags（可選）
    - **image_urls**: 圖片 URL（某些平台必須）
    - **scheduled_at**: 排程發布時間（可選）
    
    支援一鍵發布到多個平台
    """
    result, error = await distribution_service.publish_content(
        current_user["id"],
        request
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 計算成功/失敗數量
    platform_results = result.get("platform_results", {})
    successful = sum(1 for r in platform_results.values() if r.get("status") == "published")
    failed = sum(1 for r in platform_results.values() if r.get("status") == "failed")
    
    logger.info(
        f"用戶 {current_user['email']} 發布內容到 {len(request.platforms)} 個平台，"
        f"成功: {successful}，失敗: {failed}"
    )
    
    return PublishResponse(
        publish_id=result["id"],
        content_id=result["content_id"],
        total_platforms=len(request.platforms),
        successful=successful,
        failed=failed,
        results=[
            {
                "platform": platform,
                **data
            }
            for platform, data in platform_results.items()
        ],
        created_at=result["created_at"]
    )


@router.post("/preview-optimize")
async def preview_content_optimization(
    content: str = Query(..., description="原始內容"),
    hashtags: List[str] = Query(default=[], description="Hashtags"),
    platform: SocialPlatform = Query(..., description="目標平台")
):
    """
    預覽內容最佳化結果
    
    返回針對特定平台優化後的內容
    """
    optimized = optimize_content_for_platform(content, hashtags, platform)
    
    config = PLATFORM_CONFIGS.get(platform, {})
    
    return {
        "original_content": content,
        "optimized": optimized,
        "platform": {
            "name": config.get("name"),
            "max_length": config.get("max_caption_length"),
            "max_hashtags": config.get("max_hashtags"),
        }
    }


# ============================================
# 發布歷史和狀態
# ============================================

@router.get("/publish/history", response_model=PublishHistoryResponse)
async def get_publish_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
):
    """
    取得發布歷史
    """
    result = await distribution_service.get_publish_history(
        current_user["id"],
        page,
        limit
    )
    
    return PublishHistoryResponse(**result)


@router.get("/publish/{publish_id}")
async def get_publish_status(
    publish_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    取得發布狀態
    """
    job = await distribution_service.get_publish_status(
        current_user["id"],
        publish_id
    )
    
    if not job:
        language = get_user_language(user=current_user, request=request)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_message("social.publish_task_not_found", language)
        )
    
    return job


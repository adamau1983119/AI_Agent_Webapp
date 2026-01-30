"""
Channel API 端點
Phase 3: 內容功能
會員自定義頻道管理
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.channel import (
    ChannelCreate, ChannelUpdate, ChannelResponse, ChannelListResponse,
    ChannelCategory, ChannelRegion
)
from app.services.channel_service import channel_service, MAX_CHANNELS_PER_USER
from app.services.channel_collector import channel_collector
from app.middleware.jwt_auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=ChannelListResponse)
async def get_my_channels(
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的頻道列表
    
    - 返回用戶的所有活躍頻道
    - 最多 3 個頻道
    """
    channels = await channel_service.get_user_channels(current_user["id"])
    
    return ChannelListResponse(
        channels=[ChannelResponse(**ch) for ch in channels],
        total=len(channels),
        max_channels=MAX_CHANNELS_PER_USER
    )


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    建立新頻道
    
    - **name**: 頻道名稱（必須）
    - **category**: 類別（fashion/food/trend/finance/sports/tech/entertainment/other）
    - **region**: 地區（hong_kong/taiwan/japan/korea/china/usa/uk/global）
    - **custom_keywords**: 自定義關鍵字（當類別為 other 時必填）
    - **description**: 頻道描述（可選）
    
    每位用戶最多可建立 3 個頻道
    """
    channel, error = await channel_service.create_channel(
        user_id=current_user["id"],
        channel_data=channel_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 建立頻道: {channel['name']}")
    
    return ChannelResponse(**channel)


@router.get("/categories")
async def get_categories():
    """
    取得可用的類別列表
    """
    categories = await channel_service.get_available_categories()
    return {"categories": categories}


@router.get("/regions")
async def get_regions():
    """
    取得可用的地區列表
    """
    regions = await channel_service.get_available_regions()
    return {"regions": regions}


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取得特定頻道詳情
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    return ChannelResponse(**channel)


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: str,
    update_data: ChannelUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    更新頻道
    
    可更新的欄位：
    - **name**: 頻道名稱
    - **custom_keywords**: 自定義關鍵字
    - **description**: 頻道描述
    - **status**: 狀態（active/paused）
    """
    channel, error = await channel_service.update_channel(
        user_id=current_user["id"],
        channel_id=channel_id,
        update_data=update_data
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 更新頻道: {channel_id}")
    
    return ChannelResponse(**channel)


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    刪除頻道（軟刪除）
    """
    success, error = await channel_service.delete_channel(
        user_id=current_user["id"],
        channel_id=channel_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 刪除頻道: {channel_id}")
    
    return {"message": "頻道已刪除"}


@router.get("/{channel_id}/sources")
async def get_channel_sources(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    取得頻道的 RSS 來源（含三層備用）
    
    - Layer 1: 主要來源（類別 + 地區）
    - Layer 2: 備用來源（相近類別）
    - Layer 3: AI 生成（當 RSS 全部失敗時自動觸發）
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    sources = channel_service.get_rss_sources_for_channel(channel)
    
    # 分層顯示
    layer1 = [s for s in sources if s.get("layer") == 1]
    layer2 = [s for s in sources if s.get("layer") == 2]
    
    return {
        "channel_id": channel_id,
        "category": channel.get("category"),
        "region": channel.get("region"),
        "layers": {
            "layer_1": {
                "description": "主要來源",
                "sources": layer1,
                "count": len(layer1)
            },
            "layer_2": {
                "description": "備用來源（相近類別）",
                "sources": layer2,
                "count": len(layer2)
            },
            "layer_3": {
                "description": "AI 生成（當 RSS 全部失敗時自動觸發）",
                "sources": [],
                "count": 0,
                "note": "此層不需要預設來源，由 AI 即時生成"
            }
        },
        "total_sources": len(sources)
    }


@router.post("/{channel_id}/collect")
async def trigger_channel_collection(
    channel_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    手動觸發頻道內容收集
    
    - 通常由排程自動執行
    - 此端點用於手動測試
    - 使用三層備用機制確保頻道有內容
    """
    channel = await channel_service.get_channel(current_user["id"], channel_id)
    
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="頻道不存在"
        )
    
    # 取得用戶語言偏好
    target_language = current_user.get("language", "zh-TW")
    
    # 執行收集
    result = await channel_collector.collect_for_channel(
        channel_id,
        target_language
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "收集失敗")
        )
    
    logger.info(f"用戶 {current_user['email']} 觸發頻道收集: {channel_id}, 收集了 {result['topics_collected']} 個主題")
    
    return {
        "message": "收集完成",
        "channel_id": channel_id,
        "topics_collected": result["topics_collected"],
        "collection_log": result.get("collection_log", {})
    }


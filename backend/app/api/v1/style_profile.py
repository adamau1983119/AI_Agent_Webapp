"""
風格檔案 API 端點
Phase 4: AI 個人化
提供風格檔案管理和分析功能
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import Request
from app.models.style_profile import (
    StyleProfileResponse, StyleProfileUpdate, StyleProfileStats,
    PresetStyle, OutputFormat,
    PRESET_STYLE_CONFIGS, OUTPUT_FORMAT_CONFIGS
)
from app.services.style_learning_service import style_learning_service
from app.middleware.jwt_auth import get_current_user
from app.utils.i18n import get_error_message, get_user_language
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/style-profile", tags=["style-profile"])


@router.get("", response_model=StyleProfileResponse)
async def get_my_style_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    取得我的風格檔案
    
    如果不存在，會自動建立預設檔案
    """
    profile = await style_learning_service.get_or_create_profile(current_user["id"])
    return StyleProfileResponse(**profile)


@router.get("/analysis")
async def get_style_analysis(
    current_user: dict = Depends(get_current_user)
):
    """
    取得風格分析報告
    
    返回：
    - 學習階段和進度
    - 主要風格特徵
    - 評分統計
    - 個人化建議
    """
    analysis = await style_learning_service.analyze_user_style(current_user["id"])
    
    if "error" in analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=analysis["error"]
        )
    
    return analysis


@router.put("/preset-style")
async def set_preset_style(
    request: Request,
    preset_style: PresetStyle = Query(..., description="預設風格"),
    current_user: dict = Depends(get_current_user)
):
    """
    設定預設風格
    
    可選風格：
    - **professional**: 專業正式
    - **casual**: 輕鬆隨性
    - **humorous**: 幽默風趣
    - **inspiring**: 激勵人心
    - **storytelling**: 故事敘述
    """
    language = get_user_language(user=current_user, request=request)
    profile, error = await style_learning_service.set_preset_style(
        user_id=current_user["id"],
        preset_style=preset_style,
        language=language
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 設定預設風格: {preset_style.value}")
    
    return {
        "message": f"已設定為「{PRESET_STYLE_CONFIGS[preset_style]['name']}」風格",
        "profile": StyleProfileResponse(**profile)
    }


@router.post("/reset")
async def reset_style_profile(
    current_user: dict = Depends(get_current_user)
):
    """
    重置風格檔案
    
    **警告**：此操作會清除所有學習記錄和評分歷史
    """
    success, error = await style_learning_service.reset_profile(current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"用戶 {current_user['email']} 重置風格檔案")
    
    return {"message": "風格檔案已重置"}


@router.get("/styles")
async def get_available_styles():
    """
    取得可用的預設風格列表
    """
    styles = style_learning_service.get_available_styles()
    return {"styles": styles}


@router.get("/formats")
async def get_available_formats():
    """
    取得可用的輸出格式列表
    """
    formats = style_learning_service.get_available_formats()
    return {"formats": formats}


@router.get("/preview-style/{style}")
async def preview_style(
    style: PresetStyle,
    request: Request
):
    """
    預覽特定風格的配置
    """
    config = PRESET_STYLE_CONFIGS.get(style)
    if not config:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_message("style.not_found", language)
        )
    
    return {
        "style": style.value,
        "name": config["name"],
        "description": config["description"],
        "tone": config["tone"].model_dump(),
        "content": config["content"].model_dump(),
        "prompt_hints": config["prompt_hints"]
    }


@router.get("/preview-format/{format}")
async def preview_format(
    format: OutputFormat,
    request: Request
):
    """
    預覽特定輸出格式的配置
    """
    config = OUTPUT_FORMAT_CONFIGS.get(format)
    if not config:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_message("style.format_not_found", language)
        )
    
    return {
        "format": format.value,
        **config
    }


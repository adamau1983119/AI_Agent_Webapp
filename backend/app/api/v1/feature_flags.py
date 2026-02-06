"""
Feature Flag API 端點
Phase 2: 功能開關系統
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.feature_flag_service import (
    feature_flag_service, FeatureStatus, require_feature
)
from app.middleware.jwt_auth import get_current_user, get_current_user_optional
from app.models.user import UserRole
from app.utils.i18n import get_error_message, get_user_language
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/features", tags=["feature-flags"])


class FeatureFlagResponse(BaseModel):
    """Feature Flag 回應"""
    name: str
    description: str
    enabled: bool


class AllFeaturesResponse(BaseModel):
    """所有功能回應"""
    features: Dict[str, bool]


class AdminFeatureFlagResponse(BaseModel):
    """管理員 Feature Flag 回應"""
    name: str
    description: str
    status: str
    enabled_for_roles: list
    enabled_for_users: list
    rollout_percentage: int


class UpdateFeatureFlagRequest(BaseModel):
    """更新 Feature Flag 請求"""
    status: Optional[FeatureStatus] = None
    rollout_percentage: Optional[int] = None
    add_user: Optional[str] = None
    remove_user: Optional[str] = None


@router.get("/me", response_model=AllFeaturesResponse)
async def get_my_features(
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    取得當前用戶可用的所有功能
    
    - 未登入用戶只能看到公開功能
    - 登入用戶可根據角色看到更多功能
    """
    user_id = current_user.get("id") if current_user else None
    user_role = UserRole(current_user.get("role")) if current_user and current_user.get("role") else None
    
    features = feature_flag_service.get_flags_for_user(user_id, user_role)
    
    return AllFeaturesResponse(features=features)


@router.get("/check/{flag_name}", response_model=FeatureFlagResponse)
async def check_feature(
    flag_name: str,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """
    檢查特定功能是否啟用
    """
    flag = feature_flag_service.get_flag(flag_name)
    
    if not flag:
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user, request=request)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_message("feature_flag.not_found", language)
        )
    
    user_id = current_user.get("id") if current_user else None
    user_role = UserRole(current_user.get("role")) if current_user and current_user.get("role") else None
    
    enabled = feature_flag_service.is_enabled(flag_name, user_id, user_role)
    
    return FeatureFlagResponse(
        name=flag_name,
        description=flag.get("description", ""),
        enabled=enabled
    )


# ============================================
# 管理員 API
# ============================================

@router.get("/admin/all", response_model=list[AdminFeatureFlagResponse])
async def get_all_feature_flags_admin(
    current_user: dict = Depends(get_current_user)
):
    """
    取得所有 Feature Flags（管理員）
    """
    if current_user.get("role") != UserRole.ADMIN.value:
        language = get_user_language(user=current_user, request=request)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_error_message("feature_flag.admin_required", language)
        )
    
    flags = feature_flag_service.get_all_flags()
    
    result = []
    for name, config in flags.items():
        result.append(AdminFeatureFlagResponse(
            name=name,
            description=config.get("description", ""),
            status=config.get("status", FeatureStatus.DISABLED.value),
            enabled_for_roles=config.get("enabled_for_roles", []),
            enabled_for_users=config.get("enabled_for_users", []),
            rollout_percentage=config.get("rollout_percentage", 0)
        ))
    
    return result


@router.put("/admin/{flag_name}")
async def update_feature_flag(
    flag_name: str,
    request: UpdateFeatureFlagRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    更新 Feature Flag（管理員）
    """
    if current_user.get("role") != UserRole.ADMIN.value:
        language = get_user_language(user=current_user, request=request)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_error_message("feature_flag.admin_required", language)
        )
    
    flag = feature_flag_service.get_flag(flag_name)
    if not flag:
        from app.utils.i18n import get_error_message, get_user_language
        language = get_user_language(user=current_user, request=request)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_error_message("feature_flag.not_found", language)
        )
    
    # 更新狀態
    if request.status:
        feature_flag_service.set_flag_status(flag_name, request.status)
    
    # 添加/移除用戶
    if request.add_user:
        feature_flag_service.enable_for_user(flag_name, request.add_user)
    
    if request.remove_user:
        feature_flag_service.disable_for_user(flag_name, request.remove_user)
    
    logger.info(f"管理員 {current_user['email']} 更新了 Feature Flag: {flag_name}")
    
    return {"message": f"Feature Flag '{flag_name}' 已更新"}


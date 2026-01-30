"""
Feature Flag 服務
Phase 2: 功能開關系統
支援基於用戶、角色、百分比的功能控制
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from app.models.user import UserRole
import logging
import json
import os

logger = logging.getLogger(__name__)


class FeatureStatus(str, Enum):
    """Feature 狀態"""
    ENABLED = "enabled"      # 完全啟用
    DISABLED = "disabled"    # 完全禁用
    BETA = "beta"            # Beta 測試中
    ROLLOUT = "rollout"      # 漸進式部署


class FeatureFlag(BaseModel):
    """Feature Flag 模型"""
    name: str
    description: str
    status: FeatureStatus = FeatureStatus.DISABLED
    
    # 進階控制
    enabled_for_roles: List[UserRole] = []  # 特定角色啟用
    enabled_for_users: List[str] = []       # 特定用戶 ID 啟用
    rollout_percentage: int = 0             # 漸進部署百分比 (0-100)
    
    # 元數據
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============================================
# 預定義的 Feature Flags
# ============================================

DEFAULT_FEATURE_FLAGS: Dict[str, Dict[str, Any]] = {
    # 會員系統功能
    "user_registration": {
        "description": "用戶註冊功能",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "google_oauth": {
        "description": "Google OAuth 登入",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "email_verification": {
        "description": "Email 驗證功能",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "password_reset": {
        "description": "密碼重設功能",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    
    # AI 生成功能
    "ai_content_generation": {
        "description": "AI 內容生成",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "ai_style_learning": {
        "description": "AI 風格學習（Phase 3）",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value, UserRole.TESTER.value]
    },
    "ai_batch_generation": {
        "description": "AI 批量生成（Phase 3）",
        "status": FeatureStatus.BETA.value,
        "enabled_for_roles": [UserRole.ADMIN.value, UserRole.TESTER.value]
    },
    
    # 社交平台功能
    "instagram_publish": {
        "description": "Instagram 發布功能（Phase 4）",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    "facebook_publish": {
        "description": "Facebook 發布功能（Phase 4）",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    "threads_publish": {
        "description": "Threads 發布功能（Phase 4）",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    "tiktok_publish": {
        "description": "TikTok 發布功能（Phase 5）",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    
    # 付費功能（預留）
    "premium_features": {
        "description": "付費功能",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value, UserRole.PREMIUM.value]
    },
    "api_access": {
        "description": "API 存取功能",
        "status": FeatureStatus.DISABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    
    # 實驗性功能
    "infinite_scroll": {
        "description": "無限滾動",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "dark_mode": {
        "description": "深色模式",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    "multi_language": {
        "description": "多語言支援",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": []
    },
    
    # 管理員功能
    "admin_dashboard": {
        "description": "管理員儀表板",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    "user_management": {
        "description": "用戶管理功能",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
    "system_logs": {
        "description": "系統日誌檢視",
        "status": FeatureStatus.ENABLED.value,
        "enabled_for_roles": [UserRole.ADMIN.value]
    },
}


class FeatureFlagService:
    """Feature Flag 服務"""
    
    def __init__(self):
        self._flags: Dict[str, Dict[str, Any]] = {}
        self._load_flags()
    
    def _load_flags(self):
        """載入 Feature Flags"""
        # 從預設值載入
        self._flags = DEFAULT_FEATURE_FLAGS.copy()
        
        # 嘗試從環境變數覆蓋
        env_flags = os.environ.get("FEATURE_FLAGS")
        if env_flags:
            try:
                overrides = json.loads(env_flags)
                for flag_name, config in overrides.items():
                    if flag_name in self._flags:
                        self._flags[flag_name].update(config)
                    else:
                        self._flags[flag_name] = config
                logger.info(f"載入了 {len(overrides)} 個環境變數 Feature Flags")
            except json.JSONDecodeError:
                logger.warning("無法解析 FEATURE_FLAGS 環境變數")
        
        logger.info(f"Feature Flag 服務已初始化，共 {len(self._flags)} 個 flags")
    
    def is_enabled(
        self,
        flag_name: str,
        user_id: Optional[str] = None,
        user_role: Optional[UserRole] = None
    ) -> bool:
        """
        檢查 Feature Flag 是否啟用
        
        Args:
            flag_name: Feature Flag 名稱
            user_id: 用戶 ID（可選）
            user_role: 用戶角色（可選）
            
        Returns:
            是否啟用
        """
        flag = self._flags.get(flag_name)
        
        if not flag:
            logger.warning(f"未知的 Feature Flag: {flag_name}")
            return False
        
        status = FeatureStatus(flag.get("status", FeatureStatus.DISABLED.value))
        
        # 完全禁用
        if status == FeatureStatus.DISABLED:
            return False
        
        # 完全啟用
        if status == FeatureStatus.ENABLED:
            return True
        
        # Beta/Rollout - 檢查角色和用戶
        enabled_roles = flag.get("enabled_for_roles", [])
        enabled_users = flag.get("enabled_for_users", [])
        
        # 檢查特定用戶
        if user_id and user_id in enabled_users:
            return True
        
        # 檢查角色
        if user_role:
            role_value = user_role.value if isinstance(user_role, UserRole) else user_role
            if role_value in enabled_roles:
                return True
        
        # 漸進式部署
        if status == FeatureStatus.ROLLOUT:
            rollout_percentage = flag.get("rollout_percentage", 0)
            if user_id and rollout_percentage > 0:
                # 根據 user_id 哈希決定是否啟用
                hash_value = hash(f"{flag_name}:{user_id}") % 100
                return hash_value < rollout_percentage
        
        return False
    
    def get_flag(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """取得 Feature Flag 配置"""
        return self._flags.get(flag_name)
    
    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """取得所有 Feature Flags"""
        return self._flags.copy()
    
    def get_flags_for_user(
        self,
        user_id: Optional[str] = None,
        user_role: Optional[UserRole] = None
    ) -> Dict[str, bool]:
        """
        取得用戶可用的所有 Feature Flags
        
        Args:
            user_id: 用戶 ID
            user_role: 用戶角色
            
        Returns:
            Feature Flag 名稱 -> 是否啟用
        """
        result = {}
        for flag_name in self._flags:
            result[flag_name] = self.is_enabled(flag_name, user_id, user_role)
        return result
    
    def set_flag_status(
        self,
        flag_name: str,
        status: FeatureStatus
    ) -> bool:
        """
        設定 Feature Flag 狀態（運行時修改）
        
        Args:
            flag_name: Feature Flag 名稱
            status: 新狀態
            
        Returns:
            是否成功
        """
        if flag_name not in self._flags:
            logger.warning(f"未知的 Feature Flag: {flag_name}")
            return False
        
        self._flags[flag_name]["status"] = status.value
        logger.info(f"Feature Flag '{flag_name}' 狀態已更新為 {status.value}")
        return True
    
    def enable_for_user(
        self,
        flag_name: str,
        user_id: str
    ) -> bool:
        """為特定用戶啟用功能"""
        if flag_name not in self._flags:
            return False
        
        enabled_users = self._flags[flag_name].get("enabled_for_users", [])
        if user_id not in enabled_users:
            enabled_users.append(user_id)
            self._flags[flag_name]["enabled_for_users"] = enabled_users
        return True
    
    def disable_for_user(
        self,
        flag_name: str,
        user_id: str
    ) -> bool:
        """為特定用戶禁用功能"""
        if flag_name not in self._flags:
            return False
        
        enabled_users = self._flags[flag_name].get("enabled_for_users", [])
        if user_id in enabled_users:
            enabled_users.remove(user_id)
            self._flags[flag_name]["enabled_for_users"] = enabled_users
        return True


# 建立全域實例
feature_flag_service = FeatureFlagService()


# ============================================
# FastAPI 依賴項
# ============================================

def require_feature(flag_name: str):
    """
    FastAPI 依賴項：要求特定功能已啟用
    
    使用方式：
    @router.get("/endpoint")
    async def endpoint(
        current_user: dict = Depends(get_current_user),
        _: None = Depends(require_feature("feature_name"))
    ):
        ...
    """
    from fastapi import HTTPException, status
    
    async def check_feature(current_user: dict = None):
        user_id = current_user.get("id") if current_user else None
        user_role = UserRole(current_user.get("role")) if current_user and current_user.get("role") else None
        
        if not feature_flag_service.is_enabled(flag_name, user_id, user_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"功能 '{flag_name}' 目前不可用"
            )
    
    return check_feature


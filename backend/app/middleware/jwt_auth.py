"""
JWT 認證中間件
Phase 2: 會員系統
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.utils.jwt import verify_access_token, TokenError
from app.services.repositories.user_repository import UserRepository
from app.models.user import UserRole, UserStatus
import logging

logger = logging.getLogger(__name__)


class JWTAuth(HTTPBearer):
    """JWT 認證類"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTAuth, self).__init__(auto_error=auto_error)
        self.user_repo = UserRepository()
    
    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        驗證 JWT Token 並返回用戶資訊
        
        Args:
            request: FastAPI 請求對象
            
        Returns:
            用戶資訊字典，如果未提供 Token 或驗證失敗則返回 None
            
        Raises:
            HTTPException: 如果 auto_error=True 且驗證失敗
        """
        # 嘗試從 Authorization header 獲取 Token
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTAuth, self).__call__(request)
        
        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未提供認證 Token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        token = credentials.credentials
        
        # 驗證 Token（支援區分過期和無效的錯誤類型）
        try:
            payload = verify_access_token(token)
        except TokenError as e:
            if self.auto_error:
                if e.error_type == "expired":
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token 已過期，請重新登入",
                        headers={"WWW-Authenticate": "Bearer", "X-Token-Expired": "true"},
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="無效的 Token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            return None
        
        if not payload:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="無效或過期的 Token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        # 從資料庫獲取用戶資訊（確保用戶仍然存在且活躍）
        user_id = payload.get("sub")
        if not user_id:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token 格式錯誤",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用戶不存在",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        # 檢查用戶狀態
        if user.get("status") != UserStatus.ACTIVE.value:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="用戶帳號已被停用",
                )
            return None
        
        # 將用戶資訊附加到請求狀態
        request.state.user = user
        request.state.user_id = user_id
        request.state.user_role = user.get("role", UserRole.USER.value)
        
        return user


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    從請求中獲取當前用戶（依賴注入）
    
    Args:
        request: FastAPI 請求對象
        
    Returns:
        用戶資訊字典
        
    Raises:
        HTTPException: 如果用戶未認證
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未認證",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return request.state.user


async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    從請求中獲取當前用戶（可選，不會拋出異常）
    
    Args:
        request: FastAPI 請求對象
        
    Returns:
        用戶資訊字典，如果未認證則返回 None
    """
    return getattr(request.state, "user", None)


def require_role(*allowed_roles: UserRole):
    """
    角色權限檢查裝飾器
    
    Args:
        *allowed_roles: 允許的角色列表
        
    Returns:
        依賴函數
    """
    async def role_checker(request: Request) -> Dict[str, Any]:
        user = await get_current_user(request)
        user_role = UserRole(user.get("role", UserRole.USER.value))
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要以下角色之一: {', '.join([r.value for r in allowed_roles])}",
            )
        
        return user
    
    return role_checker


# 建立認證實例
jwt_auth = JWTAuth(auto_error=False)  # 預設不自動拋出異常，允許可選認證


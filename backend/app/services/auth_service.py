"""
認證服務
Phase 2: 會員系統
處理用戶註冊、登入、密碼驗證等邏輯
"""
from typing import Optional, Dict, Any
from datetime import datetime
from passlib.context import CryptContext
from app.services.repositories.user_repository import UserRepository
from app.models.user import (
    UserCreate, UserLogin, UserResponse, UserRole, UserStatus,
    Language
)
from app.utils.jwt import (
    create_access_token, create_verification_token,
    create_password_reset_token, verify_verification_token,
    verify_password_reset_token
)
from app.config_module import settings
from app.database import get_database
import logging

logger = logging.getLogger(__name__)

# 密碼加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """認證服務"""
    
    def __init__(self, user_repo: Optional[UserRepository] = None):
        """
        初始化認證服務
        
        Args:
            user_repo: UserRepository 實例（可選）
        """
        self.user_repo = user_repo or UserRepository()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        驗證密碼
        
        Args:
            plain_password: 明文密碼
            hashed_password: 雜湊密碼
            
        Returns:
            是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        取得密碼雜湊
        
        Args:
            password: 明文密碼
            
        Returns:
            雜湊密碼
        """
        return pwd_context.hash(password)
    
    async def register_user(self, user_data: UserCreate) -> tuple[Dict[str, Any], str]:
        """
        註冊用戶
        
        Args:
            user_data: 用戶註冊資料
            
        Returns:
            (用戶資料, 驗證 Token)
            
        Raises:
            ValueError: 如果 Email 已存在或達到用戶上限
        """
        # 檢查用戶數量限制
        active_count = await self.user_repo.count_active_users()
        if active_count >= settings.MAX_USERS:
            raise ValueError(f"測試版名額已滿（最多 {settings.MAX_USERS} 人）")
        
        # 檢查 Email 是否已存在
        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            # 使用 i18n 錯誤訊息（但這裡無法取得語言，會在 API 層處理）
            raise ValueError("EMAIL_ALREADY_REGISTERED")
        
        # 雜湊密碼
        password_hash = self.get_password_hash(user_data.password)
        
        # 建立用戶
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["email"] = user_dict["email"].lower()  # 轉為小寫
        
        user = await self.user_repo.create_user(user_dict, password_hash)
        
        # 建立驗證 Token
        verification_token = create_verification_token(user["email"])
        
        # 轉換為回應格式（移除敏感資訊）
        user_response = self._to_user_response(user)
        
        logger.info(f"用戶註冊成功: {user['email']}")
        
        return user_response, verification_token
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """
        驗證用戶登入
        
        Args:
            login_data: 登入資料
            
        Returns:
            用戶資料（如果驗證成功），否則返回 None
        """
        # 取得用戶
        user = await self.user_repo.get_user_by_email(login_data.email)
        if not user:
            return None
        
        # 檢查用戶狀態
        if user.get("status") != UserStatus.ACTIVE.value:
            logger.warning(f"用戶狀態異常: {user.get('email')}, status: {user.get('status')}")
            return None
        
        # 驗證密碼
        if not self.verify_password(login_data.password, user["password_hash"]):
            return None
        
        # 更新最後登入時間
        await self.user_repo.update_last_login(user["id"])
        
        logger.info(f"用戶登入成功: {user['email']}")
        
        return self._to_user_response(user)
    
    async def create_access_token_for_user(self, user: Dict[str, Any]) -> str:
        """
        為用戶建立 Access Token
        
        Args:
            user: 用戶資料
            
        Returns:
            JWT Access Token
        """
        token_data = {
            "sub": user["id"],  # subject (user ID)
            "email": user["email"],
            "role": user.get("role", UserRole.USER.value),
        }
        
        return create_access_token(token_data)
    
    async def verify_email(self, token: str) -> bool:
        """
        驗證 Email
        
        Args:
            token: Email 驗證 Token
            
        Returns:
            是否成功
        """
        email = verify_verification_token(token)
        if not email:
            return False
        
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return False
        
        # 更新驗證狀態
        await self.user_repo.verify_email(user["id"])
        
        logger.info(f"Email 驗證成功: {email}")
        
        return True
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """
        請求密碼重設
        
        Args:
            email: Email 地址
            
        Returns:
            密碼重設 Token（如果用戶存在），否則返回 None
        """
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            # 為了安全，即使用戶不存在也返回成功（避免 Email 枚舉攻擊）
            logger.warning(f"密碼重設請求：用戶不存在: {email}")
            return None
        
        # 建立密碼重設 Token
        reset_token = create_password_reset_token(email)
        
        logger.info(f"密碼重設請求: {email}")
        
        return reset_token
    
    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        重設密碼
        
        Args:
            token: 密碼重設 Token
            new_password: 新密碼
            
        Returns:
            是否成功
        """
        email = verify_password_reset_token(token)
        if not email:
            return False
        
        user = await self.user_repo.get_user_by_email(email)
        if not user:
            return False
        
        # 雜湊新密碼
        password_hash = self.get_password_hash(new_password)
        
        # 更新密碼
        await self.user_repo.update_password(user["id"], password_hash)
        
        logger.info(f"密碼重設成功: {email}")
        
        return True
    
    def _to_user_response(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        將資料庫用戶資料轉換為回應格式
        
        Args:
            user: 資料庫用戶資料
            
        Returns:
            用戶回應資料（不含敏感資訊）
        """
        # 移除敏感資訊
        user_response = {k: v for k, v in user.items() if k != "password_hash"}
        return user_response


# 建立全域實例
auth_service = AuthService()


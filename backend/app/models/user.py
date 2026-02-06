"""
User 資料模型
Phase 2: 會員系統
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class UserRole(str, Enum):
    """用戶角色"""
    GUEST = "guest"
    USER = "user"
    TESTER = "tester"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """用戶狀態"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class SubscriptionPlan(str, Enum):
    """訂閱方案（預留）"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """訂閱狀態（預留）"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class Language(str, Enum):
    """支援的語言"""
    ZH_TW = "zh-TW"  # 繁體中文
    EN = "en"        # 英文
    JA = "ja"        # 日文


class UserBase(BaseModel):
    """User 基礎模型"""
    email: EmailStr = Field(..., description="Email 地址")
    name: Optional[str] = Field(None, max_length=100, description="用戶名稱")
    language: Language = Field(default=Language.ZH_TW, description="語言偏好")
    role: UserRole = Field(default=UserRole.USER, description="用戶角色")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="用戶狀態")


class UserCreate(UserBase):
    """建立 User 的請求模型"""
    password: str = Field(..., min_length=8, description="密碼（至少 8 位）")
    
    @validator('password')
    def validate_password(cls, v):
        """驗證密碼：至少 8 位 + 1 個大寫字母 + 1 個數字"""
        if len(v) < 8:
            raise ValueError('密碼至少需要 8 個字元')
        if not any(c.isupper() for c in v):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密碼必須包含至少一個數字')
        return v


class UserUpdate(BaseModel):
    """更新 User 的請求模型"""
    name: Optional[str] = Field(None, max_length=100)
    language: Optional[Language] = None
    status: Optional[UserStatus] = None


class UserLogin(BaseModel):
    """登入請求模型"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User 回應模型（不含敏感資訊）"""
    id: str = Field(..., description="用戶 ID")
    email_verified: bool = Field(default=False, description="Email 是否已驗證")
    google_id: Optional[str] = Field(None, description="Google OAuth ID（如果使用 Google 登入）")
    avatar_url: Optional[str] = Field(None, description="頭像 URL")
    
    # 付費預留欄位
    subscription_plan: Optional[SubscriptionPlan] = Field(None, description="訂閱方案")
    subscription_status: Optional[SubscriptionStatus] = Field(None, description="訂閱狀態")
    subscription_expires_at: Optional[datetime] = Field(None, description="訂閱到期時間")
    
    # 時間戳記
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = Field(None, description="最後登入時間")
    email_verified_at: Optional[datetime] = Field(None, description="Email 驗證時間")
    
    # 警告訊息（用於註冊時郵件發送失敗等情況）
    warning: Optional[str] = Field(None, description="警告訊息（例如：郵件發送失敗）")
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """資料庫中的 User 模型（含密碼雜湊）"""
    password_hash: str = Field(..., description="密碼雜湊")
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 回應模型"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 類型")
    expires_in: int = Field(..., description="過期時間（秒）")
    user: UserResponse = Field(..., description="用戶資訊")


class EmailVerificationRequest(BaseModel):
    """Email 驗證請求模型"""
    email: EmailStr


class EmailVerificationResponse(BaseModel):
    """Email 驗證回應模型"""
    message: str
    verification_token: Optional[str] = None  # 僅在開發環境返回


class PasswordResetRequest(BaseModel):
    """忘記密碼請求模型"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """重設密碼確認模型"""
    token: str = Field(..., description="重設密碼 Token")
    new_password: str = Field(..., min_length=8, description="新密碼")
    
    @validator('new_password')
    def validate_password(cls, v):
        """驗證密碼：至少 8 位 + 1 個大寫字母 + 1 個數字"""
        if len(v) < 8:
            raise ValueError('密碼至少需要 8 個字元')
        if not any(c.isupper() for c in v):
            raise ValueError('密碼必須包含至少一個大寫字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密碼必須包含至少一個數字')
        return v


class GoogleOAuthRequest(BaseModel):
    """Google OAuth 請求模型"""
    code: str = Field(..., description="Google OAuth 授權碼")
    redirect_uri: Optional[str] = Field(None, description="重定向 URI")


class FeatureFlag(BaseModel):
    """Feature Flag 模型"""
    name: str = Field(..., description="功能名稱")
    enabled: bool = Field(default=False, description="是否啟用")
    description: Optional[str] = Field(None, description="功能描述")
    target_roles: Optional[List[UserRole]] = Field(None, description="目標角色（空則表示所有角色）")
    target_plans: Optional[List[SubscriptionPlan]] = Field(None, description="目標方案（空則表示所有方案）")


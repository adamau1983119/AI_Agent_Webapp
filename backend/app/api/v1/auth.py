"""
認證 API 端點
Phase 2: 會員系統
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query, Request
from fastapi.responses import RedirectResponse
from app.models.user import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    PasswordResetRequest, PasswordResetConfirm,
    GoogleOAuthRequest
)
from app.services.auth_service import auth_service
from app.middleware.jwt_auth import get_current_user, jwt_auth
from app.config_module import settings
from app.utils.i18n import get_error_message, get_user_language
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/check-email")
async def check_email_available(
    request: Request,
    email: str = Query(..., description="要檢查的 Email 地址")
):
    """
    檢查 Email 是否可用（未被註冊）
    
    - **email**: Email 地址
    
    返回：
    - available: true/false
    - message: 提示訊息（如果不可用）
    """
    language = get_user_language(request=request)
    
    # 基本格式驗證
    import re
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return {
            "available": False,
            "message": get_error_message("auth.invalid_email_format", language)
        }
    
    # 檢查 Email 是否已存在
    existing_user = await auth_service.user_repo.get_user_by_email(email)
    
    if existing_user:
        return {
            "available": False,
            "message": get_error_message("auth.email_already_registered", language)
        }
    
    return {
        "available": True,
        "message": None
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request):
    """
    註冊新用戶
    
    - **email**: Email 地址（必須）
    - **password**: 密碼（至少 8 位，包含至少 1 個大寫字母）
    - **name**: 用戶名稱（可選）
    - **language**: 語言偏好（預設：zh-TW）
    """
    try:
        user, verification_token = await auth_service.register_user(user_data)
        
        # Phase 2: 發送驗證郵件
        from app.services.email_service import email_service
        from app.models.user import Language
        
        language = Language(user.get("language", "zh-TW"))
        user_language = get_user_language(user=user, request=request)
        
        # 檢查郵件服務是否配置
        if not email_service.is_configured():
            logger.warning(f"郵件服務未配置，無法發送驗證郵件給 {user['email']}")
            # 註冊成功，但返回警告訊息
            user_response = UserResponse(**user)
            user_response.warning = get_error_message("auth.email_not_configured", user_language)
            return user_response
        
        # 嘗試發送驗證郵件
        email_sent = await email_service.send_verification_email(
            to_email=user["email"],
            verification_token=verification_token,
            language=language
        )
        
        if email_sent:
            logger.info(f"用戶註冊成功，驗證郵件已發送: {user['email']}")
        else:
            logger.warning(f"用戶註冊成功，但驗證郵件發送失敗: {user['email']}")
            # 註冊成功，但返回警告訊息
            user_response = UserResponse(**user)
            user_response.warning = get_error_message("auth.email_send_failed", user_language)
            return user_response
        
        return UserResponse(**user)
        
    except ValueError as e:
        language = get_user_language(request=request)
        error_message = str(e)
        
        # 處理特定的錯誤訊息，轉換為 i18n
        if error_message == "EMAIL_ALREADY_REGISTERED":
            error_message = get_error_message("auth.email_already_registered", language)
        elif "測試版名額已滿" in error_message:
            # 保持原訊息（已包含數字）
            pass
        else:
            # 其他 ValueError 訊息保持原樣
            pass
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    except Exception as e:
        logger.error(f"註冊失敗: {e}")
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=get_error_message("auth.register_failed", language)
        )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, request: Request):
    """
    用戶登入
    
    - **email**: Email 地址
    - **password**: 密碼
    
    返回 JWT Access Token
    """
    user = await auth_service.authenticate_user(login_data)
    
    if not user:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=get_error_message("auth.invalid_credentials", language),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 建立 Access Token
    access_token = await auth_service.create_access_token_for_user(user)
    
    # 計算過期時間（秒）
    expires_in = settings.JWT_EXPIRE_MINUTES * 60
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(**user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    取得當前用戶資訊
    
    需要 JWT Token 認證
    """
    return UserResponse(**current_user)


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(token: str, request: Request):
    """
    驗證 Email
    
    - **token**: Email 驗證 Token（從驗證郵件中取得）
    """
    success = await auth_service.verify_email(token)
    
    if not success:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_message("auth.verification_invalid", language)
        )
    
    language = get_user_language(request=request)
    return EmailVerificationResponse(
        message=get_error_message("auth.verification_success", language)
    )


@router.post("/resend-verification", response_model=EmailVerificationResponse)
async def resend_verification_email(request_data: EmailVerificationRequest, request: Request):
    """
    重新發送驗證郵件
    
    - **email**: Email 地址
    """
    user = await auth_service.user_repo.get_user_by_email(request_data.email)
    language = get_user_language(user=user, request=request)
    
    if not user:
        # 為了安全，即使用戶不存在也返回成功（避免 Email 枚舉攻擊）
        return EmailVerificationResponse(
            message=get_error_message("auth.verification_sent", language)
        )
    
    if user.get("email_verified"):
        return EmailVerificationResponse(
            message=get_error_message("auth.already_verified", language)
        )
    
    # 建立驗證 Token
    from app.utils.jwt import create_verification_token
    verification_token = create_verification_token(user["email"])
    
    # Phase 2: 發送驗證郵件
    from app.services.email_service import email_service
    from app.models.user import Language
    
    language = Language(user.get("language", "zh-TW"))
    await email_service.send_verification_email(
        to_email=user["email"],
        verification_token=verification_token,
        language=language
    )
    
    return EmailVerificationResponse(
        message=get_error_message("auth.verification_sent", language)
    )


@router.post("/forgot-password", response_model=dict)
async def forgot_password(request_data: PasswordResetRequest, request: Request):
    """
    忘記密碼
    
    - **email**: Email 地址
    
    發送密碼重設郵件
    """
    reset_token = await auth_service.request_password_reset(request_data.email)
    
    # Phase 2: 發送密碼重設郵件
    if reset_token:
        from app.services.email_service import email_service
        from app.models.user import Language
        
        # 取得用戶語言偏好
        user = await auth_service.user_repo.get_user_by_email(request_data.email)
        language = Language(user.get("language", "zh-TW")) if user else Language.ZH_TW
        
        await email_service.send_password_reset_email(
            to_email=request_data.email,
            reset_token=reset_token,
            language=language
        )
    
    # 為了安全，即使用戶不存在也返回成功
    language = get_user_language(request=request)
    return {
        "message": get_error_message("auth.verification_sent", language)
    }


@router.post("/reset-password", response_model=dict)
async def reset_password(request_data: PasswordResetConfirm, request: Request):
    """
    重設密碼
    
    - **token**: 密碼重設 Token（從重設郵件中取得）
    - **new_password**: 新密碼（至少 8 位，包含至少 1 個大寫字母）
    """
    success = await auth_service.reset_password(
        request_data.token,
        request_data.new_password
    )
    
    if not success:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_error_message("auth.reset_link_invalid", language)
        )
    
    language = get_user_language(request=request)
    return {
        "message": get_error_message("auth.reset_success", language)
    }


@router.get("/google/login")
async def google_login(request: Request):
    """
    Google OAuth 登入（重定向到 Google 授權頁面）
    """
    if not settings.GOOGLE_OAUTH_CLIENT_ID:
        language = get_user_language(request=request)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=get_error_message("auth.oauth_not_configured", language)
        )
    
    # Google OAuth 授權 URL
    from urllib.parse import urlencode
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Google OAuth 回調
    
    處理 Google 授權後的重定向
    """
    import httpx
    from app.services.email_service import email_service
    from app.models.user import Language, UserRole, UserStatus
    
    if error:
        # 重定向到前端錯誤頁面
        frontend_url = settings.FRONTEND_URL
        return RedirectResponse(
            url=f"{frontend_url}/login?error={error}"
        )
    
    if not code:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=no_code"
        )
    
    try:
        # 1. 使用 code 交換 access_token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                logger.error(f"Google token exchange failed: {token_response.text}")
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error=token_exchange_failed"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
        
        # 2. 使用 access_token 獲取用戶資訊
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if user_response.status_code != 200:
                logger.error(f"Google user info failed: {user_response.text}")
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error=user_info_failed"
                )
            
            google_user = user_response.json()
        
        google_id = google_user.get("id")
        email = google_user.get("email")
        name = google_user.get("name", "")
        avatar_url = google_user.get("picture")
        
        # 3. 建立或更新用戶
        # 先檢查是否已有 Google ID 關聯的帳號
        user = await auth_service.user_repo.get_user_by_google_id(google_id)
        
        if not user:
            # 檢查是否有相同 Email 的帳號
            user = await auth_service.user_repo.get_user_by_email(email)
            
            if user:
                # 關聯 Google 帳號到現有帳號
                await auth_service.user_repo.update_user(user["id"], {
                    "google_id": google_id,
                    "avatar_url": avatar_url or user.get("avatar_url"),
                    "email_verified": True,  # Google 已驗證 Email
                })
                user = await auth_service.user_repo.get_user_by_id(user["id"])
            else:
                # 檢查用戶數量限制
                active_count = await auth_service.user_repo.count_active_users()
                if active_count >= settings.MAX_USERS:
                    return RedirectResponse(
                        url=f"{settings.FRONTEND_URL}/login?error=max_users_reached"
                    )
                
                # 建立新用戶（不需要密碼，因為使用 Google 登入）
                import secrets
                from datetime import datetime
                
                user_id = f"user_{secrets.token_urlsafe(16)}"
                now = datetime.utcnow()
                
                new_user = {
                    "id": user_id,
                    "email": email.lower(),
                    "name": name,
                    "google_id": google_id,
                    "avatar_url": avatar_url,
                    "language": Language.ZH_TW.value,
                    "role": UserRole.USER.value,
                    "status": UserStatus.ACTIVE.value,
                    "email_verified": True,  # Google 已驗證 Email
                    "password_hash": "",  # 無密碼（Google OAuth 用戶）
                    "created_at": now,
                    "updated_at": now,
                }
                
                # 使用 auth_service 的 user_repo（已有資料庫連接）
                await auth_service.user_repo.create(new_user)
                user = new_user
                
                # 發送歡迎郵件
                await email_service.send_welcome_email(
                    to_email=email,
                    user_name=name or email.split("@")[0],
                    language=Language.ZH_TW
                )
        
        # 更新最後登入時間
        await auth_service.user_repo.update_last_login(user["id"])
        
        # 4. 建立 JWT Token
        jwt_token = await auth_service.create_access_token_for_user(user)
        
        # 5. 重定向到前端並帶上 Token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/oauth-callback?token={jwt_token}"
        )
        
    except Exception as e:
        import traceback
        logger.error(f"Google OAuth callback error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error=oauth_failed"
        )


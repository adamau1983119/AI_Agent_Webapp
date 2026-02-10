"""
JWT 工具
Phase 2: 會員系統
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config_module import settings
import logging

logger = logging.getLogger(__name__)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    建立 JWT Access Token
    
    Args:
        data: 要編碼的資料（通常包含 user_id, email, role 等）
        expires_delta: 過期時間（可選，預設使用配置中的時間）
        
    Returns:
        JWT Token 字串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_verification_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    建立 Email 驗證 Token
    
    Args:
        email: Email 地址
        expires_delta: 過期時間（可選，預設 24 小時）
        
    Returns:
        JWT Token 字串
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "email_verification"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_password_reset_token(
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    建立密碼重設 Token
    
    Args:
        email: Email 地址
        expires_delta: 過期時間（可選，預設 24 小時）
        
    Returns:
        JWT Token 字串
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "password_reset"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


class TokenError(Exception):
    """Token 驗證錯誤（含錯誤類型）"""
    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    驗證 JWT Token
    
    Args:
        token: JWT Token 字串
        
    Returns:
        解碼後的資料，如果無效則返回 None
        
    Raises:
        TokenError: 如果 Token 過期或無效（含詳細錯誤類型）
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT Token 已過期")
        raise TokenError("expired", "Token 已過期，請重新登入")
    except JWTError as e:
        logger.warning(f"JWT 驗證失敗: {e}")
        raise TokenError("invalid", "無效的 Token")


def verify_token_safe(token: str) -> Optional[Dict[str, Any]]:
    """
    安全版本的 verify_token（不拋出異常，返回 None）
    
    Args:
        token: JWT Token 字串
        
    Returns:
        解碼後的資料，如果無效則返回 None
    """
    try:
        return verify_token(token)
    except TokenError:
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    驗證 Access Token
    
    Args:
        token: JWT Access Token
        
    Returns:
        解碼後的資料，如果無效則返回 None
        
    Raises:
        TokenError: 如果 Token 過期或無效
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "access":
        return payload
    raise TokenError("invalid", "無效的 Access Token")


def verify_verification_token(token: str) -> Optional[str]:
    """
    驗證 Email 驗證 Token
    
    Args:
        token: Email 驗證 Token
        
    Returns:
        Email 地址，如果無效則返回 None
    """
    try:
        payload = verify_token(token)
        if payload and payload.get("type") == "email_verification":
            return payload.get("email")
        return None
    except TokenError:
        return None


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    驗證密碼重設 Token（有效期 1 小時）
    
    Args:
        token: 密碼重設 Token
        
    Returns:
        Email 地址，如果無效或過期則返回 None
    """
    try:
        payload = verify_token(token)
        if payload and payload.get("type") == "password_reset":
            return payload.get("email")
        return None
    except TokenError:
        return None


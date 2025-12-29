"""
API Key 認證中間件
用於單一使用者場景的簡單認證
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import os
from app.config import settings


class APIKeyAuth(HTTPBearer):
    """API Key 認證類"""
    
    def __init__(self, auto_error: bool = True):
        super(APIKeyAuth, self).__init__(auto_error=auto_error)
        self.api_key = settings.API_KEY if hasattr(settings, 'API_KEY') else None
    
    async def __call__(self, request: Request):
        # 如果未設定 API Key，則跳過認證
        if not self.api_key:
            return None
        
        # 檢查 X-API-Key header
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header and api_key_header == self.api_key:
            return api_key_header
        
        # 檢查 Authorization header (Bearer token)
        credentials: HTTPAuthorizationCredentials = await super(APIKeyAuth, self).__call__(request)
        if credentials and credentials.credentials == self.api_key:
            return credentials.credentials
        
        # 如果設定了 API Key 但未提供或錯誤，則拒絕
        if self.api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return None


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API Key 認證中間件"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/api/v1/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        self.api_key = settings.API_KEY if hasattr(settings, 'API_KEY') else None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 如果未設定 API Key，則跳過認證
        if not self.api_key:
            return await call_next(request)
        
        # 排除的路徑不需要認證
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 檢查 API Key
        api_key_header = request.headers.get("X-API-Key")
        auth_header = request.headers.get("Authorization")
        
        # 檢查 X-API-Key header
        if api_key_header and api_key_header == self.api_key:
            return await call_next(request)
        
        # 檢查 Authorization header (Bearer token)
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            if token == self.api_key:
                return await call_next(request)
        
        # 認證失敗
        return Response(
            content='{"detail": "Invalid or missing API Key"}',
            status_code=status.HTTP_401_UNAUTHORIZED,
            media_type="application/json",
            headers={"WWW-Authenticate": "Bearer"},
        )


# 建立認證實例
api_key_auth = APIKeyAuth(auto_error=False)


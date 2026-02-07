"""
CSRF 防護中間件
Phase 2: 安全功能

策略：
- 檢查 Referer / Origin header 是否來自允許的來源
- 對狀態變更請求（POST, PUT, PATCH, DELETE）進行檢查
- GET / HEAD / OPTIONS 請求不需要檢查
- API Key 請求可以豁免（M2M 通訊）
- JWT Bearer Token 請求可以豁免（已有認證機制）
"""
import logging
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from typing import Callable, List, Optional
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF 防護中間件"""
    
    # 不需要 CSRF 檢查的 HTTP 方法（安全方法）
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
    
    # 不需要 CSRF 檢查的路徑前綴
    EXEMPT_PATHS = [
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/api/v1/health",
        # OAuth 回調（由第三方發起）
        "/api/v1/auth/google/callback",
        # Webhook 端點（如果有）
        "/api/v1/webhooks/",
    ]
    
    def __init__(self, app, allowed_origins: Optional[List[str]] = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or self._parse_allowed_origins()
    
    def _parse_allowed_origins(self) -> List[str]:
        """從設定中解析允許的來源"""
        origins = settings.CORS_ORIGINS
        if isinstance(origins, str):
            origins = [o.strip() for o in origins.split(',') if o.strip()]
        elif not isinstance(origins, list):
            origins = list(origins) if origins else []
        
        # 確保來源列表不為空
        if not origins:
            origins = ["*"]
        
        return origins
    
    def _is_exempt(self, request: Request) -> bool:
        """檢查請求是否豁免 CSRF 檢查"""
        # 安全方法不需要檢查
        if request.method in self.SAFE_METHODS:
            return True
        
        # 排除的路徑
        for path in self.EXEMPT_PATHS:
            if request.url.path.startswith(path):
                return True
        
        # 有 API Key 的請求豁免（M2M 通訊）
        if request.headers.get("X-API-Key"):
            return True
        
        # Bearer Token 請求豁免（已有 JWT 認證，非瀏覽器表單提交）
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return True
        
        return False
    
    def _validate_origin(self, request: Request) -> bool:
        """
        驗證請求來源
        
        檢查 Origin 或 Referer header 是否來自允許的來源
        """
        # 如果允許所有來源，跳過檢查
        if "*" in self.allowed_origins:
            return True
        
        # 優先檢查 Origin header
        origin = request.headers.get("Origin")
        if origin:
            return self._is_origin_allowed(origin)
        
        # 備選：檢查 Referer header
        referer = request.headers.get("Referer")
        if referer:
            parsed = urlparse(referer)
            referer_origin = f"{parsed.scheme}://{parsed.netloc}"
            return self._is_origin_allowed(referer_origin)
        
        # 沒有 Origin 也沒有 Referer
        # 這可能是非瀏覽器請求（API 客戶端、curl 等）
        # 在開發環境中允許，生產環境中拒絕
        if settings.ENVIRONMENT == "development":
            return True
        
        logger.warning(f"CSRF: 請求缺少 Origin 和 Referer header: {request.url.path}")
        return False
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """檢查來源是否在允許列表中"""
        if "*" in self.allowed_origins:
            return True
        
        # 精確匹配
        if origin in self.allowed_origins:
            return True
        
        # 去除尾部斜杠後匹配
        origin_clean = origin.rstrip("/")
        for allowed in self.allowed_origins:
            if origin_clean == allowed.rstrip("/"):
                return True
        
        return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """處理請求"""
        # 檢查是否豁免
        if self._is_exempt(request):
            return await call_next(request)
        
        # 驗證來源
        if not self._validate_origin(request):
            logger.warning(
                f"CSRF 驗證失敗: method={request.method}, "
                f"path={request.url.path}, "
                f"origin={request.headers.get('Origin')}, "
                f"referer={request.headers.get('Referer')}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "CSRF validation failed: request origin not allowed"
                }
            )
        
        return await call_next(request)


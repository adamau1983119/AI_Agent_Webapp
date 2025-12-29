"""
請求限流中間件
防止 API 濫用
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable, Dict, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """請求限流中間件"""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        exclude_paths: list = None,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.exclude_paths = exclude_paths or [
            "/health",
            "/api/v1/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        ]
        # 儲存請求記錄：{ip: [(timestamp, ...), ...]}
        self.request_history: Dict[str, list] = defaultdict(list)
        # 清理間隔（秒）
        self.cleanup_interval = 3600  # 1 小時
        self.last_cleanup = time.time()
    
    def _get_client_ip(self, request: Request) -> str:
        """取得客戶端 IP"""
        # 檢查 X-Forwarded-For header（用於反向代理）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 檢查 X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 使用直接連接的 IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_requests(self):
        """清理舊的請求記錄"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        cutoff_time = current_time - 3600  # 保留 1 小時內的記錄
        
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                ts for ts in self.request_history[ip] if ts > cutoff_time
            ]
            if not self.request_history[ip]:
                del self.request_history[ip]
    
    def _check_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """檢查是否超過限流"""
        current_time = time.time()
        one_minute_ago = current_time - 60
        one_hour_ago = current_time - 3600
        
        # 取得該 IP 的請求記錄
        requests = self.request_history[ip]
        
        # 計算最近 1 分鐘的請求數
        recent_minute = [ts for ts in requests if ts > one_minute_ago]
        if len(recent_minute) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        
        # 計算最近 1 小時的請求數
        recent_hour = [ts for ts in requests if ts > one_hour_ago]
        if len(recent_hour) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
        
        # 記錄此次請求
        requests.append(current_time)
        
        return True, ""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 排除的路徑不需要限流
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # 清理舊記錄
        self._cleanup_old_requests()
        
        # 取得客戶端 IP
        client_ip = self._get_client_ip(request)
        
        # 檢查限流
        allowed, error_message = self._check_rate_limit(client_ip)
        
        if not allowed:
            return Response(
                content=f'{{"detail": "{error_message}"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60",
                },
            )
        
        # 計算剩餘請求數
        current_time = time.time()
        one_minute_ago = current_time - 60
        requests = self.request_history[client_ip]
        recent_minute = [ts for ts in requests if ts > one_minute_ago]
        remaining = max(0, self.requests_per_minute - len(recent_minute))
        
        # 執行請求
        response = await call_next(request)
        
        # 添加限流資訊到響應頭
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


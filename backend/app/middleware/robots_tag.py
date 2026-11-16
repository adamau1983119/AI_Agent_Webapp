"""
API 子域搜尋引擎擋索引（GSC：api.ai-alterego.com 不應進索引）。

- 所有回應加 X-Robots-Tag: noindex, nofollow
- GET/HEAD /robots.txt → Disallow: /（最外層短路，免 API Key／限流擋 Googlebot）
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response
from typing import Callable

ROBOTS_BODY = "User-agent: *\nDisallow: /\n"
ROBOTS_TAG = "noindex, nofollow"


class RobotsTagMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path == "/robots.txt" and request.method in ("GET", "HEAD"):
            return PlainTextResponse(
                ROBOTS_BODY,
                media_type="text/plain; charset=utf-8",
                headers={"X-Robots-Tag": ROBOTS_TAG},
            )
        response = await call_next(request)
        response.headers["X-Robots-Tag"] = ROBOTS_TAG
        return response

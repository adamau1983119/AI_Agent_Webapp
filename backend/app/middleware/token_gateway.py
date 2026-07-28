"""
v7 Token Gateway — 剝除 llm_input 等大文本；Starlette body 重放（Phase 3）
僅作用於 POST /api/v1/contents/{id}/generate|regenerate
"""
import json
import logging
import re
from typing import Any, Dict, Set, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)

_GATEWAY_RE = re.compile(r"^/api/v1/contents/[^/]+/(generate|regenerate)$")
_STRIP_KEYS: Set[str] = {
    "llm_input",
    "user_prompt",
    "original_content",
    "full_text",
    "article_body",
    "prompt",
    "context",
    "html_content",
}
_MAX_BODY_BYTES = 65536


def _is_gateway_path(path: str, method: str) -> bool:
    return method == "POST" and bool(_GATEWAY_RE.match(path))


def _strip_payload(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    clean = dict(data)
    stripped = False
    for key in list(clean.keys()):
        if key in _STRIP_KEYS:
            if clean.pop(key, None):
                stripped = True
        elif isinstance(clean.get(key), str) and len(clean[key]) > 4000:
            clean[key] = clean[key][:4000]
            stripped = True
    return clean, stripped


def _replay_body(request: Request, body: bytes) -> None:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive  # Starlette body 重放


class TokenGatewayMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not _is_gateway_path(request.url.path, request.method):
            return await call_next(request)

        raw = await request.body()
        if len(raw) > _MAX_BODY_BYTES:
            return JSONResponse(status_code=413, content={"detail": "payload_too_large"})

        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JSONResponse(status_code=400, content={"detail": "invalid_json"})

        if not isinstance(data, dict):
            data = {}

        clean, stripped = _strip_payload(data)
        new_body = json.dumps(clean, ensure_ascii=False).encode("utf-8")
        _replay_body(request, new_body)

        response = await call_next(request)

        if response.status_code < 500:
            parts = request.url.path.rstrip("/").split("/")
            topic_id = parts[-2] if len(parts) >= 2 else "unknown"
            log_cost_event(
                "TOKEN_GATEWAY_PASSED",
                topic_id=topic_id,
                stripped=str(stripped).lower(),
            )
        return response

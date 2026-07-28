"""
Alter Ego Body Gateway — POST /api/v1/alter-ego/* body 上限 64KB；剝大文本鍵（PD-AE1-03）
"""
import json
import re
from typing import Any, Dict, Set, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.utils.logger import log_cost_event

_GATEWAY_RE = re.compile(r"^/api/v1/alter-ego/")
_MAX_BODY_BYTES = 65536
_MAX_EXEMPLAR_CHARS = 8000
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


def _is_gateway_path(path: str, method: str) -> bool:
    return method == "POST" and bool(_GATEWAY_RE.match(path))


def _replay_body(request: Request, body: bytes) -> None:
    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request._receive = receive


def _sanitize_payload(data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    clean = dict(data)
    stripped = False
    for key in list(clean.keys()):
        if key in _STRIP_KEYS:
            if clean.pop(key, None):
                stripped = True
        elif isinstance(clean.get(key), str) and len(clean[key]) > 4000:
            clean[key] = clean[key][:4000]
            stripped = True

    exemplars = clean.get("exemplars")
    if isinstance(exemplars, list):
        clipped = [
            (str(item)[:_MAX_EXEMPLAR_CHARS] if item is not None else "")
            for item in exemplars[:3]
        ]
        if clipped != exemplars:
            stripped = True
        clean["exemplars"] = clipped

    return clean, stripped


class AlterEgoBodyGatewayMiddleware(BaseHTTPMiddleware):
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

        clean, stripped = _sanitize_payload(data)
        _replay_body(request, json.dumps(clean, ensure_ascii=False).encode("utf-8"))

        response = await call_next(request)
        if response.status_code < 500:
            log_cost_event(
                "ALTER_EGO_BODY_GATEWAY_PASSED",
                path=request.url.path,
                stripped=str(stripped).lower(),
            )
        return response

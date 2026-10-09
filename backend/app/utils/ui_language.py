"""畫面語言。只接受請求上的 X-Language，不讀瀏覽器 Accept-Language。"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config_module import settings

ALLOWED = ("zh-TW", "en", "ja")


def allowed_language(value: Optional[str]) -> Optional[str]:
    if value in ALLOWED:
        return value
    return None


def screen_language(request: Optional[object]) -> Optional[str]:
    if request is None or not hasattr(request, "headers"):
        return None
    return allowed_language(request.headers.get("X-Language", ""))


def seal_oauth_language(lang: Optional[str]) -> Optional[str]:
    clean = allowed_language(lang)
    if not clean:
        return None
    payload = {
        "lang": clean,
        "type": "oauth_lang",
        "exp": datetime.utcnow() + timedelta(minutes=20),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def open_oauth_language(state: Optional[str]) -> Optional[str]:
    if not state:
        return None
    try:
        payload = jwt.decode(
            state,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
    if payload.get("type") != "oauth_lang":
        return None
    return allowed_language(payload.get("lang"))

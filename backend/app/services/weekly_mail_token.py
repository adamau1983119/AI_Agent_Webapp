"""週報退訂 token。與驗證信、重設密碼的 token 類型分開。"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from app.config_module import settings


def create_unsubscribe_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email.lower(),
        "type": "weekly_unsubscribe",
        "exp": datetime.utcnow() + timedelta(days=180),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def read_unsubscribe_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None
    if payload.get("type") != "weekly_unsubscribe":
        return None
    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        return None
    return {"user_id": user_id, "email": str(email).lower()}

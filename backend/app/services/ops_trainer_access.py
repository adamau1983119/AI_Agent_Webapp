"""Ops Style Trainer access: admin/tester + optional email allowlist."""
from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import HTTPException, status

from app.models.user import UserRole

_ALLOWED_ROLES = {UserRole.ADMIN.value, UserRole.TESTER.value}


def trainer_email_allowlist() -> List[str]:
    raw = (os.environ.get("OPS_STYLE_TRAINER_EMAILS") or "").strip()
    if not raw:
        try:
            from app.config import settings

            raw = (getattr(settings, "OPS_STYLE_TRAINER_EMAILS", None) or "").strip()
        except Exception:
            raw = ""
    return [e.strip().lower() for e in raw.split(",") if e.strip()]


def user_may_access_trainer(user: Dict[str, Any]) -> bool:
    role = str(user.get("role") or "")
    if role not in _ALLOWED_ROLES:
        return False
    allow = trainer_email_allowlist()
    if not allow:
        return True
    email = str(user.get("email") or "").strip().lower()
    return email in allow


def require_trainer(user: Dict[str, Any]) -> None:
    if not user_may_access_trainer(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ops_trainer_forbidden",
        )

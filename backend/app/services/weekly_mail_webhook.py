"""Resend 退信／檢舉簽章。密鑰未設定時一律拒絕。"""
from __future__ import annotations

import base64
import hashlib
import hmac
import time
from typing import Mapping, Optional


def verify_resend_signature(
    secret: str,
    body: bytes,
    headers: Mapping[str, str],
    now: Optional[float] = None,
) -> bool:
    secret = (secret or "").strip()
    if not secret:
        return False
    msg_id = headers.get("svix-id") or headers.get("webhook-id") or ""
    timestamp = headers.get("svix-timestamp") or headers.get("webhook-timestamp") or ""
    signature = headers.get("svix-signature") or headers.get("webhook-signature") or ""
    if not msg_id or not timestamp or not signature:
        return False
    try:
        ts = int(timestamp)
    except ValueError:
        return False
    current = time.time() if now is None else now
    if abs(current - ts) > 300:
        return False
    raw = secret[6:] if secret.startswith("whsec_") else secret
    try:
        key = base64.b64decode(raw)
    except Exception:
        return False
    signed = f"{msg_id}.{timestamp}.".encode() + body
    expected = base64.b64encode(hmac.new(key, signed, hashlib.sha256).digest()).decode()
    for part in signature.split():
        value = part[3:] if part.startswith("v1,") else part
        if hmac.compare_digest(value, expected):
            return True
    return False


def recipient_emails(event: dict) -> list[str]:
    data = event.get("data") or {}
    raw = data.get("to") or data.get("email") or []
    if isinstance(raw, str):
        raw = [raw]
    return [str(item).strip().lower() for item in raw if str(item).strip()]

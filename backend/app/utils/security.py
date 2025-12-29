"""
安全工具函數
包含加密、雜湊等功能
"""
import hashlib
import secrets
from typing import Optional
import os


def generate_api_key(length: int = 32) -> str:
    """生成安全的 API Key"""
    return secrets.token_urlsafe(length)


def hash_password(password: str) -> str:
    """雜湊密碼（SHA-256）"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """驗證密碼"""
    return hash_password(password) == hashed


def generate_secret_key() -> str:
    """生成密鑰（用於 Session 等）"""
    return secrets.token_urlsafe(32)


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """遮罩 API Key（僅顯示前幾個字元）"""
    if not api_key or len(api_key) <= visible_chars:
        return "****"
    return api_key[:visible_chars] + "*" * (len(api_key) - visible_chars)


def is_secure_connection(request) -> bool:
    """檢查是否為安全連接（HTTPS）"""
    # 檢查 X-Forwarded-Proto header（用於反向代理）
    forwarded_proto = request.headers.get("X-Forwarded-Proto")
    if forwarded_proto:
        return forwarded_proto.lower() == "https"
    
    # 檢查 URL scheme
    return request.url.scheme == "https"


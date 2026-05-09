"""
使用者貼上之 Feed URL 驗證（MVP）：格式、SSRF 基本防護、可選 HTTP 抓取與 feedparser 粗判。
"""
from __future__ import annotations

import ipaddress
import logging
import re
import socket
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

import httpx

try:
    import feedparser
except ImportError:
    feedparser = None

logger = logging.getLogger(__name__)

MAX_URL_LEN = 2048
MAX_BODY_BYTES = 500_000
REQUEST_TIMEOUT = 10.0
MAX_REDIRECTS = 5

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "metadata.google.internal",
        "metadata",
    }
)


def _normalize_url(url: str) -> str:
    u = (url or "").strip()
    if len(u) > MAX_URL_LEN:
        raise ValueError("invalid_url")
    return u


def _hostname_is_safe(hostname: str) -> bool:
    if not hostname:
        return False
    h = hostname.strip().lower().rstrip(".")
    if h in _BLOCKED_HOSTNAMES:
        return False
    if h.endswith(".localhost") or h.endswith(".local"):
        return False
    try:
        ip = ipaddress.ip_address(h)
        return ip.is_global
    except ValueError:
        pass
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except OSError:
        return False
    for info in infos:
        sockaddr = info[4]
        ip_str = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            if not ip_obj.is_global:
                return False
        except ValueError:
            return False
    return bool(infos)


def assert_url_safe_for_fetch(url: str) -> Tuple[str, str]:
    """
    檢查 URL 是否允許由伺服器抓取。

    Returns:
        (normalized_url, hostname)

    Raises:
        ValueError: error code string（invalid_url / ssrf_blocked）
    """
    raw = _normalize_url(url)
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("invalid_url")
    host = (parsed.hostname or "").strip()
    if not host:
        raise ValueError("invalid_url")
    if not _hostname_is_safe(host):
        raise ValueError("ssrf_blocked")
    netloc_lower = (parsed.netloc or "").lower()
    if "@" in netloc_lower and re.search(r"@\d+\.\d+\.\d+\.\d+", netloc_lower):
        raise ValueError("invalid_url")
    return raw, host


async def probe_feed_url(url: str) -> Dict[str, Any]:
    """
    GET URL，檢查最終 URL（含 redirect）仍通過 SSRF，並以 feedparser 粗判是否像 RSS/Atom。

    Returns:
        dict: valid, title?, suggested_name?, error_code?
    """
    try:
        initial, _ = assert_url_safe_for_fetch(url)
    except ValueError as e:
        code = str(e.args[0]) if e.args else "invalid_url"
        return {"valid": False, "error_code": code}

    if feedparser is None:
        logger.error("feedparser not installed")
        return {"valid": False, "error_code": "service_unavailable"}

    try:
        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT,
            follow_redirects=True,
            max_redirects=MAX_REDIRECTS,
        ) as client:
            resp = await client.get(
                initial,
                headers={"User-Agent": "InfluencersAI/1.0 (ChannelFeedValidator)"},
            )
    except httpx.TimeoutException:
        return {"valid": False, "error_code": "timeout"}
    except httpx.RequestError:
        return {"valid": False, "error_code": "fetch_failed"}

    final_url = str(resp.url)
    try:
        assert_url_safe_for_fetch(final_url)
    except ValueError as e:
        code = str(e.args[0]) if e.args else "ssrf_blocked"
        return {"valid": False, "error_code": code}

    if resp.status_code >= 400:
        return {"valid": False, "error_code": "http_error"}

    text = resp.text
    if len(text.encode("utf-8", errors="ignore")) > MAX_BODY_BYTES:
        text = text[:MAX_BODY_BYTES]

    parsed_feed = feedparser.parse(text)
    feed_title = (parsed_feed.feed.get("title") or "").strip() if parsed_feed.feed else ""
    sample = ""
    if parsed_feed.entries:
        sample = (parsed_feed.entries[0].get("title") or "").strip()

    if not feed_title and not parsed_feed.entries:
        return {"valid": False, "error_code": "not_feed"}

    title = feed_title or sample or None
    host_only = urlparse(final_url).hostname or "RSS"
    suggested = title or host_only

    return {
        "valid": True,
        "title": title,
        "suggested_name": suggested[:120] if suggested else None,
        "error_code": None,
    }

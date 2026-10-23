"""入選三關：正文夠長、不是付費牆、圖可解碼。MD-M2 ≤150。"""
from __future__ import annotations

import re
from typing import Optional, Sequence

_MIN_CJK = 150
_MIN_WORDS = 150
_CONTINUE = re.compile(
    r"(continue reading|read more|続きを読む|繼續閱讀|继续阅读)\s*$",
    re.I,
)
_CJK = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")
_WORD = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")
_PAYWALL_DECL = re.compile(r'"isAccessibleForFree"\s*:\s*false', re.I)
_PREMIUM_PATHS = ("/premium/", "/subscribers/", "/membership/")


def declared_paywall(html: str) -> bool:
    return bool(_PAYWALL_DECL.search(html or ""))


def body_is_complete(text: str) -> bool:
    """中文數字元，英文數字。收在「繼續閱讀」不算完整。"""
    raw = (text or "").strip()
    if not raw or _CONTINUE.search(raw):
        return False
    cjk = len(_CJK.findall(raw))
    words = len(_WORD.findall(raw))
    if cjk >= words:
        return cjk >= _MIN_CJK
    return words >= _MIN_WORDS


def block_reason(
    *,
    url: str,
    body: str,
    paywall_declared: bool = False,
) -> Optional[str]:
    """不過關的原因。None 表示文字關過了，圖還要另測。"""
    link = (url or "").lower()
    if paywall_declared or any(part in link for part in _PREMIUM_PATHS):
        return "paywall"
    if not body_is_complete(body):
        return "short_or_teaser"
    return None


async def rejection(
    *,
    url: str,
    body: str,
    images: Sequence[str],
    paywall_declared: bool = False,
) -> Optional[str]:
    reason = block_reason(url=url, body=body, paywall_declared=paywall_declared)
    if reason:
        return reason
    if not await first_decodable_image(images):
        return "image"
    return None


async def first_decodable_image(urls: Sequence[str], limit: int = 3) -> Optional[str]:
    """試著抓前幾張並壓成 JPG。失敗回 None，不寫入庫。"""
    from app.services.images.jpeg_compress import fetch_and_compress

    tried = 0
    for item in urls or []:
        if tried >= limit:
            break
        if not isinstance(item, str) or not item.startswith("http"):
            continue
        tried += 1
        try:
            await fetch_and_compress(item)
            return item
        except Exception:
            continue
    return None

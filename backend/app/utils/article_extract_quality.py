"""Extract body quality: shell vs keep. MD-M2 ≤150. Wide-gate: reject body only."""
from __future__ import annotations

import re
from typing import Any, Dict

_MEGA = re.compile(
    r"(Fashion|Beauty|Wellness|Lifestyle|Celebrities|Lookbook|Streetsnaps)",
    re.I,
)
_CJK = re.compile(r"[\u4e00-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")
_TOC = re.compile(r"your next read|jump to categor", re.I)
RSS_STRONG_CHARS = 400


def mega_menu_hits(text: str) -> int:
    return len(_MEGA.findall(text or ""))


def looks_like_toc(text: str) -> bool:
    """True for recirc/TOC stubs that are not a news body."""
    t = (text or "").strip()
    if not t:
        return False
    return bool(_TOC.search(t) and len(t) < 800)


def text_quality(text: str) -> Dict[str, Any]:
    """Score body candidacy. is_shell => do not treat as success article body."""
    t = (text or "").strip()
    cjk = len(_CJK.findall(t))
    latin = len(_LATIN.findall(t))
    denom = max(cjk + latin, 1)
    ratio = cjk / denom
    mega = mega_menu_hits(t)
    is_shell = False
    reason = ""
    if looks_like_toc(t):
        is_shell = True
        reason = "toc_or_recirc"
    elif mega >= 6 and len(t) < 800:
        is_shell = True
        reason = "mega_menu_density"
    elif mega >= 4 and len(t) < 400:
        is_shell = True
        reason = "mega_menu_short"
    elif mega >= 2 and len(t) < 220 and cjk < 50 and ratio < 0.3:
        is_shell = True
        reason = "mega_plus_low_cjk"
    return {
        "cjk": cjk,
        "cjk_ratio": round(ratio, 3),
        "mega_hits": mega,
        "chars": len(t),
        "is_shell": is_shell,
        "reason": reason,
        "ok": bool(t) and len(t) >= 30 and not is_shell and not looks_like_toc(t),
    }


def accept_extracted_body(text: str) -> bool:
    return bool(text_quality(text).get("ok"))


def rss_body_is_strong(text: str) -> bool:
    """Only skip HTTP when RSS already has a real article, not a dek."""
    t = (text or "").strip()
    return accept_extracted_body(t) and len(t) >= RSS_STRONG_CHARS


def body_is_storable(text: str) -> bool:
    """Production gate: persist only a real article, never a dek or TOC."""
    t = (text or "").strip()
    return accept_extracted_body(t) and len(t) >= 200 and not looks_like_toc(t)

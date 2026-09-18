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


def mega_menu_hits(text: str) -> int:
    return len(_MEGA.findall(text or ""))


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
    if mega >= 6:
        is_shell = True
        reason = "mega_menu_density"
    elif mega >= 2 and cjk < 50 and ratio < 0.3:
        is_shell = True
        reason = "mega_plus_low_cjk"
    elif cjk < 50 and ratio < 0.3 and len(t) > 150 and mega >= 1:
        is_shell = True
        reason = "long_low_cjk_chrome"
    return {
        "cjk": cjk,
        "cjk_ratio": round(ratio, 3),
        "mega_hits": mega,
        "chars": len(t),
        "is_shell": is_shell,
        "reason": reason,
        "ok": bool(t) and len(t) >= 30 and not is_shell,
    }


def accept_extracted_body(text: str) -> bool:
    return bool(text_quality(text).get("ok"))

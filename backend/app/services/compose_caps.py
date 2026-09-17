"""Product character caps for the public post composer (not Meta preview YAML)."""
from __future__ import annotations

from typing import Dict, Tuple

# MVP：短 ≤500／長 ≤1500（IG／FB）；Threads 產品路徑 UI 隱藏
LENGTH_CHOICES: Tuple[int, ...] = (500, 1500)

PRODUCT_CAPS: Dict[str, int] = {
    "instagram": 2200,
    "facebook": 5000,
    # 保留鍵供舊測試／預覽契約；compose 主路不再接受 threads
    "threads": 150,
}

HASHTAG_HINTS: Dict[str, Tuple[int, int]] = {
    "instagram": (3, 5),
    "facebook": (3, 5),
    "threads": (1, 5),
}

COMPOSE_PLATFORMS = frozenset({"facebook", "instagram"})


def platform_cap(platform: str) -> int:
    return PRODUCT_CAPS.get(platform, 1500)


def clamp_max_chars(platform: str, requested: int) -> int:
    cap = platform_cap(platform)
    n = requested if requested in LENGTH_CHOICES else 500
    return min(n, cap)


def length_enabled(platform: str, n: int) -> bool:
    if platform not in COMPOSE_PLATFORMS and platform != "threads":
        return False
    return n in LENGTH_CHOICES and n <= platform_cap(platform)


def compose_credit_cost(max_chars: int) -> int:
    """短 500 → 1 點；長 1500 → 2 點。"""
    return 2 if int(max_chars) > 500 else 1

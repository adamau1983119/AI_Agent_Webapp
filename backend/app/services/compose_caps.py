"""Product character caps for the public post composer (not Meta preview YAML)."""
from __future__ import annotations

from typing import Dict, Tuple

LENGTH_CHOICES: Tuple[int, ...] = (50, 100, 150)

# Threads product cap is 150 (not Meta 500). IG caption / FB post are platform limits.
PRODUCT_CAPS: Dict[str, int] = {
    "threads": 150,
    "instagram": 2200,
    "facebook": 5000,
}

HASHTAG_HINTS: Dict[str, Tuple[int, int]] = {
    "threads": (0, 1),
    "instagram": (5, 10),
    "facebook": (4, 6),
}


def platform_cap(platform: str) -> int:
    return PRODUCT_CAPS.get(platform, 150)


def clamp_max_chars(platform: str, requested: int) -> int:
    cap = platform_cap(platform)
    n = requested if requested in LENGTH_CHOICES else 150
    return min(n, cap)


def length_enabled(platform: str, n: int) -> bool:
    return n in LENGTH_CHOICES and n <= platform_cap(platform)

"""選文開關與比例（預設 off＝舊路徑）。MD-M2 ≤150。"""
from __future__ import annotations

from typing import Any, Dict

_MODES = frozenset({"off", "shadow", "enforce"})


def _raw() -> Dict[str, Any]:
    try:
        from app.config.topic_config import get_topic_config

        cfg = get_topic_config()._config or {}
        blob = cfg.get("selection")
        return blob if isinstance(blob, dict) else {}
    except Exception:
        return {}


def selection_mode() -> str:
    mode = str(_raw().get("mode") or "off").lower().strip()
    return mode if mode in _MODES else "off"


def cold_slot_count(category_count: int) -> int:
    try:
        ratio = float(_raw().get("cold_ratio", 0.20))
    except (TypeError, ValueError):
        ratio = 0.20
    n = int(category_count or 0)
    if n <= 1:
        return 0
    return max(0, round(n * ratio))


def candidate_factor() -> int:
    try:
        n = int(_raw().get("candidate_factor", 8))
    except (TypeError, ValueError):
        n = 8
    return max(2, min(n, 24))


def max_per_source() -> int:
    try:
        n = int(_raw().get("max_per_source", 1))
    except (TypeError, ValueError):
        n = 1
    return max(1, n)

"""
熱門頻道模板（MC-6 · 靜態 JSON · D7.1-M1 採靜態）
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

_TEMPLATES_PATH = Path(__file__).resolve().parents[2] / "config" / "channel_templates.json"


@lru_cache(maxsize=1)
def load_channel_templates() -> List[Dict[str, Any]]:
    data = json.loads(_TEMPLATES_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return data

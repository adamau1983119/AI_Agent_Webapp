"""建立頻道助手的回答規則。不呼叫模型、不寫資料庫。"""
from typing import Any, Dict, Optional

ASSIST_CATEGORIES = frozenset({
    "fashion", "food", "trend", "finance", "sports", "tech",
    "entertainment", "beauty", "games", "travel", "growth",
})
ASSIST_REGIONS = frozenset({
    "hong_kong", "taiwan", "japan", "korea", "china", "usa", "uk", "global",
})
CHANNEL_ANALYSIS_CAP = 10
DAILY_ANALYSIS_CAP = 30

_CATEGORY_ALIASES = {
    "fashion": "fashion",
    "food": "food",
    "trend": "trend",
    "finance": "finance",
    "sports": "sports",
    "tech": "tech",
    "technology": "tech",
    "entertainment": "entertainment",
    "beauty": "beauty",
    "makeup": "beauty",
    "games": "games",
    "gaming": "games",
    "travel": "travel",
    "growth": "growth",
}
_REGION_ALIASES = {
    "hong_kong": "hong_kong",
    "hk": "hong_kong",
    "taiwan": "taiwan",
    "tw": "taiwan",
    "japan": "japan",
    "jp": "japan",
    "korea": "korea",
    "kr": "korea",
    "china": "china",
    "cn": "china",
    "usa": "usa",
    "us": "usa",
    "uk": "uk",
    "global": "global",
}


def normalize_category(raw: Optional[str]) -> Optional[str]:
    if not isinstance(raw, str) or not raw.strip():
        return None
    mapped = _CATEGORY_ALIASES.get(raw.lower().strip(), raw.lower().strip())
    return mapped if mapped in ASSIST_CATEGORIES else None


def normalize_region(raw: Optional[str]) -> Optional[str]:
    if not isinstance(raw, str) or not raw.strip():
        return None
    mapped = _REGION_ALIASES.get(raw.lower().strip(), raw.lower().strip())
    return mapped if mapped in ASSIST_REGIONS else None


def decide_quota(
    pending: int,
    day_count: int,
    stored_day: Optional[str],
    today: str,
) -> Dict[str, Any]:
    """第 10 次與當日第 30 次仍允許。已滿則不打模型。換日只重算每日次數。"""
    pending_now = max(0, int(pending or 0))
    used_today = day_count if stored_day == today else 0
    used_today = max(0, int(used_today or 0))
    if pending_now >= CHANNEL_ANALYSIS_CAP or used_today >= DAILY_ANALYSIS_CAP:
        return {
            "allowed": False,
            "last_analysis": False,
            "pending": pending_now,
            "day_count": used_today,
            "day": today,
        }
    next_pending = pending_now + 1
    next_day = used_today + 1
    return {
        "allowed": True,
        "last_analysis": (
            next_pending >= CHANNEL_ANALYSIS_CAP or next_day >= DAILY_ANALYSIS_CAP
        ),
        "pending": next_pending,
        "day_count": next_day,
        "day": today,
    }


def _keywords(raw: Any) -> list:
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw:
        text = str(item).strip() if item is not None else ""
        if text:
            out.append(text[:30])
        if len(out) >= 5:
            break
    return out


def _intent(**overrides: Any) -> Dict[str, Any]:
    base = {
        "category": None,
        "region": None,
        "keywords": [],
        "confidence": 0.0,
        "clarification_needed": True,
        "clarification_question": "",
        "suggested_channel_name": None,
        "suggested_channel_description": None,
        "out_of_catalog": False,
        "region_defaulted": False,
        "split_channel": False,
        "quota_blocked": False,
        "last_analysis": False,
    }
    base.update(overrides)
    return base


def blocked_intent() -> Dict[str, Any]:
    return _intent(quota_blocked=True)


def finalize_intent(result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """11 類以外不進來源。地區不在八個裡，或沒說地區，就定為全球。"""
    data = result if isinstance(result, dict) else {}
    category = normalize_category(data.get("category"))
    if category is None:
        return _intent(out_of_catalog=True)
    region = normalize_region(data.get("region"))
    if region is None:
        region = "global"
        region_defaulted = True
    else:
        region_defaulted = bool(data.get("region_defaulted")) and region == "global"
    return _intent(
        category=category,
        region=region,
        keywords=_keywords(data.get("keywords")),
        confidence=0.9,
        clarification_needed=False,
        region_defaulted=region_defaulted,
        split_channel=bool(data.get("split_channel")),
    )

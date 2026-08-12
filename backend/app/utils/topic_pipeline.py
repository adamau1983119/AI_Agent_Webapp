"""v8 主題卡世代：軟切換過濾（MD-M2 ≤150）。"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, Optional
from zoneinfo import ZoneInfo

_HKT = ZoneInfo("Asia/Hong_Kong")


def current_topic_pipeline_version() -> int:
    try:
        return max(1, int(os.getenv("TOPIC_PIPELINE_VERSION", "8")))
    except ValueError:
        return 8


def stamp_pipeline_fields(topic_data: Dict[str, Any]) -> Dict[str, Any]:
    """產卡時寫入世代標記。"""
    topic_data["pipeline_version"] = current_topic_pipeline_version()
    return topic_data


def _cutover_utc_naive() -> Optional[datetime]:
    """TOPIC_V8_CUTOVER_HKT=YYYY-MM-DD 或 YYYY-MM-DDTHH:MM（香港時間）。"""
    raw = (os.getenv("TOPIC_V8_CUTOVER_HKT") or "").strip()
    if not raw:
        return None
    try:
        if "T" in raw:
            local = datetime.fromisoformat(raw)
        else:
            local = datetime.strptime(raw[:10], "%Y-%m-%d")
        if local.tzinfo is None:
            local = local.replace(tzinfo=_HKT)
        return local.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    except ValueError:
        return None


def list_topics_generation_filter(*, include_legacy: bool = False) -> Dict[str, Any]:
    """預設只顯示 v8 世代卡；include_legacy 則不過濾。"""
    if include_legacy:
        return {}
    ver = current_topic_pipeline_version()
    cutover = _cutover_utc_naive()
    clauses = [{"pipeline_version": {"$gte": ver}}]
    if cutover is not None:
        clauses.append({"generated_at": {"$gte": cutover}})
    if len(clauses) == 1:
        return clauses[0]
    # 同時要求世代＋切換時刻（勿用 $or，否則 cutover 後未 stamp 舊卡會再擋滿額）
    return {"$and": clauses}

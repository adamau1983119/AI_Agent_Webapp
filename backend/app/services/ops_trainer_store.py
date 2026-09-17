"""Mongo store for style trainer exemplars (isolated collection)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.database import get_database

COLL = "style_trainer_exemplars"
DOMAINS = ("fashion", "food", "trend")
LENGTHS = ("short", "long")
PER_CELL = 3
TARGET = len(DOMAINS) * len(LENGTHS) * PER_CELL  # 18


async def _col():
    db = await get_database()
    return db[COLL]


async def insert_published(doc: Dict[str, Any]) -> str:
    col = await _col()
    now = datetime.now(timezone.utc)
    payload = {
        **doc,
        "status": "published",
        "created_at": now,
        "updated_at": now,
    }
    res = await col.insert_one(payload)
    return str(res.inserted_id)


async def coverage_for_language(language: str) -> Dict[str, Any]:
    col = await _col()
    filled_cells = 0
    for domain in DOMAINS:
        for length in LENGTHS:
            n = await col.count_documents(
                {
                    "status": "published",
                    "ref_type": "positive",
                    "language": language,
                    "domain": domain,
                    "length_bucket": length,
                }
            )
            if n >= PER_CELL:
                filled_cells += 1
    # filled count as exemplars toward 18: each full cell = 3
    filled = filled_cells * PER_CELL
    mode = "B" if filled_cells == len(DOMAINS) * len(LENGTHS) else "A"
    return {
        "language": language,
        "filled": filled,
        "target": TARGET,
        "mode": mode,
    }


async def coverage_all() -> List[Dict[str, Any]]:
    out = []
    for lang in ("zh-TW", "en", "ja"):
        out.append(await coverage_for_language(lang))
    return out


async def fetch_fewshot(
    *,
    language: str,
    domain: str,
    length_bucket: str,
    write_profile: str,
    limit_pos: int = 3,
    limit_neg: int = 1,
) -> Dict[str, List[Dict[str, Any]]]:
    col = await _col()
    base = {
        "status": "published",
        "language": language,
        "domain": domain,
        "length_bucket": length_bucket,
        "write_profile": write_profile,
    }
    pos = (
        await col.find({**base, "ref_type": "positive"})
        .sort("created_at", -1)
        .limit(limit_pos)
        .to_list(length=limit_pos)
    )
    neg = (
        await col.find({**base, "ref_type": "negative"})
        .sort("created_at", -1)
        .limit(limit_neg)
        .to_list(length=limit_neg)
    )
    return {"positive": pos, "negative": neg}


def cell_ready(language_cov: Dict[str, Any]) -> bool:
    return language_cov.get("mode") == "B"

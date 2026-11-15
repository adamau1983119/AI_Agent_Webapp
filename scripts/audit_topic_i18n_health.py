#!/usr/bin/env python3
"""唯讀掃 Mongo 主題卡 titles_i18n／source_content_i18n（規則17；MD-M2≤150）。

不改庫／不觸發翻譯／不改前端按鈕 i18n。複用 topic_languages。
用法: cd backend && python ../scripts/audit_topic_i18n_health.py [--days N] [--id TID]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))
LANGS = ("zh-TW", "en", "ja")
CHROME = (
    "view this post on instagram",
    "a post shared by",
    "follow us on instagram",
    "share this post",
)


def _ok(text: str, lang: str) -> bool:
    from app.utils.topic_languages import usable_cached_title

    return usable_cached_title((text or "")[:500], lang) is not None


def _chrome(text: str) -> bool:
    low = (text or "").lower()
    return any(s in low for s in CHROME)


def _flags(doc: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    titles, src = dict(doc.get("titles_i18n") or {}), dict(doc.get("source_content_i18n") or {})
    for lang in LANGS:
        t, s = (titles.get(lang) or "").strip(), (src.get(lang) or "").strip()
        if not t:
            out.append(f"TITLE_{lang}_MISSING")
        elif not _ok(t, lang):
            out.append(f"TITLE_{lang}_SCRIPT_FAIL")
        if not s:
            out.append(f"SRC_{lang}_MISSING")
        elif not _ok(s, lang):
            out.append(f"SRC_{lang}_SCRIPT_FAIL")
    if _chrome((src.get("zh-TW") or "").strip()):
        out.append("SRC_ZH_EN_CHROME")
    sources = doc.get("sources") or []
    oc = ""
    if sources and isinstance(sources[0], dict):
        oc = sources[0].get("content_clean") or sources[0].get("original_content") or ""
    if _chrome(oc):
        out.append("ORIG_EN_CHROME")
    return out


async def _run(*, days: Optional[int], topic_id: Optional[str]) -> int:
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()
    q: Dict[str, Any] = {"hidden": {"$ne": True}}
    if days and days > 0:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        q["generated_at"] = {"$gte": since.replace(tzinfo=None)}
    proj = {
        "id": 1, "category": 1, "generated_at": 1, "titles_i18n": 1,
        "source_content_i18n": 1, "sources": 1,
    }
    rows = await db.topics.find(q, proj).to_list(5000)
    if topic_id and not any(r.get("id") == topic_id for r in rows):
        extra = await db.topics.find_one({"id": topic_id}, proj)
        if extra:
            rows.append(extra)
    counts: Counter = Counter()
    bad_ids: List[Dict[str, Any]] = []
    sample: Optional[Dict[str, Any]] = None
    for doc in rows:
        tid, flags = str(doc.get("id") or ""), _flags(doc)
        if flags:
            counts.update(flags)
            bad_ids.append({
                "id": tid, "category": doc.get("category"),
                "generated_at": str(doc.get("generated_at") or ""), "flags": flags,
            })
        if topic_id and tid == topic_id:
            src = dict(doc.get("source_content_i18n") or {})
            sample = {
                "id": tid, "flags": flags,
                "titles_i18n_keys": list((doc.get("titles_i18n") or {}).keys()),
                "source_keys": list(src.keys()),
                "src_preview": {k: (src.get(k) or "")[:120] for k in LANGS},
            }
    total, bad_n = len(rows), len(bad_ids)
    ja_body = sum(1 for b in bad_ids if any(f.startswith("SRC_ja_") for f in b["flags"]))
    zh_chrome = sum(1 for b in bad_ids if "SRC_ZH_EN_CHROME" in b["flags"])
    report = {
        "scanned": total, "bad": bad_n,
        "bad_rate": round(bad_n / total, 4) if total else 0,
        "ja_body_fail": ja_body, "zh_en_chrome": zh_chrome,
        "flag_counts": dict(counts), "sample": sample, "bad_ids": bad_ids[:200],
    }
    out_dir = ROOT / "docs" / "evidence" / "v8" / "2026-11-16"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "topic_i18n_health.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== topic i18n health (read-only) ===")
    print(f"scanned={total} bad={bad_n} rate={report['bad_rate']}")
    print(f"ja_body_fail={ja_body} zh_en_chrome={zh_chrome}")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    if sample:
        print("--- sample ---")
        print(json.dumps(sample, ensure_ascii=False, indent=2))
    print(f"evidence: {path}")
    await close_mongo_connection()
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=0, help="0=all visible")
    p.add_argument("--id", default="topic_fashion_20261115160206_2")
    a = p.parse_args()
    return asyncio.run(_run(days=a.days or None, topic_id=a.id or None))


if __name__ == "__main__":
    raise SystemExit(main())

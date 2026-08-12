#!/usr/bin/env python3
"""清除 titles_i18n／topic_translations 內 [Fallback-] 假譯文（MD-M2 ≤150）。

用法（backend venv）：
  cd backend && python ../scripts/clear_fallback_titles_i18n.py --dry-run
  python ../scripts/clear_fallback_titles_i18n.py --apply
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


async def _run(*, apply: bool) -> int:
    from app.database import get_database

    db = await get_database()
    topics = db["topics"]
    trans = db["topic_translations"]
    touched = cleaned_keys = 0
    async for doc in topics.find({"titles_i18n": {"$exists": True}}):
        i18n = dict(doc.get("titles_i18n") or {})
        new_i18n = {
            k: v
            for k, v in i18n.items()
            if not str(v or "").strip().startswith("[Fallback")
        }
        if new_i18n == i18n:
            continue
        touched += 1
        cleaned_keys += len(i18n) - len(new_i18n)
        if apply:
            await topics.update_one(
                {"_id": doc["_id"]}, {"$set": {"titles_i18n": new_i18n}}
            )
    fb = {"cached_title": {"$regex": r"^\[Fallback"}}
    n_trans = await trans.count_documents(fb)
    if apply and n_trans:
        await trans.delete_many(fb)
    print(
        f"{'APPLY' if apply else 'DRY'}: topics_patched={touched} "
        f"keys_removed={cleaned_keys} trans_fallback={n_trans}"
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    apply = bool(args.apply) and not args.dry_run
    return asyncio.run(_run(apply=apply))


if __name__ == "__main__":
    raise SystemExit(main())

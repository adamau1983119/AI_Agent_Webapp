#!/usr/bin/env python3
"""Hide bad topic cards in Mongo (no delete; MD-M2 ≤150).

Usage (backend on PYTHONPATH):
  python scripts/hide_topics.py --ids topic_food_xxx,topic_trend_yyy --reason wrong_images
  python scripts/hide_topics.py --ids topic_a --unhide

Requires MONGODB_URL. Does not call LLM. Docs stay in DB until retention cleanup.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


async def _run(ids: list[str], *, hidden: bool, reason: str) -> int:
    from app.database import get_database
    from app.services.repositories.topic_repository import TopicRepository

    db = await get_database()
    repo = TopicRepository(db=db)
    n = await repo.set_topics_hidden(ids, hidden=hidden, reason=reason)
    print(f"{'hidden' if hidden else 'unhidden'} modified={n} ids={ids}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Hide/unhide topic cards without delete")
    p.add_argument("--ids", required=True, help="Comma-separated topic ids")
    p.add_argument("--reason", default="ops_hide", help="Short reason on doc")
    p.add_argument("--unhide", action="store_true", help="Clear hidden flag")
    args = p.parse_args()
    ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    if not ids:
        print("no topic ids", file=sys.stderr)
        return 1
    return asyncio.run(_run(ids, hidden=not args.unhide, reason=args.reason))


if __name__ == "__main__":
    raise SystemExit(main())

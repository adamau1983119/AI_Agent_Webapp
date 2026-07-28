#!/usr/bin/env python3
"""PF-B static checks (A-track · program segment · not CD-B/E0 screenshots)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEM = ROOT / "backend/app/services/public_feed/item_builder.py"
MAPPER = ROOT / "backend/app/services/public_feed/feed_card_mapper.py"
LOADER = ROOT / "backend/app/services/public_feed/feed_translation_loader.py"
PUBLIC = ROOT / "backend/app/api/v1/public_topics.py"
CACHE = ROOT / "backend/app/services/public_feed/public_feed_cache.py"
SCHEDULER = ROOT / "backend/app/services/automation/scheduler.py"


def main() -> int:
    fails = 0
    item = ITEM.read_text(encoding="utf-8")
    mapper = MAPPER.read_text(encoding="utf-8")
    loader = LOADER.read_text(encoding="utf-8")
    public = PUBLIC.read_text(encoding="utf-8")
    cache = CACHE.read_text(encoding="utf-8")
    sched = SCHEDULER.read_text(encoding="utf-8") if SCHEDULER.exists() else ""

    checks: list[tuple[str, bool, str]] = [
        ("PD-B-01 item_builder upsert topic_translations", "upsert_translation" in item and "TranslationType.STANDARD" in item, ""),
        ("PD-B-01 zh-TW + ja batch langs", '"zh-TW"' in item and '"ja"' in item, ""),
        ("PD-B-02 feed_translation_loader exists", LOADER.exists() and "load_standard_titles" in loader, ""),
        ("PD-B-02 mapper prefers translation_titles", "_resolve_title" in mapper and "translation_titles" in mapper, ""),
        ("PD-B-02 topics_to_feed_cards_async", "topics_to_feed_cards_async" in mapper, ""),
        ("PD-B-02 public_topics uses async mapper", "topics_to_feed_cards_async" in public, ""),
        ("PD-B-02 cache refresh uses async mapper", "topics_to_feed_cards_async" in cache, ""),
        ("PD-B-03 summary_flash in mapper", "summary_flash" in mapper, ""),
        ("PD-B-03 read path no generate_summary", "generate_summary_flash" not in public and "generate_summary_flash" not in mapper, ""),
        ("CD-M-2 no trend_alert scheduler job", "trend_alert" not in sched.lower(), "grep scheduler"),
    ]

    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{status} | {name}{extra}")

    total = len(checks)
    print(f"---\n{total - fails}/{total} checks passed")
    print("NOTE: PD-B checklist [x] needs check_pf_b_mongo.py after run_public_feed_batch.")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Static checks for fluent topic i18n atoms (≤150-line modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
MAX = 150
FILES = [
    BACKEND / "app/services/automation/title_lang_detect.py",
    BACKEND / "app/services/automation/topic_i18n_prefetch.py",
]


def main() -> int:
    fails = 0
    sys.path.insert(0, str(BACKEND))
    for path in FILES:
        n = len(path.read_text(encoding="utf-8").splitlines())
        ok = path.is_file() and n <= MAX
        print(f"{'PASS' if ok else 'FAIL'} | {path.name} lines={n}")
        fails += 0 if ok else 1

    from app.services.automation.title_lang_detect import (
        detect_title_language,
        resolve_stored_display_language,
    )

    assert detect_title_language("今日旺角美食") == "zh-TW"
    assert detect_title_language("Hello fashion week runway") == "en"
    assert (
        resolve_stored_display_language(
            source_title="今日旺角美食",
            stored_title="今日旺角美食",
            requested_lang="en",
            translation_applied=False,
        )
        == "zh-TW"
    )
    print("PASS | detect + no false en tag")

    dash = (ROOT / "frontend/src/pages/Dashboard.tsx").read_text(encoding="utf-8")
    if "topicsSectionLoading" not in dash:
        print("FAIL | Dashboard missing topicsSectionLoading")
        fails += 1
    else:
        print("PASS | Dashboard topicsSectionLoading")

    disp = (ROOT / "frontend/src/lib/topicDisplay.ts").read_text(encoding="utf-8")
    if "titles[ui]" not in disp or "descriptions[ui]" not in disp:
        print("FAIL | topicDisplay must prefer titles/descriptions[ui]")
        fails += 1
    else:
        print("PASS | topicDisplay titles+descriptions[ui]")

    if "_finalize_topics_i18n" not in (
        ROOT / "backend/app/services/automation/topic_collector.py"
    ).read_text(encoding="utf-8"):
        print("FAIL | collector missing _finalize_topics_i18n")
        fails += 1
    else:
        print("PASS | collector finalize after dedup")

    ch = (ROOT / "backend/app/services/channel_collector.py").read_text(encoding="utf-8")
    if "finalize_topic_languages" not in ch:
        print("FAIL | channel_collector must finalize i18n")
        fails += 1
    else:
        print("PASS | channel_collector finalize")

    pref = (BACKEND / "app/services/automation/topic_i18n_prefetch.py").read_text(
        encoding="utf-8"
    )
    if "description_i18n" not in pref:
        print("FAIL | prefetch must write description_i18n")
        fails += 1
    else:
        print("PASS | prefetch description_i18n")

    if fails:
        print(f"FAIL | {fails}")
        return 1
    print("PASS | topic fluent i18n static OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

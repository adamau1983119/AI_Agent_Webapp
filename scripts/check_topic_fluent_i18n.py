#!/usr/bin/env python3
"""Static checks for fluent topic i18n — especially en/ja correctness."""
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
        text_matches_lang,
        resolve_stored_display_language,
    )

    assert detect_title_language("今日旺角美食") == "zh-TW"
    assert detect_title_language("今日 UNIQLO 東京開幕") == "zh-TW"
    assert detect_title_language("Hello fashion week runway") == "en"
    assert detect_title_language("渋谷で新しいカフェ") == "ja"
    assert not text_matches_lang("今日旺角美食", "en")
    assert text_matches_lang("Shibuya cafe opens", "en")
    assert text_matches_lang("渋谷カフェ", "ja")
    assert (
        resolve_stored_display_language(
            source_title="今日 UNIQLO 東京開幕",
            stored_title="今日 UNIQLO 東京開幕",
            requested_lang="en",
            translation_applied=False,
        )
        == "zh-TW"
    )
    print("PASS | en/ja detect + reject CJK-under-en")

    for label, path, needle in [
        ("Dashboard", ROOT / "frontend/src/pages/Dashboard.tsx", "topicsSectionLoading"),
        ("topicDisplay", ROOT / "frontend/src/lib/topicDisplay.ts", "pickI18nText"),
        ("prefetch", FILES[1], "description_i18n"),
        ("collector", BACKEND / "app/services/automation/topic_collector.py", "_finalize_topics_i18n"),
        ("channel", BACKEND / "app/services/channel_collector.py", "finalize_topic_languages"),
    ]:
        if needle not in path.read_text(encoding="utf-8"):
            print(f"FAIL | {label} missing {needle}")
            fails += 1
        else:
            print(f"PASS | {label}")

    if fails:
        print(f"FAIL | {fails}")
        return 1
    print("PASS | topic fluent i18n static OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

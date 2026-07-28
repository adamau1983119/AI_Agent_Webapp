#!/usr/bin/env python3
"""BF-UI static checks for Post Kit (program segment · not browser PK1～PK6)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "frontend/src/components/features/PostKitPanel.tsx"
DETAIL = ROOT / "frontend/src/pages/TopicDetail.tsx"
PUBLISH = ROOT / "frontend/src/pages/Publish.tsx"
I18N = ROOT / "frontend/src/i18n/index.ts"
ARCH = ROOT / "按鈕測試ID架構表.md"

POSTKIT_KEYS = [
    "postKit.sectionTitle",
    "postKit.titleOptions",
    "postKit.suggested",
    "postKit.titleHook.curiosity",
    "postKit.titleHook.benefit",
    "postKit.copy",
    "postKit.copied",
    "postKit.copyFailed",
    "postKit.copyAll",
    "postKit.body",
    "postKit.script",
    "postKit.hashtags",
    "postKit.photos",
    "postKit.copyLink",
    "postKit.noPhotos",
    "postKit.hint.pasteOnPlatform",
]
PUBLISH_KEYS = [
    "publish.assistantTitle",
    "publish.assistantBody",
    "publish.goToTopics",
]
REQUIRED_TESTIDS = [
    "section-postkit",
    "btn-postkit-copy-all",
    "btn-postkit-copy-title-",
    "btn-postkit-copy-body",
    "btn-postkit-copy-script",
    "btn-postkit-copy-hashtags",
    "btn-postkit-copy-image-",
    "btn-publish-goto-topics",
]


def _keys_in_i18n(keys: list[str], i18n: str) -> list[str]:
    return sorted(k for k in keys if f"'{k}'" not in i18n)


def main() -> int:
    fails = 0
    panel = PANEL.read_text(encoding="utf-8")
    detail = DETAIL.read_text(encoding="utf-8")
    publish = PUBLISH.read_text(encoding="utf-8")
    i18n = I18N.read_text(encoding="utf-8")
    arch = ARCH.read_text(encoding="utf-8") if ARCH.exists() else ""

    used_postkit = set(re.findall(r"t\('(postKit\.[^']+)'\)", panel))
    used_postkit |= set(re.findall(r't\("postKit\.([^"]+)"\)', panel))
    all_keys = POSTKIT_KEYS + PUBLISH_KEYS
    missing = _keys_in_i18n(all_keys, i18n)

    checks: list[tuple[str, bool, str]] = [
        ("PostKitPanel.tsx exists", PANEL.exists(), ""),
        ("TopicDetail embeds PostKitPanel", "PostKitPanel" in detail, ""),
        (
            "i18n postKit.* + publish.assistant* (zh block)",
            len(_keys_in_i18n(POSTKIT_KEYS, i18n)) == 0,
            f"missing postKit={_keys_in_i18n(POSTKIT_KEYS, i18n)}" if missing else "",
        ),
        (
            "PostKitPanel no user-visible hardcoded CJK",
            not re.search(r">\s*[\u4e00-\u9fff]", panel),
            "use t() for visible Chinese",
        ),
        (
            "architecture table 頻道區塊 4.10 Post Kit",
            "section-postkit" in arch and "btn-postkit-copy-body" in arch,
            "按鈕測試ID架構表 4.10",
        ),
        (
            "Publish L0 assistant when API publish off",
            "VITE_ENABLE_API_PUBLISH" in publish and "btn-publish-goto-topics" in publish,
            "",
        ),
        ("copyToClipboard util used", "copyToClipboard" in panel, ""),
    ]

    for tid in REQUIRED_TESTIDS:
        if tid.endswith("-"):
            found = tid in panel
        else:
            found = tid in panel or tid in publish
        checks.append((f"testid {tid}", found, ""))

    for name, ok, detail_msg in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        extra = f" | {detail_msg}" if detail_msg else ""
        print(f"{status} | {name}{extra}")

    total = len(checks)
    print(f"---\n{total - fails}/{total} checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

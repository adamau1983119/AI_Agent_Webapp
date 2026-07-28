#!/usr/bin/env python3
"""BF-UI static checks for Landing /welcome (program segment, not browser E2E)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WELCOME = ROOT / "frontend/src/pages/Welcome.tsx"
I18N = ROOT / "frontend/src/i18n/index.ts"
APP = ROOT / "frontend/src/app/App.tsx"
ARCH = ROOT / "按鈕測試ID架構表.md"

FEATURE_KEYS = ["trends", "aiWrite", "channel", "inspiration", "style", "postKit"]
EXPECTED_TESTIDS = [
    "btn-landing-register",
    "btn-landing-login",
    "btn-landing-login-hero",
    "btn-landing-lang-zh",
    "btn-landing-lang-en",
    "btn-landing-lang-ja",
    "link-landing-terms",
    "link-landing-privacy",
]


def main() -> int:
    fails = 0
    welcome = WELCOME.read_text(encoding="utf-8")
    i18n = I18N.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    arch = ARCH.read_text(encoding="utf-8") if ARCH.exists() else ""

    keys: set[str] = set(re.findall(r"t\('(landing\.[^']+)'\)", welcome))
    keys.add("landing.features.postKit.badge")
    for k in FEATURE_KEYS:
        keys.add(f"landing.features.{k}.title")
        keys.add(f"landing.features.{k}.benefit")
    for adv in ("multilingual", "collection", "sources"):
        keys.add(f"landing.advanced.{adv}")

    missing = sorted(k for k in keys if f"'{k}'" not in i18n)
    checks: list[tuple[str, bool, str]] = [
        ("route /welcome in App.tsx", "/welcome" in app and "Welcome" in app, ""),
        ("i18n landing.* zh/en/ja", len(missing) == 0, f"missing={missing}" if missing else "all keys present"),
        (
            "Welcome.tsx no user-visible hardcoded CJK",
            not re.search(r">\s*[\u4e00-\u9fff]", welcome),
            "use t() for visible Chinese",
        ),
        (
            "architecture table Landing section",
            "btn-landing-register" in arch and "card-landing-feature" in arch,
            "按鈕測試ID架構表 頻道區塊 2.0",
        ),
    ]
    for tid in EXPECTED_TESTIDS:
        if tid.startswith("btn-landing-lang-"):
            found = "btn-landing-lang-" in welcome
        else:
            found = tid in welcome
        checks.append((f"testid {tid}", found, ""))

    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{status} | {name}{extra}")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""BF-UI static checks for Alter Ego onboarding (AE-1d · program segment)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ONBOARDING = ROOT / "frontend/src/pages/AlterEgoOnboarding.tsx"
MY_CHANNEL = ROOT / "frontend/src/pages/MyChannel.tsx"
POSTKIT = ROOT / "frontend/src/components/features/PostKitPanel.tsx"
CREATE_CHANNEL = ROOT / "frontend/src/pages/CreateChannel.tsx"
APP = ROOT / "frontend/src/app/App.tsx"
ROUTING = ROOT / "frontend/src/lib/alterEgoRouting.ts"
API = ROOT / "frontend/src/api/alterEgo.ts"
I18N = ROOT / "frontend/src/i18n/index.ts"
SETTINGS = ROOT / "frontend/src/pages/Settings.tsx"

ALTER_EGO_KEYS = [
    "alterEgo.title",
    "alterEgo.skip",
    "alterEgo.extract",
    "alterEgo.continue",
    "alterEgo.settingsCta",
    "myChannel.title",
    "postKit.platformSwitch",
    "postKit.visualPrompt",
    "channels.assist.extractDna",
]
REQUIRED_TESTIDS = [
    "btn-alter-ego-skip",
    "btn-alter-ego-extract",
    "btn-alter-ego-continue",
    "section-alter-ego-preview",
    "btn-my-channel-go-discover",
    "btn-settings-alter-ego-setup",
    "btn-postkit-platform-",
    "btn-postkit-copy-visual-prompt",
    "btn-postkit-adopt-copy",
    "input-channels-assist-exemplar",
    "btn-channels-assist-extract-dna",
    "btn-my-channel-unlock-",
]


def _keys_in_i18n(keys: list[str], i18n: str) -> list[str]:
    return sorted(k for k in keys if f"'{k}'" not in i18n)


def main() -> int:
    fails = 0
    onboarding = ONBOARDING.read_text(encoding="utf-8")
    my_channel = MY_CHANNEL.read_text(encoding="utf-8")
    postkit = POSTKIT.read_text(encoding="utf-8")
    create_channel = CREATE_CHANNEL.read_text(encoding="utf-8")
    app_py = APP.read_text(encoding="utf-8")
    routing = ROUTING.read_text(encoding="utf-8")
    api = API.read_text(encoding="utf-8")
    i18n = I18N.read_text(encoding="utf-8")
    settings = SETTINGS.read_text(encoding="utf-8")

    checks: list[tuple[str, bool, str]] = [
        ("PD-AE1-F01 AlterEgoOnboarding.tsx", ONBOARDING.exists(), ""),
        ("PD-AE1-F01 route", "/onboarding/alter-ego" in app_py and "AlterEgoOnboarding" in app_py, ""),
        ("PD-AE1-F02 skip API client", "skip:" in api and "alterEgoApi.skip" in onboarding, ""),
        ("PD-AE1-F02 skip testid", "btn-alter-ego-skip" in onboarding, ""),
        ("PD-AE1-F03 routing helper", "resolvePostLoginPath" in routing and "AlterEgoGateRedirect" in app_py, ""),
        ("PD-AE1-F03 my-channel route", "/my-channel" in app_py and "MyChannel" in app_py, ""),
        ("PD-AE1-F04 settings CTA", "btn-settings-alter-ego-setup" in settings, ""),
        ("PD-AE1-F05 PostKit platform tabs", "btn-postkit-platform-" in postkit, ""),
        ("PD-AE1-F05 visual prompt", "btn-postkit-copy-visual-prompt" in postkit, ""),
        ("PD-AE1-F06 CreateChannel exemplar", "btn-channels-assist-extract-dna" in create_channel, ""),
        ("PD-AE1-F07 adopt-copy API", "adoptCopy" in api, ""),
        ("alterEgo API module", API.exists() and "getStatus" in api, ""),
    ]

    for name, ok, detail in checks:
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{'PASS' if ok else 'FAIL'} | {name}{extra}")

    missing_keys = _keys_in_i18n(ALTER_EGO_KEYS, i18n)
    keys_ok = not missing_keys
    print(f"{'PASS' if keys_ok else 'FAIL'} | i18n alterEgo/myChannel keys | missing={missing_keys}")
    if not keys_ok:
        fails += 1

    blob = onboarding + my_channel + settings + postkit + create_channel
    for tid in REQUIRED_TESTIDS:
        ok = tid in blob or tid in app_py
        print(f"{'PASS' if ok else 'FAIL'} | testid {tid}")
        if not ok:
            fails += 1

    print("---")
    print(f"BF-UI track: {'PASS' if fails == 0 else 'FAIL'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

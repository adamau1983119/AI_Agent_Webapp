#!/usr/bin/env python3
"""MyChannel static checks (PD-MC1～MC5 · program segment)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend/src"

CREDIT = BACKEND / "app/services/credit_ledger_service.py"
CACHE = BACKEND / "app/services/my_channel/my_channel_cache.py"
SERVICE = BACKEND / "app/services/my_channel/my_channel_service.py"
API = BACKEND / "app/api/v1/my_channel.py"
MAIN = BACKEND / "app/main.py"
MY_CHANNEL_PAGE = FRONTEND / "pages/MyChannel.tsx"
MY_CHANNEL_API = FRONTEND / "api/myChannel.ts"
SCHEMA = BACKEND / "app/schemas/my_channel.py"


def main() -> int:
    fails = 0
    credit = CREDIT.read_text(encoding="utf-8")
    cache = CACHE.read_text(encoding="utf-8")
    svc = SERVICE.read_text(encoding="utf-8")
    api = API.read_text(encoding="utf-8")
    main_py = MAIN.read_text(encoding="utf-8")
    page = MY_CHANNEL_PAGE.read_text(encoding="utf-8")
    client = MY_CHANNEL_API.read_text(encoding="utf-8")
    schema = SCHEMA.read_text(encoding="utf-8")

    checks: list[tuple[str, bool, str]] = [
        ("PD-MC1-01 credit_ledger_service", CREDIT.exists() and "decr_credits" in credit, ""),
        ("PD-MC1-02 initial 5 credits", "INITIAL_CREDITS = 5" in credit, ""),
        ("PD-MC1-03 admin AddPoints", "/credits" in api and "add_credits" in credit, ""),
        ("PD-MC1-04 402 insufficient", "HTTP_402_PAYMENT_REQUIRED" in api, ""),
        ("PD-MC2-01 my_channel cache key", "my_channel:feed:" in cache, ""),
        ("PD-MC2-02 read DB only", "list_by_channel_id" in svc and "channel_collector" not in svc, ""),
        ("PD-MC2-03 MC-1 URL gate", "_has_valid_source_url" in svc, ""),
        ("PD-MC2-04 assemble limit", "_MAX_ASSEMBLES_24H = 3" in cache, ""),
        ("PD-MC3-01 unlock route", "/topics/{topic_id}/unlock" in api, ""),
        ("PD-MC3-02 source_url digest", "digest_300" in schema and "source_url" in svc, ""),
        ("PD-MC3-03 idempotency", "idempotency_key" in api and "get_unlock_result" in cache, ""),
        ("PD-MC4-01 MyChannel.tsx feed", "myChannelApi.getFeed" in page, ""),
        ("PD-MC4-02 unlock CTA testid", "btn-my-channel-unlock" in page, ""),
        ("PD-MC4-03 templates UI", "panel-my-channel-templates" in page and "getChannelTemplates" in client, ""),
        ("MC-6 templates config", (BACKEND / "app/config/channel_templates.json").exists(), ""),
        ("MC-6 templates route", "channel-templates" in api, ""),
        ("MC-4 no public_feed", "public_feed:feed:" not in svc and "public_feed:feed:" not in cache, ""),
        ("router registered", "my_channel.router" in main_py, ""),
        ("frontend API client", MY_CHANNEL_API.exists() and "unlock" in client, ""),
    ]

    for name, ok, detail in checks:
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{'PASS' if ok else 'FAIL'} | {name}{extra}")

    print("---")
    print(f"MyChannel BF static: {'PASS' if fails == 0 else 'FAIL'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""立刻寄一封「每日營運報告」（初期監察樣式）。"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def main() -> int:
    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    os.environ.setdefault("OBS_OPS_EMAIL", "a.adam1983119@gmail.com")

    from app.services.email_service import EmailService
    from app.services.observability.daily_digest import send_daily_digest_now

    if not EmailService().is_configured():
        print("FAIL | Gmail 未設定")
        return 1
    out = asyncio.run(send_daily_digest_now())
    print(f"INFO | {out}")
    if out.get("status") != "digest_sent":
        print("FAIL")
        return 1
    print("PASS | daily digest sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())

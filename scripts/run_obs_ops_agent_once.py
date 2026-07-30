#!/usr/bin/env python3
"""
啟動後台 Observability Ops Agent 一次（真實 /health → emit → 電郵）。

  python scripts/run_obs_ops_agent_once.py
"""
from __future__ import annotations

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

    # 本次執行開通 Agent 寄信（不寫入 .env；不影響未設旗標的正式站）
    os.environ["OBS_ALERTING_ENABLED"] = "true"
    os.environ["OBS_ALERT_COST"] = "true"
    os.environ["OBS_ALERT_CRASH"] = "true"
    os.environ["OBS_ALERT_EMAIL_SEND"] = "true"
    os.environ.setdefault("OBS_OPS_EMAIL", "a.adam1983119@gmail.com")

    from app.services.email_service import EmailService
    from app.services.observability.ops_agent import run_ops_agent_once

    if not EmailService().is_configured():
        print("FAIL | Gmail SMTP 未設定")
        return 1

    out = run_ops_agent_once()
    print(f"INFO | channel={out.get('channel')} title={out.get('title')}")
    print(f"INFO | detail={out.get('detail')}")
    print(f"INFO | status={out.get('status')} to={out.get('ops_email')}")
    if out.get("status") not in ("email_sent", "email_queued", "logged"):
        # email_sent 為成功；logged 表示未開 EMAIL_SEND
        if out.get("status") == "email_failed":
            print("FAIL | email_failed")
            return 1
        if out.get("status") == "skipped":
            print("FAIL | skipped — 開關未開")
            return 1
    if out.get("status") in ("email_sent", "email_queued"):
        print("PASS | Ops Agent 已依真實狀態寄出電郵")
        return 0
    print(f"FAIL | unexpected status={out.get('status')!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

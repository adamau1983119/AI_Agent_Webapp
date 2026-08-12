#!/usr/bin/env python3
"""
Email process double-check（主題卡姊妹核心：每日監察電郵）。

驗：設定 → 雙主旨組信 → health → digest 真寄一封（可 --dry-run）。

  python scripts/check_email_process_double.py
  python scripts/check_email_process_double.py --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def _step(ok: bool, name: str, detail: str = "") -> bool:
    mark = "PASS" if ok else "FAIL"
    suffix = f" | {detail}" if detail else ""
    print(f"{mark} | {name}{suffix}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只組信／驗設定，不呼叫 Resend",
    )
    args = parser.parse_args()

    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    os.environ.setdefault("OBS_OPS_EMAIL", "a.adam1983119@gmail.com")

    fails = 0

    # 1) 設定
    from app.services.email_service import EmailService
    from app.services.observability.channels import ops_email

    svc = EmailService()
    to = ops_email()
    has_resend = bool((svc.resend_api_key or "").strip())
    configured = svc.is_configured()
    if not _step(configured, "email_configured", "resend" if has_resend else "smtp"):
        fails += 1
    if not _step(bool(to and "@" in to), "ops_email", to):
        fails += 1
    from_hdr = svc._from_header()
    _step(bool(from_hdr), "from_header", from_hdr[:48])

    # 2) 雙主旨組信（不寄）
    from app.services.observability.alert_mailer import build_zh_email
    from app.services.observability.channels import AlertChannel

    sub_d, html_d, text_d = build_zh_email(
        AlertChannel.COST,
        "每日基本檢查 2026-08-12",
        detail="double-check dry",
        extra={"report_type": "daily_digest", "traffic_light": "green"},
    )
    if not _step(
        "[每日基本檢查]" in sub_d and "即時告警" not in sub_d,
        "digest_subject",
        sub_d,
    ):
        fails += 1
    if not _step("信種：每日基本檢查" in text_d, "digest_body_kind"):
        fails += 1

    sub_a, _, text_a = build_zh_email(
        AlertChannel.CRASH,
        "模擬崩潰",
        detail="double-check alert",
        extra={"traffic_light": "red"},
    )
    if not _step(
        "[即時告警]" in sub_a and "每日基本檢查" not in sub_a,
        "alert_subject",
        sub_a,
    ):
        fails += 1
    if not _step("信種：即時告警" in text_a, "alert_body_kind"):
        fails += 1

    # 3) digest 模組護欄（產卡摘要不可擋寄）
    import app.services.observability.daily_digest as dd

    if not _step(
        "永不拋出" in (dd.topics_hkt_summary.__doc__ or "")
        or "永不拋出"
        in __import__(
            "app.services.observability.digest_topics", fromlist=["topics_hkt_summary"]
        ).topics_hkt_summary.__doc__,
        "digest_summary_never_blocks",
    ):
        fails += 1

    # 4) health（digest 會打）
    from app.services.observability.ops_agent import DEFAULT_HEALTH, fetch_health
    from app.services.observability.traffic_light import evaluate_health

    health_err = None
    body = None
    try:
        body = fetch_health(DEFAULT_HEALTH)
    except Exception as exc:  # noqa: BLE001
        health_err = str(exc)
    signal = evaluate_health(body, error=health_err)
    _step(
        True,
        "health_fetch",
        f"light={signal.light.value} url={DEFAULT_HEALTH} err={health_err or '-'}",
    )

    if args.dry_run:
        print("INFO | dry-run：略過 Resend 真寄")
        print("EMAIL_PROCESS_DOUBLE_CHECK_PASS" if fails == 0 else "EMAIL_PROCESS_DOUBLE_CHECK_FAIL")
        return 1 if fails else 0

    # 5) 真寄「每日基本檢查」一封（與 Watchdog 同路徑）
    if not configured:
        print("FAIL | 未設定寄信，無法真寄")
        return 1

    out = asyncio.run(dd.send_daily_digest_now())
    ok = out.get("status") == "digest_sent"
    if not _step(
        ok,
        "digest_live_send",
        f"status={out.get('status')} title={out.get('title')} light={out.get('traffic_light')}",
    ):
        fails += 1

    if fails:
        print("EMAIL_PROCESS_DOUBLE_CHECK_FAIL")
        return 1
    print("EMAIL_PROCESS_DOUBLE_CHECK_PASS")
    print("INFO | 請到信箱搜「每日基本檢查」確認主旨雙軌")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
真實測試：假設「明天 07:45 HKT」→ 應 too_early；
再假設「明天 08:00 HKT」→ 應寄出「每日基本檢查」（Resend 真寄）。

  python scripts/test_digest_at_745_then_800.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
_HKT = ZoneInfo("Asia/Hong_Kong")


def main() -> int:
    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))
    from dotenv import load_dotenv

    load_dotenv(BACKEND / ".env")
    os.environ["OBS_DAILY_DIGEST_ENABLED"] = "true"
    os.environ.setdefault("OBS_DAILY_DIGEST_HOUR_HKT", "8")
    os.environ.setdefault("OBS_OPS_EMAIL", "a.adam1983119@gmail.com")

    from app.services.email_service import EmailService
    import app.services.observability.daily_digest as dd

    if not EmailService().is_configured():
        print("FAIL | email not configured")
        return 1

    # 以「真實現在」推算「明天」HKT 日曆
    now_hkt = datetime.now(_HKT)
    tomorrow = (now_hkt + timedelta(days=1)).date()
    fake_745 = datetime(
        tomorrow.year, tomorrow.month, tomorrow.day, 7, 45, 0, tzinfo=_HKT
    )
    fake_800 = datetime(
        tomorrow.year, tomorrow.month, tomorrow.day, 8, 0, 0, tzinfo=_HKT
    )
    day_str = tomorrow.strftime("%Y-%m-%d")

    print(f"INFO | real_now_hkt={now_hkt.isoformat()}")
    print(f"INFO | simulated_tomorrow={day_str}")
    print(f"INFO | digest_hour_hkt={dd._digest_hour()}")
    print(f"INFO | step1_clock={fake_745.isoformat()} (expect too_early)")
    print(f"INFO | step2_clock={fake_800.isoformat()} (expect digest_sent)")

    # 清記憶體鎖，模擬「明天尚未寄過」
    dd._last_digest_day = ""

    class _FakeDateTime(datetime):
        """可控 now()；其餘行為與 datetime 相同。"""

        _frozen: datetime | None = None

        @classmethod
        def now(cls, tz=None):
            assert cls._frozen is not None
            if tz is None:
                return cls._frozen.replace(tzinfo=None)
            return cls._frozen.astimezone(tz)

    # --- Step 1: 07:45 → 不可寄 ---
    _FakeDateTime._frozen = fake_745
    with patch.object(dd, "datetime", _FakeDateTime):
        out_early = asyncio.run(dd.maybe_send_daily_digest())
    print(f"INFO | step1_result={out_early}")
    if out_early.get("status") != "too_early":
        print(f"FAIL | expected too_early at 07:45, got {out_early}")
        return 1
    print("PASS | 07:45 HKT → too_early（不會發電郵）")

    # --- Step 2: 08:00 → 真寄 ---
    dd._last_digest_day = ""
    _FakeDateTime._frozen = fake_800
    with patch.object(dd, "datetime", _FakeDateTime):
        out_send = asyncio.run(dd.maybe_send_daily_digest())
    print(f"INFO | step2_result={out_send}")
    if out_send.get("status") != "digest_sent":
        print(f"FAIL | expected digest_sent at 08:00, got {out_send}")
        return 1
    if out_send.get("day") != day_str:
        print(f"FAIL | day mismatch want={day_str} got={out_send.get('day')}")
        return 1
    if "每日基本檢查" not in str(out_send.get("title", "")):
        print(f"FAIL | title missing 每日基本檢查: {out_send.get('title')}")
        return 1

    print("PASS | 08:00 HKT → digest_sent（Resend 已寄）")
    print(f"PASS | title={out_send.get('title')} light={out_send.get('traffic_light')}")
    print("INFO | 請到 Gmail 搜「每日基本檢查」；主旨日期應為明天", day_str)
    print(
        "INFO | 正式域真實行為：07:45 不寄；過 08:00 後 Watchdog 下一 tick"
        "（最多約 5 分鐘內）才寄，故 15 分鐘後（08:00）理論上會收到。"
    )
    print("DIGEST_745_800_REAL_TEST_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

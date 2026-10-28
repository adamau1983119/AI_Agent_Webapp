"""Shared helpers for marketing_period_* scripts (HKT week, staff exclude)."""
from __future__ import annotations

import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
HKT = ZoneInfo("Asia/Hong_Kong")
SCHEMA_VERSION = 1
GEN_ACTIONS = ("ae_compose", "ae_compose_part")
SNAP_COL = "marketing_period_snapshots"
FX_USD_HKD = 7.8


def boot_backend() -> None:
    os.chdir(BACKEND)
    sys.path.insert(0, str(BACKEND))


def parse_ymd(s: str) -> date:
    return date.fromisoformat(s.strip())


def hkt_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    """Inclusive calendar dates in HKT → UTC-naive range for Mongo (store as HKT wall→UTC)."""
    start_hkt = datetime(start.year, start.month, start.day, 0, 0, 0, tzinfo=HKT)
    end_hkt = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=HKT)
    return start_hkt.astimezone(timezone.utc).replace(tzinfo=None), end_hkt.astimezone(
        timezone.utc
    ).replace(tzinfo=None)


def prev_week(start: date, end: date) -> tuple[date, date]:
    span = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=span - 1)
    return prev_start, prev_end


def staff_emails() -> set[str]:
    from app.services.staff_identity import staff_credit_emails

    return staff_credit_emails()


def is_external(email: str | None, staff: set[str]) -> bool:
    from app.services.staff_identity import norm_email

    e = norm_email(email)
    return bool(e) and e not in staff


def as_utc_naive(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    return None


def filter_external_users(users: Iterable[dict], staff: set[str]) -> list[dict]:
    return [u for u in users if is_external(u.get("email"), staff)]

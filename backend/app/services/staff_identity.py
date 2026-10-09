"""內部識別信箱與發文同事補點規則。不含登入帳號。"""
from __future__ import annotations

import os

MARKER_EMAIL = "adamau1983119@gmail.com"
MAIL_SINK = "a.adam1983119@gmail.com"
STAFF_REFILL = 60
STAFF_DAILY_TIMES = 10
STAFF_FLOOR = 60


def norm_email(email: str | None) -> str:
    return (email or "").strip().lower()


def is_marker_email(email: str | None) -> bool:
    return norm_email(email) == MARKER_EMAIL


def deliver_to(email: str) -> str:
    """識別信箱的信改寄到營運信箱，不建立該信箱的會員。"""
    if is_marker_email(email):
        return MAIL_SINK
    return email


def staff_credit_emails() -> set[str]:
    raw = os.environ.get("STAFF_CREDIT_EMAILS", MAIL_SINK)
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def is_staff_credit_email(email: str | None) -> bool:
    return norm_email(email) in staff_credit_emails()


def next_staff_refill(balance: int, used_today: int) -> int | None:
    """餘額低於 60 才補 60，同一天最多 10 次。"""
    if used_today >= STAFF_DAILY_TIMES or balance >= STAFF_FLOOR:
        return None
    return STAFF_REFILL

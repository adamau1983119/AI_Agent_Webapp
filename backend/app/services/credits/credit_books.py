"""Monthly Stripe books for the accountant. No card numbers or emails."""
from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.credits.credit_stripe import stripe_ready

try:
    import stripe
except Exception:  # pragma: no cover
    stripe = None

_HKT = ZoneInfo("Asia/Hong_Kong")
_ZERO_DECIMAL = {"bif", "clp", "djf", "gnf", "jpy", "kmf", "krw", "mga", "pyg", "rwf", "ugx", "vnd", "vuv", "xaf", "xof", "xpf"}
_KIND = {
    "charge": "income",
    "payment": "income",
    "refund": "refund",
    "payment_refund": "refund",
    "stripe_fee": "fee",
    "application_fee": "fee",
    "payout": "payout",
}


def books_ready() -> bool:
    token = str(getattr(settings, "BOOKS_READ_TOKEN", "") or "").strip()
    return stripe_ready() and bool(token)


def books_token_ok(got: str) -> bool:
    expected = str(getattr(settings, "BOOKS_READ_TOKEN", "") or "").strip()
    if not expected:
        return False
    return secrets.compare_digest(str(got or ""), expected)


def list_month_books(month: str) -> dict[str, Any]:
    start, end = _month_bounds(month)
    stripe.api_key = str(settings.STRIPE_SECRET_KEY).strip()
    rows: list[dict[str, Any]] = []
    starting_after = None
    for _ in range(20):
        kwargs: dict[str, Any] = {"created": {"gte": start, "lt": end}, "limit": 100}
        if starting_after:
            kwargs["starting_after"] = starting_after
        page = stripe.BalanceTransaction.list(**kwargs)
        data = _as_dict(page).get("data") or []
        if not data:
            break
        for item in data:
            rows.append(_row(_as_dict(item)))
        if not _as_dict(page).get("has_more"):
            break
        starting_after = _as_dict(data[-1]).get("id")
    return {"month": month, "timezone": "Asia/Hong_Kong", "rows": rows}


def _month_bounds(month: str) -> tuple[int, int]:
    text = str(month or "").strip()
    parts = text.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2:
        raise ValueError("bad_month")
    year, mon = int(parts[0]), int(parts[1])
    if mon < 1 or mon > 12:
        raise ValueError("bad_month")
    start = datetime(year, mon, 1, tzinfo=_HKT)
    end = datetime(year + 1, 1, 1, tzinfo=_HKT) if mon == 12 else datetime(year, mon + 1, 1, tzinfo=_HKT)
    return int(start.timestamp()), int(end.timestamp())


def _row(item: dict[str, Any]) -> dict[str, Any]:
    currency = str(item.get("currency") or "").lower()
    stripe_type = str(item.get("type") or "")
    reporting = str(item.get("reporting_category") or "")
    kind = "dispute" if reporting == "dispute" else _KIND.get(stripe_type, stripe_type or "other")
    source = item.get("source")
    source_id = source if isinstance(source, str) else str((source or {}).get("id") or "") if isinstance(source, dict) else ""
    return {
        "id": str(item.get("id") or ""),
        "kind": kind,
        "stripe_type": stripe_type,
        "created_hkt": _hkt_date(item.get("created")),
        "available_hkt": _hkt_date(item.get("available_on")),
        "currency": currency,
        "gross": _major(item.get("amount"), currency),
        "fee": _major(item.get("fee"), currency),
        "net": _major(item.get("net"), currency),
        "charge_id": source_id if source_id.startswith("ch_") else "",
    }


def _hkt_date(stamp: Any) -> str:
    if stamp in (None, ""):
        return ""
    return datetime.fromtimestamp(int(stamp), tz=_HKT).strftime("%Y-%m-%d")


def _major(minor: Any, currency: str) -> str:
    value = int(minor or 0)
    sign = "-" if value < 0 else ""
    whole = abs(value)
    if currency in _ZERO_DECIMAL:
        return f"{sign}{whole}"
    unit, frac = divmod(whole, 100)
    return f"{sign}{unit}.{frac:02d}"


def _as_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return {}

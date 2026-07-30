"""Observability package — Atom-1 skeleton (default OFF)."""

from app.services.observability.alert_dispatcher import (
    emit_alert,
    emit_cost,
    emit_crash,
    emit_customer,
)
from app.services.observability.channels import AlertChannel

__all__ = [
    "AlertChannel",
    "emit_alert",
    "emit_crash",
    "emit_cost",
    "emit_customer",
]

"""週報名單的純判斷。不讀資料庫。"""
from __future__ import annotations


def weekly_eligible(user: dict) -> bool:
    if user.get("status") != "active":
        return False
    if not user.get("email_verified"):
        return False
    if user.get("weekly_mail_opt_out"):
        return False
    if user.get("email_deliverable") is False:
        return False
    email = str(user.get("email") or "")
    return "@" in email


def topic_title(doc: dict, language: str) -> str:
    i18n = doc.get("titles_i18n") or {}
    picked = i18n.get(language) or doc.get("original_title") or doc.get("title") or ""
    return str(picked)

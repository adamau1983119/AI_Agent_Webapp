"""週報退訂與 Resend 退信。不寄信。"""
from __future__ import annotations

import json
import logging
import os

from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

from app.services.repositories.user_repository import UserRepository
from app.services.weekly_mail_page import render_unsubscribe_page
from app.services.weekly_mail_preview import build_weekly_rows, preview_token_ok
from app.services.weekly_mail_token import read_unsubscribe_token
from app.services.weekly_mail_webhook import recipient_emails, verify_resend_signature
from app.utils.ui_language import allowed_language

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weekly-mail", tags=["weekly-mail"])
_users = UserRepository()


async def _stop_weekly(user_id: str, bounced: bool) -> None:
    fields = {"weekly_mail_opt_out": True}
    if bounced:
        fields["email_deliverable"] = False
    await _users.update_user(user_id, fields)


@router.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe(token: str = ""):
    claim = read_unsubscribe_token(token)
    if not claim:
        return HTMLResponse(render_unsubscribe_page("zh-TW", ok=False), status_code=400)
    user = await _users.get_user_by_id(claim["user_id"])
    language = allowed_language((user or {}).get("language")) or "zh-TW"
    if not user or str(user.get("email") or "").lower() != claim["email"]:
        return HTMLResponse(render_unsubscribe_page(language, ok=False), status_code=400)
    await _stop_weekly(user["id"], bounced=False)
    return HTMLResponse(render_unsubscribe_page(language, ok=True))


@router.post("/unsubscribe")
async def unsubscribe_once(token: str = ""):
    claim = read_unsubscribe_token(token)
    if not claim:
        raise HTTPException(status_code=400, detail="invalid_token")
    user = await _users.get_user_by_id(claim["user_id"])
    if not user or str(user.get("email") or "").lower() != claim["email"]:
        raise HTTPException(status_code=400, detail="invalid_token")
    await _stop_weekly(user["id"], bounced=False)
    return {"ok": True}


@router.post("/resend-webhook")
async def resend_webhook(request: Request):
    body = await request.body()
    secret = os.getenv("RESEND_WEBHOOK_SECRET", "")
    if not verify_resend_signature(secret, body, request.headers):
        raise HTTPException(status_code=401, detail="invalid_signature")
    try:
        event = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="invalid_json") from exc
    kind = event.get("type") or ""
    if kind not in ("email.bounced", "email.complained"):
        return {"ok": True, "ignored": True}
    bounced = kind == "email.bounced"
    for email in recipient_emails(event):
        user = await _users.get_user_by_email(email)
        if user:
            await _stop_weekly(user["id"], bounced=bounced)
    return {"ok": True}


@router.get("/preview")
async def preview(x_weekly_token: str = Header(default="", alias="X-Weekly-Token")):
    if not preview_token_ok(x_weekly_token):
        raise HTTPException(status_code=404, detail="not_found")
    payload = await build_weekly_rows()
    return JSONResponse(payload)

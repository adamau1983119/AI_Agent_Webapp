"""
Observability 中文告警郵件 — 紅／綠燈置頂。
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.services.email_service import EmailService
from app.services.observability.channels import AlertChannel, ops_email
from app.services.observability.traffic_light import TrafficLight, light_zh, verdict_zh

_CHANNEL_ZH = {
    AlertChannel.CRASH: "系統異常／崩潰",
    AlertChannel.COST: "Token／成本",
    AlertChannel.CUSTOMER: "客戶訊息",
}


def build_zh_email(
    channel: AlertChannel,
    title: str,
    *,
    detail: str = "",
    extra: dict[str, Any] | None = None,
) -> tuple[str, str, str]:
    extra = extra or {}
    raw = str(extra.get("traffic_light", "red")).lower()
    light = TrafficLight.RED if raw == "red" else TrafficLight.GREEN
    lamp = light_zh(light)
    verdict = verdict_zh(light)
    ch = _CHANNEL_ZH[channel]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    color = "#b91c1c" if light is TrafficLight.RED else "#15803d"
    lines = [
        f"【{lamp}】{verdict}",
        f"通道：{ch}",
        f"標題：{title}",
        f"時間：{ts}",
    ]
    if detail:
        lines.append(f"說明：{detail}")
    for k, v in extra.items():
        if k == "traffic_light":
            continue
        lines.append(f"  - {k}：{v}")
    lines += ["", "此信由後台 Observability Agent 發出（異常才通知）。請勿回覆。"]
    text = "\n".join(lines)
    subject = f"【{lamp}】[Alter Ego][{ch}] {title}"
    body = "<br>".join(lines)
    html = (
        "<html><body style='font-family:sans-serif;line-height:1.6'>"
        f"<h1 style='color:{color};margin:0'>【{lamp}】{verdict}</h1>"
        f"<p>{body}</p></body></html>"
    )
    return subject, html, text


async def send_alert_email(
    channel: AlertChannel,
    title: str,
    *,
    detail: str = "",
    extra: dict[str, Any] | None = None,
    to_email: str | None = None,
) -> bool:
    subject, html, text = build_zh_email(
        channel, title, detail=detail, extra=extra
    )
    return await EmailService().send_email(
        to_email=to_email or ops_email(),
        subject=subject,
        html_content=html,
        text_content=text,
    )

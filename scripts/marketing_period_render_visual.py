#!/usr/bin/env python3
"""Render the Alter Ego ops weekly visual report (HTML) from evidence JSONs.

Reads (per week, in docs/evidence/marketing/):
  {period_start}_counts.json        Mongo core (人數 SoT)
  {period_start}_ads.json           Ads API spend/clicks/impr
  {period_start}_ga4.json           GA4 event counts
  {period_start}_ga4_traffic.json   GA4 traffic breakdowns (this script's sibling fetcher)
  {period_start}_week_draft.json    traffic_light + decisions

  python scripts/marketing_period_render_visual.py \
      --period-start 2026-10-27 --period-end 2026-11-02 \
      --prev-start 2026-10-20 --prev-end 2026-10-26 \
      --out docs/evidence/marketing/ops_weekly_visual_2026-11-02.html

No PII. Numbers only. Layout follows docs/marketing_alter_ego_ops_layout_spec.md
(orange = this week, grey = last week; 6 cards on top; row 2 = valid / email / revenue).
"""
from __future__ import annotations

import argparse
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "docs" / "evidence" / "marketing"

ORANGE = "#E8590C"
ORANGE_LIGHT = "#FD7E14"
GREY = "#D7D2CB"
INK = "#1A1A1A"
MUTED = "#6B6B6B"
PANEL = "#FFFFFF"
CANVAS = "#F4F1EC"


def load(name: str) -> dict:
    p = EV / name
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def week(start: str) -> dict:
    counts = load(f"{start}_counts.json")
    upsert = load(f"{start}_week_upsert.json")
    ads = load(f"{start}_ads.json")
    ga4 = load(f"{start}_ga4.json")
    traffic = load(f"{start}_ga4_traffic.json")
    draft = load(f"{start}_week_draft.json")
    core = dict(upsert.get("core") or draft.get("core") or {})
    core.update(counts.get("core") or {})
    return {
        "start": start,
        "end": counts.get("period_end") or traffic.get("period_end") or "",
        "core": core,
        "ads": ads,
        "ga4": ga4,
        "traffic": traffic,
        "totals": traffic.get("totals") or {},
        "daily": traffic.get("daily") or [],
        "medium": traffic.get("by_medium") or [],
        "landing": traffic.get("by_landing") or [],
        "country": traffic.get("by_country") or [],
        "device": traffic.get("by_device") or [],
        "light": (core.get("traffic_light") or draft.get("traffic_light") or "—").lower(),
    }


def num(v, digits: int = 0) -> str:
    if v is None or v == "":
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return f"{f:,.{digits}f}" if digits else f"{f:,.0f}"


def delta(cur, prev) -> tuple[str, str]:
    """Return (text, css_class) for WoW change."""
    try:
        c, p = float(cur), float(prev)
    except (TypeError, ValueError):
        return "—", "flat"
    if p == 0:
        return ("new" if c else "—"), ("up" if c else "flat")
    pct = (c - p) / p * 100
    if abs(pct) < 0.05:
        return "0.0%", "flat"
    cls = "up" if pct > 0 else "down"
    sign = "▲" if pct > 0 else ("▼" if pct < 0 else "—")
    return f"{sign} {abs(pct):.1f}%", cls


def sparkline(points: list[float], w: int = 132, h: int = 34) -> str:
    if not points:
        return ""
    mx = max(points) or 1
    n = len(points)
    step = w / max(n - 1, 1)
    coords = " ".join(
        f"{i * step:.1f},{h - (p / mx) * (h - 4) - 2:.1f}" for i, p in enumerate(points)
    )
    area = f"0,{h} " + coords + f" {w},{h}"
    return (
        f'<svg class="spark" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'preserveAspectRatio="none"><polygon points="{area}" fill="{ORANGE_LIGHT}" '
        f'opacity="0.16"/><polyline points="{coords}" fill="none" stroke="{ORANGE}" '
        f'stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )


def card(title: str, value: str, unit: str, cur, prev, spark: str, note: str) -> str:
    text, cls = delta(cur, prev)
    return f"""
    <div class="card">
      <div class="card-head"><span class="card-title">{html.escape(title)}</span></div>
      <div class="card-body">
        <div>
          <div class="value">{value}<span class="unit">{unit}</span></div>
          <div class="delta {cls}">{text}</div>
          <div class="prev">Last week {num(prev)}</div>
        </div>
        {spark}
      </div>
      <div class="card-note">{html.escape(note)}</div>
    </div>"""


def grouped_bars(rows: list[tuple[str, float, float]], unit: str = "") -> str:
    if not rows:
        return '<p class="empty">無資料</p>'
    peak = max(max(c, p) for _, c, p in rows) or 1
    out = ['<div class="grouped">']
    for label, cur, prev in rows:
        cw = cur / peak * 100
        pw = prev / peak * 100
        out.append(
            f"""
      <div class="bar-row">
        <div class="bar-label">{html.escape(label)}</div>
        <div class="bar-track">
          <div class="bar prev" style="width:{pw:.1f}%"></div>
          <div class="bar cur" style="width:{cw:.1f}%"></div>
        </div>
        <div class="bar-val"><b>{num(cur)}</b><span class="muted"> / {num(prev)}</span></div>
      </div>"""
        )
    out.append("</div>")
    return "".join(out)


def landing_bars(rows: list[tuple[str, float, float]], total: float) -> str:
    if not rows:
        return '<p class="empty">無資料</p>'
    peak = max(max(c, p) for _, c, p in rows) or 1
    out = ['<div class="grouped">']
    for label, cur, prev in rows:
        share = (cur / total * 100) if total else 0
        out.append(
            f"""
      <div class="bar-row">
        <div class="bar-label path">{html.escape(label)}</div>
        <div class="bar-track">
          <div class="bar prev" style="width:{prev / peak * 100:.1f}%"></div>
          <div class="bar cur" style="width:{cur / peak * 100:.1f}%"></div>
        </div>
        <div class="bar-val"><b>{num(cur)}</b><span class="share">{share:.0f}%</span></div>
      </div>"""
        )
    out.append("</div>")
    return "".join(out)


DEVICE_COLOR = {
    "desktop": ORANGE,
    "mobile": "#9A9A9A",
    "tablet": "#D9D3CB",
    "smart tv": "#C9C3BB",
}


def donut(rows: list[tuple[str, float]]) -> str:
    rows = [(k, v) for k, v in rows if v > 0]
    total = sum(v for _, v in rows) or 1
    palette = [DEVICE_COLOR.get(k.lower(), "#BDB7AE") for k, _ in rows]
    r, stroke = 62, 26
    circ = 2 * 3.14159 * r
    offset = 0.0
    segs = []
    for i, (name, v) in enumerate(rows):
        frac = v / total
        dash = frac * circ
        segs.append(
            f'<circle cx="90" cy="90" r="{r}" fill="none" stroke="{palette[i % len(palette)]}" '
            f'stroke-width="{stroke}" stroke-dasharray="{dash:.1f} {circ - dash:.1f}" '
            f'stroke-dashoffset="{-offset:.1f}" transform="rotate(-90 90 90)"/>'
        )
        offset += dash
    legend = "".join(
        f'<li><i style="background:{palette[i % len(palette)]}"></i>'
        f"{html.escape(name)}<b>{v / total * 100:.0f}%</b><span>{num(v)}</span></li>"
        for i, (name, v) in enumerate(rows)
    )
    return f"""
    <div class="donut-wrap">
      <svg viewBox="0 0 180 180" width="180" height="180">{''.join(segs)}
        <text x="90" y="86" text-anchor="middle" class="donut-num">{num(total)}</text>
        <text x="90" y="106" text-anchor="middle" class="donut-cap">sessions</text>
      </svg>
      <ul class="legend">{legend}</ul>
    </div>"""


COUNTRY_NAME = {
    "Hong Kong": "Hong Kong, China",
    "Taiwan": "Taiwan, China",
    "Macao": "Macao, China",
    "Macau": "Macao, China",
    "(not set)": "Unknown",
}

TILE_POS = {
    "United Kingdom": (3, 0),
    "United States": (0, 1),
    "Iran": (5, 1),
    "Afghanistan": (6, 1),
    "China": (7, 1),
    "Japan": (9, 1),
    "Hong Kong, China": (7, 2),
    "Taiwan, China": (8, 2),
}

TILE_LABEL = {
    "United States": "美國",
    "United Kingdom": "英國",
    "Iran": "伊朗",
    "Afghanistan": "阿富汗",
    "China": "中國",
    "Japan": "日本",
    "Hong Kong, China": "中國香港",
    "Taiwan, China": "中國台灣",
}


def tile_map(rows: list[tuple[str, float]]) -> tuple[str, str]:
    """Grid cartogram: relative position only, no borders, no map tile service."""
    vals = {n: v for n, v in rows if v > 0}
    vals.setdefault("China", 0.0)
    known = {n: v for n, v in vals.items() if n in TILE_POS}
    stray = sorted(
        [(n, v) for n, v in vals.items() if n not in TILE_POS and n != "China"],
        key=lambda kv: -kv[1],
    )
    mx = max(list(known.values()) + [1])
    tw, th, px, py = 60, 44, 68, 56
    out = ['<svg class="tilemap" viewBox="0 0 680 170" width="100%" role="img">']
    for name, (col, row) in sorted(TILE_POS.items(), key=lambda kv: (kv[1][1], kv[1][0])):
        v = known.get(name, 0.0)
        x = 8 + col * px
        y = 6 + row * py
        if v > 0:
            op = 0.30 + 0.70 * (v / mx)
            fill, txt = ORANGE, ("#FFFFFF" if op > 0.58 else INK)
            op_attr = f' fill-opacity="{op:.2f}"'
            name_txt = "#FFFFFF" if op > 0.58 else "#8A5A3A"
        else:
            fill, txt, op_attr, name_txt = "#EDE9E3", "#A9A29A", "", "#A9A29A"
        out.append(
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="7" fill="{fill}"{op_attr}/>'
        )
        out.append(
            f'<text x="{x + tw / 2}" y="{y + 21}" text-anchor="middle" class="tile-val" '
            f'fill="{txt}">{num(v)}</text>'
        )
        out.append(
            f'<text x="{x + tw / 2}" y="{y + 36}" text-anchor="middle" class="tile-name" '
            f'fill="{name_txt}">{TILE_LABEL.get(name, name)}</text>'
        )
    out.append("</svg>")
    stray_txt = ""
    if stray:
        stray_txt = " · 其他：" + "、".join(
            f"{html.escape(n)} {num(v)}" for n, v in stray[:4]
        )
    note = (
        "格子示意圖（僅相對位置，非國界底圖；未使用任何境外地圖服務）"
        " · 深橙＝本週 sessions 高；灰＝0" + stray_txt
    )
    return "".join(out), note


def pct_rows(rows: list[dict], top: int = 5) -> list[tuple[str, float, float]]:
    return [
        (r["dims"][0], r["metrics"][0], 0.0)
        for r in rows[:top]
    ]


def merge_rows(cur_rows: list[dict], prev_rows: list[dict], top: int = 6):
    prev_map = {r["dims"][0]: r["metrics"][0] for r in prev_rows}
    merged = [
        (r["dims"][0], r["metrics"][0], prev_map.get(r["dims"][0], 0.0))
        for r in cur_rows[:top]
    ]
    # include a last-week item that vanished this week (shows the drop)
    cur_keys = {r["dims"][0] for r in cur_rows}
    missing = [
        (r["dims"][0], 0.0, r["metrics"][0]) for r in prev_rows if r["dims"][0] not in cur_keys
    ]
    return merged + missing[:2]


LIGHT_COLOR = {"green": "#2F9E44", "yellow": "#E8A400", "red": "#E03131"}


def render(cur: dict, prev: dict) -> str:
    c, p = cur, prev
    ct, pt = c["core"], p["core"]
    light = c["light"]
    light_color = LIGHT_COLOR.get(light, "#8A8A8A")
    light_label = {"green": "GREEN · Healthy", "yellow": "YELLOW · Normal / Warning", "red": "RED · Action"}.get(
        light, light.upper()
    )
    sess = c["totals"].get("sessions", 0)
    eng = c["totals"].get("engaged_sessions", 0)
    spend = c["ads"].get("ads_spend_hkd", 0)
    signups = c["ga4"].get("ga4_sign_up", 0)

    spark_s = sparkline([d.get("sessions", 0) for d in c["daily"]])
    spark_e = sparkline([d.get("engaged_sessions", 0) for d in c["daily"]])

    cards = "".join(
        [
            card("Sessions", num(sess), "", sess, p["totals"].get("sessions", 0), spark_s, "GA4 工作階段"),
            card("Engaged sessions", num(eng), "", eng, p["totals"].get("engaged_sessions", 0), spark_e, "互動工作階段"),
            card("External new users", num(ct.get("external_new_users")), "",
                 ct.get("external_new_users"), pt.get("external_new_users"), "", "Mongo 外部新客（人數 SoT）"),
            card("Ads spend HKD", num(spend, 2), " HK$", spend, p["ads"].get("ads_spend_hkd", 0), "",
                 f"點擊 {num(c['ads'].get('ads_clicks'))} · 曝光 {num(c['ads'].get('ads_impr'))}"),
            card("GA4 sign_up (events)", num(signups), "", signups, p["ga4"].get("ga4_sign_up", 0), "",
                 "事件數 ≠ 客戶數"),
        ]
    )

    sub_total = ct.get("email_subscribers_total")
    sub_new = ct.get("email_subscribers_new")
    rev = ct.get("revenue_usd")
    rev_prev = pt.get("revenue_usd")
    rev_none = rev in (None, "")
    rev_value = "—" if rev_none else f"{float(rev):,.2f}"
    rev_unit = "" if rev_none else " USD"
    rev_note = (
        f"Stripe USD · ≈HK$ {float(rev) * 7.8:,.0f}（×7.8 僅顯示）· 禁 ROI 混幣"
        if not rev_none
        else "Stripe USD · 無資料顯示 — · 禁 ROI 混幣"
    )
    cards2 = "".join(
        [
            card(
                "Valid members",
                num(ct.get("valid_members")),
                "",
                ct.get("valid_members"),
                pt.get("valid_members"),
                "",
                "外部 ∧ 本期成功生成 ∧ 本期扣點；≠ sign_up 事件",
            ),
            card(
                "Email subscribers",
                num(sub_total),
                "",
                sub_total,
                pt.get("email_subscribers_total"),
                "",
                f"total {num(sub_total)} · new {num(sub_new)}；訂閱者 ≠ 客戶數",
            ),
            card("Revenue (Stripe USD)", rev_value, rev_unit, rev, rev_prev, "", rev_note),
        ]
    )

    medium_rows = merge_rows(c["medium"], p["medium"], top=4)
    med_map = {r["dims"][0]: r["metrics"][0] for r in c["medium"]}
    cpc = med_map.get("cpc", 0)
    organic = med_map.get("organic", 0)
    medium_note = (
        f"cpc（Ads 付費）{num(cpc)} 次＝{cpc / (sess or 1) * 100:.0f}%；"
        f"organic {num(organic)} 次 → 自然搜尋幾乎未起量"
    )
    landing_rows = [r for r in merge_rows(c["landing"], p["landing"], top=7) if r[1] > 0][:6]
    med_cur = {r["dims"][0]: r["metrics"][0] for r in c["medium"]}
    channels = []
    for name in ("cpc", "(none)", "organic", "referral"):
        v = med_cur.get(name, 0)
        if v:
            channels.append(
                f'<div class="chip"><span>{html.escape(name)}</span>'
                f"<b>{num(v)}</b><i>{v / (sess or 1) * 100:.0f}%</i></div>"
            )
    channel_chips = f'<div class="chips">{"".join(channels)}</div>'
    def _rn(rows: list[dict], cn: bool = False) -> list[dict]:
        out = []
        for r in rows:
            name = COUNTRY_NAME.get(r["dims"][0], r["dims"][0])
            out.append(dict(r, dims=[TILE_LABEL.get(name, name) if cn else name]))
        return out

    country_rows = merge_rows(_rn(c["country"], cn=True), _rn(p["country"], cn=True), top=5)
    country_map, country_note = tile_map(
        [(d["dims"][0], d["metrics"][0]) for d in _rn(c["country"])]
    )
    country_note += " · Learning Signal Only（樣本過小，勿用週值做市場結論）"
    device_rows = [(r["dims"][0], r["metrics"][0]) for r in c["device"]]

    total_sessions = sess or 1

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>Alter Ego Ops · Weekly Report · {c['start']} – {c['end']}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:{CANVAS}; color:{INK};
         font-family:"Segoe UI","Helvetica Neue",Arial,"Microsoft JhengHei",sans-serif; }}
  .sheet {{ width:1240px; margin:24px auto 40px; background:{CANVAS}; }}
  header {{ position:relative; background:linear-gradient(100deg,{ORANGE} 0%,{ORANGE_LIGHT} 100%);
            border-radius:18px 18px 0 0; padding:22px 28px; color:#fff; display:flex;
            align-items:center; gap:18px; }}
  .logo {{ width:74px;height:74px;border-radius:16px;background:#fff;color:{ORANGE};
           display:flex;flex-direction:column;align-items:center;justify-content:center;
           font-weight:800;line-height:1.05;font-size:15px;letter-spacing:.2px; }}
  .titles h1 {{ margin:0; font-size:29px; letter-spacing:.6px; font-weight:800; line-height:1.1; }}
  .titles .sub {{ margin:5px 0 0; font-size:13px; font-weight:700; letter-spacing:5px;
                  opacity:.95; text-transform:uppercase; }}
  .titles p {{ margin:6px 0 0; font-size:12.5px; opacity:.9; }}
  .cards.row2 {{ margin-top:12px; }}
  .tilemap {{ width:100%; height:auto; display:block; }}
  .tile-val {{ font-size:15px; font-weight:800; }}
  .tile-name {{ font-size:8.5px; font-weight:600; }}
  .legend-top {{ margin-left:auto; text-align:right; font-size:12.5px; }}
  .legend-top span {{ display:inline-flex; align-items:center; gap:6px; margin-left:14px; }}
  .dot {{ width:10px;height:10px;border-radius:3px;display:inline-block; }}
  .period {{ display:block; margin-top:6px; font-weight:600; }}
  .body {{ background:#fff; padding:18px 20px 22px; border-radius:0 0 18px 18px;
           box-shadow:0 14px 34px rgba(0,0,0,.08); }}
  .cards {{ display:grid; grid-template-columns:repeat(6,1fr); gap:12px; }}
  .card {{ border:1px solid #EDE9E3; border-radius:14px; padding:12px 12px 10px; background:{PANEL}; }}
  .card-head {{ font-size:12.5px; font-weight:700; color:{MUTED}; letter-spacing:.2px; }}
  .card-body {{ display:flex; align-items:flex-end; justify-content:space-between; gap:8px; margin-top:6px; }}
  .value {{ font-size:30px; font-weight:800; line-height:1; }}
  .unit {{ font-size:13px; font-weight:600; color:{MUTED}; margin-left:3px; }}
  .delta {{ font-size:12px; font-weight:700; margin-top:7px; }}
  .delta.up {{ color:#2F9E44; }} .delta.down {{ color:#E03131; }} .delta.flat {{ color:{MUTED}; }}
  .prev {{ font-size:11px; color:{MUTED}; margin-top:3px; }}
  .card-note {{ font-size:10.5px; color:#9A9A9A; margin-top:8px; min-height:13px; }}
  .light-value {{ font-size:22px; font-weight:800; letter-spacing:.4px; }}
  .grid2 {{ display:grid; grid-template-columns:1.15fr 1fr; gap:14px; margin-top:16px;
            align-items:start; }}
  .grid2.b {{ grid-template-columns:1.6fr 1fr; }}
  .panel {{ border:1px solid #EDE9E3; border-radius:14px; padding:14px 16px 10px;
            display:flex; flex-direction:column; align-self:start; }}
  .panel > .empty:last-child {{ margin-top:auto; margin-bottom:0; padding-top:8px; }}
  .panel h2 {{ margin:0 0 12px; font-size:14.5px; font-weight:800; }}
  .panel h2 small {{ font-weight:600; color:{MUTED}; font-size:11px; margin-left:8px; }}
  .grouped {{ display:flex; flex-direction:column; gap:9px; }}
  .bar-row {{ display:grid; grid-template-columns:112px 1fr 78px; align-items:center; gap:10px; }}
  .bar-label {{ font-size:12px; color:#333; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .bar-label.path {{ font-family:Consolas,Menlo,monospace; font-size:11.5px; }}
  .bar-track {{ position:relative; height:16px; }}
  .bar {{ position:absolute; top:0; height:16px; border-radius:3px; }}
  .bar.cur {{ background:{ORANGE}; }}
  .bar.prev {{ background:{GREY}; top:-4px; height:7px; }}
  .bar-val {{ font-size:12px; text-align:right; white-space:nowrap; }}
  .bar-val .muted {{ color:{MUTED}; font-size:11px; }}
  .bar-val .share {{ display:block; font-size:10.5px; color:{MUTED}; }}
  .donut-wrap {{ display:flex; align-items:center; gap:18px; }}
  .donut-num {{ font-size:26px; font-weight:800; fill:{INK}; }}
  .donut-cap {{ font-size:11px; fill:{MUTED}; }}
  .legend {{ list-style:none; margin:0; padding:0; font-size:12px; }}
  .legend li {{ display:grid; grid-template-columns:14px 1fr 44px 44px; align-items:center;
               gap:8px; padding:5px 0; }}
  .legend i {{ width:11px;height:11px;border-radius:3px;display:block; }}
  .legend b {{ text-align:right; }} .legend span {{ text-align:right; color:{MUTED}; }}
  .empty {{ color:{MUTED}; font-size:12px; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
  .chip {{ border:1px solid #EDE9E3; border-radius:10px; padding:7px 10px; background:#FBFAF8;
           display:flex; align-items:baseline; gap:6px; font-size:11.5px; color:{MUTED}; }}
  .chip b {{ font-size:15px; color:{INK}; font-weight:800; }}
  .chip i {{ font-style:normal; font-size:10.5px; color:{MUTED}; }}
  footer {{ margin-top:14px; display:flex; gap:18px; font-size:11px; color:{MUTED};
            border-top:1px dashed #E2DCD3; padding-top:10px; flex-wrap:wrap; }}
  footer b {{ color:#333; }}
  @media print {{ body {{ background:#fff; }} .sheet {{ margin:0; }} }}
</style>
</head>
<body>
<div class="sheet">
  <header>
    <div class="logo">Alter<br>Ego</div>
    <div class="titles">
      <h1>Alter Ego Ops</h1>
      <p class="sub">Weekly Report</p>
      <p>This week vs Last week · HKT Mon–Sun</p>
    </div>
    <div class="legend-top">
      <span><i class="dot" style="background:{GREY}"></i>Last week</span>
      <span><i class="dot" style="background:{ORANGE}"></i>This week</span>
      <span class="period">{c['start']} → {c['end']}</span>
    </div>
  </header>

  <div class="body">
    <div class="cards">
      {cards}
      <div class="card">
        <div class="card-head">Traffic light</div>
        <div class="card-body">
          <div>
            <div class="light-value" style="color:{light_color}">● {light.upper()}</div>
            <div class="prev">{html.escape(light_label)}</div>
          </div>
        </div>
        <div class="card-note">CEO 拍板；本週沿用</div>
      </div>
    </div>

    <div class="cards row2">
      {cards2}
    </div>

    <div class="grid2">
      <div class="panel">
        <h2>Sessions by Medium <small>GA4 · 條＝本週（橙）／上週（灰）</small></h2>
        {grouped_bars(medium_rows)}
        {channel_chips}
        <p class="empty">{html.escape(medium_note)}</p>
      </div>
      <div class="panel">
        <h2>Top Landing Pages <small>GA4 · 佔本週 sessions</small></h2>
        {landing_bars(landing_rows, total_sessions)}
      </div>
    </div>

    <div class="grid2 b">
      <div class="panel">
        <h2>Sessions by Country <small>GA4 · 本週（格子圖）＋本週／上週對照</small></h2>
        {country_map}
        <p class="empty">{html.escape(country_note)}</p>
        <div style="margin-top:8px">{grouped_bars(country_rows)}</div>
      </div>
      <div class="panel">
        <h2>Device category <small>GA4 · 本週</small></h2>
        {donut(device_rows)}
      </div>
    </div>

    <footer>
      <span><b>人數／新客</b>＝Mongo（外部用戶），GA4 事件 ≠ 客戶數</span>
      <span><b>流量</b>＝GA4（provisional=false）</span>
      <span><b>花費</b>＝Google Ads API</span>
      <span><b>燈號</b>＝CEO 拍板</span>
      <span><b>Email</b>＝訂閱者（≠ 客戶）</span>
      <span><b>Revenue</b>＝Stripe USD（非 ga4_purchase；無則 —；HK$ 僅顯示，禁 ROI 混幣）</span>
      <span><b>Valid members</b>＝外部 ∧ 本期成功生成 ∧ 本期扣點</span>
      <span><b>Report Schema Version</b>＝v1.0</span>
      <span>generated {datetime.now().strftime('%Y-%m-%d %H:%M')} HKT</span>
    </footer>
  </div>
</div>
</body>
</html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Render ops weekly visual report (HTML)")
    ap.add_argument("--period-start", required=True)
    ap.add_argument("--period-end")
    ap.add_argument("--prev-start", required=True)
    ap.add_argument("--prev-end")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cur, prev = week(args.period_start), week(args.prev_start)
    doc = render(cur, prev)
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

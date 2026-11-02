#!/usr/bin/env python3
"""Fetch GA4 traffic breakdowns (sessions/engaged, medium, landing, country, device).

Complements marketing_period_fetch_ga4.py (which only pulls event counts).
Used to build the Alter Ego ops weekly visual report.

Env:
  GA4_PROPERTY_ID                 numeric property id
  GA4_PROVISIONAL                 default true until Internal Traffic filter is Active

  python scripts/marketing_period_fetch_ga4_traffic.py \
      --period-start 2026-10-27 --period-end 2026-11-02 \
      --out docs/evidence/marketing/2026-10-27_ga4_traffic.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import SCHEMA_VERSION  # noqa: E402


def _client():
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    return BetaAnalyticsDataClient()


def _report(client, pid: str, start: str, end: str, dims: list[str], mets: list[str]):
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    req = RunReportRequest(
        property=f"properties/{pid}",
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name=m) for m in mets],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name=mets[0]), desc=True)],
        limit=10,
    )
    resp = client.run_report(req)
    rows = []
    for r in resp.rows:
        rows.append(
            {
                "dims": [d.value for d in r.dimension_values],
                "metrics": [float(m.value or 0) for m in r.metric_values],
            }
        )
    return rows


def _totals(client, pid: str, start: str, end: str) -> dict[str, float]:
    from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest

    req = RunReportRequest(
        property=f"properties/{pid}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="totalUsers"),
            Metric(name="screenPageViews"),
        ],
        date_ranges=[DateRange(start_date=start, end_date=end)],
    )
    resp = client.run_report(req)
    row = resp.rows[0] if resp.rows else None
    keys = ("sessions", "engaged_sessions", "total_users", "page_views")
    if not row:
        return {k: 0.0 for k in keys}
    return {k: float(v.value or 0) for k, v in zip(keys, row.metric_values)}


def _daily(client, pid: str, start: str, end: str) -> list[dict]:
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    req = RunReportRequest(
        property=f"properties/{pid}",
        dimensions=[Dimension(name="date")],
        metrics=[Metric(name="sessions"), Metric(name="engagedSessions")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
        limit=400,
    )
    resp = client.run_report(req)
    out = []
    for r in resp.rows:
        d = r.dimension_values[0].value
        out.append(
            {
                "date": f"{d[:4]}-{d[4:6]}-{d[6:]}",
                "sessions": float(r.metric_values[0].value or 0),
                "engaged_sessions": float(r.metric_values[1].value or 0),
            }
        )
    return out


def fetch(pid: str, start: str, end: str) -> dict:
    client = _client()
    return {
        "schema_version": SCHEMA_VERSION,
        "period_start": start,
        "period_end": end,
        "provisional": os.environ.get("GA4_PROVISIONAL", "true").lower()
        not in ("0", "false", "no"),
        "source": "ga4_data_api",
        "property_id": pid,
        "totals": _totals(client, pid, start, end),
        "daily": _daily(client, pid, start, end),
        "by_medium": _report(client, pid, start, end, ["sessionMedium"], ["sessions"]),
        "by_landing": _report(
            client, pid, start, end, ["landingPagePlusQueryString"], ["sessions"]
        ),
        "by_country": _report(client, pid, start, end, ["country"], ["sessions"]),
        "by_device": _report(client, pid, start, end, ["deviceCategory"], ["sessions"]),
        "source_notes": (
            "traffic only; 人數／新客 SoT 仍是 Mongo counts；"
            "HKT week dates as GA4 date_range"
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch GA4 traffic breakdowns for a period")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    p.add_argument("--property-id", default=os.environ.get("GA4_PROPERTY_ID", ""))
    p.add_argument("--out", help="write JSON here (default stdout)")
    args = p.parse_args()
    pid = (args.property_id or "").strip()
    if not pid:
        print("missing GA4_PROPERTY_ID / --property-id", file=sys.stderr)
        return 2
    doc = fetch(pid, args.period_start, args.period_end)
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

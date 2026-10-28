#!/usr/bin/env python3
"""Fetch GA4 event counts for a HKT week via Analytics Data API. JSON stdout.

Env:
  GA4_PROPERTY_ID  numeric property id (Admin → Property settings; not G-XXXXXXXX)
  GOOGLE_APPLICATION_CREDENTIALS  path to service-account JSON
  GA4_PROVISIONAL  default true until Internal Traffic filter is Active

  python scripts/marketing_period_fetch_ga4.py --period-start 2026-10-20 --period-end 2026-10-26
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

EVENTS = ("sign_up", "generate_post", "purchase")


def _run_report(property_id: str, start: str, end: str) -> dict[str, int]:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

    client = BetaAnalyticsDataClient()
    req = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        date_ranges=[DateRange(start_date=start, end_date=end)],
    )
    resp = client.run_report(req)
    out = {f"ga4_{n}": 0 for n in EVENTS}
    for row in resp.rows:
        name = row.dimension_values[0].value
        if name in EVENTS:
            out[f"ga4_{name}"] = int(row.metric_values[0].value or 0)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch GA4 event counts for marketing period")
    p.add_argument("--period-start", required=True, help="YYYY-MM-DD (HKT week start)")
    p.add_argument("--period-end", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument("--property-id", default=os.environ.get("GA4_PROPERTY_ID", ""))
    args = p.parse_args()
    pid = (args.property_id or "").strip()
    cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")
    if not pid:
        print("missing GA4_PROPERTY_ID / --property-id", file=sys.stderr)
        return 2
    if not cred or not Path(cred).is_file():
        print("missing or invalid GOOGLE_APPLICATION_CREDENTIALS", file=sys.stderr)
        return 2
    provisional = os.environ.get("GA4_PROVISIONAL", "true").lower() not in ("0", "false", "no")
    metrics = _run_report(pid, args.period_start, args.period_end)
    doc = {
        "schema_version": SCHEMA_VERSION,
        "period_start": args.period_start,
        "period_end": args.period_end,
        "provisional": provisional,
        "source": "ga4_data_api",
        "property_id": pid,
        **metrics,
        "source_notes": (
            "eventCount by eventName; ≠ external customers; "
            "HKT week dates as GA4 date_range; Ads API not in this script"
        ),
    }
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

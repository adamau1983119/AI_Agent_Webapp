#!/usr/bin/env python3
"""Fetch Google Ads spend/clicks/impr for a HKT week. JSON stdout.

API path (needs Basic Access + developer token + OAuth refresh):
  GOOGLE_ADS_DEVELOPER_TOKEN
  GOOGLE_ADS_CUSTOMER_ID          digits only, e.g. 9708645947
  GOOGLE_ADS_CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN
  optional GOOGLE_ADS_LOGIN_CUSTOMER_ID  (MCC)

Handfill path (console paste until API ready):
  python scripts/marketing_period_fetch_ads.py --period-start … --period-end … \\
    --handfill --spend-hkd 26.0 --clicks 22 --impr 2083
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


def _digits(cid: str) -> str:
    return "".join(c for c in (cid or "") if c.isdigit())


def _handfill(start: str, end: str, spend: float, clicks: int, impr: int) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "period_start": start,
        "period_end": end,
        "source": "ads_handfill",
        "ads_spend_hkd": spend,
        "ads_clicks": clicks,
        "ads_impr": impr,
        "source_notes": "Ads handfill from console; API pending Developer Token / Basic Access",
    }


def _api_fetch(start: str, end: str, customer_id: str) -> dict:
    from google.ads.googleads.client import GoogleAdsClient

    cfg = {
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "use_proto_plus": True,
    }
    login = _digits(os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", ""))
    if login:
        cfg["login_customer_id"] = login
    client = GoogleAdsClient.load_from_dict(cfg)
    ga = client.get_service("GoogleAdsService")
    # GAQL dates are inclusive YYYY-MM-DD; metrics in account currency (HKD)
    q = f"""
      SELECT
        metrics.cost_micros,
        metrics.clicks,
        metrics.impressions
      FROM customer
      WHERE segments.date BETWEEN '{start}' AND '{end}'
    """
    spend_micros = 0
    clicks = 0
    impr = 0
    for row in ga.search(customer_id=customer_id, query=q):
        m = row.metrics
        spend_micros += int(m.cost_micros or 0)
        clicks += int(m.clicks or 0)
        impr += int(m.impressions or 0)
    return {
        "schema_version": SCHEMA_VERSION,
        "period_start": start,
        "period_end": end,
        "source": "google_ads_api",
        "customer_id": customer_id,
        "ads_spend_hkd": round(spend_micros / 1_000_000, 2),
        "ads_clicks": clicks,
        "ads_impr": impr,
        "source_notes": "Ads API metrics.cost_micros/1e6 as HKD; HKT week as segments.date",
    }


def _api_ready() -> bool:
    need = (
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
    )
    return all(os.environ.get(k) for k in need)


def main() -> int:
    p = argparse.ArgumentParser(description="Fetch Google Ads metrics for marketing period")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    p.add_argument("--customer-id", default=os.environ.get("GOOGLE_ADS_CUSTOMER_ID", "9708645947"))
    p.add_argument("--handfill", action="store_true", help="Use CLI numbers instead of API")
    p.add_argument("--spend-hkd", type=float, default=None)
    p.add_argument("--clicks", type=int, default=None)
    p.add_argument("--impr", type=int, default=None)
    args = p.parse_args()
    cid = _digits(args.customer_id)
    if args.handfill:
        if args.spend_hkd is None or args.clicks is None or args.impr is None:
            print("--handfill needs --spend-hkd --clicks --impr", file=sys.stderr)
            return 2
        doc = _handfill(args.period_start, args.period_end, args.spend_hkd, args.clicks, args.impr)
        print(json.dumps(doc, ensure_ascii=False, indent=2))
        return 0
    if not _api_ready() or not cid:
        print(
            "Ads API env incomplete. Set GOOGLE_ADS_* or use --handfill "
            "--spend-hkd --clicks --impr",
            file=sys.stderr,
        )
        return 2
    try:
        doc = _api_fetch(args.period_start, args.period_end, cid)
    except Exception as e:  # noqa: BLE001 — surface API errors as JSON exit
        print(f"Ads API failed: {e}", file=sys.stderr)
        return 1
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

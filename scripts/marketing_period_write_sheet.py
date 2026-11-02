#!/usr/bin/env python3
"""Write ops_weekly CSV into the native Google Sheet via user OAuth refresh token.

Env (backend/.env): MARKETING_OPS_SHEET_ID, MARKETING_OPS_SHEET_TAB,
MARKETING_SHEETS_CLIENT_ID, MARKETING_SHEETS_CLIENT_SECRET,
MARKETING_SHEETS_REFRESH_TOKEN.

  python scripts/marketing_period_write_sheet.py --csv docs/evidence/marketing/ops_weekly.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
TOKEN_URI = "https://oauth2.googleapis.com/token"

# Column types — Looker Studio infers the field type from the SHEET CELL FORMAT,
# so numbers must be written as numbers AND get a NUMBER format, otherwise every
# metric is read as text (ABC) and scorecards can only do "count".
DATE_COLS = {"period_start", "period_end"}
INT_COLS = {
    "schema_version", "external_new_users", "external_total_users",
    "valid_members", "active_users_30d", "successful_generations",
    "email_subscribers_total", "email_subscribers_new",
    "ads_clicks", "ads_impr", "ga4_sign_up", "ga4_generate_post", "ga4_purchase",
}
FLOAT_COLS = {"ads_spend_hkd", "revenue_usd", "revenue_hkd_equiv"}
BOOL_COLS = {"provisional"}


def coerce(header: list[str], rows: list[list[str]]) -> list[list[object]]:
    """Turn CSV strings into real numbers / bools so Sheets stores numbers."""
    out: list[list[object]] = [list(header)]
    for r in rows:
        rec: list[object] = []
        for col, raw in zip(header, r):
            v = (raw or "").strip()
            if col in DATE_COLS:
                rec.append(v)
            elif col in BOOL_COLS:
                rec.append(v.lower() in ("true", "1", "yes")) if v else rec.append("")
            elif col in INT_COLS:
                try:
                    rec.append(int(float(v))) if v else rec.append("")
                except ValueError:
                    rec.append(v)
            elif col in FLOAT_COLS:
                try:
                    rec.append(float(v)) if v else rec.append("")
                except ValueError:
                    rec.append(v)
            else:
                rec.append(v)
        out.append(rec)
    return out


def apply_formats(svc, sheet_id: str, tab: str, header: list[str],
                  n_rows: int) -> dict:
    """Set per-column number/date formats so Looker reads typed fields."""
    meta = svc.spreadsheets().get(
        spreadsheetId=sheet_id,
        fields="sheets.properties(sheetId,title)",
    ).execute()
    gid = next(
        s["properties"]["sheetId"] for s in meta["sheets"]
        if s["properties"]["title"] == tab
    )
    reqs = []
    for idx, col in enumerate(header):
        if col in DATE_COLS:
            fmt = {"type": "DATE", "pattern": "yyyy-mm-dd"}
        elif col in INT_COLS:
            fmt = {"type": "NUMBER", "pattern": "#,##0"}
        elif col in FLOAT_COLS:
            fmt = {"type": "NUMBER", "pattern": "#,##0.00"}
        else:
            continue
        reqs.append({"repeatCell": {
            "range": {"sheetId": gid, "startRowIndex": 1,
                      "endRowIndex": 1 + n_rows,
                      "startColumnIndex": idx, "endColumnIndex": idx + 1},
            "cell": {"userEnteredFormat": {"numberFormat": fmt}},
            "fields": "userEnteredFormat.numberFormat",
        }})
    if reqs:
        svc.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={"requests": reqs}).execute()
    return {"formatted_columns": len(reqs)}


def access_token() -> str:
    data = urllib.parse.urlencode(
        {
            "client_id": os.environ["MARKETING_SHEETS_CLIENT_ID"],
            "client_secret": os.environ["MARKETING_SHEETS_CLIENT_SECRET"],
            "refresh_token": os.environ["MARKETING_SHEETS_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request(TOKEN_URI, data=data)
    tok = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return tok["access_token"]


def creds():
    from google.oauth2.credentials import Credentials

    return Credentials(
        token=access_token(),
        refresh_token=os.environ["MARKETING_SHEETS_REFRESH_TOKEN"],
        client_id=os.environ["MARKETING_SHEETS_CLIENT_ID"],
        client_secret=os.environ["MARKETING_SHEETS_CLIENT_SECRET"],
        token_uri=TOKEN_URI,
    )


def main() -> int:
    p = argparse.ArgumentParser(description="Push ops_weekly CSV to the native Google Sheet")
    p.add_argument("--csv", required=True)
    p.add_argument("--sheet-id", default=os.environ.get("MARKETING_OPS_SHEET_ID", ""))
    p.add_argument("--tab", default=os.environ.get("MARKETING_OPS_SHEET_TAB", "ops_weekly"))
    args = p.parse_args()
    if not args.sheet_id:
        print("missing MARKETING_OPS_SHEET_ID", file=sys.stderr)
        return 2

    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        raw = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    if not raw:
        print("empty csv", file=sys.stderr)
        return 2
    header, body_rows = raw[0], raw[1:]
    values = coerce(header, body_rows)

    svc = build("sheets", "v4", credentials=creds(), cache_discovery=False)
    rng = f"'{args.tab}'!A1"
    svc.spreadsheets().values().clear(
        spreadsheetId=args.sheet_id, range=f"'{args.tab}'!A:AZ", body={}
    ).execute()
    res = svc.spreadsheets().values().update(
        spreadsheetId=args.sheet_id,
        range=rng,
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()
    fmt = apply_formats(svc, args.sheet_id, args.tab, header, len(body_rows))

    back = svc.spreadsheets().values().get(
        spreadsheetId=args.sheet_id, range=f"'{args.tab}'!A1:AZ20",
        valueRenderOption="UNFORMATTED_VALUE",
    ).execute()
    rows = back.get("values", [])
    typed = {}
    if rows:
        for i, col in enumerate(rows[0]):
            if col in (INT_COLS | FLOAT_COLS | DATE_COLS):
                sample = next((r[i] for r in rows[1:] if i < len(r)), None)
                typed[col] = type(sample).__name__
    print(json.dumps({
        "sheet_id": args.sheet_id,
        "tab": args.tab,
        "wrote_rows": len(values),
        "updated_cells": res.get("updatedCells"),
        "formatted_columns": fmt["formatted_columns"],
        "readback_rows": len(rows),
        "periods": [r[0] for r in rows[1:]] if rows else [],
        "column_types": typed,
        "url": f"https://docs.google.com/spreadsheets/d/{args.sheet_id}/edit",
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

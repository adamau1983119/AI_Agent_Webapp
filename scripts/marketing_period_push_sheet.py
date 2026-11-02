#!/usr/bin/env python3
"""Push week snapshots to Google Sheet for Looker. No PII. Replaces manual paste.

Env:
  GOOGLE_APPLICATION_CREDENTIALS  service-account JSON (share Sheet Editor to SA)
  MARKETING_OPS_SHEET_ID          spreadsheet id
  MARKETING_OPS_SHEET_TAB         tab name (default ops_weekly)

  python scripts/marketing_period_push_sheet.py --all
  python scripts/marketing_period_push_sheet.py --period-start 2026-10-27
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_sheet_io import (  # noqa: E402
    SHEET_COLS,
    load_week_snapshots,
    row_values,
    snapshot_to_row,
)

SCOPES = ("https://www.googleapis.com/auth/spreadsheets",)
DEFAULT_SHEET_ID = "109Xw93X8VEQNc4yxRzIJF7-VhAjeNkycxstLyucneK8"


def _sheets_service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not cred_path or not Path(cred_path).is_file():
        raise SystemExit("missing GOOGLE_APPLICATION_CREDENTIALS file")
    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _cell(v: object) -> object:
    if v is None:
        return ""
    if isinstance(v, bool):
        return v
    return v


def push_rows(sheet_id: str, tab: str, weeks: list[dict]) -> int:
    from googleapiclient.errors import HttpError

    values: list[list[object]] = [list(SHEET_COLS)]
    for doc in weeks:
        values.append([_cell(x) for x in row_values(snapshot_to_row(doc))])
    svc = _sheets_service()
    rng = f"'{tab}'"
    try:
        svc.spreadsheets().values().clear(
            spreadsheetId=sheet_id, range=rng, body={}
        ).execute()
        svc.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=f"'{tab}'!A1",
            valueInputOption="USER_ENTERED",
            body={"values": values},
        ).execute()
    except HttpError as e:
        msg = str(e)
        hint = ""
        if "SERVICE_DISABLED" in msg or "has not been used" in msg:
            hint = (
                " Enable Google Sheets API on the GCP project that owns "
                "GOOGLE_APPLICATION_CREDENTIALS, then retry."
            )
        elif (
            "PERMISSION_DENIED" in msg
            or "403" in msg
            or "404" in msg
            or "not found" in msg.lower()
        ):
            hint = (
                " Share the Sheet (Editor) with the service-account client_email "
                "(Google often returns 404 if unshared), then retry."
            )
        raise SystemExit(f"Sheets API failed: {e}.{hint}") from e
    return len(weeks)


def main() -> int:
    p = argparse.ArgumentParser(description="Push marketing snapshots to Google Sheet")
    p.add_argument("--period-start", help="Single week start YYYY-MM-DD")
    p.add_argument("--all", action="store_true", help="All week snapshots")
    p.add_argument(
        "--sheet-id",
        default=os.environ.get("MARKETING_OPS_SHEET_ID", DEFAULT_SHEET_ID),
    )
    p.add_argument(
        "--tab",
        default=os.environ.get("MARKETING_OPS_SHEET_TAB", "ops_weekly"),
    )
    args = p.parse_args()
    if not args.all and not args.period_start:
        print("need --period-start or --all", file=sys.stderr)
        return 2
    if not args.sheet_id:
        print("need MARKETING_OPS_SHEET_ID or --sheet-id", file=sys.stderr)
        return 2
    weeks = asyncio.run(load_week_snapshots(args.period_start, args.all))
    n = push_rows(args.sheet_id, args.tab, weeks)
    print(f"pushed {n} row(s) → sheet {args.sheet_id} tab={args.tab}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export week snapshot(s) to CSV for Google Sheet / Looker. No PII.

  python scripts/marketing_period_export_sheet.py --period-start 2026-10-20 --out docs/evidence/marketing/ops_weekly.csv
  python scripts/marketing_period_export_sheet.py --all --out docs/evidence/marketing/ops_weekly.csv
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_sheet_io import SHEET_COLS, load_week_snapshots, snapshot_to_row  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser(description="Export marketing snapshots to CSV for Sheet/Looker")
    p.add_argument("--period-start", help="Single week start YYYY-MM-DD")
    p.add_argument("--all", action="store_true", help="All week snapshots")
    p.add_argument("--out", required=True, help="CSV path")
    args = p.parse_args()
    if not args.all and not args.period_start:
        print("need --period-start or --all", file=sys.stderr)
        return 2
    weeks = asyncio.run(load_week_snapshots(args.period_start, args.all))
    path = Path(args.out)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(SHEET_COLS))
        w.writeheader()
        for doc in weeks:
            w.writerow(snapshot_to_row(doc))
    print(f"wrote {len(weeks)} row(s) → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

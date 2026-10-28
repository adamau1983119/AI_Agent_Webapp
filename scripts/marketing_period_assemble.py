#!/usr/bin/env python3
"""Assemble week draft: Mongo counts + optional GA4/Ads JSON.

  python scripts/marketing_period_assemble.py --period-start 2026-10-20 --period-end 2026-10-26
  python scripts/marketing_period_assemble.py ... --ga4-file ga4.json --ads-file ads.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from marketing_period_lib import SCHEMA_VERSION  # noqa: E402


def _run_counts(start: str, end: str) -> dict:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "marketing_period_counts.py"),
        "--period-start",
        start,
        "--period-end",
        end,
    ]
    raw = subprocess.check_output(cmd, cwd=str(ROOT), text=True)
    text = raw.strip()
    if not text.startswith("{"):
        i = text.find("{")
        text = text[i:] if i >= 0 else text
    return json.loads(text)


def _load_json(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main() -> int:
    p = argparse.ArgumentParser(description="Assemble marketing week draft JSON")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    p.add_argument("--ga4-file", help="JSON from marketing_period_fetch_ga4.py")
    p.add_argument("--ads-file", help="JSON from marketing_period_fetch_ads.py")
    p.add_argument("--out", help="Write draft path (default stdout)")
    p.add_argument(
        "--provisional",
        choices=["true", "false", "auto"],
        default="auto",
        help="Override provisional (auto=from GA4 file / default true)",
    )
    args = p.parse_args()
    counts = _run_counts(args.period_start, args.period_end)
    ga4 = _load_json(args.ga4_file)
    ads = _load_json(args.ads_file)
    core = dict(counts.get("core") or {})
    for k in ("ga4_sign_up", "ga4_generate_post", "ga4_purchase"):
        if k in ga4:
            core[k] = ga4[k]
        else:
            core.setdefault(k, None)
    for k in ("ads_spend_hkd", "ads_clicks", "ads_impr"):
        if k in ads:
            core[k] = ads[k]
        else:
            core.setdefault(k, None)
    core.setdefault("revenue_usd", None)
    if args.provisional == "auto":
        provisional = bool(ga4.get("provisional", True)) if ga4 else True
    else:
        provisional = args.provisional == "true"
    notes = [counts.get("source_notes") or ""]
    notes.append(ga4.get("source_notes") if ga4 else "ga4 not provided; ga4_* null")
    notes.append(ads.get("source_notes") if ads else "ads not provided; ads_* null")
    draft = {
        "schema_version": SCHEMA_VERSION,
        "period_type": "week",
        "period_start": args.period_start,
        "period_end": args.period_end,
        "env": "production",
        "provisional": provisional,
        "core": core,
        "focus": {"theme": "hygiene", "metrics": {}, "notes": ""},
        "segments": {},
        "source_notes": "; ".join(x for x in notes if x),
    }
    text = json.dumps(draft, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

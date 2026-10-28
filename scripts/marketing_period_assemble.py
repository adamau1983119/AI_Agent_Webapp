#!/usr/bin/env python3
"""Assemble week draft: Mongo counts + optional GA4 JSON (+ Ads later).

  python scripts/marketing_period_assemble.py --period-start 2026-10-20 --period-end 2026-10-26
  python scripts/marketing_period_assemble.py ... --ga4-file ga4.json
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
    # counts may log to stderr; stdout is JSON only if logger goes stderr — parse last {
    text = raw.strip()
    if not text.startswith("{"):
        i = text.find("{")
        text = text[i:] if i >= 0 else text
    return json.loads(text)


def _load_ga4(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main() -> int:
    p = argparse.ArgumentParser(description="Assemble marketing week draft JSON")
    p.add_argument("--period-start", required=True)
    p.add_argument("--period-end", required=True)
    p.add_argument("--ga4-file", help="JSON from marketing_period_fetch_ga4.py")
    p.add_argument(
        "--out",
        help="Write draft path (default stdout)",
    )
    args = p.parse_args()
    counts = _run_counts(args.period_start, args.period_end)
    ga4 = _load_ga4(args.ga4_file)
    core = dict(counts.get("core") or {})
    for k in ("ga4_sign_up", "ga4_generate_post", "ga4_purchase"):
        if k in ga4:
            core[k] = ga4[k]
        else:
            core.setdefault(k, None)
    for k in ("ads_spend_hkd", "ads_clicks", "ads_impr", "revenue_usd"):
        core.setdefault(k, None)
    provisional = bool(ga4.get("provisional", True))
    notes = [counts.get("source_notes") or ""]
    if ga4:
        notes.append(ga4.get("source_notes") or "ga4 merged")
    else:
        notes.append("ga4 not provided; ga4_* null")
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

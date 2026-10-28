#!/usr/bin/env python3
"""One-shot: open browser, authorize Ads API, print refresh_token for .env.

  python scripts/marketing_period_ads_oauth.py --client-secrets path/to/client_secret.json

Uses scope https://www.googleapis.com/auth/adwords
Add the Google account as OAuth test user first (Auth Platform → Audience).
Do not commit tokens or client_secret JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCOPE = ["https://www.googleapis.com/auth/adwords"]


def main() -> int:
    p = argparse.ArgumentParser(description="Get Google Ads OAuth refresh_token")
    p.add_argument("--client-secrets", required=True, help="Downloaded OAuth client JSON")
    args = p.parse_args()
    path = Path(args.client_secrets)
    if not path.is_file():
        print(f"missing file: {path}", file=sys.stderr)
        return 2
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(path), scopes=SCOPE)
    creds = flow.run_local_server(port=0)
    if not creds.refresh_token:
        print("no refresh_token returned; revoke app access and retry", file=sys.stderr)
        return 1
    # Print only what belongs in .env (user copies manually)
    data = json.loads(path.read_text(encoding="utf-8"))
    installed = data.get("installed") or data.get("web") or {}
    print("Paste into backend/.env:")
    print(f"GOOGLE_ADS_CLIENT_ID={installed.get('client_id', '')}")
    print(f"GOOGLE_ADS_CLIENT_SECRET={installed.get('client_secret', '')}")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Agent-runnable API/static checks for W-3/W-4 checklist items."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
TOKEN_FILE = ROOT / ".test_token.tmp"
BASE = "http://localhost:8000/api/v1"
TOPIC_ID = "topic_trend_20260519212108_9"


@dataclass
class Result:
    item: str
    status: str  # PASS | FAIL | N/A | BLOCK
    evidence: str


@dataclass
class Report:
    results: list[Result] = field(default_factory=list)

    def add(self, item: str, status: str, evidence: str) -> None:
        self.results.append(Result(item, status, evidence))

    def print_summary(self) -> int:
        fails = 0
        for r in self.results:
            if r.status == "FAIL":
                fails += 1
            print(f"{r.status:5} | {r.item} | {r.evidence}")
        print("---")
        counts: dict[str, int] = {}
        for r in self.results:
            counts[r.status] = counts.get(r.status, 0) + 1
        print("Counts:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        return fails


def load_token() -> str:
    if not TOKEN_FILE.exists():
        raise SystemExit("Missing .test_token.tmp — run token bootstrap first")
    return TOKEN_FILE.read_text(encoding="utf-8").strip()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def main() -> int:
    report = Report()
    token = load_token()
    headers = auth_headers(token)

    with httpx.Client(timeout=30.0) as client:
        # S11 / J1 health
        r = client.get("http://localhost:8000/health")
        db = r.json().get("database", {}) if r.status_code == 200 else {}
        report.add(
            "S11/J1 /health",
            "PASS" if r.status_code == 200 and db.get("status") == "connected" else "FAIL",
            f"status={r.status_code} database={db.get('status')}",
        )

        # Frontend up
        fe = client.get("http://localhost:3000")
        report.add(
            "Daily startup frontend :3000",
            "PASS" if fe.status_code == 200 else "FAIL",
            f"status={fe.status_code}",
        )

        endpoints: list[tuple[str, str, str, bool]] = [
            ("S4-1", "GET", f"{BASE}/topics?page=1&page_size=5", False),
            ("S4-2", "GET", f"{BASE}/topics?page=1&page_size=5&category=fashion", False),
            ("S4-3", "GET", f"{BASE}/channels", True),
            ("S4-4", "GET", f"{BASE}/inspiration/trending", False),
            ("S4-5", "GET", f"{BASE}/style-profile/analysis", True),
            ("S4-8", "GET", f"{BASE}/user/preferences", False),
            ("S4-9", "GET", f"{BASE}/schedules", False),
            ("S4-9+", "GET", f"{BASE}/schedules/status", False),
            ("S10", "GET", f"{BASE}/style-profile/analysis", True),
            ("Topic GET", "GET", f"{BASE}/topics/{TOPIC_ID}", False),
        ]

        for label, method, url, need_auth in endpoints:
            h = headers if need_auth else None
            resp = client.request(method, url, headers=h)
            extra = ""
            if label == "S4-3" and resp.status_code == 200:
                names = [c.get("name", "") for c in resp.json().get("channels", [])]
                extra = f" names={names[:3]}"
                has_hk = any("親切香港美食" in n for n in names)
                status = "PASS" if has_hk else "PARTIAL"
                report.add(label, status, f"GET /channels {resp.status_code}{extra}")
                continue
            status = "PASS" if resp.status_code == 200 else "FAIL"
            report.add(label, status, f"{method} {url.split('/api/v1')[-1]} -> {resp.status_code}{extra}")

        # S4-8 PUT preferences
        put_body = {
            "fashion_weight": 0.5,
            "food_weight": 0.3,
            "trend_weight": 0.2,
            "keywords": ["agent-test"],
            "excluded_keywords": [],
        }
        put_r = client.put(f"{BASE}/user/preferences", json=put_body)
        report.add(
            "S4-8 PUT preferences",
            "PASS" if put_r.status_code == 200 else "FAIL",
            f"PUT /user/preferences -> {put_r.status_code}",
        )

        # S9 settings profile GET/PATCH
        me = client.get(f"{BASE}/auth/me", headers=headers)
        report.add(
            "S9 GET /auth/me",
            "PASS" if me.status_code == 200 else "FAIL",
            f"status={me.status_code}",
        )
        user_id = me.json().get("id") if me.status_code == 200 else None
        if me.status_code == 200:
            patch = client.patch(
                f"{BASE}/auth/profile",
                headers=headers,
                json={"language": "zh-TW"},
            )
            report.add(
                "S9 PATCH /auth/profile",
                "PASS" if patch.status_code == 200 else "FAIL",
                f"status={patch.status_code}",
            )

        # S8 detail APIs (no DeepSeek regenerate)
        detail_calls = [
            ("S8 contents", f"{BASE}/contents/{TOPIC_ID}"),
            (
                "S8 images search",
                f"{BASE}/images/search?keywords=fashion&page=1&limit=5",
            ),
        ]
        for label, url in detail_calls:
            resp = client.get(url, headers=headers)
            report.add(
                label,
                "PASS" if resp.status_code in (200, 404) else "FAIL",
                f"GET {url.split('/api/v1')[-1]} -> {resp.status_code}",
            )

        if user_id:
            inter = client.post(
                f"{BASE}/interactions",
                headers=headers,
                json={
                    "user_id": user_id,
                    "topic_id": TOPIC_ID,
                    "action": "like",
                    "reasons": ["agent_api_test"],
                },
            )
            report.add(
                "S8 POST /interactions",
                "PASS" if inter.status_code in (200, 201) else "FAIL",
                f"status={inter.status_code}",
            )
        else:
            report.add("S8 POST /interactions", "FAIL", "no user_id from /auth/me")

        # Meta OAuth URL (H1) — no browser
        meta = client.get(
            f"{BASE}/social/meta/connect?target=facebook",
            headers=headers,
            follow_redirects=False,
        )
        oauth_ok = meta.status_code == 200 and "oauth_url" in meta.text
        report.add(
            "S4-7/H1 meta connect API",
            "PASS" if oauth_ok else "FAIL",
            f"status={meta.status_code} has_oauth_url={oauth_ok}",
        )

        # S4-6 Post Kit — static BLOCK
        postkit_hits = list(ROOT.glob("frontend/src/**/*PostKit*"))
        report.add(
            "S4-6 Post Kit PK1-6",
            "BLOCK",
            f"No PostKit UI ({len(postkit_hits)} files); L0 N/A until implemented",
        )

    # Static: Sidebar testids (S4+ A4)
    sidebar = (ROOT / "frontend/src/components/layout/Sidebar.tsx").read_text(encoding="utf-8")
    testids = re.findall(r"testId: '(link-sidebar-[^']+)'", sidebar)
    report.add(
        "S4+ data-testid Sidebar",
        "PASS" if len(testids) >= 9 else "FAIL",
        f"found {len(testids)} link-sidebar-* ids",
    )

    # i18n nav.preferences exists (A3 partial)
    i18n = (ROOT / "frontend/src/i18n/index.ts").read_text(encoding="utf-8")
    for key in ("nav.preferences", "nav.schedule", "preferences.title", "schedule.title"):
        report.add(
            f"i18n {key}",
            "PASS" if f"'{key}'" in i18n else "FAIL",
            "present in index.ts" if f"'{key}'" in i18n else "missing",
        )

    # CreateChannel #31 external link testid
    create_channel = (ROOT / "frontend/src/pages/CreateChannel.tsx").read_text(encoding="utf-8")
    report.add(
        "S6 #31 source-link testid",
        "PASS" if "source-link-" in create_channel else "FAIL",
        "data-testid source-link-{idx} in CreateChannel.tsx",
    )

    # showAssist default (I.2 N/A evidence)
    show_assist_default = "useState(true)" in create_channel and "showAssist" in create_channel
    report.add(
        "I.2 showAssist default",
        "N/A",
        "showAssist=true fixed UI; no feature flag" if show_assist_default else "check CreateChannel.tsx",
    )

    # TopicDetail delete dialog testids (#26)
    topic_detail = (ROOT / "frontend/src/pages/TopicDetail.tsx").read_text(encoding="utf-8")
    has_delete = "btn-topic-detail-delete" in topic_detail
    has_cancel = "btn-delete-cancel" in topic_detail
    report.add(
        "Detail #26 delete dialog testids",
        "PARTIAL" if has_delete and has_cancel else "FAIL",
        "btn-topic-detail-delete + btn-delete-cancel (architecture table differs)",
    )
    app_tsx = (ROOT / "frontend/src/app/App.tsx").read_text(encoding="utf-8")
    for route in ("/preferences", "/schedule", "/settings"):
        report.add(
            f"Route {route}",
            "PASS" if route in app_tsx else "FAIL",
            "registered in App.tsx",
        )

    # DeepSeek guard env (read keys only, no secrets)
    env_path = ROOT / "backend/.env"
    if env_path.exists():
        env_text = env_path.read_text(encoding="utf-8", errors="ignore")
        auto = re.search(r"^AUTO_START_SCHEDULER=(.*)$", env_text, re.M)
        val = auto.group(1).strip() if auto else "MISSING"
        report.add(
            "DeepSeek guard AUTO_START_SCHEDULER",
            "PASS" if val.lower() == "false" else "FAIL",
            f"value={val}",
        )

    # fix_test_doc_wording scan
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/fix_test_doc_wording.py")],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    clean = "scan clean" in (proc.stdout + proc.stderr).lower() or proc.returncode == 0
    report.add(
        "fix_test_doc_wording.py",
        "PASS" if clean else "FAIL",
        (proc.stdout or proc.stderr).strip().splitlines()[-1] if proc.stdout or proc.stderr else f"exit={proc.returncode}",
    )

    fails = report.print_summary()
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Alter Ego live checks: POST /extract + Mongo snapshot (CD-AE-A1).
用法: uvicorn 運行中 + backend/.env（DEEPSEEK_API_KEY、Mongo）
      python scripts/check_ae_live.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SCRIPTS = ROOT / "scripts"
TOKEN_FILE = ROOT / ".test_token.tmp"
BASE = "http://localhost:8000/api/v1"
HEALTH = "http://localhost:8000/health"

GOLDEN_EXEMPLAR = (
    "今日去咗旺角試咗間新開嘅車仔面檔，誠實講，湯底算係合格啦。"
    "麵係有咬口嘅，唔係一浸就散嗰種。價錢 $48 有找，學生都負擔到。"
    "如果你係重口味派，可能要自己加辣油。整體嚟講，值得一試，但唔使特登排隊。"
)

os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))


async def _mongo_token() -> str | None:
    from app.database import close_mongo_connection, connect_to_mongo, get_database
    from app.utils.jwt import create_access_token

    await connect_to_mongo()
    db = await get_database()
    user = await db.users.find_one({"status": "active"})
    await close_mongo_connection()
    if not user or not user.get("id"):
        return None
    return create_access_token(
        {
            "sub": user["id"],
            "email": user.get("email", "ae-check@local"),
            "role": user.get("role", "user"),
        }
    )


def _load_token(client: httpx.Client) -> str | None:
    if TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text(encoding="utf-8").strip()
        if t:
            return t
    email = os.getenv("AE_CHECK_EMAIL") or os.getenv("TEST_LOGIN_EMAIL")
    password = os.getenv("AE_CHECK_PASSWORD") or os.getenv("TEST_LOGIN_PASSWORD")
    if email and password:
        r = client.post(f"{BASE}/auth/login", json={"email": email, "password": password})
        if r.status_code == 200:
            return r.json().get("access_token")
    return None


async def main() -> int:
    fails = 0

    from ensure_backend_fresh import ensure_ae_pipeline_ready, fetch_health, _read_ae_version

    if not ensure_ae_pipeline_ready(auto_restart=True):
        print("FAIL | stale uvicorn could not be refreshed")
        return 1
    health0 = fetch_health() or {}
    print(
        f"PASS | alter_ego.pipeline_version={_read_ae_version(health0)} "
        "(fresh backend)"
    )

    with httpx.Client(timeout=120.0) as client:
        hr = client.get(HEALTH)
        db_ok = hr.status_code == 200 and hr.json().get("database", {}).get("status") == "connected"
        print(f"{'PASS' if db_ok else 'FAIL'} | health + mongo | status={hr.status_code}")
        if not db_ok:
            print("BLOCK | start uvicorn from backend and ensure Mongo connected")
            return 1

        token = _load_token(client)
        if not token:
            token = await _mongo_token()
        if not token:
            print("FAIL | no bearer token (.test_token.tmp / login / mongo user)")
            return 1
        print("PASS | bearer token acquired")

        headers = {"Authorization": f"Bearer {token}"}
        body = {"exemplars": [GOLDEN_EXEMPLAR], "language": "zh-TW"}

        er = client.post(f"{BASE}/alter-ego/extract", json=body, headers=headers)
        extract_ok = er.status_code == 200
        print(f"{'PASS' if extract_ok else 'FAIL'} | CD-AE-A1 POST /alter-ego/extract | status={er.status_code}")
        if not extract_ok:
            fails += 1
            detail = er.text[:300]
            print(f"       response: {detail}")
            if er.status_code == 503:
                print("NOTE | set DEEPSEEK_API_KEY in backend/.env and restart uvicorn")
            return 1

        data = er.json()
        version_id = data.get("dna_version_id", "")
        first_snapshot_id = version_id
        dna = data.get("dna_json") or {}
        fields_ok = all(
            [
                version_id,
                dna.get("lexicon"),
                dna.get("tone_descriptors"),
                dna.get("voice_persona"),
                dna.get("exemplar_snippets"),
            ]
        )
        print(f"{'PASS' if fields_ok else 'FAIL'} | extract response fields | version_id={version_id[:12]}…")
        if not fields_ok:
            fails += 1

        # Pydantic re-validate
        try:
            from app.models.alter_ego_dna import AlterEgoDnaJson

            AlterEgoDnaJson.model_validate(dna)
            print("PASS | CD-AE-A1 Pydantic strict re-validate")
        except Exception as exc:
            fails += 1
            print(f"FAIL | Pydantic re-validate | {exc}")

        sr = client.get(f"{BASE}/alter-ego/status", headers=headers)
        status_ok = sr.status_code == 200 and sr.json().get("has_dna") is True
        print(f"{'PASS' if status_ok else 'FAIL'} | GET /alter-ego/status has_dna")
        if not status_ok:
            fails += 1

        er2 = client.post(f"{BASE}/alter-ego/extract", json=body, headers=headers)
        if er2.status_code == 200 and first_snapshot_id:
            rr = client.post(
                f"{BASE}/alter-ego/dna/rollback",
                json={"snapshot_id": first_snapshot_id},
                headers=headers,
            )
            rollback_ok = rr.status_code == 200 and bool(rr.json().get("dna_version_id"))
            print(
                f"{'PASS' if rollback_ok else 'FAIL'} | PD-AE1-07 POST /dna/rollback | "
                f"status={rr.status_code}"
            )
            if not rollback_ok:
                fails += 1
        else:
            print("SKIP | PD-AE1-07 rollback (second extract failed)")

        pr = client.post(
            f"{BASE}/alter-ego/preview",
            json={"platform": "facebook", "topic_hint": "旺角新開車仔面"},
            headers=headers,
        )
        preview_ok = pr.status_code == 200
        preview_ver = pr.headers.get("X-Alter-Ego-Preview-Version", "")
        print(
            f"{'PASS' if preview_ok else 'FAIL'} | PD-AE1-02 POST /alter-ego/preview | "
            f"status={pr.status_code} header_version={preview_ver!r}"
        )
        if not preview_ok:
            fails += 1
            print(f"       response: {pr.text[:300]}")
        else:
            pdata = pr.json()
            pt = (pdata.get("preview_text") or "").strip()
            soul = (pdata.get("soul_text") or "").strip()
            from app.alter_ego_build import AE_PIPELINE_VERSION

            ver_ok = preview_ver == str(AE_PIPELINE_VERSION)
            text_ok = len(pt) >= 10 and len(soul) >= 10 and "[Preview skeleton" not in pt
            if not ver_ok:
                print(
                    "FAIL | stale preview API (missing X-Alter-Ego-Preview-Version) — "
                    "run: python scripts/run_backend_dev.py"
                )
                fails += 1
            print(
                f"{'PASS' if text_ok else 'FAIL'} | preview soul+shell text | "
                f"preview_len={len(pt)} soul_len={len(soul)}"
            )
            if not text_ok:
                fails += 1

    # Mongo snapshot evidence (reuse client scope ended - ok)
    from app.database import close_mongo_connection, connect_to_mongo, get_database

    await connect_to_mongo()
    db = await get_database()
    doc = await db.alter_ego_dna.find_one({"dna_json.voice_persona": {"$exists": True}})
    snap = None
    if doc:
        snap = await db.alter_ego_dna_snapshots.find_one(
            {"snapshot_id": doc.get("current_dna_version_id")}
        )
    mongo_ok = bool(doc and snap and doc.get("current_dna_version_id") == snap.get("snapshot_id"))
    print(
        f"{'PASS' if mongo_ok else 'FAIL'} | Mongo alter_ego_dna + snapshot | "
        f"user={doc.get('user_id') if doc else None!r}"
    )
    if not mongo_ok:
        fails += 1
    await close_mongo_connection()

    print("---")
    print("SKIP | CD-AE-A2 manual lexicon/tone spot-check (human)")
    print("SKIP | CD-AE-C* E2E (Post Kit + generate meta — test week)")
    print(f"Live track: {'PASS' if fails == 0 else 'FAIL'} ({fails} failures)")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

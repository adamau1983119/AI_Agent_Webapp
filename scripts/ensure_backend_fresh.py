#!/usr/bin/env python3
"""
確保本機 uvicorn 已載入目前程式（Alter Ego pipeline_version 對照）。
過期進程 → 結束 :8000 → 以 --reload 重啟 → 等待 /health。
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

import httpx

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
HEALTH_URL = "http://127.0.0.1:8000/health"
# 與 backend/app/alter_ego_build.py 同步
REQUIRED_AE_PIPELINE_VERSION = 4
_STARTUP_TIMEOUT_SEC = 45


def _read_ae_version(health_json: dict[str, Any]) -> Optional[int]:
    ae = health_json.get("alter_ego") or {}
    ver = ae.get("pipeline_version")
    if ver is None:
        return None
    try:
        return int(ver)
    except (TypeError, ValueError):
        return None


def fetch_health() -> Optional[dict[str, Any]]:
    try:
        r = httpx.get(HEALTH_URL, timeout=3.0)
        if r.status_code == 200:
            return r.json()
    except httpx.HTTPError:
        pass
    return None


def is_pipeline_fresh(health_json: Optional[dict[str, Any]] = None) -> bool:
    data = health_json if health_json is not None else fetch_health()
    if not data:
        return False
    ver = _read_ae_version(data)
    return ver is not None and ver >= REQUIRED_AE_PIPELINE_VERSION


def kill_port(port: int = 8000) -> None:
    if sys.platform == "win32":
        ps = (
            f"$p = Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | "
            f"Select-Object -First 1 -ExpandProperty OwningProcess; "
            f"if ($p) {{ Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }}"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False)
    else:
        subprocess.run(
            ["sh", "-c", f"lsof -ti:{port} | xargs -r kill -9"],
            check=False,
        )


def start_uvicorn_reload() -> subprocess.Popen:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=str(BACKEND),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def ensure_ae_pipeline_ready(*, auto_restart: bool = True) -> bool:
    """
    回傳 True 若 /health alter_ego.pipeline_version 已達標。
    auto_restart=False 時僅檢查不重启。
    """
    health = fetch_health()
    if is_pipeline_fresh(health):
        return True
    if not auto_restart:
        return False

    print(
        f"BLOCK | stale uvicorn (need alter_ego.pipeline_version>={REQUIRED_AE_PIPELINE_VERSION}); "
        "restarting with --reload..."
    )
    kill_port(8000)
    time.sleep(1.5)
    start_uvicorn_reload()

    deadline = time.time() + _STARTUP_TIMEOUT_SEC
    while time.time() < deadline:
        time.sleep(1.0)
        health = fetch_health()
        if is_pipeline_fresh(health):
            print(f"PASS | backend fresh | alter_ego.pipeline_version={_read_ae_version(health)}")
            return True

    print(
        f"FAIL | backend not fresh after {_STARTUP_TIMEOUT_SEC}s — "
        f"manual: cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
    )
    return False


if __name__ == "__main__":
    ok = ensure_ae_pipeline_ready(auto_restart="--no-restart" not in sys.argv)
    raise SystemExit(0 if ok else 1)

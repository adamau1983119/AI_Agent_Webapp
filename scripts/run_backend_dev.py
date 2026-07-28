#!/usr/bin/env python3
"""本機後端：結束舊 :8000 進程，以 uvicorn --reload 啟動（改碼自動重載）。"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

# 重用 ensure 模組的 kill
sys.path.insert(0, str(ROOT / "scripts"))
from ensure_backend_fresh import kill_port  # noqa: E402


def main() -> int:
    kill_port(8000)
    print("Starting uvicorn --reload on http://127.0.0.1:8000 ...")
    proc = subprocess.Popen(
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
    )
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    return proc.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())

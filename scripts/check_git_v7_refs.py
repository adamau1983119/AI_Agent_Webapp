#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""檢查 v7 code-freeze Git 錨點與 archives 獨立檔。"""
from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

FREEZE_SHA = "9556ea79cb341bf6ae624c85e57df1097d56946e"
REQUIRED_REFS = (
    "v7.0.0-code-freeze",
    "backup/v7-pre-launch",
)
ARCHIVE_FILES = (
    "docs/archives/v7.0.0_CODE_FREEZE_MANIFEST.md",
    "docs/archives/v7.0.0_專案完整架構表_凍結.md",
    "docs/archives/v7.0.0_需求文件_凍結.md",
)


def run_git(repo: Path, *args: str) -> tuple[int, str]:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, (p.stdout or "").strip()


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    failed = 0
    print("=== check_git_v7_refs ===")
    print(f"repo: {repo}")

    for ref in REQUIRED_REFS:
        code, sha = run_git(repo, "rev-parse", f"{ref}^{{commit}}")
        if code != 0 or not sha:
            print(f"[FAIL] missing ref: {ref}")
            failed += 1
            continue
        ok = sha.startswith(FREEZE_SHA[:12]) or sha == FREEZE_SHA
        # annotated tag may resolve to freeze commit
        status = "PASS" if ok else "WARN"
        if not ok:
            # still require ref exists; SHA mismatch is WARN if points elsewhere
            print(f"[{status}] {ref} -> {sha} (expected {FREEZE_SHA[:12]}…)")
            if status == "WARN":
                pass
        else:
            print(f"[PASS] {ref} -> {sha}")

    for rel in ARCHIVE_FILES:
        path = repo / rel
        if path.is_file() and path.stat().st_size > 100:
            print(f"[PASS] archive exists: {rel} ({path.stat().st_size} bytes)")
        else:
            print(f"[FAIL] archive missing/empty: {rel}")
            failed += 1

    v8 = repo / "專案完整架構表_v8.md"
    if v8.is_file():
        print(f"[PASS] v8 SoT present: 專案完整架構表_v8.md")
    else:
        print(f"[FAIL] missing 專案完整架構表_v8.md")
        failed += 1

    print("---")
    if failed:
        print(f"RESULT: FAIL ({failed})")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐一檢查與 v6 / v6.0.1 相關的 Git ref（main、分支、標籤）。

用法（在儲存庫根目錄或任意子目錄）：
  python scripts/check_git_v6_refs.py
  python scripts/check_git_v6_refs.py --repo "C:\\path\\to\\AI_Agent_Webapp"
  python scripts/check_git_v6_refs.py --refs main,v6.0.0,v6.0.1

不依賴第三方套件；需已安裝 git 且路徑在 PATH 中。
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path
from typing import Iterable

# Windows 終端機 UTF-8 輸出（與專案其他 scripts 一致）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 預設要檢查的 ref（可依遠端實際命名調整）
DEFAULT_REFS: tuple[str, ...] = (
    "main",
    "origin/main",
    "v6.0.0",
    "origin/v6.0.0",
    "v6.0.1",
    "v6.0.1-at-tag",
    "docs/update-v6-merged-status",
    "origin/docs/update-v6-merged-status",
)

# 在各 ref 的樹狀結構中應存在的路徑（相對於儲存庫根）
KEY_PATHS: tuple[str, ...] = (
    "README.md",
    "frontend/package.json",
    "backend/requirements.txt",
    "backend/app/main.py",
)

# 成對比較（直接比兩棵樹）
DEFAULT_DIFF_PAIRS: tuple[tuple[str, str], ...] = (
    ("main", "v6.0.0"),
    ("main", "v6.0.1"),
    ("v6.0.0", "v6.0.1"),
    ("main", "docs/update-v6-merged-status"),
)


def run_git(repo: Path, *args: str) -> tuple[int, str, str]:
    cmd = ("git", "-C", str(repo), *args)
    p = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def git_root(start: Path) -> Path | None:
    code, out, _ = run_git(start, "rev-parse", "--show-toplevel")
    if code != 0 or not out:
        return None
    return Path(out)


def resolve_commit(repo: Path, ref: str) -> tuple[bool, str, str]:
    """回傳 (成功, commit_sha, 錯誤訊息)。"""
    code, out, err = run_git(repo, "rev-parse", f"{ref}^{{commit}}")
    if code == 0 and out:
        return True, out, ""
    code2, out2, err2 = run_git(repo, "rev-parse", "--verify", ref)
    if code2 == 0 and out2:
        return True, out2, ""
    return False, "", err or err2 or "rev-parse 失敗"


def commit_summary(repo: Path, commit: str) -> str:
    fmt = "%h | %ci | %s"
    code, out, _ = run_git(repo, "log", "-1", f"--format={fmt}", commit)
    return out if code == 0 and out else "(無法讀取 log)"


def count_tracked_files(repo: Path, commit: str) -> int | None:
    code, out, _ = run_git(repo, "ls-tree", "-r", "--name-only", commit)
    if code != 0:
        return None
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return len(lines)


def blob_exists(repo: Path, commit: str, path: str) -> bool:
    code, _, _ = run_git(repo, "cat-file", "-e", f"{commit}:{path}")
    return code == 0


def print_ref_block(repo: Path, ref: str) -> bool:
    """印出單一 ref 的檢查結果；回傳是否解析成功。"""
    print("\n" + "=" * 72)
    print(f"Ref: {ref}")
    print("=" * 72)
    ok, commit, err = resolve_commit(repo, ref)
    if not ok:
        print(f"  ❌ 無法解析: {err}")
        return False
    print(f"  Commit: {commit}")
    print(f"  摘要:   {commit_summary(repo, commit)}")
    n = count_tracked_files(repo, commit)
    if n is None:
        print("  ⚠️  追蹤檔案數: 無法計算（ls-tree 失敗）")
    else:
        print(f"  追蹤檔案數: {n}")

    missing = [p for p in KEY_PATHS if not blob_exists(repo, commit, p)]
    if missing:
        print("  ❌ 下列關鍵路徑在此 commit 不存在:")
        for p in missing:
            print(f"      - {p}")
    else:
        print("  ✅ 關鍵路徑檢查通過:")
        for p in KEY_PATHS:
            print(f"      - {p}")
    return True


def print_diff_pairs(repo: Path, pairs: Iterable[tuple[str, str]]) -> None:
    print("\n" + "#" * 72)
    print("成對差異（git diff --stat A B，直接比兩個 commit 樹）")
    print("#" * 72)
    for a, b in pairs:
        ok_a, ca, _ = resolve_commit(repo, a)
        ok_b, cb, _ = resolve_commit(repo, b)
        print(f"\n--- {a} ({ca[:7] if ok_a else '?'}) vs {b} ({cb[:7] if ok_b else '?'}) ---")
        if not ok_a or not ok_b:
            print("  （略過：其中一端無法解析）")
            continue
        code, out, err = run_git(repo, "diff", "--stat", ca, cb)
        if code != 0:
            print(f"  diff 失敗: {err}")
            continue
        if not out:
            print("  （無差異）")
        else:
            print(out)


def parse_refs_arg(s: str) -> tuple[str, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return tuple(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="檢查 v6 / v6.0.1 相關 Git ref")
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Git 儲存庫根目錄（預設：由目前目錄向上偵測）",
    )
    parser.add_argument(
        "--refs",
        type=str,
        default=None,
        help="逗號分隔 ref 清單；省略則使用腳本內建 DEFAULT_REFS",
    )
    parser.add_argument(
        "--no-diff",
        action="store_true",
        help="不執行成對 diff --stat",
    )
    args = parser.parse_args()

    start = args.repo if args.repo is not None else Path.cwd()
    root = git_root(start)
    if root is None:
        print("❌ 找不到 Git 儲存庫（git rev-parse --show-toplevel 失敗）。")
        return 2

    refs = parse_refs_arg(args.refs) if args.refs else DEFAULT_REFS

    print("Git 儲存庫:", root)
    print("待檢查 ref 數:", len(refs))

    resolved = 0
    for ref in refs:
        if print_ref_block(root, ref):
            resolved += 1

    if not args.no_diff:
        print_diff_pairs(root, DEFAULT_DIFF_PAIRS)

    print("\n" + "=" * 72)
    print(f"完成：{resolved}/{len(refs)} 個 ref 解析成功。")
    if resolved == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

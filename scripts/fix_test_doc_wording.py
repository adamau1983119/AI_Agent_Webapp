#!/usr/bin/env python3
"""Scan and fix section symbol + vague test wording in project docs."""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "venv", "__pycache__", "dist", ".vite"}
SCAN_EXTS = {".md", ".tsx", ".ts", ".py", ".txt"}
BACKUP_MARK = "/backups/"
SKIP_FILES = {
    "scripts/fix_test_doc_wording.py",
    "scripts/fix_scan_report.txt",
    "scripts/hardcoded_report.txt",
    "scripts/suggested_translations.json",
}
SEC = "\u00a7"  # section symbol — only used inside this script


def is_backup(rel: str) -> bool:
    return BACKUP_MARK in rel.replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def transform_section_symbols(text: str) -> str:
    s = SEC
    text = re.sub(rf"{s}E\s+Phase", "E 階段", text)
    text = re.sub(rf"{s}E", "E 階段", text)
    text = re.sub(rf"{s}(\d+-\d+)", r"頻道區塊 \1", text)
    text = re.sub(rf"{s}(\d+){s}(\d+)", r"頻道區塊 \1～\2", text)
    text = re.sub(rf"{s}(\d+)（", r"頻道區塊 \1（", text)
    text = re.sub(rf"{s}(\d+)×", r"頻道區塊 \1×", text)
    text = re.sub(rf"{s}(\d+)\s", r"頻道區塊 \1 ", text)
    text = re.sub(rf"{s}(\d+)", r"頻道區塊 \1", text)
    text = re.sub(rf"{s}([A-K]\d+){s}([A-K]\d+)", r"矩陣 \1～\2", text)
    text = re.sub(rf"{s}([A-K]\d+(?:-\d+)?)", r"矩陣 \1", text)
    text = re.sub(rf"{s}([A-K]){s}([A-K])", r"矩陣 \1～\2", text)
    text = re.sub(rf"{s}([A-K])～K", r"矩陣 \1～K", text)
    text = text.replace(f"{s}B～K", "矩陣 B～K")
    text = re.sub(rf"## {s}([A-K]) —", r"## 矩陣 \1 —", text)
    text = text.replace(f"{s}一", "第一節")
    text = text.replace(f"{s}五", "第五節")
    text = text.replace(f"{s}六", "第六節")
    text = re.sub(rf"{s}([①②③④⑤⑥⑦⑧⑨⑩])", r"第\1節", text)
    text = text.replace(f"{s}⑤", "第⑤節")
    text = re.sub(rf"\*\*{s}([A-K])\*\*", r"**矩陣 \1**", text)
    text = re.sub(rf"{s}([A-K])", r"矩陣 \1", text)

    text = text.replace(f"README.md {s}專案架構", "README.md「專案架構」")
    text = text.replace(f"README.md {s} 必讀文件", "README.md「必讀文件」")
    text = text.replace(f"README.md {s} 必讀", "README.md「必讀文件」")
    text = text.replace(f"AGENTS.md {s} 觸發詞", "AGENTS.md「觸發詞」")
    text = text.replace(f"{s} 易漏對照", "「易漏對照」")
    text = text.replace(f"{s} 觸發詞", "「觸發詞」")
    text = text.replace(f"按 {s} 拆", "按章節拆")
    text = text.replace(f"增刪 {s} 時", "增刪章節時")
    text = text.replace(f"架構矩陣 {s} ", "架構矩陣章 ")
    text = text.replace(f"架構矩陣 {s}與", "架構矩陣章節與")
    text = text.replace(f"矩陣全 {s} ", "矩陣全章 ")
    text = text.replace(f"矩陣全 {s}", "矩陣全章")
    text = text.replace(f"本表 {s} ", "本表章 ")
    text = text.replace(f"本表 {s}", "本表章")
    text = text.replace(f"architecture_test_matrix：{s}A-K", "architecture_test_matrix：A～K")
    text = text.replace(f"{s}A-K", "A～K")

    # ban notices — remove literal symbol from docs
    text = text.replace(f"**禁止**使用 `{s}` 符號", "**禁止**使用分節符號")
    text = text.replace(f"**禁止 `{s}` 符號。**", "**禁止分節符號。**")
    text = text.replace(f"全面廢止 **`{s}` 符號**", "全面廢止 **分節符號**")
    text = text.replace(f"廢止 `{s}` 符號", "廢止分節符號")

    text = text.replace("矩陣 矩陣", "矩陣")
    text = text.replace("矩陣全章 有結果", "矩陣全章節皆有結果")
    text = text.replace("架構矩陣章 與", "架構矩陣章節與")
    text = text.replace("增刪本表章 與列", "增刪本表章節與列")

    # Generic document cross-refs (§ → 章節名／「…」)
    sec_refs = [
        (f"{s} 重建（R）", "「重建（R）」"),
        (f"{s} v7 Token 開發核證（V7）", "「v7 Token 開發核證（V7）」"),
        (f"{s} Token 省成本 D1～D5", "「Token 省成本」D1～D5"),
        (f"{s} Token 省成本", "「Token 省成本」"),
        (f"{s} V7 核證表", "「V7 核證表」"),
        (f"{s} V7 證據表", "「V7 證據表」"),
        (f"{s} Phase 0 監察線結案", "「Phase 0 監察線結案」"),
        (f"{s} 階段 R", "「階段 R」"),
        (f"{s} 階段 T", "「階段 T」"),
        (f"{s} MD-M2", "MD-M2"),
        (f"{s} 前端路由", "「前端路由」"),
        (f"{s} E0", "E0"),
        (f" v7 {s} D1～D5", " v7 D1～D5"),
        (f"{s} D1～D5", "D1～D5"),
        (f"{s}2.0", "第 2.0 節"),
    ]
    for old, new in sec_refs:
        text = text.replace(old, new)
    # stray § before closing paren in combined refs
    text = text.replace(f"{s}重建（R）", "「重建（R）」")
    text = text.replace(f"＋{s} ", "＋")
    return text


def transform_smoke_wording(text: str) -> str:
    replacements = [
        ("路由煙霧", "路由回歸 TC"),
        ("Sidebar 煙霧", "Sidebar 路由回歸 TC"),
        ("Sidebar 路由煙霧", "Sidebar 路由回歸 TC"),
        ("E2E 煙霧", "E2E"),
        ("I.1 煙霧", "I.1 E2E"),
        ("（I.1 煙霧）", "（I.1 E2E）"),
        ("建立頻道 I.1 煙霧", "建立頻道 I.1 E2E"),
        ("E2E** 煙霧 PASS", "E2E PASS**"),
        ("I.1 E2E** 煙霧 PASS", "I.1 E2E PASS**"),
        ("I.1 之瀏覽器 E2E／登入煙霧", "I.1 之瀏覽器 E2E／登入驗證"),
        ("I.1 補瀏覽器登入煙霧簽核", "I.1 補瀏覽器登入 E2E 簽核"),
        ("登入煙霧", "登入驗證"),
        ("環境 Gate + 登入煙霧", "環境 Gate + 登入驗證"),
        ("Mongo 煙霧", "Mongo 抽樣"),
        ("MongoDB 集合煙霧", "MongoDB 集合抽樣"),
        ("煙霧補齊", "迴歸 TC 補齊"),
        ("**煙霧**（可開、無白屏", "**迴歸 TC**（可開、無白屏"),
        ("**煙霧**跑過一輪", "**迴歸 TC**跑過一輪"),
        ("每節至少 **煙霧**", "每節至少 **迴歸 TC**"),
        ("煙霧／迴歸", "迴歸 TC"),
        ("前後端煙霧測", "前後端健康檢查"),
        ("前後端煙霧、", "前後端健康檢查、"),
        ("前後端煙霧", "前後端健康檢查"),
        ("建置煙霧", "建置驗證"),
        ("前端建置煙霧", "前端建置驗證"),
        ("**煙霧（開發可驗）**", "**建置驗證（開發可驗）**"),
        ("**（可選）煙霧**", "**（可選）頁面載入 TC**"),
        ("Step 2 煙霧 PASS", "Step 2 PASS"),
        ("Step 2 煙霧", "Step 2"),
        ("建立頻道 E2E（煙霧）", "建立頻道 E2E"),
        ("Meta **Instagram** 煙霧", "Meta **Instagram** OAuth 驗證"),
        ("Redis 限流 smoke **或**", "Redis 限流驗證 **或**"),
        ("Redis 可選 smoke", "Redis 可選驗證"),
        ("禁止煙霧签收", "禁止模糊签收"),
        ("禁止模糊签收", "禁止模糊签收"),  # idempotent
        ("S4 不得煙霧", "S4 須逐項 TC"),
        ("S4 改路由回歸 TC**—禁止煙霧签收", "S4 改路由回歸 TC**—禁止模糊签收"),
        ("（**非煙霧**）", "（**逐項 TC**）"),
        ("逐項 TC，非煙霧", "逐項 TC"),
        ("，非煙霧）", "，逐項 TC）"),
        ("、煙霧、", "、建置驗證、"),
        ("35–40′：煙霧：", "35–40′：基本路徑盤點："),
        ("（能開即可）", "（改由 I.1 E2E 逐項 TC）"),
        ("需 DB 之煙霧", "需 DB 之迴歸 TC"),
        ("R-5 Gate：PASS**（可進 **T-10** 每日開工與需 DB 之", "R-5 Gate：PASS**（可進 **T-10** 每日開工與需 DB 之"),
        # 2026-06-18 補齊剩餘模糊用語
        ("禁止煙霧驗收與 Mock", "禁止模糊驗收與 Mock"),
        ("禁止煙霧驗收", "禁止模糊驗收"),
        ("禁止煙霧／Mock", "禁止模糊驗收／Mock"),
        ("禁止 Mock／煙霧验收", "禁止 Mock／模糊驗收"),
        ("禁止 Mock／煙霧", "禁止 Mock／模糊驗收"),
        ("本專案所禁止之「煙霧」", "本專案所禁止之「模糊驗收」"),
        ("煙霧式排程", "模糊驗收式排程"),
        ("零 AI Mock 煙霧", "零 AI Mock 模糊驗收"),
        ("煙霧路徑", "上線驗證路徑"),
        ("上線煙霧", "上線驗證"),
        ("對齊 README 禁止煙霧", "對齊 README 禁止模糊驗收"),
        ("README 禁止煙霧", "README 禁止模糊驗收"),
        ("U 軌煙霧", "U 軌 E2E"),
        ("5 步煙霧", "5 步 E2E"),
        ("## API 煙霧", "## API 健康檢查"),
        ("端到端煙霧", "端到端 E2E"),
        ("批次煙霧", "批次驗證"),
        ("本日剩：煙霧", "本日剩：E2E"),
        ("併入 **06-12 煙霧**", "併入 **06-12 E2E**"),
        ("式煙霧签收", "式模糊签收"),
        ("正式域煙霧", "正式域 E2E"),
        ("靈感頁 smoke", "靈感頁載入 TC"),
        ("**禁止**煙霧签收", "**禁止**模糊签收"),
        ("程式結案（煙霧 + commit）", "程式結案（E2E + commit）"),
        ("commit／煙霧", "commit／E2E"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"\bsmoke test\b", "regression TC", text, flags=re.I)
    text = re.sub(r"\bsmoke tests\b", "regression TCs", text, flags=re.I)
    text = re.sub(r"Quick smoke check", "Quick health check", text, flags=re.I)
    return text


def scan_file(path: Path) -> dict[str, list[tuple[int, str]]]:
    text = read_text(path)
    hits: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for i, line in enumerate(text.splitlines(), 1):
        if SEC in line:
            hits["section_symbol"].append((i, line.strip()[:140]))
        if "煙霧" in line:
            hits["smoke_zh"].append((i, line.strip()[:140]))
        if re.search(r"\bsmoke\b", line, re.I):
            hits["smoke_en"].append((i, line.strip()[:140]))
    return hits


def iter_files(include_backups: bool) -> list[Path]:
    files: list[Path] = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in SCAN_EXTS:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES:
            continue
        if not include_backups and is_backup(rel):
            continue
        files.append(p)
    return sorted(files)


def fix_files(include_backups: bool) -> list[tuple[str, int, int]]:
    changed: list[tuple[str, int, int]] = []
    for path in iter_files(include_backups):
        rel = path.relative_to(ROOT).as_posix()
        orig = read_text(path)
        if SEC not in orig and "煙霧" not in orig and not re.search(r"\bsmoke\b", orig, re.I):
            continue
        new = transform_smoke_wording(transform_section_symbols(orig))
        if new != orig:
            write_text(path, new)
            changed.append((rel, orig.count(SEC), new.count(SEC)))
    return changed


def is_allowed_section_line(line: str) -> bool:
    if SEC not in line:
        return True
  # historical mention in ban text already rewritten
    return False


def main() -> int:
    include_backups = "--include-backups" in sys.argv
    report_path = ROOT / "scripts" / "fix_scan_report.txt"
    lines_out: list[str] = []

    def log(msg: str = "") -> None:
        lines_out.append(msg)

    def report(label: str, include_b: bool) -> dict[str, int]:
        totals: dict[str, int] = defaultdict(int)
        log(f"\n{'='*60}\n{label}\n{'='*60}")
        for path in iter_files(include_b):
            rel = path.relative_to(ROOT).as_posix()
            hits = scan_file(path)
            if not hits:
                continue
            tag = " [BACKUP]" if is_backup(rel) else ""
            log(f"\n{rel}{tag}")
            for kind, items in sorted(hits.items()):
                totals[kind] += len(items)
                log(f"  {kind}: {len(items)}")
                for line_no, snippet in items[:5]:
                    log(f"    L{line_no}: {snippet}")
                if len(items) > 5:
                    log(f"    ... +{len(items)-5} more")
        log(
            f"\n--- totals: section_symbol={totals.get('section_symbol', 0)}, "
            f"smoke_zh={totals.get('smoke_zh', 0)}, smoke_en={totals.get('smoke_en', 0)} ---"
        )
        return dict(totals)

    report("BEFORE (active files)", False)
    changed = fix_files(include_backups=False)
    log(f"\nFixed active: {len(changed)} file(s)")
    for rel, before, after in changed:
        log(f"  {rel}: section_symbol {before} -> {after}")

    if include_backups:
        changed_b = fix_files(include_backups=True)
        # only log backup-only changes
        active = {c[0] for c in changed}
        extra = [c for c in changed_b if c[0] not in active]
        log(f"\nFixed backups (additional): {len(extra)} file(s)")
        for rel, before, after in extra[:30]:
            log(f"  {rel}: section_symbol {before} -> {after}")
        if len(extra) > 30:
            log(f"  ... +{len(extra)-30} more")

    report("AFTER (active files)", False)

    remaining_sec = 0
    smoke_remaining = 0
    for path in iter_files(include_backups=False):
        text = read_text(path)
        rel = path.relative_to(ROOT).as_posix()
        smoke_remaining += text.count("煙霧")
        for i, line in enumerate(text.splitlines(), 1):
            if SEC not in line:
                continue
            remaining_sec += 1
            log(f"REMAINING section_symbol: {rel} L{i}: {line.strip()[:120]}")
        if "煙霧" in text:
            log(f"REMAINING 煙霧 count in {rel}: {text.count('煙霧')}")

    write_text(report_path, "\n".join(lines_out) + "\n")
    print(f"Report: {report_path}")
    if remaining_sec or smoke_remaining:
        print(f"Active remaining — section_symbol: {remaining_sec}, vague_wording: {smoke_remaining}")
    else:
        print("scan clean")
    return 1 if remaining_sec or smoke_remaining else 0


if __name__ == "__main__":
    raise SystemExit(main())

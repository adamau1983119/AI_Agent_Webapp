#!/usr/bin/env python3
"""Generate docs/calendar_2026_reference.md — single source of truth for 2026 weekdays."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "calendar_2026_reference.md"

WEEKDAY_ZH = ("一", "二", "三", "四", "五", "六", "日")


def weekday_zh(d: dt.date) -> str:
    return WEEKDAY_ZH[d.weekday()]


def main() -> None:
    start = dt.date(2026, 1, 1)
    end = dt.date(2026, 12, 31)

    lines: list[str] = [
        "# 2026 年日曆參考（SoT）",
        "",
        "> **用途**：本專案凡寫入「日期 + 星期」，**必須對照本檔**，禁止憑記憶或上下文推斷。",
        "> **生成**：`python scripts/generate_calendar_2026.py`（可重跑驗證；輸出應與本檔一致）",
        "> **專案規則**：**週一不排**本專段（YouTuber 創作）；可排日為 **週二～五**。",
        "> **最後生成**：自動產生",
        "",
        "## 驗證指令（助手／人工）",
        "",
        "```bash",
        "python scripts/generate_calendar_2026.py",
        "python -c \"import datetime as d; print('2026-05-26', ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d.date(2026,5,26).weekday()])\"",
        "```",
        "",
        "預期：`2026-05-26 Tue`（即 **星期二**）。",
        "",
        "## 快速對照 — 2026 年 5 月（測試週收口 W-1～W-4）",
        "",
        "| 日期 | 星期 | 專案 |",
        "|------|------|------|",
        "| 2026-05-19 | 二 | T-10 詳情 2.6（實曆補跑） |",
        "| 2026-05-20 | 三 | T-10 Meta OAuth |",
        "| 2026-05-21 | 四 | T-10～T-12 併記 |",
        "| 2026-05-22 | 五 | T-13 靈感 |",
        "| 2026-05-25 | 一 | **不排** |",
        "| 2026-05-26 | 二 | **W-1** 收口（一） |",
        "| 2026-05-27 | 三 | **W-2** 收口（二） |",
        "| 2026-05-28 | 四 | **W-3** 收口（三） |",
        "| 2026-05-29 | 五 | **W-4** 迭代（一） |",
        "| 2026-05-30 | 六 | — |",
        "",
        "## 2026 年完整日曆（01-01～12-31）",
        "",
        "| 日期 | 星期 |",
        "|------|------|",
    ]

    cur = start
    while cur <= end:
        lines.append(f"| {cur.isoformat()} | {weekday_zh(cur)} |")
        cur += dt.timedelta(days=1)

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({(end - start).days + 1} days)")


if __name__ == "__main__":
    main()

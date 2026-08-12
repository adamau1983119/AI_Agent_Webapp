#!/usr/bin/env python3
"""Topic core regression (MD-M2 ≤150 行；本檔 149 行)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SIBLING_SCRIPTS = [
    "scripts/validate_structure.py",
    "scripts/check_ae_bf_static.py",
    "scripts/check_mychannel_bf_static.py",
    "scripts/check_pf_b_static.py",
]


def _run(rel: str) -> bool:
    proc = subprocess.run(
        [sys.executable, str(ROOT / rel)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ok = proc.returncode == 0
    tag = "PASS" if ok else "FAIL"
    print(f"{tag} | {rel}")
    if not ok:
        blob = (proc.stdout + proc.stderr).strip()
        if blob:
            print(blob[:400])
    return ok


def _static_checks() -> list[tuple[str, bool, str]]:
    util = ROOT / "frontend/src/lib/topicDayHkt.ts"
    dash = ROOT / "frontend/src/pages/Dashboard.tsx"
    today = ROOT / "frontend/src/components/features/TodayTopics.tsx"
    repo = ROOT / "backend/app/services/repositories/topic_repository.py"
    preload = ROOT / "backend/app/services/automation/topic_triple_preload.py"
    normalize_mod = ROOT / "backend/app/services/automation/topic_title_normalize.py"
    lang_cfg = ROOT / "backend/config/topic_languages.json"
    lang_cfg_legacy = ROOT / "shared/topic_languages.json"
    lang_util = ROOT / "backend/app/utils/topic_languages.py"
    topic_langs_fe = ROOT / "frontend/src/lib/topicLanguages.ts"
    routing = ROOT / "frontend/src/lib/alterEgoRouting.ts"
    schedules = ROOT / "backend/app/api/v1/schedules.py"
    cost_ctrl = ROOT / "backend/app/utils/cost_controls.py"
    i18n = ROOT / "frontend/src/i18n/index.ts"
    out: list[tuple[str, bool, str]] = []

    out.append(("topicDayHkt.ts exists", util.exists(), ""))
    if dash.exists():
        text = dash.read_text(encoding="utf-8")
        out.append(("Dashboard imports topicDayHkt", "topicDayHkt" in text, ""))
        out.append(
            (
                "schedules fail does not wipe topics",
                "const topics = topicsError ? []" in text
                and "(topicsError || schedulesError) ? []" not in text,
                "only topicsError clears list",
            )
        )
        out.append(
            (
                "daily cap uses EXPECTED_DAILY_TOPICS",
                "EXPECTED_DAILY_TOPICS" in text,
                "",
            )
        )
    if today.exists():
        text = today.read_text(encoding="utf-8")
        out.append(("TodayTopics imports topicDayHkt", "topicDayHkt" in text, ""))
        out.append(
            ("TodayTopics empty uses preparing key", "todayTopicsPreparing" in text, "")
        )
    if repo.exists():
        text = repo.read_text(encoding="utf-8")
        out.append(("repo uses hkt_day_utc_bounds", "hkt_day_utc_bounds" in text, ""))
    out.append(("topic_triple_preload module", preload.exists(), ""))
    out.append(("topic_title_normalize module", normalize_mod.exists(), ""))
    out.append(("backend/config topic_languages.json", lang_cfg.exists(), ""))
    if lang_cfg_legacy.exists() and lang_cfg.exists():
        out.append(
            (
                "legacy shared json matches backend/config",
                lang_cfg.read_text(encoding="utf-8") == lang_cfg_legacy.read_text(encoding="utf-8"),
                "",
            )
        )
    out.append(("backend topic_languages util", lang_util.exists(), ""))
    out.append(("frontend topicLanguages.ts", topic_langs_fe.exists(), ""))
    if preload.exists():
        pt = preload.read_text(encoding="utf-8")
        out.append(
            (
                "preload uses normalize + preload_languages_for",
                "normalize_topic_title_for_display_lang" in pt
                and "preload_languages_for" in pt
                and "topic_preload_zh" not in pt,
                "",
            )
        )
    if cost_ctrl.exists():
        out.append(
            (
                "cost_controls triple preload flag",
                "topic_triple_preload_enabled" in cost_ctrl.read_text(encoding="utf-8"),
                "",
            )
        )
    if routing.exists():
        out.append(
            ("dashboard-first routing", "DASHBOARD_PATH" in routing.read_text(encoding="utf-8"), "")
        )
    if schedules.exists():
        st = schedules.read_text(encoding="utf-8")
        out.append(
            (
                "generate-today uses HKT generated_at",
                "hkt_day_utc_bounds" in st and '"generated_at"' in st,
                "",
            )
        )
    if i18n.exists():
        text = i18n.read_text(encoding="utf-8")
        out.append(
            (
                "i18n todayTopicsPreparing zh/en/ja",
                text.count("'dashboard.todayTopicsPreparing'") >= 3,
                "",
            )
        )
    return out


def _hkt_import_check() -> tuple[str, bool, str]:
    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from app.services.automation.topic_day_hkt import expected_topics_today, hkt_day_utc_bounds
        from app.utils.cost_controls import topic_triple_preload_cap
        from app.utils.topic_languages import (
            preload_languages_for,
            title_script_mismatch,
            is_fallback_title,
            usable_cached_title,
        )
        from app.utils.topic_pipeline import (
            current_topic_pipeline_version,
            list_topics_generation_filter,
        )

        start, end = hkt_day_utc_bounds("2026-08-11")
        gen_f = list_topics_generation_filter(include_legacy=False)
        ok = (
            start < end
            and expected_topics_today() == 15
            and topic_triple_preload_cap() == 30
            and preload_languages_for("zh-TW") == ("en", "ja")
            and title_script_mismatch("Hello fashion", "zh-TW")
            and not title_script_mismatch("時尚潮流", "zh-TW")
            and is_fallback_title("[Fallback-ZH] Hello")
            and usable_cached_title("[Fallback-JA] x") is None
            and current_topic_pipeline_version() >= 8
            and "pipeline_version" in str(gen_f)
        )
        return ("topic_day_hkt bounds + daily=15", ok, f"{start}..{end}")
    except Exception as exc:  # pragma: no cover
        return ("topic_day_hkt import", False, str(exc))


def main() -> int:
    fails = 0
    for rel in SIBLING_SCRIPTS:
        if not _run(rel):
            fails += 1

    for name, ok, detail in _static_checks():
        tag = "PASS" if ok else "FAIL"
        if not ok:
            fails += 1
        extra = f" | {detail}" if detail else ""
        print(f"{tag} | {name}{extra}")

    name, ok, detail = _hkt_import_check()
    tag = "PASS" if ok else "FAIL"
    if not ok:
        fails += 1
    extra = f" | {detail}" if detail else ""
    print(f"{tag} | {name}{extra}")

    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

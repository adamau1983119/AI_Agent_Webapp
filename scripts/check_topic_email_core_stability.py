"""Core stability double-check: topic cards + daily digest email."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.utils.topic_pipeline import (  # noqa: E402
    current_topic_pipeline_version,
    list_topics_generation_filter,
    stamp_pipeline_fields,
)
from app.utils.topic_languages import is_fallback_title, usable_cached_title  # noqa: E402
from app.services.observability import alert_mailer as am  # noqa: E402
import app.services.observability.daily_digest as dd  # noqa: E402


def main() -> int:
    assert current_topic_pipeline_version() >= 8
    filt = list_topics_generation_filter(include_legacy=False)
    assert "pipeline_version" in str(filt)
    stamped = stamp_pipeline_fields({})
    assert stamped.get("pipeline_version") >= 8
    assert is_fallback_title("[Fallback-JA] hello")
    assert usable_cached_title("[Fallback-ZH] hello") is None

    mailer_src = Path(am.__file__).read_text(encoding="utf-8")
    assert "[每日基本檢查]" in mailer_src
    assert "[即時告警]" in mailer_src
    assert "report_type" in mailer_src

    pipe_src = (BACKEND / "app/utils/topic_pipeline.py").read_text(encoding="utf-8")
    assert "$and" in pipe_src
    assert "$or" not in pipe_src.split("list_topics_generation_filter")[-1] or (
        '"$or"' not in pipe_src and "'$or'" not in pipe_src
    )
    # cutover join must be $and (not $or)
    assert 'return {"$and": clauses}' in pipe_src

    assert "永不拋出" in (dd._topics_hkt_summary.__doc__ or "")
    digest_src = Path(dd.__file__).read_text(encoding="utf-8")
    assert "topics_hkt_summary unexpected" in digest_src
    assert "今日產卡(v8)" in digest_src

    sched = (BACKEND / "app/api/v1/schedules.py").read_text(encoding="utf-8")
    mon = (BACKEND / "app/services/automation/scheduler_monitor.py").read_text(
        encoding="utf-8"
    )
    assert "list_topics_generation_filter" in sched
    assert "list_topics_generation_filter" in mon

    dash = (ROOT / "frontend/src/pages/Dashboard.tsx").read_text(encoding="utf-8")
    assert "btn-dashboard-generate" not in dash
    assert "systemUpdatesEvery6h" in dash
    assert "generateTodayAllTopics" not in dash

    print("CORE_DOUBLE_CHECK_PASS")
    print("  pipeline_version=", current_topic_pipeline_version())
    print("  list_filter=", filt)
    print("  digest_subjects=每日基本檢查 / 即時告警")
    print("  generate_today=v8 count filter")
    print("  dashboard=scheduler-only (no manual generate)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

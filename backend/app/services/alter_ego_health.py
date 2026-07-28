"""Alter Ego 健康檢查 payload（供 /health 與結案腳本）。"""
from app.alter_ego_build import AE_PIPELINE_VERSION


def alter_ego_health_payload() -> dict:
    return {
        "pipeline_version": AE_PIPELINE_VERSION,
        "preview_includes_soul": True,
        "content_style_service": True,
        "rollback_api": True,
        "onboarding_skip_api": True,
        "weekly_batch": True,
        "feedback_logs": True,
        "reextract_gate": True,
    }

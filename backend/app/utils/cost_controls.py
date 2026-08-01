"""
DeepSeek／AI 成本開關（測試期與小規模部署）
"""
from app.config import settings


def _flag(name: str, default: str = "false") -> bool:
    return getattr(settings, name, default).lower() == "true"


def scheduled_topic_collection_enabled() -> bool:
    """是否執行排程／自動「主打分類」主題卡收集（fashion/food/trend）。"""
    return _flag("ENABLE_SCHEDULED_TOPIC_COLLECTION", "false")


def ai_topic_translation_enabled() -> bool:
    """是否對 RSS 標題呼叫 AI 翻譯（每則 1 次 API；高成本）。"""
    return _flag("ENABLE_AI_TOPIC_TRANSLATION", "false")


def ai_topic_fallback_enabled() -> bool:
    """RSS 不足時是否用 AI 補標題（關鍵字備援、Layer 3）。"""
    return _flag("ENABLE_AI_TOPIC_FALLBACK", "false")


def channel_prefetch_pipeline_enabled() -> bool:
    return _flag("ENABLE_CHANNEL_PREFETCH_PIPELINE", "false")


def public_feed_pipeline_enabled() -> bool:
    return _flag("ENABLE_PUBLIC_FEED_PIPELINE", "false")


def auto_start_scheduler_enabled() -> bool:
    return (
        settings.ENVIRONMENT == "production"
        or _flag("AUTO_START_SCHEDULER", "false")
    )


def topic_i18n_prefetch_enabled() -> bool:
    return _flag("ENABLE_TOPIC_I18N_PREFETCH", "true")


def cost_controls_summary() -> dict:
    return {
        "auto_start_scheduler": auto_start_scheduler_enabled(),
        "scheduled_topic_collection": scheduled_topic_collection_enabled(),
        "ai_topic_translation": ai_topic_translation_enabled(),
        "ai_topic_fallback": ai_topic_fallback_enabled(),
        "topic_i18n_prefetch": topic_i18n_prefetch_enabled(),
        "channel_prefetch_pipeline": channel_prefetch_pipeline_enabled(),
        "public_feed_pipeline": public_feed_pipeline_enabled(),
        "safe_batch_size": settings.safe_batch_size,
        "public_feed_batch_size": int(settings.PUBLIC_FEED_BATCH_SIZE),
        "ai_service": settings.AI_SERVICE,
        "deepseek_model": getattr(settings, "DEEPSEEK_MODEL", "deepseek-v4-flash"),
        "deepseek_model_flash": getattr(
            settings, "DEEPSEEK_MODEL_FLASH", getattr(settings, "DEEPSEEK_MODEL", "deepseek-v4-flash")
        ),
        "deepseek_model_pro": getattr(settings, "DEEPSEEK_MODEL_PRO", "deepseek-v4-pro"),
    }

"""
Flash 一次提煉 summary_flash（~300 字 · v7 Phase 1）
"""
import re
import logging
from typing import Optional

from app.config import settings
from app.prompts.system_constants import SUMMARY_FLASH_SYSTEM
from app.utils.logger import log_cost_event

logger = logging.getLogger(__name__)

SUMMARY_FLASH_MAX_CHARS = 300
_INPUT_SNIPPET_MAX = 4000


def strip_html(text: str) -> str:
    """L0：去除 HTML 標籤。"""
    return re.sub(r"<[^>]+>", "", text or "").strip()


async def generate_summary_flash(
    title: str,
    raw_text: Optional[str] = None,
    topic_id: Optional[str] = None,
) -> str:
    """
    L0 清洗後以 Flash 提煉摘要；失敗時回退清洗後原文截斷。
    """
    cleaned = strip_html(raw_text or "") or strip_html(title)
    snippet = cleaned[:_INPUT_SNIPPET_MAX]

    from app.services.ai.ai_service_factory import AIServiceFactory

    ai = AIServiceFactory.get_service(settings.AI_SERVICE)
    flash_model = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL

    prompt = f"""{SUMMARY_FLASH_SYSTEM}

標題：{title}

原文片段（已去 HTML）：
{snippet}

請輸出繁體中文客觀摘要，單段、約 {SUMMARY_FLASH_MAX_CHARS} 字以內，不要標題或條列。"""

    try:
        summary = (await ai._call_api(prompt, model=flash_model)).strip()
        summary = summary[:SUMMARY_FLASH_MAX_CHARS]
        log_cost_event(
            "SUMMARY_FLASH_SUCCESS",
            topic_id=topic_id or "pending",
            chars=len(summary),
        )
        return summary
    except Exception as e:
        logger.warning("summary_flash Flash 失敗，使用 L0 截斷: %s", e)
        return cleaned[:SUMMARY_FLASH_MAX_CHARS]

"""
v7 定向夜間預載：港日 Channel → DeepL ja/en standard_translation（無 kol_style）
"""
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

from app.models.topic_translation import TranslationProvider, TranslationType
from app.services.repositories.channel_repository import ChannelRepository
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository
from app.services.translation.deepl_provider import translate_with_fallback

logger = logging.getLogger(__name__)


def _load_config() -> Dict[str, Any]:
    path = Path(__file__).resolve().parents[2] / "config" / "channel_prefetch.yaml"
    if not path.exists():
        return {"regions": ["hong_kong", "japan"], "preload_langs": ["ja", "en"], "max_topics_per_channel": 20}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


async def run_channel_prefetch_pipeline() -> Dict[str, int]:
    """L0 已完成於收集；此 job 僅 DeepL 預載 ja/en → topic_translations。"""
    cfg = _load_config()
    regions: List[str] = cfg.get("regions") or ["hong_kong", "japan"]
    langs: List[str] = cfg.get("preload_langs") or ["ja", "en"]
    max_per = int(cfg.get("max_topics_per_channel") or 20)

    channel_repo = ChannelRepository()
    topic_repo = TopicRepository()
    trans_repo = TopicTranslationRepository()
    await trans_repo.ensure_indexes()

    channels = await channel_repo.find_many({"region": {"$in": regions}, "status": {"$ne": "deleted"}})
    stats = {"channels": len(channels), "translations_written": 0, "skipped_cached": 0}

    for ch in channels:
        channel_id = ch.get("id")
        if not channel_id:
            continue
        topics, _ = await topic_repo.list_by_channel_id(channel_id, limit=max_per)
        for topic in topics:
            topic_id = topic.get("id")
            summary = (topic.get("summary_flash") or topic.get("description") or topic.get("title") or "").strip()
            if not topic_id or not summary:
                continue
            title_src = (topic.get("title") or summary)[:500]
            for lang in langs:
                existing = await trans_repo.get_translation(
                    topic_id, lang, TranslationType.STANDARD
                )
                if existing and existing.get("cached_content"):
                    stats["skipped_cached"] += 1
                    continue
                translated, provider = await translate_with_fallback(
                    summary, lang, summary_flash_for_fallback=summary
                )
                title_t, _ = await translate_with_fallback(
                    title_src, lang, summary_flash_for_fallback=title_src
                )
                await trans_repo.upsert_translation({
                    "topic_id": topic_id,
                    "lang": lang,
                    "type": TranslationType.STANDARD,
                    "cached_title": title_t[:200],
                    "cached_content": translated[:400],
                    "provider": provider,
                })
                stats["translations_written"] += 1

    logger.info("channel_prefetch_pipeline 完成: %s", stats)
    return stats

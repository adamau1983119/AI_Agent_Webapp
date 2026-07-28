"""
PF-B：批次讀取 topic_translations 標題／摘要（feed 零 LLM）
"""
from typing import Any, Dict, List, Tuple

from app.models.topic_translation import TranslationType
from app.services.repositories.topic_translation_repository import TopicTranslationRepository


async def load_standard_localizations(
    topic_ids: List[str], lang: str
) -> Tuple[Dict[str, str], Dict[str, str]]:
    """回傳 (title_map, summary_map)。"""
    repo = TopicTranslationRepository()
    titles: Dict[str, str] = {}
    summaries: Dict[str, str] = {}
    for tid in topic_ids:
        if not tid:
            continue
        doc = await repo.get_translation(tid, lang, TranslationType.STANDARD)
        if not doc:
            continue
        title = doc.get("cached_title")
        if title:
            titles[tid] = str(title)
        content = doc.get("cached_content")
        if content:
            summaries[tid] = str(content)
    return titles, summaries


async def load_standard_titles(
    topic_ids: List[str], lang: str
) -> Dict[str, str]:
    titles, _ = await load_standard_localizations(topic_ids, lang)
    return titles


async def title_map_for_topics(
    topics: List[Dict[str, Any]], lang: str
) -> Dict[str, str]:
    ids = [str(t["id"]) for t in topics if t.get("id")]
    return await load_standard_titles(ids, lang)


async def localization_maps_for_topics(
    topics: List[Dict[str, Any]], lang: str
) -> Tuple[Dict[str, str], Dict[str, str]]:
    ids = [str(t["id"]) for t in topics if t.get("id")]
    return await load_standard_localizations(ids, lang)

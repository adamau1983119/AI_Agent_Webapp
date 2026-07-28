"""
公共 feed 卡片序列化（讀取路徑 · 零 LLM）
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.public_feed.feed_translation_loader import localization_maps_for_topics


def _first_image_url(previews: Any) -> Optional[str]:
    """preview_images 可能是 URL 字串或 dict（RSS media）。"""
    if not previews or not isinstance(previews, list):
        return None
    item = previews[0]
    if isinstance(item, str) and item.strip():
        return item.strip()
    if isinstance(item, dict):
        url = (item.get("url") or item.get("src") or "").strip()
        return url or None
    return None


def _resolve_title(
    topic: Dict[str, Any],
    lang: str,
    translation_titles: Optional[Dict[str, str]] = None,
) -> str:
    if lang == "en":
        return topic.get("title") or topic.get("original_title") or ""
    tid = str(topic.get("id") or "")
    if translation_titles and tid and tid in translation_titles:
        return translation_titles[tid]
    titles = topic.get("titles_i18n") or {}
    return titles.get(lang) or topic.get("title") or ""


def _english_summary_fallback(topic: Dict[str, Any]) -> str:
    i18n = topic.get("summary_i18n") or {}
    if isinstance(i18n, dict) and i18n.get("en"):
        return str(i18n["en"])
    sources = topic.get("sources") or []
    if sources and isinstance(sources[0], dict):
        snip = (sources[0].get("title") or "").strip()
        if snip and snip != (topic.get("title") or ""):
            return snip[:400]
    # 最後：英文標題（避免落到繁中 summary_flash）
    return (topic.get("title") or topic.get("original_title") or "")[:400]


def _resolve_summary(
    topic: Dict[str, Any],
    lang: str,
    translation_summaries: Optional[Dict[str, str]] = None,
) -> str:
    if lang == "en":
        tid = str(topic.get("id") or "")
        if translation_summaries and tid and tid in translation_summaries:
            return translation_summaries[tid]
        return _english_summary_fallback(topic)
    tid = str(topic.get("id") or "")
    if translation_summaries and tid and tid in translation_summaries:
        return translation_summaries[tid]
    i18n = topic.get("summary_i18n") or {}
    if isinstance(i18n, dict) and i18n.get(lang):
        return str(i18n[lang])
    return topic.get("summary_flash") or topic.get("description") or ""


def topic_to_feed_card(
    topic: Dict[str, Any],
    lang: str,
    translation_titles: Optional[Dict[str, str]] = None,
    translation_summaries: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    title = _resolve_title(topic, lang, translation_titles)
    summary = _resolve_summary(topic, lang, translation_summaries)
    previews = topic.get("preview_images") or []
    created = topic.get("created_at") or topic.get("generated_at")
    if isinstance(created, datetime):
        created = created.isoformat()
    return {
        "id": topic.get("id", ""),
        "title": title,
        "description": summary,
        "summary_flash": summary,
        "category": topic.get("category"),
        "image_url": _first_image_url(previews),
        "source": topic.get("source"),
        "source_lang": topic.get("source_lang") or "en",
        "created_at": created,
    }


def topics_to_feed_cards(
    topics: List[Dict[str, Any]],
    lang: str,
    translation_titles: Optional[Dict[str, str]] = None,
    translation_summaries: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    return [
        topic_to_feed_card(t, lang, translation_titles, translation_summaries)
        for t in topics
    ]


async def topics_to_feed_cards_async(
    topics: List[Dict[str, Any]], lang: str
) -> List[Dict[str, Any]]:
    title_map, summary_map = await localization_maps_for_topics(topics, lang)
    return topics_to_feed_cards(topics, lang, title_map, summary_map)

"""
公共 feed 卡片序列化（讀取路徑 · 零 LLM）
"""
from datetime import datetime
from typing import Any, Dict, List, Optional


def topic_to_feed_card(topic: Dict[str, Any], lang: str) -> Dict[str, Any]:
    titles = topic.get("titles_i18n") or {}
    title = titles.get(lang) or topic.get("title") or ""
    summary = topic.get("summary_flash") or topic.get("description") or ""
    previews = topic.get("preview_images") or []
    created = topic.get("created_at") or topic.get("generated_at")
    if isinstance(created, datetime):
        created = created.isoformat()
    return {
        "id": topic.get("id", ""),
        "title": title,
        "description": summary,
        "summary_flash": topic.get("summary_flash"),
        "category": topic.get("category"),
        "image_url": previews[0] if previews else None,
        "source": topic.get("source"),
        "source_lang": topic.get("source_lang") or "en",
        "created_at": created,
    }


def topics_to_feed_cards(topics: List[Dict[str, Any]], lang: str) -> List[Dict[str, Any]]:
    return [topic_to_feed_card(t, lang) for t in topics]

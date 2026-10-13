"""刪除頻道時清掉該頻道的主題卡與已生成貼文。"""
from __future__ import annotations

from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.topic_translation_repository import TopicTranslationRepository


async def purge_channel_topics(channel_id: str) -> int:
    """硬刪主題、貼文、圖片與三語快取，再清 topics.channel_id。"""
    if not channel_id:
        return 0
    topics = TopicRepository()
    col = await topics._get_collection()
    rows = await col.find({"channel_id": channel_id}, {"id": 1}).to_list(length=500)
    ids = [str(row.get("id")) for row in rows if row.get("id")]
    if ids:
        content = await ContentRepository()._get_collection()
        await content.delete_many({"topic_id": {"$in": ids}})
        images = await ImageRepository()._get_collection()
        await images.delete_many({"topic_id": {"$in": ids}})
        translations = await TopicTranslationRepository()._get_collection()
        await translations.delete_many({"topic_id": {"$in": ids}})
    return await topics.delete_by_channel_id(channel_id)

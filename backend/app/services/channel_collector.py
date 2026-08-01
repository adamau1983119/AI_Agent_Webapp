"""
頻道主題收集服務
對齊專案架構：全球多語 RSS → AI 翻譯為用戶語言（資訊差）；
三層備援（L1 頻道 RSS → L2 相近類別 → L3 僅 RSS 全失敗時）。
"""
from typing import Optional, Dict, Any, List, Set, Tuple
from datetime import datetime
import re
import secrets
import feedparser
import httpx
from app.services.repositories.channel_repository import ChannelRepository
from app.services.repositories.topic_repository import TopicRepository
from app.services.channel_service import ChannelService
from app.services.automation.topic_collector import TopicCollector
from app.services.automation.topic_i18n_prefetch import finalize_topic_languages
from app.models.topic import Status, Category
from app.models.channel import ChannelCollectionStatus
from app.services.ai.ai_service_factory import AIServiceFactory
from app.utils.cost_controls import ai_topic_translation_enabled
import logging

logger = logging.getLogger(__name__)

# v4.0：每頻道每次收集目標（不強制 AI 補滿；有幾筆 RSS 算幾筆）
TOPICS_PER_CHANNEL = 10
ITEMS_PER_SOURCE_LAYER1 = 3
ITEMS_PER_SOURCE_LAYER2 = 2

_TOPIC_CATEGORIES = frozenset({"fashion", "food", "trend"})

# Layer 2 僅做「類別」粗篩（保留國際視野，不以語言過濾）
_CATEGORY_HINTS: Dict[str, Set[str]] = {
    "fashion": {
        "fashion", "style", "wear", "runway", "designer", "vogue", "時尚", "穿搭", "服裝",
    },
    "food": {
        "food", "restaurant", "recipe", "dining", "chef", "cuisine", "eat", "meal", "cook",
        "美食", "餐廳", "料理", "飲食", "食譜", "廚師",
    },
    "trend": {
        "trend", "news", "tech", "culture", "market", "innovation", "趨勢", "科技", "文化",
    },
}


class ChannelCollector:
    """頻道主題收集器（RSS + 翻譯 + 三層備援）"""

    def __init__(self):
        self.channel_repo = ChannelRepository()
        self.channel_service = ChannelService()
        self.topic_repo = TopicRepository()
        self._topic_collector = TopicCollector()

    async def collect_for_channel(
        self,
        channel_id: str,
        target_language: str = "zh-TW",
    ) -> Dict[str, Any]:
        """
        為單一頻道收集主題（對齊 v4.0 / 專案完整架構表「資訊差」）。

        - 接受任何語言的 RSS；標題／摘要經 TopicCollector._translate_title 轉為用戶語言
        - Layer 1 → 不足時 Layer 2（相近類別）
        - 僅當 RSS 完全無結果時才 Layer 3 AI（不為湊滿 10 筆而憑空生成）
        - 使用者 selected_feeds：Layer 1 信任來源，不做關鍵字剔除
        """
        channel = await self.channel_repo.get_channel_by_id(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}

        has_selected_feeds = bool(
            [
                f
                for f in (channel.get("selected_feeds") or [])
                if isinstance(f, dict) and (f.get("url") or "").strip().startswith(("http://", "https://"))
            ]
        )

        await self.channel_repo.update_collection_status(
            channel_id,
            ChannelCollectionStatus.COLLECTING,
        )

        try:
            sources = self.channel_service.get_rss_sources_for_channel(channel) or []
            layer1 = [s for s in sources if s.get("layer") == 1]
            layer2 = [s for s in sources if s.get("layer") == 2]

            collection_log: Dict[str, Any] = {
                "layer_1": {"attempted": 0, "success": 0, "sources": []},
                "layer_2": {"attempted": 0, "success": 0, "sources": []},
                "layer_3": {"attempted": 0, "success": 0},
                "translated": 0,
                "rejected_category": 0,
                "rejected_duplicate": 0,
                "replaced_previous": 0,
                "target_language": target_language,
                "has_selected_feeds": has_selected_feeds,
            }

            if not sources:
                await self.channel_repo.update_collection_status(
                    channel_id, ChannelCollectionStatus.COMPLETED, topic_count=0
                )
                return {
                    "success": True,
                    "channel_id": channel_id,
                    "topics_collected": 0,
                    "topics": [],
                    "collection_log": collection_log,
                    "message": "no_rss_sources",
                }

            removed = await self.topic_repo.delete_by_channel_id(channel_id)
            collection_log["replaced_previous"] = removed

            topics: List[Dict[str, Any]] = []
            seen_links: Set[str] = set()
            seen_titles: Set[str] = set()
            topic_category = self._to_topic_category(channel.get("category", "trend"))

            # Layer 1：信任頻道設定來源（含使用者自選 RSS），不以語言或關鍵字剔除
            await self._collect_from_source_list(
                layer1,
                channel,
                target_language,
                topic_category,
                topics,
                seen_links,
                seen_titles,
                collection_log["layer_1"],
                max_per_source=ITEMS_PER_SOURCE_LAYER1,
                apply_category_filter=False,
                apply_keyword_filter=False,
            )

            if len(topics) < TOPICS_PER_CHANNEL and layer2:
                await self._collect_from_source_list(
                    layer2,
                    channel,
                    target_language,
                    topic_category,
                    topics,
                    seen_links,
                    seen_titles,
                    collection_log["layer_2"],
                    max_per_source=ITEMS_PER_SOURCE_LAYER2,
                    apply_category_filter=True,
                    apply_keyword_filter=bool(channel.get("custom_keywords")),
                )

            if len(topics) == 0:
                from app.utils.cost_controls import ai_topic_fallback_enabled
                if ai_topic_fallback_enabled():
                    collection_log["layer_3"]["attempted"] = 1
                    ai_topics = await self._generate_ai_topics(
                        channel, min(TOPICS_PER_CHANNEL, 5), target_language
                    )
                    if ai_topics:
                        collection_log["layer_3"]["success"] = 1
                        topics.extend(ai_topics)
                else:
                    logger.info(
                        "頻道 %s RSS 無結果；Layer3 AI 已關閉 (ENABLE_AI_TOPIC_FALLBACK=false)",
                        channel_id,
                    )

            saved_count = await self._persist_topics(channel, topics, target_language)

            await self.channel_repo.update_collection_status(
                channel_id,
                ChannelCollectionStatus.COMPLETED,
                topic_count=saved_count,
            )

            message = "ok" if saved_count > 0 else "no_rss_items"
            return {
                "success": True,
                "channel_id": channel_id,
                "topics_collected": saved_count,
                "topics": topics,
                "collection_log": collection_log,
                "message": message,
            }

        except Exception as e:
            logger.error(f"頻道收集失敗: {channel_id} - {e}")
            import traceback
            logger.error(traceback.format_exc())
            try:
                await self.channel_repo.update_collection_status(
                    channel_id, ChannelCollectionStatus.FAILED
                )
            except Exception as update_error:
                logger.error(f"更新收集狀態失敗: {update_error}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "channel_id": channel_id,
            }

    async def _collect_from_source_list(
        self,
        source_list: List[Dict[str, Any]],
        channel: Dict[str, Any],
        target_language: str,
        topic_category: Category,
        topics: List[Dict[str, Any]],
        seen_links: Set[str],
        seen_titles: Set[str],
        layer_log: Dict[str, Any],
        max_per_source: int,
        apply_category_filter: bool,
        apply_keyword_filter: bool,
    ) -> None:
        keyword_terms = self._build_custom_keyword_terms(channel)

        for source in source_list:
            if len(topics) >= TOPICS_PER_CHANNEL:
                break
            source_name = source.get("name", "未知來源")
            layer_log["attempted"] += 1
            try:
                items = await self._fetch_rss(source["url"])
            except Exception as e:
                logger.warning(f"RSS 取得失敗: {source_name} - {e}")
                continue

            if not items:
                continue

            layer_log["success"] += 1
            layer_log["sources"].append(source_name)
            accepted = 0

            for item in items:
                if len(topics) >= TOPICS_PER_CHANNEL or accepted >= max_per_source:
                    break

                original_title = (item.get("title") or "").strip()
                raw_summary = self._strip_html(item.get("summary") or "")
                link = (item.get("link") or "").strip()
                if not original_title:
                    continue

                if apply_category_filter and not self._matches_category_hints(
                    original_title, raw_summary, topic_category.value
                ):
                    continue

                if apply_keyword_filter and keyword_terms and not self._matches_custom_keywords(
                    original_title, raw_summary, keyword_terms
                ):
                    continue

                norm_title = original_title.lower()
                if link and link in seen_links:
                    continue
                if norm_title in seen_titles:
                    continue

                translated_title, description = await self._topic_collector._translate_title(
                    original_title, topic_category, target_language
                )

                if link:
                    seen_links.add(link)
                seen_titles.add(norm_title)

                topics.append({
                    "title": translated_title,
                    "original_title": original_title,
                    "summary": description or raw_summary[:200] if raw_summary else "",
                    "source_url": link,
                    "source_name": source_name,
                    "source_layer": source.get("layer", 1),
                    "image_url": item.get("image"),
                    "channel_id": channel.get("id", ""),
                    "category": channel.get("category", "trend"),
                    "region": channel.get("region", "global"),
                    "collected_at": datetime.utcnow().isoformat(),
                    "is_ai_generated": False,
                })
                accepted += 1

    def _build_custom_keyword_terms(self, channel: Dict[str, Any]) -> Set[str]:
        terms: Set[str] = set()
        for kw in channel.get("custom_keywords") or []:
            k = (kw or "").strip()
            if len(k) >= 2:
                terms.add(k.lower())
                terms.add(k)
        return terms

    def _matches_category_hints(self, title: str, summary: str, category: str) -> bool:
        hints = _CATEGORY_HINTS.get(category, set())
        if not hints:
            return True
        blob = f"{title} {summary}".lower()
        return any(h in blob for h in hints)

    def _matches_custom_keywords(
        self, title: str, summary: str, terms: Set[str]
    ) -> bool:
        blob = f"{title} {summary}"
        blob_lower = blob.lower()
        for term in terms:
            if term.lower() in blob_lower or term in blob:
                return True
        return False

    def _to_topic_category(self, channel_category: str) -> Category:
        mapped = self._map_topic_category(channel_category)
        return Category(mapped)

    def _map_topic_category(self, channel_category: str) -> str:
        cat = (channel_category or "trend").lower()
        return cat if cat in _TOPIC_CATEGORIES else "trend"

    def _strip_html(self, text: str) -> str:
        return re.sub(r"<[^>]+>", "", text or "").strip()

    async def _persist_topics(
        self,
        channel: Dict[str, Any],
        topics: List[Dict[str, Any]],
        target_language: str,
    ) -> int:
        if not topics:
            return 0

        channel_id = channel.get("id") or ""
        user_id = channel.get("user_id")
        mapped_category = self._map_topic_category(channel.get("category", "trend"))
        now = datetime.utcnow()
        stamp = now.strftime("%Y%m%d%H%M%S")
        saved = 0
        display_lang = target_language or "zh-TW"

        for raw in topics:
            try:
                title = (raw.get("title") or "").strip() or "無標題"
                original_title = raw.get("original_title") or title
                source_name = raw.get("source_name") or "未知來源"
                source_url = raw.get("source_url") or ""
                summary = (raw.get("summary") or "")[:200]
                image_url = raw.get("image_url")
                is_ai = bool(raw.get("is_ai_generated", False))

                topic_id = f"topic_{mapped_category}_{stamp}_{secrets.token_hex(4)}"

                from app.services.summarization.summary_flash_service import generate_summary_flash

                raw_for_flash = summary or original_title
                summary_flash = await generate_summary_flash(
                    title=original_title,
                    raw_text=raw_for_flash,
                    topic_id=topic_id,
                )

                source_entry: Dict[str, Any] = {
                    "type": "rss" if not is_ai else "ai",
                    "name": source_name,
                    "url": source_url,
                    "title": title,
                    "original_title": original_title,
                    "fetched_at": now,
                    "verified": not is_ai,
                }
                if image_url:
                    source_entry["images"] = [image_url]

                topic_doc: Dict[str, Any] = {
                    "id": topic_id,
                    "title": title,
                    "original_title": original_title,
                    "category": mapped_category,
                    "status": Status.PENDING.value,
                    "source": source_name,
                    "sources": [source_entry],
                    "description": summary or None,
                    "summary_flash": summary_flash,
                    "preview_images": [image_url] if image_url else [],
                    "is_expanded": False,
                    "display_language": display_lang,
                    "channel_id": channel_id,
                    "user_id": user_id,
                    "is_ai_generated": is_ai,
                    "generated_at": now,
                    "updated_at": now,
                    "created_at": now,
                }
                await finalize_topic_languages(
                    topic_doc,
                    source_title=original_title,
                    requested_lang=display_lang,
                    translation_applied=(
                        ai_topic_translation_enabled()
                        and title.strip() != original_title.strip()
                    ),
                )
                await self.topic_repo.create_topic(topic_doc)
                saved += 1
            except Exception as e:
                logger.warning(f"寫入主題失敗（略過）: {e}")

        logger.info(f"頻道 {channel_id} 已寫入 {saved}/{len(topics)} 個主題至 topics")
        return saved

    async def _fetch_rss(self, url: str) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return []
                feed = feedparser.parse(response.content)
                items = []
                for entry in feed.entries[:10]:
                    items.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "published": entry.get("published", entry.get("updated", "")),
                        "image": self._extract_image(entry),
                    })
                return items
        except Exception as e:
            logger.warning(f"RSS 取得失敗: {url} - {e}")
            return []

    def _extract_image(self, entry: Dict[str, Any]) -> Optional[str]:
        media_content = entry.get("media_content", [])
        if media_content:
            return media_content[0].get("url")
        media_thumbnail = entry.get("media_thumbnail", [])
        if media_thumbnail:
            return media_thumbnail[0].get("url")
        for enc in entry.get("enclosures", []):
            if enc.get("type", "").startswith("image/"):
                return enc.get("href", enc.get("url"))
        return None

    async def _generate_ai_topics(
        self,
        channel: Dict[str, Any],
        count: int,
        target_language: str,
    ) -> List[Dict[str, Any]]:
        """Layer 3：僅在 RSS 全失敗時，依頻道設定生成（並翻譯）。"""
        try:
            ai_service = AIServiceFactory.get_service()
            category = channel.get("category", "trend")
            region = channel.get("region", "global")
            keywords = channel.get("custom_keywords", [])
            lang_labels = {"zh-TW": "繁體中文", "en": "English", "ja": "日本語"}
            category_labels = {
                "fashion": "時尚", "food": "美食", "trend": "趨勢",
                "finance": "財經", "sports": "運動", "tech": "科技",
                "entertainment": "娛樂", "other": "其他",
            }
            prompt = f"""作為內容策劃專家，請為以下頻道生成 {count} 個具國際視野的靈感主題（非虛構新聞標題，而是可追蹤的內容方向）。

頻道設定：
- 類別：{category_labels.get(category, category)}
- 地區：{region}
- 關鍵字：{', '.join(keywords) if keywords else '無'}
- 輸出語言：{lang_labels.get(target_language, "繁體中文")}

格式（嚴格遵守）：
主題1: [標題]
描述: [描述]

主題2: [標題]
描述: [描述]"""

            response = await ai_service.generate(prompt)
            if not response:
                return []

            parsed = self._parse_ai_topics(response, channel, count)
            topic_category = self._to_topic_category(category)
            out: List[Dict[str, Any]] = []
            for p in parsed:
                translated_title, desc = await self._topic_collector._translate_title(
                    p["title"], topic_category, target_language
                )
                out.append({
                    "title": translated_title,
                    "original_title": p["title"],
                    "summary": desc or p.get("summary", ""),
                    "source_url": None,
                    "source_name": "AI Generated (RSS unavailable)",
                    "source_layer": 3,
                    "image_url": None,
                    "channel_id": channel.get("id", ""),
                    "category": category,
                    "region": region,
                    "collected_at": datetime.utcnow().isoformat(),
                    "is_ai_generated": True,
                })
            return out
        except Exception as e:
            logger.error(f"Layer 3 AI 生成失敗: {e}")
            return []

    def _parse_ai_topics(
        self, response: str, channel: Dict[str, Any], count: int
    ) -> List[Dict[str, Any]]:
        topics = []
        pattern = r"主題\d+:\s*(.+?)\n描述:\s*(.+?)(?=\n主題|\n\n|$)"
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches[:count]:
            topics.append({
                "title": match[0].strip(),
                "summary": match[1].strip(),
            })
        return topics

    async def collect_all_channels(self) -> Dict[str, Any]:
        channels = await self.channel_repo.get_active_channels()
        results = {
            "total_channels": len(channels),
            "successful": 0,
            "failed": 0,
            "channels": [],
        }
        for channel in channels:
            result = await self.collect_for_channel(channel["id"], "zh-TW")
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
            results["channels"].append({
                "channel_id": channel["id"],
                "channel_name": channel["name"],
                "success": result["success"],
                "topics_collected": result.get("topics_collected", 0),
            })
        return results


channel_collector = ChannelCollector()

"""
頻道主題收集服務
Phase 3: 內容功能
整合頻道系統與主題收集，實現三層備用機制
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import feedparser
import httpx
from app.services.repositories.channel_repository import ChannelRepository
from app.services.channel_service import ChannelService
from app.models.channel import (
    ChannelCollectionStatus, ChannelCategory, ChannelRegion,
    DEFAULT_RSS_SOURCES, CATEGORY_FALLBACK_MAP
)
from app.services.ai.ai_service_factory import AIServiceFactory
import logging

logger = logging.getLogger(__name__)

# 每頻道每次收集的主題數量
TOPICS_PER_CHANNEL = 10


class ChannelCollector:
    """頻道主題收集器"""
    
    def __init__(self):
        self.channel_repo = ChannelRepository()
        self.channel_service = ChannelService()
    
    async def collect_for_channel(
        self,
        channel_id: str,
        target_language: str = "zh-TW"
    ) -> Dict[str, Any]:
        """
        為單一頻道收集主題（三層備用機制）
        
        Layer 1: 主要 RSS 來源
        Layer 2: 備用 RSS 來源（相近類別）
        Layer 3: AI 生成（當 RSS 全部失敗時）
        
        Args:
            channel_id: 頻道 ID
            target_language: 目標語言
            
        Returns:
            收集結果
        """
        channel = await self.channel_repo.get_channel_by_id(channel_id)
        if not channel:
            return {"success": False, "error": "Channel not found"}
        
        # 更新收集狀態
        await self.channel_repo.update_collection_status(
            channel_id,
            ChannelCollectionStatus.COLLECTING
        )
        
        try:
            topics = []
            collection_log = {
                "layer_1": {"attempted": 0, "success": 0, "sources": []},
                "layer_2": {"attempted": 0, "success": 0, "sources": []},
                "layer_3": {"attempted": 0, "success": 0},
            }
            
            # 取得 RSS 來源
            sources = self.channel_service.get_rss_sources_for_channel(channel)
            
            # Layer 1: 主要來源
            layer1_sources = [s for s in sources if s.get("layer") == 1]
            for source in layer1_sources:
                collection_log["layer_1"]["attempted"] += 1
                try:
                    items = await self._fetch_rss(source["url"])
                    if items:
                        collection_log["layer_1"]["success"] += 1
                        collection_log["layer_1"]["sources"].append(source["name"])
                        for item in items[:3]:  # 每個來源取 3 個
                            topics.append(self._create_topic_from_rss(item, source, channel))
                except Exception as e:
                    logger.warning(f"Layer 1 RSS 失敗: {source['name']} - {e}")
            
            # 如果 Layer 1 不足，使用 Layer 2
            if len(topics) < TOPICS_PER_CHANNEL:
                layer2_sources = [s for s in sources if s.get("layer") == 2]
                for source in layer2_sources:
                    if len(topics) >= TOPICS_PER_CHANNEL:
                        break
                    collection_log["layer_2"]["attempted"] += 1
                    try:
                        items = await self._fetch_rss(source["url"])
                        if items:
                            collection_log["layer_2"]["success"] += 1
                            collection_log["layer_2"]["sources"].append(source["name"])
                            for item in items[:2]:  # 每個備用來源取 2 個
                                if len(topics) < TOPICS_PER_CHANNEL:
                                    topics.append(self._create_topic_from_rss(item, source, channel))
                    except Exception as e:
                        logger.warning(f"Layer 2 RSS 失敗: {source['name']} - {e}")
            
            # 如果仍然不足，使用 Layer 3 (AI 生成)
            if len(topics) < TOPICS_PER_CHANNEL:
                collection_log["layer_3"]["attempted"] = 1
                try:
                    ai_topics = await self._generate_ai_topics(
                        channel,
                        TOPICS_PER_CHANNEL - len(topics),
                        target_language
                    )
                    if ai_topics:
                        collection_log["layer_3"]["success"] = 1
                        topics.extend(ai_topics)
                except Exception as e:
                    logger.error(f"Layer 3 AI 生成失敗: {e}")
            
            # 更新收集狀態為完成
            await self.channel_repo.update_collection_status(
                channel_id,
                ChannelCollectionStatus.COMPLETED,
                topic_count=len(topics)
            )
            
            return {
                "success": True,
                "channel_id": channel_id,
                "topics_collected": len(topics),
                "topics": topics,
                "collection_log": collection_log
            }
            
        except Exception as e:
            logger.error(f"頻道收集失敗: {channel_id} - {e}")
            
            # 更新收集狀態為失敗
            await self.channel_repo.update_collection_status(
                channel_id,
                ChannelCollectionStatus.FAILED
            )
            
            return {"success": False, "error": str(e)}
    
    async def _fetch_rss(self, url: str) -> List[Dict[str, Any]]:
        """取得 RSS 內容"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return []
                
                feed = feedparser.parse(response.content)
                items = []
                
                for entry in feed.entries[:5]:
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
        """從 RSS entry 提取圖片"""
        # 嘗試從 media_content 提取
        media_content = entry.get("media_content", [])
        if media_content and len(media_content) > 0:
            return media_content[0].get("url")
        
        # 嘗試從 media_thumbnail 提取
        media_thumbnail = entry.get("media_thumbnail", [])
        if media_thumbnail and len(media_thumbnail) > 0:
            return media_thumbnail[0].get("url")
        
        # 嘗試從 enclosures 提取
        enclosures = entry.get("enclosures", [])
        for enc in enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href", enc.get("url"))
        
        return None
    
    def _create_topic_from_rss(
        self,
        item: Dict[str, Any],
        source: Dict[str, Any],
        channel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """從 RSS item 建立主題"""
        return {
            "title": item["title"],
            "summary": item["summary"][:500] if item["summary"] else "",
            "source_url": item["link"],
            "source_name": source["name"],
            "source_layer": source.get("layer", 1),
            "image_url": item.get("image"),
            "channel_id": channel["id"],
            "category": channel["category"],
            "region": channel["region"],
            "collected_at": datetime.utcnow().isoformat(),
            "is_ai_generated": False,
        }
    
    async def _generate_ai_topics(
        self,
        channel: Dict[str, Any],
        count: int,
        target_language: str
    ) -> List[Dict[str, Any]]:
        """使用 AI 生成主題（Layer 3）"""
        try:
            ai_service = AIServiceFactory.get_service()
            
            category = channel.get("category", "trend")
            region = channel.get("region", "global")
            keywords = channel.get("custom_keywords", [])
            
            # 語言標籤
            lang_labels = {
                "zh-TW": "繁體中文",
                "en": "English",
                "ja": "日本語",
            }
            
            # 類別標籤
            category_labels = {
                "fashion": "時尚",
                "food": "美食",
                "trend": "趨勢",
                "finance": "財經",
                "sports": "運動",
                "tech": "科技",
                "entertainment": "娛樂",
                "other": "其他",
            }
            
            prompt = f"""作為內容策劃專家，請為以下頻道生成 {count} 個熱門主題。

頻道設定：
- 類別：{category_labels.get(category, category)}
- 地區：{region}
- 關鍵字：{', '.join(keywords) if keywords else '無'}
- 輸出語言：{lang_labels.get(target_language, "繁體中文")}

要求：
1. 每個主題應該是當前熱門或有話題性的內容
2. 標題要吸引人，適合社交媒體
3. 提供簡短描述（100字內）
4. 主題要符合頻道的類別和地區

格式（嚴格遵守）：
主題1: [標題]
描述: [描述]

主題2: [標題]
描述: [描述]

...以此類推"""

            response = await ai_service.generate(prompt)
            
            if not response:
                return []
            
            # 解析 AI 回應
            topics = self._parse_ai_topics(response, channel, count)
            
            return topics
            
        except Exception as e:
            logger.error(f"AI 生成主題失敗: {e}")
            return []
    
    def _parse_ai_topics(
        self,
        response: str,
        channel: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """解析 AI 生成的主題"""
        import re
        
        topics = []
        pattern = r'主題\d+:\s*(.+?)\n描述:\s*(.+?)(?=\n主題|\n\n|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches[:count]:
            title = match[0].strip()
            summary = match[1].strip()
            
            topics.append({
                "title": title,
                "summary": summary,
                "source_url": None,
                "source_name": "AI Generated",
                "source_layer": 3,
                "image_url": None,
                "channel_id": channel["id"],
                "category": channel["category"],
                "region": channel["region"],
                "collected_at": datetime.utcnow().isoformat(),
                "is_ai_generated": True,
            })
        
        return topics
    
    async def collect_all_channels(self) -> Dict[str, Any]:
        """收集所有活躍頻道的主題"""
        channels = await self.channel_repo.get_active_channels()
        
        results = {
            "total_channels": len(channels),
            "successful": 0,
            "failed": 0,
            "channels": []
        }
        
        for channel in channels:
            # 取得用戶語言偏好（這裡使用預設）
            # TODO: 從用戶設定取得語言偏好
            target_language = "zh-TW"
            
            result = await self.collect_for_channel(
                channel["id"],
                target_language
            )
            
            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
            
            results["channels"].append({
                "channel_id": channel["id"],
                "channel_name": channel["name"],
                "success": result["success"],
                "topics_collected": result.get("topics_collected", 0)
            })
        
        return results


# 建立全域實例
channel_collector = ChannelCollector()


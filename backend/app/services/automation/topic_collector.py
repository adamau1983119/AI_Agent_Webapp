"""
主題收集器服務
從各種來源（RSS、新聞、社交媒體等）收集熱門話題
"""
import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.topic import Category, SourceInfo

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

logger = logging.getLogger(__name__)


class TopicCollector:
    """主題收集器"""
    
    def __init__(self):
        self.rss_feeds = {
            Category.FASHION: [
                "https://www.vogue.com/feed/rss",
                "https://www.elle.com/rss/all.xml",
                "https://www.harpersbazaar.com/feed/",
            ],
            Category.FOOD: [
                "https://www.foodnetwork.com/feeds/all.rss",
                "https://www.bonappetit.com/feed/rss",
                "https://www.seriouseats.com/feeds/all",
            ],
            Category.TREND: [
                "https://feeds.feedburner.com/oreilly/radar",
                "https://techcrunch.com/feed/",
                "https://www.theverge.com/rss/index.xml",
            ],
        }
        
        # 備用關鍵字（當 RSS 無法取得時使用）
        self.fallback_keywords = {
            Category.FASHION: [
                "2025春夏時尚趨勢", "可持續時尚", "復古風格回歸",
                "街頭時尚", "時尚科技", "環保時尚"
            ],
            Category.FOOD: [
                "香港美食推薦", "街頭小吃", "傳統美食",
                "新興餐廳", "美食趨勢", "健康飲食"
            ],
            Category.TREND: [
                "AI技術發展", "可持續發展", "社會趨勢",
                "科技創新", "文化現象", "生活方式"
            ],
        }
    
    async def collect_topics(
        self,
        category: Category,
        count: int = 3,
        use_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        收集主題
        
        Args:
            category: 主題分類
            count: 需要收集的主題數量
            use_fallback: 如果 RSS 失敗，是否使用備用關鍵字
            
        Returns:
            主題列表
        """
        topics = []
        
        try:
            # 嘗試從 RSS 收集
            rss_topics = await self._collect_from_rss(category, count)
            topics.extend(rss_topics)
            
            # 如果收集到足夠的主題，返回
            if len(topics) >= count:
                return topics[:count]
            
            # 如果不足且允許使用備用方案，使用備用關鍵字生成主題
            if use_fallback and len(topics) < count:
                fallback_topics = await self._generate_from_keywords(
                    category,
                    count - len(topics)
                )
                topics.extend(fallback_topics)
                
        except Exception as e:
            logger.error(f"收集主題失敗: {e}")
            # 如果完全失敗，使用備用關鍵字
            if use_fallback:
                topics = await self._generate_from_keywords(category, count)
        
        return topics[:count]
    
    async def _collect_from_rss(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """從 RSS 收集主題"""
        topics = []
        feeds = self.rss_feeds.get(category, [])
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for feed_url in feeds:
                try:
                    response = await client.get(feed_url)
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries[:count]:
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        published = entry.get("published_parsed")
                        
                        if title:
                            # 提取關鍵字
                            keywords = self._extract_keywords(title, category)
                            
                            # 如果標題是英文，嘗試翻譯成中文並生成30字撮要
                            chinese_title, description = await self._translate_title_to_chinese(title, category)
                            
                            topic = {
                                "title": chinese_title,
                                "category": category.value,
                                "source": feed.feed.get("title", "RSS Feed"),
                                "description": description,  # 添加30字撮要
                                "sources": [
                                    {
                                        "type": "rss",
                                        "name": feed.feed.get("title", "RSS Feed"),
                                        "url": link,
                                        "title": chinese_title,
                                        "original_title": title,  # 保留原始英文標題
                                        "fetched_at": datetime.utcnow(),
                                        "verified": True,
                                        "keywords": keywords,
                                    }
                                ],
                            }
                            topics.append(topic)
                            
                            if len(topics) >= count:
                                break
                                
                except Exception as e:
                    logger.warning(f"無法從 RSS {feed_url} 收集主題: {e}")
                    continue
        
        return topics
    
    async def _generate_from_keywords(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """從備用關鍵字生成主題（使用 AI 生成中文標題）"""
        topics = []
        keywords = self.fallback_keywords.get(category, [])
        
        # 嘗試使用 AI 生成中文標題
        try:
            from app.services.ai.ai_service_factory import AIServiceFactory
            from app.config import settings
            from app.prompts.title_prompt import build_title_prompt
            
            ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
            
            for keyword in keywords[:count]:
                try:
                    # 使用 AI 生成中文標題和摘要
                    prompt = build_title_prompt(category, keyword=keyword)
                    ai_response = await ai_service._call_api(prompt)
                    
                    # 解析 AI 返回的標題和摘要
                    title = None
                    description = None
                    
                    # 嘗試解析格式：標題：[標題]\n摘要：[摘要]
                    lines = ai_response.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('標題：') or line.startswith('标题：'):
                            title = line.replace('標題：', '').replace('标题：', '').strip().strip('"').strip("'")
                        elif line.startswith('摘要：') or line.startswith('摘要：'):
                            description = line.replace('摘要：', '').replace('摘要：', '').strip().strip('"').strip("'")
                    
                    # 如果解析失敗，嘗試其他格式
                    if not title:
                        # 嘗試第一行作為標題
                        title = lines[0].strip().strip('"').strip("'")
                        if len(lines) > 1:
                            description = lines[1].strip().strip('"').strip("'")
                    
                    # 如果還是沒有標題，使用整個響應作為標題
                    if not title:
                        title = ai_response.strip().strip('"').strip("'").split('\n')[0]
                    
                    # 確保標題不為空
                    if not title or len(title) < 3:
                        title = keyword
                    
                    topic = {
                        "title": title,
                        "category": category.value,
                        "source": "AI Generated",
                        "description": description,  # 添加摘要字段
                        "sources": [
                            {
                                "type": "ai",
                                "name": "AI Generated Topic",
                                "url": "",
                                "title": title,
                                "fetched_at": datetime.utcnow(),
                                "verified": False,
                                "keywords": [keyword],
                            }
                        ],
                    }
                    topics.append(topic)
                except Exception as e:
                    logger.warning(f"使用 AI 生成標題失敗，使用關鍵字作為標題: {e}")
                    # 如果 AI 生成失敗，使用關鍵字作為標題（沒有摘要）
                    topic = {
                        "title": keyword,
                        "category": category.value,
                        "source": "AI Generated",
                        "description": None,  # AI 失敗時沒有摘要
                        "sources": [
                            {
                                "type": "ai",
                                "name": "AI Generated Topic",
                                "url": "",
                                "title": keyword,
                                "fetched_at": datetime.utcnow(),
                                "verified": False,
                                "keywords": [keyword],
                            }
                        ],
                    }
                    topics.append(topic)
        except Exception as e:
            logger.warning(f"無法使用 AI 生成標題，使用關鍵字作為標題: {e}")
            # 如果完全無法使用 AI，直接使用關鍵字（沒有摘要）
            for keyword in keywords[:count]:
                topic = {
                    "title": keyword,
                    "category": category.value,
                    "source": "AI Generated",
                    "description": None,  # AI 不可用時沒有摘要
                    "sources": [
                        {
                            "type": "ai",
                            "name": "AI Generated Topic",
                            "url": "",
                            "title": keyword,
                            "fetched_at": datetime.utcnow(),
                            "verified": False,
                            "keywords": [keyword],
                        }
                    ],
                }
                topics.append(topic)
        
        return topics
    
    async def _translate_title_to_chinese(
        self,
        english_title: str,
        category: Category
    ) -> tuple[str, Optional[str]]:
        """
        將英文標題翻譯成中文，並生成30字撮要
        
        Returns:
            (chinese_title, description) 元組
        """
        # 簡單判斷是否為英文（包含英文字母）
        has_english = any(c.isalpha() and ord(c) < 128 for c in english_title)
        
        if not has_english:
            # 如果已經是中文，直接返回（沒有撮要）
            return english_title, None
        
        # 嘗試使用 AI 翻譯並生成撮要
        try:
            from app.services.ai.ai_service_factory import AIServiceFactory
            from app.config import settings
            from app.prompts.title_prompt import build_title_prompt
            
            ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
            prompt = build_title_prompt(category, english_title=english_title)
            ai_response = await ai_service._call_api(prompt)
            
            # 解析 AI 返回的標題和摘要
            title = None
            description = None
            
            # 嘗試解析格式：標題：[標題]\n摘要：[摘要]
            lines = ai_response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('標題：') or line.startswith('标题：'):
                    title = line.replace('標題：', '').replace('标题：', '').strip().strip('"').strip("'")
                elif line.startswith('摘要：') or line.startswith('摘要：'):
                    description = line.replace('摘要：', '').replace('摘要：', '').strip().strip('"').strip("'")
            
            # 如果解析失敗，嘗試其他格式
            if not title:
                # 嘗試第一行作為標題
                title = lines[0].strip().strip('"').strip("'")
                if len(lines) > 1:
                    description = lines[1].strip().strip('"').strip("'")
            
            # 如果還是沒有標題，使用整個響應的第一行作為標題
            if not title:
                title = ai_response.strip().strip('"').strip("'").split('\n')[0]
            
            # 清理標題
            title = title.strip().strip('"').strip("'").strip()
            if description:
                description = description.strip().strip('"').strip("'").strip()
            
            if title and len(title) > 5:  # 確保翻譯成功
                return title, description
        except Exception as e:
            logger.warning(f"翻譯標題失敗: {e}，使用原始標題")
        
        # 如果翻譯失敗，返回原始標題（沒有撮要）
        return english_title, None
    
    def _extract_keywords(
        self,
        text: str,
        category: Category
    ) -> List[str]:
        """從文本中提取關鍵字"""
        keywords = []
        
        # 簡單的關鍵字提取邏輯
        # 可以根據需要改進（使用 NLP 庫）
        words = text.split()
        
        # 根據分類添加相關關鍵字
        if category == Category.FASHION:
            fashion_keywords = ["時尚", "潮流", "風格", "設計", "服裝"]
            keywords.extend([w for w in words if any(kw in w for kw in fashion_keywords)])
        elif category == Category.FOOD:
            food_keywords = ["美食", "餐廳", "料理", "小吃", "料理"]
            keywords.extend([w for w in words if any(kw in w for kw in food_keywords)])
        elif category == Category.TREND:
            trend_keywords = ["趨勢", "發展", "創新", "技術", "社會"]
            keywords.extend([w for w in words if any(kw in w for kw in trend_keywords)])
        
        # 去重並限制數量
        return list(set(keywords))[:5]


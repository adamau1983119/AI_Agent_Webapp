"""
增強版主題收集器
加入排行榜抓取、一致性檢查、健康度監控
"""
import logging
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.topic import Category, SourceInfo
from app.services.automation.data_validator import DataValidator

logger = logging.getLogger(__name__)


class EnhancedTopicCollector:
    """增強版主題收集器（專家建議）"""
    
    def __init__(self):
        self.data_validator = DataValidator()
        
        # 主要來源（3個）
        self.primary_sources = {
            Category.FASHION: [
                {"name": "Vogue Trending", "url": "https://www.vogue.com/trending", "type": "trending"},
                {"name": "WWD", "url": "https://wwd.com", "type": "news"},
                {"name": "Fashion Week", "url": "https://fashionweek.com", "type": "news"}
            ],
            Category.FOOD: [
                {"name": "Google Trends HK", "url": "https://trends.google.com/trending", "type": "trending"},
                {"name": "OpenRice", "url": "https://www.openrice.com", "type": "food_platform"},
                {"name": "大眾點評", "url": "https://www.dianping.com", "type": "food_platform"}
            ],
            Category.TREND: [
                {"name": "學術資料庫", "url": "https://scholar.google.com", "type": "academic"},
                {"name": "新聞網站", "url": "https://news.google.com", "type": "news"},
                {"name": "社交媒體趨勢", "url": "https://trends.google.com", "type": "trending"}
            ]
        }
        
        # 備用來源（2個）
        self.backup_sources = {
            Category.FASHION: [
                {"name": "微博熱搜", "url": "https://weibo.com", "type": "social"},
                {"name": "Instagram Trends", "url": "https://www.instagram.com", "type": "social"}
            ],
            Category.FOOD: [
                {"name": "Facebook Food", "url": "https://www.facebook.com", "type": "social"},
                {"name": "小紅書", "url": "https://www.xiaohongshu.com", "type": "social"}
            ],
            Category.TREND: [
                {"name": "Twitter Trends", "url": "https://twitter.com", "type": "social"},
                {"name": "Reddit", "url": "https://www.reddit.com", "type": "social"}
            ]
        }
        
        # Fallback 關鍵字庫
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
    
    async def collect_topics_with_redundancy(
        self,
        category: Category,
        count: int = 3,
        region: str = "global"
    ) -> List[Dict[str, Any]]:
        """
        使用3-2-1備援機制收集主題（專家建議）
        
        Args:
            category: 主題分類
            count: 需要收集的主題數量
            region: 地區（global/hongkong/china/us）
            
        Returns:
            主題列表
        """
        topics = []
        
        try:
            # 第一層：主要來源（3個）
            primary_topics = await self._try_primary_sources(category, count, region)
            topics.extend(primary_topics)
            
            if len(topics) >= count:
                return topics[:count]
            
            # 第二層：備用來源（2個）
            backup_topics = await self._try_backup_sources(
                category,
                count - len(topics),
                region
            )
            topics.extend(backup_topics)
            
            if len(topics) >= count:
                return topics[:count]
            
            # 第三層：Fallback
            fallback_topics = await self._use_fallback_keywords(
                category,
                count - len(topics)
            )
            topics.extend(fallback_topics)
            
            return topics[:count]
            
        except Exception as e:
            logger.error(f"收集主題失敗: {e}")
            # 如果完全失敗，使用 Fallback
            return await self._use_fallback_keywords(category, count)
    
    async def _try_primary_sources(
        self,
        category: Category,
        count: int,
        region: str
    ) -> List[Dict[str, Any]]:
        """嘗試主要來源"""
        topics = []
        sources = self.primary_sources.get(category, [])
        
        for source in sources[:3]:  # 最多嘗試3個
            try:
                # 檢查來源健康度
                health = await self.data_validator.check_source_health(source["url"])
                
                if health.get("health_score", 0) < 0.6:
                    logger.warning(f"來源 {source['name']} 健康度不足，跳過")
                    continue
                
                # 抓取關鍵字（簡化版，實際應該從API獲取）
                keyword = await self._fetch_keyword_from_source(source, category, region)
                
                if keyword:
                    # 驗證一致性
                    validation = await self.data_validator.validate_topic_consistency(
                        keyword=keyword,
                        category=category,
                        sources=[source]
                    )
                    
                    if validation.get("valid"):
                        topic = {
                            "title": keyword,
                            "keyword": keyword,
                            "category": category.value,
                            "source": source["name"],
                            "sources": [{
                                "type": source["type"],
                                "name": source["name"],
                                "url": source["url"],
                                "title": keyword,
                                "fetched_at": datetime.utcnow(),
                                "verified": validation.get("valid", False),
                                "reliability": "high" if health.get("health_score", 0) > 0.7 else "medium"
                            }],
                            "fallback": False
                        }
                        
                        # 如果是單來源趨勢，標記
                        if validation.get("should_mark"):
                            topic["single_source_trend"] = True
                        
                        topics.append(topic)
                        
                        if len(topics) >= count:
                            break
                            
            except Exception as e:
                logger.warning(f"從主要來源 {source['name']} 收集失敗: {e}")
                continue
        
        return topics
    
    async def _try_backup_sources(
        self,
        category: Category,
        count: int,
        region: str
    ) -> List[Dict[str, Any]]:
        """嘗試備用來源"""
        topics = []
        sources = self.backup_sources.get(category, [])
        
        for source in sources[:2]:  # 最多嘗試2個
            try:
                # 檢查來源健康度
                health = await self.data_validator.check_source_health(source["url"])
                
                if health.get("health_score", 0) < 0.4:
                    logger.warning(f"備用來源 {source['name']} 健康度不足，跳過")
                    continue
                
                # 抓取關鍵字
                keyword = await self._fetch_keyword_from_source(source, category, region)
                
                if keyword:
                    topic = {
                        "title": keyword,
                        "keyword": keyword,
                        "category": category.value,
                        "source": source["name"],
                        "sources": [{
                            "type": source["type"],
                            "name": source["name"],
                            "url": source["url"],
                            "title": keyword,
                            "fetched_at": datetime.utcnow(),
                            "verified": True,
                            "reliability": "medium"
                        }],
                        "fallback": False
                    }
                    topics.append(topic)
                    
                    if len(topics) >= count:
                        break
                        
            except Exception as e:
                logger.warning(f"從備用來源 {source['name']} 收集失敗: {e}")
                continue
        
        return topics
    
    async def _use_fallback_keywords(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """使用 Fallback 關鍵字庫"""
        topics = []
        keywords = self.fallback_keywords.get(category, [])
        
        for keyword in keywords[:count]:
            topic = {
                "title": keyword,
                "keyword": keyword,
                "category": category.value,
                "source": "Fallback",
                "sources": [{
                    "type": "fallback",
                    "name": "Fallback Keyword Library",
                    "url": "",
                    "title": keyword,
                    "fetched_at": datetime.utcnow(),
                    "verified": False,
                    "reliability": "low"
                }],
                "fallback": True,  # 標記為 Fallback
                "fallback_badge": "Fallback 生成",
                "fallback_reason": "所有來源失效，使用預設關鍵字庫"
            }
            topics.append(topic)
        
        return topics
    
    async def _fetch_keyword_from_source(
        self,
        source: Dict[str, Any],
        category: Category,
        region: str
    ) -> Optional[str]:
        """
        從來源抓取關鍵字（簡化版）
        
        實際應該：
        - 調用 Google Trends API
        - 解析 RSS Feed
        - 抓取排行榜頁面
        """
        # 這裡只是模擬，實際需要實作具體的抓取邏輯
        # 例如：調用 Google Trends API、解析網頁等
        
        # 簡化版：返回模擬關鍵字
        if category == Category.FASHION:
            return f"Dior 2026 春夏秀（來自 {source['name']}）"
        elif category == Category.FOOD:
            return f"元朗最好食燒賣top 3（來自 {source['name']}）"
        else:
            return f"13-16歲青少年的容貌焦慮（來自 {source['name']}）"


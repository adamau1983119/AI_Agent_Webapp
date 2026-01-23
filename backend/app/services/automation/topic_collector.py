"""
主題收集器服務 v3.0
從各種來源（RSS、新聞、社交媒體等）收集熱門話題
使用角色分配策略確保內容來源多樣性
"""
import logging
import httpx
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import Counter

from app.models.topic import Category, SourceInfo
from app.config.feed_roles import (
    get_roles_for_category,
    get_role_distribution,
    get_source_weight,
    get_all_feeds_for_category,
)
from app.services.scoring_service import ScoringService, DiversityScorer
from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.services.feed_health_service import FeedHealthService

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
    """主題收集器 v3.0 - 支援角色分配策略 + 健康監控"""
    
    def __init__(self):
        # 評分服務
        self.scoring_service = ScoringService()
        self.diversity_scorer = DiversityScorer()
        
        # 健康監控服務
        self.health_repo = FeedHealthRepository()
        self.health_service = FeedHealthService(self.health_repo)
        
        # 備用關鍵字（當 RSS 無法取得時使用）
        self.fallback_keywords = {
            Category.FASHION: [
                "2025春夏時尚趨勢", "可持續時尚", "復古風格回歸",
                "街頭時尚", "時尚科技", "環保時尚",
                "設計師系列", "名人穿搭", "時裝週", "潮流配件"
            ],
            Category.FOOD: [
                "香港美食推薦", "街頭小吃", "傳統美食",
                "新興餐廳", "美食趨勢", "健康飲食",
                "異國料理", "甜點推薦", "深夜食堂", "週末早午餐"
            ],
            Category.TREND: [
                "AI技術發展", "可持續發展", "社會趨勢",
                "科技創新", "文化現象", "生活方式",
                "數位轉型", "未來工作", "元宇宙", "綠色科技"
            ],
        }
    
    async def collect_topics(
        self,
        category: Category,
        count: int = 10,
        use_fallback: bool = True
    ) -> List[Dict[str, Any]]:
        """
        收集主題（使用角色分配策略）
        
        Args:
            category: 主題分類
            count: 需要收集的主題數量（預設 10）
            use_fallback: 如果 RSS 失敗，是否使用備用關鍵字
            
        Returns:
            主題列表
        """
        topics = []
        
        try:
            # 使用角色分配策略收集
            rss_topics = await self._collect_by_roles(category, count)
            topics.extend(rss_topics)
            
            # 計算多樣性分數
            diversity_report = self.diversity_scorer.get_diversity_report(topics)
            logger.info(f"多樣性報告: score={diversity_report['score']}, "
                       f"sources={diversity_report['unique_sources']}, "
                       f"status={diversity_report['status']}")
            
            # 如果多樣性不足，記錄警告
            if not diversity_report['passed']:
                logger.warning(f"⚠️ 多樣性分數不足: {diversity_report['score']} < 0.6")
            
            # 如果收集到足夠的主題，返回
            if len(topics) >= count:
                return topics[:count]
            
            # 如果不足且允許使用備用方案，使用備用關鍵字生成主題
            if use_fallback and len(topics) < count:
                logger.info(f"主題不足 ({len(topics)}/{count})，使用備用關鍵字補充")
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
    
    async def _collect_by_roles(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        使用角色分配策略收集主題
        
        每個角色分配固定數量的主題，確保來源多樣性
        """
        topics = []
        roles = get_roles_for_category(category)
        role_distribution = get_role_distribution(category)
        
        if not roles:
            logger.warning(f"分類 {category.value} 沒有配置角色，使用舊版收集方式")
            return await self._collect_from_rss_legacy(category, count)
        
        # 導入文章提取器
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            for role_name, role_count in role_distribution.items():
                feeds = roles.get(role_name, [])
                if not feeds:
                    logger.warning(f"角色 {role_name} 沒有配置 Feed")
                    continue
                
                logger.info(f"從角色 '{role_name}' 收集 {role_count} 個主題")
                role_topics = await self._collect_from_role(
                    client=client,
                    extractor=extractor,
                    category=category,
                    feeds=feeds,
                    count=role_count,
                    role_name=role_name
                )
                topics.extend(role_topics)
                
                logger.info(f"角色 '{role_name}' 收集完成: {len(role_topics)} 個主題")
        
        return topics
    
    async def _collect_from_role(
        self,
        client: httpx.AsyncClient,
        extractor,
        category: Category,
        feeds: List[Tuple[str, str, float]],
        count: int,
        role_name: str
    ) -> List[Dict[str, Any]]:
        """
        從單一角色的 Feed 列表收集主題（含健康監控）
        
        Args:
            client: HTTP 客戶端
            extractor: 文章提取器
            category: 分類
            feeds: [(來源名稱, URL, 權重), ...]
            count: 需要收集的數量
            role_name: 角色名稱
        """
        topics = []
        
        for source_name, feed_url, source_weight in feeds:
            if len(topics) >= count:
                break
            
            # 健康監控：檢查是否暫停
            try:
                if await self.health_service.should_skip_feed(feed_url):
                    logger.warning(f"⏸️ 跳過暫停的來源: {source_name} ({feed_url})")
                    continue
            except Exception as e:
                logger.debug(f"健康檢查失敗，繼續抓取: {e}")
            
            try:
                logger.info(f"嘗試從 {source_name} ({feed_url}) 收集主題")
                response = await client.get(feed_url)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                feed_title = feed.feed.get("title", source_name)
                
                # 處理每個條目
                for entry in feed.entries[:count * 2]:  # 取更多以便過濾
                    if len(topics) >= count:
                        break
                    
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    
                    if not title or not link:
                        continue
                    
                    # 過濾優惠券/折扣文章
                    if category == Category.TREND and self._is_deal_or_coupon_article(title, link):
                        logger.info(f"🚫 跳過優惠券文章: {title}")
                        continue
                    
                    # 提取關鍵字
                    keywords = self._extract_keywords(title, category)
                    
                    # 翻譯標題並生成摘要
                    chinese_title, description = await self._translate_title_to_chinese(title, category)
                    
                    # 提取原文圖片和內容
                    article_info = await extractor.extract_article_info(link)
                    
                    # 構建來源資訊
                    source_info = {
                        "type": "rss",
                        "name": feed_title,
                        "url": link,
                        "title": chinese_title,
                        "original_title": title,
                        "fetched_at": datetime.utcnow(),
                        "verified": True,
                        "keywords": keywords,
                        "role": role_name,  # 記錄角色
                        "source_weight": source_weight,  # 記錄來源權重
                    }
                    
                    # 添加提取的資訊
                    if article_info.get("success"):
                        source_info["images"] = article_info.get("images", [])
                        source_info["original_content"] = article_info.get("original_content")
                        source_info["language"] = article_info.get("language")
                        
                        style_info = article_info.get("style")
                        if style_info:
                            source_info["style"] = style_info if isinstance(style_info, dict) else style_info
                    
                    # 計算文章評分
                    article_data = {
                        "title": chinese_title,
                        "source": source_name,
                        "source_name": source_name,
                        "images": source_info.get("images", []),
                        "summary": description,
                        "original_content": source_info.get("original_content"),
                        "keywords": keywords,
                        "published": entry.get("published_parsed"),
                        "fetched_at": datetime.utcnow(),
                    }
                    
                    score_result = self.scoring_service.compute_score(article_data, category)
                    
                    topic = {
                        "title": chinese_title,
                        "category": category.value,
                        "source": source_name,
                        "source_name": source_name,  # 用於多樣性計算
                        "description": description,
                        "sources": [source_info],
                        "role": role_name,
                        "score": score_result["score"],
                        "score_breakdown": score_result["score_breakdown"],
                    }
                    topics.append(topic)
                    logger.info(f"✅ 收集主題: {chinese_title[:30]}... (score: {score_result['score']:.2f})")
                
                # 健康監控：記錄成功
                try:
                    await self.health_service.record_fetch_result(
                        feed_url=feed_url,
                        source_name=source_name,
                        success=True
                    )
                except Exception as e:
                    logger.debug(f"記錄成功狀態失敗: {e}")
                
            except httpx.TimeoutException:
                logger.warning(f"⏱️ {source_name} 請求超時")
                # 健康監控：記錄失敗
                try:
                    await self.health_service.record_fetch_result(
                        feed_url=feed_url,
                        source_name=source_name,
                        success=False,
                        error="TimeoutException"
                    )
                except Exception:
                    pass
                continue
            except Exception as e:
                logger.warning(f"❌ 無法從 {source_name} 收集主題: {e}")
                # 健康監控：記錄失敗
                try:
                    await self.health_service.record_fetch_result(
                        feed_url=feed_url,
                        source_name=source_name,
                        success=False,
                        error=str(e)
                    )
                except Exception:
                    pass
                continue
        
        return topics
    
    async def _collect_from_rss_legacy(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """舊版 RSS 收集方式（備用）"""
        topics = []
        feeds = get_all_feeds_for_category(category)
        
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for source_name, feed_url, source_weight in feeds:
                if len(topics) >= count:
                    break
                
                try:
                    response = await client.get(feed_url)
                    feed = feedparser.parse(response.text)
                    
                    for entry in feed.entries[:count * 3]:
                        if len(topics) >= count:
                            break
                        
                        title = entry.get("title", "")
                        link = entry.get("link", "")
                        
                        if category == Category.TREND and self._is_deal_or_coupon_article(title, link):
                            continue
                        
                        if title:
                            keywords = self._extract_keywords(title, category)
                            chinese_title, description = await self._translate_title_to_chinese(title, category)
                            article_info = await extractor.extract_article_info(link)
                            
                            source_info = {
                                "type": "rss",
                                "name": feed.feed.get("title", source_name),
                                "url": link,
                                "title": chinese_title,
                                "original_title": title,
                                "fetched_at": datetime.utcnow(),
                                "verified": True,
                                "keywords": keywords,
                            }
                            
                            if article_info.get("success"):
                                source_info["images"] = article_info.get("images", [])
                                source_info["original_content"] = article_info.get("original_content")
                                source_info["language"] = article_info.get("language")
                                style_info = article_info.get("style")
                                if style_info:
                                    source_info["style"] = style_info if isinstance(style_info, dict) else style_info
                            
                            topic = {
                                "title": chinese_title,
                                "category": category.value,
                                "source": source_name,
                                "source_name": source_name,
                                "description": description,
                                "sources": [source_info],
                            }
                            topics.append(topic)
                            
                except Exception as e:
                    logger.warning(f"無法從 RSS {feed_url} 收集主題: {e}")
                    continue
        
        return topics
    
    def _is_deal_or_coupon_article(self, title: str, link: str) -> bool:
        """檢查文章是否為優惠券/折扣相關內容 - v3 更精確的過濾"""
        coupon_patterns = [
            ("coupon", "code"),
            ("promo", "code"),
            ("discount", "code"),
            ("% off", ""),
            ("$", "off"),
        ]
        
        definite_coupon_keywords = [
            "coupon code", "promo code", "discount code", "voucher",
            "clearance sale", "flash sale", "black friday", "cyber monday",
            "prime day", "best price", "lowest price", "price drop",
        ]
        
        url_coupon_paths = [
            "/deals/", "/coupons/", "/offers/", "/sales/", "/shopping/", "/promo/"
        ]
        
        title_lower = title.lower()
        link_lower = link.lower()
        
        for path in url_coupon_paths:
            if path in link_lower:
                return True
        
        for keyword in definite_coupon_keywords:
            if keyword in title_lower:
                return True
        
        for pattern in coupon_patterns:
            if all(p in title_lower for p in pattern if p):
                return True
        
        return False
    
    async def _generate_from_keywords(
        self,
        category: Category,
        count: int
    ) -> List[Dict[str, Any]]:
        """從備用關鍵字生成主題（使用 AI 生成中文標題）"""
        topics = []
        keywords = self.fallback_keywords.get(category, [])
        
        try:
            from app.services.ai.ai_service_factory import AIServiceFactory
            from app.config import settings
            from app.prompts.title_prompt import build_title_prompt
            
            ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
            
            for keyword in keywords[:count]:
                try:
                    prompt = build_title_prompt(category, keyword=keyword)
                    ai_response = await ai_service._call_api(prompt)
                    
                    title = None
                    description = None
                    
                    lines = ai_response.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('標題：') or line.startswith('标题：'):
                            title = line.replace('標題：', '').replace('标题：', '').strip().strip('"').strip("'")
                        elif line.startswith('摘要：') or line.startswith('摘要：'):
                            description = line.replace('摘要：', '').replace('摘要：', '').strip().strip('"').strip("'")
                    
                    if not title:
                        title = lines[0].strip().strip('"').strip("'")
                        if len(lines) > 1:
                            description = lines[1].strip().strip('"').strip("'")
                    
                    if not title:
                        title = ai_response.strip().strip('"').strip("'").split('\n')[0]
                    
                    if not title or len(title) < 3:
                        title = keyword
                    
                    topic = {
                        "title": title,
                        "category": category.value,
                        "source": "AI Generated",
                        "source_name": "AI Generated",
                        "description": description,
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
                    topic = {
                        "title": keyword,
                        "category": category.value,
                        "source": "AI Generated",
                        "source_name": "AI Generated",
                        "description": None,
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
            for keyword in keywords[:count]:
                topic = {
                    "title": keyword,
                    "category": category.value,
                    "source": "AI Generated",
                    "source_name": "AI Generated",
                    "description": None,
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
        has_english = any(c.isalpha() and ord(c) < 128 for c in english_title)
        
        if not has_english:
            return english_title, None
        
        try:
            from app.services.ai.ai_service_factory import AIServiceFactory
            from app.config import settings
            from app.prompts.title_prompt import build_title_prompt
            
            ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
            prompt = build_title_prompt(category, english_title=english_title)
            ai_response = await ai_service._call_api(prompt)
            
            title = None
            description = None
            
            lines = ai_response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('標題：') or line.startswith('标题：'):
                    title = line.replace('標題：', '').replace('标题：', '').strip().strip('"').strip("'")
                elif line.startswith('摘要：') or line.startswith('摘要：'):
                    description = line.replace('摘要：', '').replace('摘要：', '').strip().strip('"').strip("'")
            
            if not title:
                title = lines[0].strip().strip('"').strip("'")
                if len(lines) > 1:
                    description = lines[1].strip().strip('"').strip("'")
            
            if not title:
                title = ai_response.strip().strip('"').strip("'").split('\n')[0]
            
            title = title.strip().strip('"').strip("'").strip()
            if description:
                description = description.strip().strip('"').strip("'").strip()
            
            if title and len(title) > 5:
                return title, description
        except Exception as e:
            logger.warning(f"翻譯標題失敗: {e}，使用原始標題")
        
        return english_title, None
    
    def _extract_keywords(
        self,
        text: str,
        category: Category
    ) -> List[str]:
        """從文本中提取關鍵字"""
        keywords = []
        
        words = text.split()
        
        if category == Category.FASHION:
            fashion_keywords = ["時尚", "潮流", "風格", "設計", "服裝", "fashion", "style", "trend"]
            keywords.extend([w for w in words if any(kw in w.lower() for kw in fashion_keywords)])
        elif category == Category.FOOD:
            food_keywords = ["美食", "餐廳", "料理", "小吃", "food", "restaurant", "recipe"]
            keywords.extend([w for w in words if any(kw in w.lower() for kw in food_keywords)])
        elif category == Category.TREND:
            trend_keywords = ["趨勢", "發展", "創新", "技術", "tech", "innovation", "ai"]
            keywords.extend([w for w in words if any(kw in w.lower() for kw in trend_keywords)])
        
        return list(set(keywords))[:5]

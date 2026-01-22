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
                # ========== 權威趨勢類（Top 3）==========
                "https://www.vogue.com/feed/rss",  # 1. Vogue - 時尚聖經，全球趨勢、名流穿搭及時裝週最權威報導
                "https://www.elle.com/rss/all.xml",  # 4. Elle - 全球最大時尚雜誌網絡之一，內容涵蓋美容、生活方式與潮流資訊
                # 注意：Harper's Bazaar 目前沒有公開 RSS Feed，可能需要手動添加或使用其他方式
                
                # ========== 產業分析類 ==========
                "https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml",  # 2. Business of Fashion (BoF) - 全球時尚產業分析領導者，專注商業新聞與深度市場研究
                "https://wwd.com/feed/",  # 3. WWD (Women's Wear Daily) - 時尚界每日通訊，時尚管理與 B2B 資訊首選
                # 注意：Vogue Business 可能需要訂閱才能訪問 RSS
                
                # ========== 街頭潮牌類 ==========
                "https://hypebeast.com/feed",  # 7. Hypebeast - 全球潮流與街頭文化領導媒體
                "https://www.highsnobiety.com/feeds/rss",  # 8. Highsnobiety - 專注潮流鞋款、街頭穿搭與當代藝術
                
                # ========== 穿搭靈感類 ==========
                "https://www.whowhatwear.com/feeds.xml",  # 9. Who What Wear - 引領消費者穿搭靈感與購物趨勢，親民且實用
                "https://popbee.com/feed",  # 20. Popbee - 亞洲極具影響力的時尚新聞平台，專注快速更新的亞洲及全球潮流資訊
                
                # ========== 時尚新聞與評論類 ==========
                "https://fashionista.com/.rss/excerpt/",  # 10. Fashionista - 提供獨立時尚評論、職業發展資訊及行業八卦
                "https://www.cosmopolitan.com/rss/all.xml",  # 11. Cosmopolitan - 針對年輕女性，將時尚與情感、娛樂與生活深度結合
                "https://www.gq.com/feed/rss",  # 12. GQ Style - 全球男裝與男性品味的指標性新聞網站
                "https://www.dazeddigital.com/rss",  # 14. Dazed Digital - 以大膽的藝術風格與邊緣文化報導著稱
                "https://www.marieclaire.com/rss/all.xml",  # 15. Marie Claire - 結合時尚潮流與社會性議題報導的全球性媒體
                
                # ========== 其他重要來源 ==========
                # 注意：以下網站可能沒有公開 RSS Feed 或需要特殊處理
                # - i-D Magazine (13) - 可能需要使用網頁爬蟲
                # - FashionUnited (17) - B2B 平台，可能需要訂閱
                # - Models.com (18) - 可能需要特殊權限
                # - The Cut (19) - 可能需要使用網頁爬蟲
                # - Lyst Index (16) - 電商平台，沒有 RSS Feed
                
                # ========== 全球新聞來源（補充）==========
                "https://feeds.bbci.co.uk/news/rss.xml",  # BBC News - 全球公認最具中立性與廣度的多語言新聞平台
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",  # The New York Times - 全球數位訂閱量第一，提供權威的深度調查與專題報導
                "https://www.theguardian.com/world/rss",  # The Guardian - 以獨立報導著稱的英國媒體，在全球擁有極高數位讀者量
                "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",  # Google News - 全球最強大的新聞聚合平台，個人化推薦的關鍵入口
                "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera - 從中東視角出發，提供全球特別是南方世界的深度報導
                "https://feeds.washingtonpost.com/rss/world",  # The Washington Post - 專注於美國政治與全球政策的權威媒體
                "https://feeds.a.dj.com/rss/RSSWorldNews.xml",  # Wall Street Journal - 全球商業、財經與政策新聞的首選
                "https://www.ft.com/rss/home/uk",  # Financial Times - 專注於全球市場分析與歐洲經濟趨勢
                "https://www.theatlantic.com/feed/all/",  # The Atlantic - 專注於當代思想、文化與政治深論的長篇報導媒體
                "https://www.scmp.com/rss/91/feed/",  # South China Morning Post - 報導中國與亞洲動態的全球關鍵窗口
            ],
            Category.FOOD: [
                # ========== 餐廳與動態類 ==========
                "https://www.eater.com/rss/index.xml",  # 2. Eater - 全美最頂尖的餐廳新聞、食評及飲食地圖網站
                # 注意：Grub Street (20) - 目前無公開 RSS Feed，可能需要使用網頁爬蟲
                
                # ========== 產業與商業類 ==========
                # 注意：Food Dive (9) - 目前無公開 RSS Feed，可能需要訂閱
                # 注意：Food Navigator (17) - 目前無公開 RSS Feed，可能需要訂閱
                
                # ========== 烹飪與食譜類 ==========
                "https://www.bonappetit.com/feed/rss",  # 6. Bon Appétit - 兼具時尚美感與美食文化的指標性雜誌網站
                "https://www.epicurious.com/feed/rss",  # 10. Epicurious - 集結權威食譜、烹飪影片及廚具評測的綜合平台
                "https://www.thekitchn.com/main.rss",  # 5. The Kitchn - 專注於家庭廚房靈感、清潔技巧及日常餐點的新聞網
                "https://feeds.feedburner.com/simplyrecipes",  # 12. Simply Recipes - 以家庭主婦/夫為核心，提供可靠且易上手的家常菜資訊
                # 注意：AllRecipes (1) - 返回 460，可能需要訂閱
                # 注意：Serious Eats (4) - 返回 460，可能需要訂閱
                # 注意：Food Network (3) - 返回 403，可能需要特殊權限
                
                # ========== 健康與營養類 ==========
                "https://www.eatthis.com/feed/",  # 14. Eat This, Not That! - 專注於食品營養、健康新聞與超市商品對比
                # 注意：Cooking Light (19) - 返回 460，可能需要訂閱
                
                # ========== 其他美食資訊類 ==========
                "https://www.thetakeout.com/feed/",  # 15. The Takeout - 風格幽默，專注於快餐文化、零食評論與現代飲食趨勢
                "https://www.mashed.com/feed/",  # 18. Mashed - 提供餐廳祕辛、名廚動態及食品趣聞的綜合性網站
                "https://www.bbcgoodfood.com/feed",  # BBC Good Food - 英國來源，涵蓋飲食文化、食材指南與全球食譜
                
                # ========== 需要特殊處理的網站 ==========
                # 注意：以下網站可能需要訂閱、特殊權限或使用網頁爬蟲
                # - Food & Wine (7) - 返回 460，可能需要訂閱
                # - Delish (8) - RSS 格式可能有問題
                # - Tastemade (11) - 目前無公開 RSS Feed
                # - Food52 (13) - 返回 429（請求過多），可能需要限制頻率
                # - Civil Eats (16) - 返回 403，可能需要特殊權限
                
                # ========== 亞洲美食網站 ==========
                # 注意：以下網站可能需要使用網頁爬蟲
                # - OpenRice (香港) - 餐廳評論平台
                # - 愛食記 (台灣) - 台灣美食部落格
                # - 食尚玩家 (台灣) - 美食節目與網站
                # - PopDaily 波波發胖 (台灣) - 美食推薦
                # - 愛料理 (台灣) - 食譜分享平台
                
                # ========== 全球新聞來源（補充）==========
                "https://feeds.bbci.co.uk/news/rss.xml",  # BBC News - 全球公認最具中立性與廣度的多語言新聞平台
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",  # The New York Times - 全球數位訂閱量第一，提供權威的深度調查與專題報導
                "https://www.theguardian.com/world/rss",  # The Guardian - 以獨立報導著稱的英國媒體，在全球擁有極高數位讀者量
                "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",  # Google News - 全球最強大的新聞聚合平台，個人化推薦的關鍵入口
                "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera - 從中東視角出發，提供全球特別是南方世界的深度報導
                "https://feeds.washingtonpost.com/rss/world",  # The Washington Post - 專注於美國政治與全球政策的權威媒體
                "https://feeds.a.dj.com/rss/RSSWorldNews.xml",  # Wall Street Journal - 全球商業、財經與政策新聞的首選
                "https://www.ft.com/rss/home/uk",  # Financial Times - 專注於全球市場分析與歐洲經濟趨勢
                "https://www.theatlantic.com/feed/all/",  # The Atlantic - 專注於當代思想、文化與政治深論的長篇報導媒體
                "https://www.scmp.com/rss/91/feed/",  # South China Morning Post - 報導中國與亞洲動態的全球關鍵窗口
            ],
            Category.TREND: [
                # ========== 前瞻科學與社會類 ==========
                "https://www.wired.com/feed/rss",  # 2. WIRED - 專注於科技、科學與商業對未來社會、政治與生活的深遠影響
                "https://www.technologyreview.com/feed/",  # 4. MIT Technology Review - 麻省理工學院主辦，提供最具公信力的技術分析與未來社會預測
                "https://singularityhub.com/feed/",  # 7. Singularity Hub - 探討指數型成長科技（如通用人工智能、生物科技）對人類未來的衝擊
                "https://spectrum.ieee.org/feeds/feed.rss",  # 18. IEEE Spectrum - 全球最大技術專家協會主辦，提供高度專業的工程與趨勢報告
                # 注意：Futureism (8) - 目前無可用 RSS Feed，可能需要使用網頁爬蟲
                # 注意：Neo.Life (17) - SSL 證書問題，可能需要特殊處理
                
                # ========== 商業與新創動態類 ==========
                "https://techcrunch.com/feed/",  # 3. TechCrunch - 全球創業投資與新興科技（尤其是 AI 與機器人）的首選新聞網
                "https://www.fastcompany.com/latest/rss",  # 9. Fast Company - 專注於創新設計、科技與社會進步的交叉點
                "https://thenextweb.com/feed",  # 15. The Next Web (TNW) - 探討科技在歐洲及全球的創新脈動與世代觀點
                
                # ========== 產品與數位生活類 ==========
                "https://www.theverge.com/rss/index.xml",  # 1. The Verge - 全球科技媒體龍頭，深入解析科技如何改變主流文化與社會
                "https://www.cnet.com/rss/all/",  # 11. CNET - 全球流量最大的科技生活導購與新聞平台
                "https://www.digitaltrends.com/feed/",  # 12. Digital Trends - 致力於向大眾解釋科技如何影響人們日常工作與休閒
                "https://www.engadget.com/rss.xml",  # 6. Engadget - 專注於消費性電子產品與其在現代生活中的應用
                
                # ========== 文化與政策分析類 ==========
                "https://www.vox.com/rss/index.xml",  # 16. Vox (Science & Health) - 以「解釋型新聞」聞名，擅長分析科技政策與社會問題的深層連結
                "https://restofworld.org/feed/latest/",  # 10. Rest of World - 報導西方國家以外（如東南亞、非洲）科技如何重塑當地社會的獨特媒體
                "https://arstechnica.com/feed/",  # 5. Ars Technica - 深度的技術評論，涵蓋科技政策、法律與科學趨勢
                
                # ========== 其他科技資訊類 ==========
                "https://mashable.com/feeds/rss/all",  # 13. Mashable - 報導網路文化、社交媒體趨勢與科技娛樂的綜合性平台
                "https://www.zdnet.com/news/rss.xml",  # 14. ZDNET - 專注於 B2B 科技、數位轉型與企業技術趨勢
                # 注意：Gizmodo (19) - 返回 403，可能需要特殊權限
                # 注意：TrendHunter (20) - 返回 403，可能需要特殊權限
                
                # ========== 備用來源 ==========
                "https://feeds.feedburner.com/oreilly/radar",  # O'Reilly Radar - 技術趨勢分析
                
                # ========== 全球新聞來源（補充）==========
                "https://feeds.bbci.co.uk/news/rss.xml",  # BBC News - 全球公認最具中立性與廣度的多語言新聞平台
                "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",  # The New York Times - 全球數位訂閱量第一，提供權威的深度調查與專題報導
                "https://www.theguardian.com/world/rss",  # The Guardian - 以獨立報導著稱的英國媒體，在全球擁有極高數位讀者量
                "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",  # Google News - 全球最強大的新聞聚合平台，個人化推薦的關鍵入口
                "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera - 從中東視角出發，提供全球特別是南方世界的深度報導
                "https://feeds.washingtonpost.com/rss/world",  # The Washington Post - 專注於美國政治與全球政策的權威媒體
                "https://feeds.a.dj.com/rss/RSSWorldNews.xml",  # Wall Street Journal - 全球商業、財經與政策新聞的首選
                "https://www.ft.com/rss/home/uk",  # Financial Times - 專注於全球市場分析與歐洲經濟趨勢
                "https://www.theatlantic.com/feed/all/",  # The Atlantic - 專注於當代思想、文化與政治深論的長篇報導媒體
                "https://www.scmp.com/rss/91/feed/",  # South China Morning Post - 報導中國與亞洲動態的全球關鍵窗口
                "https://www.dailymail.co.uk/news/index.rss",  # Daily Mail - 以極快的更新速度與娛樂新聞吸引全球大量流量
                "https://feeds.nbcnews.com/nbcnews/public/world",  # NBC News - 美國主要廣播公司轉型的數位新聞領導者
                "https://moxie.foxnews.com/google-publisher/world.xml",  # Fox News - 美國最具影響力的保守派視角新聞平台
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
        """從 RSS 收集主題（改進版：提取原文圖片和內容）"""
        topics = []
        feeds = self.rss_feeds.get(category, [])
        
        # 導入文章提取器
        from app.utils.article_extractor import ArticleExtractor
        extractor = ArticleExtractor()
        
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
                            
                            # 提取原文圖片和內容
                            article_info = await extractor.extract_article_info(link)
                            
                            # 構建來源資訊
                            source_info = {
                                "type": "rss",
                                "name": feed.feed.get("title", "RSS Feed"),
                                "url": link,
                                "title": chinese_title,
                                "original_title": title,  # 保留原始英文標題
                                "fetched_at": datetime.utcnow(),
                                "verified": True,
                                "keywords": keywords,
                            }
                            
                            # 添加提取的資訊（如果成功）
                            if article_info.get("success"):
                                source_info["images"] = article_info.get("images", [])
                                source_info["original_content"] = article_info.get("original_content")
                                source_info["language"] = article_info.get("language")
                                
                                # 添加風格資訊（轉換為 dict 以便 MongoDB 儲存）
                                style_info = article_info.get("style")
                                if style_info:
                                    # 直接使用 dict，不需要轉換為 Pydantic 模型
                                    source_info["style"] = style_info if isinstance(style_info, dict) else style_info
                            
                            topic = {
                                "title": chinese_title,
                                "category": category.value,
                                "source": feed.feed.get("title", "RSS Feed"),
                                "description": description,  # 添加30字撮要
                                "sources": [source_info],
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


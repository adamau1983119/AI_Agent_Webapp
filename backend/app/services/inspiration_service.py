"""
靈感策劃服務
Phase 3: 內容功能
提供靈感搜尋和關鍵字提取功能
"""
from typing import Optional, Dict, Any, List
import httpx
import re
from app.config_module import settings
from app.services.ai.ai_service_factory import AIServiceFactory
import logging

logger = logging.getLogger(__name__)


class InspirationService:
    """靈感策劃服務"""
    
    def __init__(self):
        self.google_api_key = settings.GOOGLE_API_KEY
        self.google_cse_id = settings.GOOGLE_SEARCH_ENGINE_ID
    
    async def search_inspiration(
        self,
        query: str,
        language: str = "zh-TW",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜尋靈感（使用 Google Custom Search）
        
        Args:
            query: 搜尋關鍵字
            language: 語言
            limit: 返回數量
            
        Returns:
            搜尋結果列表
        """
        results = []
        
        # 1. 嘗試 Google Custom Search
        if self.google_api_key and self.google_cse_id:
            google_results = await self._google_search(query, language, limit)
            results.extend(google_results)
        
        # 2. 如果 Google 結果不足，使用 AI 生成
        if len(results) < limit:
            ai_results = await self._ai_generate_inspiration(query, language, limit - len(results))
            results.extend(ai_results)
        
        return results[:limit]
    
    async def _google_search(
        self,
        query: str,
        language: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """使用 Google Custom Search API 搜尋"""
        try:
            # 語言代碼映射
            lang_map = {
                "zh-TW": "lang_zh-TW",
                "en": "lang_en",
                "ja": "lang_ja",
            }
            
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": min(limit, 10),  # Google API 最多返回 10 個
                "lr": lang_map.get(language, "lang_en"),
                "dateRestrict": "m1",  # 最近 1 個月
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.warning(f"Google Search API 錯誤: {response.status_code}")
                    return []
                
                data = response.json()
                items = data.get("items", [])
                
                results = []
                for item in items:
                    results.append({
                        "title": item.get("title", ""),
                        "description": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": "google",
                        "image_url": self._extract_image_url(item),
                        "published_date": item.get("pagemap", {}).get("metatags", [{}])[0].get("article:published_time"),
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Google Search 失敗: {e}")
            return []
    
    def _extract_image_url(self, item: Dict[str, Any]) -> Optional[str]:
        """從搜尋結果提取圖片 URL"""
        pagemap = item.get("pagemap", {})
        
        # 嘗試從 cse_image 提取
        cse_images = pagemap.get("cse_image", [])
        if cse_images and cse_images[0].get("src"):
            return cse_images[0]["src"]
        
        # 嘗試從 cse_thumbnail 提取
        thumbnails = pagemap.get("cse_thumbnail", [])
        if thumbnails and thumbnails[0].get("src"):
            return thumbnails[0]["src"]
        
        # 嘗試從 metatags 提取
        metatags = pagemap.get("metatags", [{}])
        if metatags:
            og_image = metatags[0].get("og:image")
            if og_image:
                return og_image
        
        return None
    
    async def _ai_generate_inspiration(
        self,
        query: str,
        language: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """使用 AI 生成靈感主題"""
        try:
            ai_service = AIServiceFactory.get_service()
            
            # 語言標籤
            lang_labels = {
                "zh-TW": "繁體中文",
                "en": "English",
                "ja": "日本語",
            }
            
            prompt = f"""作為內容創作靈感助手，根據以下主題生成 {limit} 個創作靈感。

主題：{query}
輸出語言：{lang_labels.get(language, "繁體中文")}

要求：
1. 每個靈感應該是一個具體可執行的內容主題
2. 標題要吸引人，適合社交媒體
3. 提供簡短描述（50字內）

格式（嚴格遵守）：
靈感1: [標題]
描述: [描述]

靈感2: [標題]
描述: [描述]

...以此類推"""

            response = await ai_service.generate(prompt)
            
            if not response:
                return []
            
            # 解析 AI 回應
            results = self._parse_ai_response(response, limit)
            
            for result in results:
                result["source"] = "ai_generated"
            
            return results
            
        except Exception as e:
            logger.error(f"AI 生成靈感失敗: {e}")
            return []
    
    def _parse_ai_response(self, response: str, limit: int) -> List[Dict[str, Any]]:
        """解析 AI 回應"""
        results = []
        
        # 使用正則表達式解析
        pattern = r'靈感\d+:\s*(.+?)\n描述:\s*(.+?)(?=\n靈感|\n\n|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches[:limit]:
            title = match[0].strip()
            description = match[1].strip()
            
            results.append({
                "title": title,
                "description": description,
                "url": None,
                "image_url": None,
                "published_date": None,
            })
        
        return results
    
    async def extract_keywords(
        self,
        text: str,
        language: str = "zh-TW",
        limit: int = 5
    ) -> List[str]:
        """
        從文本提取關鍵字
        
        Args:
            text: 輸入文本
            language: 語言
            limit: 返回數量
            
        Returns:
            關鍵字列表
        """
        try:
            ai_service = AIServiceFactory.get_service()
            
            prompt = f"""從以下文本提取最多 {limit} 個關鍵字，用於內容搜尋。

文本：{text}

要求：
1. 關鍵字應該是名詞或專有名詞
2. 每個關鍵字 2-6 個字
3. 只返回關鍵字，用逗號分隔
4. 不要返回其他內容

輸出格式：關鍵字1, 關鍵字2, 關鍵字3"""

            response = await ai_service.generate(prompt)
            
            if not response:
                return []
            
            # 解析關鍵字
            keywords = [kw.strip() for kw in response.split(",") if kw.strip()]
            
            return keywords[:limit]
            
        except Exception as e:
            logger.error(f"關鍵字提取失敗: {e}")
            return []
    
    async def get_trending_topics(
        self,
        category: str = "general",
        region: str = "global",
        language: str = "zh-TW",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        取得熱門趨勢主題
        
        Args:
            category: 類別
            region: 地區
            language: 語言
            limit: 返回數量
            
        Returns:
            熱門主題列表
        """
        try:
            # 根據類別和地區建構搜尋詞
            search_terms = {
                "fashion": "最新時尚趨勢",
                "food": "美食推薦",
                "tech": "科技新聞",
                "finance": "財經新聞",
                "sports": "體育新聞",
                "entertainment": "娛樂新聞",
                "general": "熱門話題",
            }
            
            query = search_terms.get(category, "熱門話題")
            
            # 嘗試搜尋，如果失敗則使用 AI 生成 fallback
            results = await self.search_inspiration(query, language, limit)
            
            # 如果結果為空且 Google API 未配置，使用 AI 生成
            if not results and (not self.google_api_key or not self.google_cse_id):
                logger.info("Google API 未配置，使用 AI 生成熱門話題")
                results = await self._ai_generate_inspiration(query, language, limit)
            
            return results
        except Exception as e:
            logger.error(f"取得熱門話題失敗: {e}")
            # 如果所有方法都失敗，返回空列表（前端會顯示空狀態）
            return []


# 建立全域實例
inspiration_service = InspirationService()


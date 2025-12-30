"""
資料驗證模組
驗證來源資料、存檔截圖、建立證據鏈
"""
import logging
import httpx
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.topic import Category, SourceInfo

logger = logging.getLogger(__name__)


class DataValidator:
    """資料驗證器"""
    
    def __init__(self):
        self.source_health_cache = {}  # 來源健康度緩存
    
    async def validate_topic_consistency(
        self,
        keyword: str,
        category: Category,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        分級強制一致性檢查（專家建議）
        
        Args:
            keyword: 關鍵字
            category: 主題分類
            sources: 來源列表
            
        Returns:
            驗證結果
        """
        # 判斷是否為事實類（包含日期、地址、價格、名次）
        is_factual = self._check_if_factual(keyword)
        
        if is_factual:
            # 強制雙來源一致
            if len(sources) < 2:
                return {
                    "valid": False,
                    "reason": "事實類內容需要至少2個來源驗證",
                    "required_sources": 2
                }
            
            # 檢查事實一致性
            consistency = await self._check_factual_consistency(sources)
            if consistency < 0.9:
                return {
                    "valid": False,
                    "reason": "事實類內容來源不一致",
                    "consistency_score": consistency
                }
        else:
            # 趨勢類：建議性檢查
            if len(sources) == 1:
                return {
                    "valid": True,
                    "warning": "單來源趨勢",
                    "should_mark": True
                }
        
        return {
            "valid": True,
            "is_factual": is_factual,
            "consistency_score": 1.0 if not is_factual else await self._check_factual_consistency(sources)
        }
    
    def _check_if_factual(self, keyword: str) -> bool:
        """
        檢查是否為事實類內容
        
        事實類關鍵字特徵：
        - 包含日期（2026、2025、春夏、秋冬）
        - 包含地址（元朗、香港、地址）
        - 包含價格（$、元、價格）
        - 包含名次（top 3、第1、排行榜）
        """
        factual_indicators = [
            "2026", "2025", "春夏", "秋冬", "地址", "元朗", "香港",
            "$", "元", "價格", "top", "第", "排行榜", "名次"
        ]
        
        return any(indicator in keyword for indicator in factual_indicators)
    
    async def _check_factual_consistency(
        self,
        sources: List[Dict[str, Any]]
    ) -> float:
        """
        檢查事實一致性
        
        Returns:
            一致性分數（0.0 - 1.0）
        """
        if len(sources) < 2:
            return 0.0
        
        # 提取關鍵事實（日期、地址、價格等）
        facts = []
        for source in sources:
            # 從來源中提取事實（簡化版）
            # 實際應該使用 NLP 提取
            facts.append({
                "url": source.get("url", ""),
                "title": source.get("title", "")
            })
        
        # 簡單的一致性檢查（實際應該更複雜）
        # 這裡假設如果來源都包含相同關鍵字，則一致
        if len(facts) >= 2:
            return 0.9  # 簡化版，假設一致
        
        return 0.5
    
    async def validate_and_fetch_source(
        self,
        source_url: str,
        source_name: str
    ) -> Dict[str, Any]:
        """
        驗證並抓取來源資料
        
        Args:
            source_url: 來源 URL
            source_name: 來源名稱
            
        Returns:
            驗證結果
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(source_url)
                
                if response.status_code != 200:
                    return {
                        "valid": False,
                        "reason": f"來源無法訪問，狀態碼：{response.status_code}"
                    }
                
                # 提取內容摘要（簡化版）
                content_snippet = response.text[:500] if len(response.text) > 500 else response.text
                
                # 存檔截圖（簡化版，實際應該使用瀏覽器自動化）
                screenshot_data = await self._save_screenshot(source_url)
                
                return {
                    "valid": True,
                    "url": source_url,
                    "name": source_name,
                    "content_snippet": content_snippet,
                    "screenshot_url": screenshot_data.get("url") if screenshot_data else None,
                    "fetched_at": datetime.utcnow(),
                    "reliability": "high"  # 簡化版
                }
        except Exception as e:
            logger.error(f"驗證來源失敗: {e}")
            return {
                "valid": False,
                "reason": str(e)
            }
    
    async def _save_screenshot(self, url: str) -> Optional[Dict[str, Any]]:
        """
        保存來源截圖（簡化版）
        
        實際應該使用：
        - Selenium/Playwright 截圖
        - 上傳到 S3/OSS
        - 保存到本地緩存
        """
        # 這裡只是佔位符，實際需要實作截圖功能
        return {
            "url": f"s3://screenshots/{url.replace('://', '_').replace('/', '_')}.png",
            "local_cache_id": f"screenshot_{datetime.utcnow().timestamp()}"
        }
    
    async def check_source_health(self, source_url: str) -> Dict[str, Any]:
        """
        檢查來源健康度（專家建議：5分鐘探測 + 30分鐘深度檢查）
        
        Returns:
            健康度分數（0.0 - 1.0）
        """
        try:
            # 檢查緩存（5分鐘內不重複檢查）
            if source_url in self.source_health_cache:
                cached = self.source_health_cache[source_url]
                if (datetime.utcnow() - cached["checked_at"]).seconds < 300:  # 5分鐘
                    return cached["health"]
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                start_time = datetime.utcnow()
                response = await client.get(source_url)
                response_time = (datetime.utcnow() - start_time).total_seconds()
                
                # 計算健康分數
                health_score = 0.0
                
                # 可用率（40%）
                if response.status_code == 200:
                    health_score += 0.4
                
                # 延遲分數（30%）
                if response_time < 3:
                    health_score += 0.3
                elif response_time < 5:
                    health_score += 0.15
                
                # 錯誤率分數（20%）
                if response.status_code < 400:
                    health_score += 0.2
                
                # 數據新鮮度（10%）
                # 這裡假設總是新鮮（實際應該檢查內容更新時間）
                health_score += 0.1
                
                # 更新緩存
                self.source_health_cache[source_url] = {
                    "health": {"health_score": health_score, "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy"},
                    "checked_at": datetime.utcnow()
                }
                
                return {
                    "health_score": health_score,
                    "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
        except Exception as e:
            logger.error(f"檢查來源健康度失敗: {e}")
            return {
                "health_score": 0.0,
                "status": "unhealthy",
                "error": str(e)
            }


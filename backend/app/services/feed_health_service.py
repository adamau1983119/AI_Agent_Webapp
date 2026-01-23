"""
Feed 健康監控服務
提供 Feed 健康狀態的業務邏輯層
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.config.feed_roles import get_all_feeds_for_category, CATEGORY_ROLES
from app.models.topic import Category

logger = logging.getLogger(__name__)


class FeedHealthService:
    """Feed 健康監控服務"""
    
    def __init__(self, repository: Optional[FeedHealthRepository] = None):
        """
        初始化服務
        
        Args:
            repository: FeedHealthRepository 實例（可選，如果不提供則創建新實例）
        """
        self.repository = repository or FeedHealthRepository()
    
    async def record_fetch_result(
        self,
        feed_url: str,
        source_name: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        記錄 Feed 抓取結果
        
        Args:
            feed_url: Feed URL
            source_name: 來源名稱
            success: 是否成功
            error: 錯誤訊息（失敗時）
        """
        if success:
            await self.repository.record_success(feed_url, source_name)
        else:
            await self.repository.record_failure(feed_url, error or "Unknown error", source_name)
    
    async def should_skip_feed(self, feed_url: str) -> bool:
        """
        檢查是否應該跳過此 Feed（基於健康狀態）
        
        Args:
            feed_url: Feed URL
            
        Returns:
            True 如果應該跳過
        """
        return await self.repository.is_paused(feed_url)
    
    def calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """
        計算健康分數 (0-100)
        
        Args:
            metrics: 包含 reliability_score, failure_count 等的指標
            
        Returns:
            健康分數
        """
        reliability = metrics.get("reliability_score", 1.0)
        is_paused = metrics.get("is_paused", False)
        
        if is_paused:
            return 0
        
        # 將可靠度轉換為 0-100 分數
        score = int(reliability * 100)
        
        return max(0, min(100, score))
    
    def get_health_status(self, score: int) -> str:
        """
        根據分數返回健康狀態
        
        Args:
            score: 健康分數 (0-100)
            
        Returns:
            健康狀態字串
        """
        if score == 0:
            return "paused"
        elif score >= 90:
            return "healthy"
        elif score >= 70:
            return "degraded"
        elif score >= 50:
            return "warning"
        else:
            return "unhealthy"
    
    async def get_feed_health(self, feed_url: str) -> Dict[str, Any]:
        """
        獲取單一 Feed 的健康狀態
        
        Args:
            feed_url: Feed URL
            
        Returns:
            健康狀態詳情
        """
        is_paused = await self.repository.is_paused(feed_url)
        reliability = await self.repository.get_reliability_score(feed_url)
        recent_records = await self.repository.get_health_report(feed_url, limit=5)
        
        health_score = self.calculate_health_score({
            "reliability_score": reliability,
            "is_paused": is_paused
        })
        
        return {
            "feed_url": feed_url,
            "health_score": health_score,
            "health_status": self.get_health_status(health_score),
            "reliability_score": reliability,
            "is_paused": is_paused,
            "recent_records": recent_records,
            "checked_at": datetime.utcnow()
        }
    
    async def get_category_health(self, category: Category) -> Dict[str, Any]:
        """
        獲取分類下所有 Feed 的健康狀態
        
        Args:
            category: 分類
            
        Returns:
            分類健康狀態報告
        """
        feeds = get_all_feeds_for_category(category)
        feed_health_list = []
        
        for source_name, feed_url, weight in feeds:
            health = await self.get_feed_health(feed_url)
            health["source_name"] = source_name
            health["weight"] = weight
            feed_health_list.append(health)
        
        # 計算分類整體健康狀態
        total_feeds = len(feed_health_list)
        healthy_count = sum(1 for h in feed_health_list if h["health_status"] == "healthy")
        paused_count = sum(1 for h in feed_health_list if h["is_paused"])
        avg_score = sum(h["health_score"] for h in feed_health_list) / total_feeds if total_feeds > 0 else 100
        
        return {
            "category": category.value,
            "total_feeds": total_feeds,
            "healthy_feeds": healthy_count,
            "paused_feeds": paused_count,
            "average_health_score": round(avg_score, 2),
            "overall_status": self.get_health_status(int(avg_score)),
            "feeds": feed_health_list,
            "generated_at": datetime.utcnow()
        }
    
    async def get_all_categories_health(self) -> Dict[str, Any]:
        """
        獲取所有分類的健康狀態
        
        Returns:
            所有分類健康狀態報告
        """
        categories_health = {}
        
        for category in [Category.FASHION, Category.FOOD, Category.TREND]:
            categories_health[category.value] = await self.get_category_health(category)
        
        # 計算整體統計
        total_feeds = sum(c["total_feeds"] for c in categories_health.values())
        healthy_feeds = sum(c["healthy_feeds"] for c in categories_health.values())
        paused_feeds = sum(c["paused_feeds"] for c in categories_health.values())
        
        return {
            "summary": {
                "total_feeds": total_feeds,
                "healthy_feeds": healthy_feeds,
                "paused_feeds": paused_feeds,
                "overall_health_rate": round(healthy_feeds / total_feeds, 4) if total_feeds > 0 else 1.0
            },
            "categories": categories_health,
            "generated_at": datetime.utcnow()
        }
    
    async def get_stats_summary(self) -> Dict[str, Any]:
        """
        獲取統計摘要
        
        Returns:
            統計摘要
        """
        return await self.repository.get_stats_summary()
    
    async def get_problematic_feeds(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        獲取有問題的 Feed 列表（可靠度低於閾值）
        
        Args:
            threshold: 可靠度閾值
            
        Returns:
            問題 Feed 列表
        """
        all_health = await self.repository.get_all_feed_health()
        
        problematic = [
            h for h in all_health
            if h.get("reliability_score", 1.0) < threshold or h.get("is_paused", False)
        ]
        
        return sorted(problematic, key=lambda x: x.get("reliability_score", 0))


# 創建全域實例
feed_health_service = FeedHealthService()


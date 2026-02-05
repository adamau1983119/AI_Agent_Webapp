"""
Feed 健康監控服務 v4.0
提供 Feed 健康狀態的業務邏輯層

Phase 1 新增功能：
- Level 1-4 分級健康監控
- 白名單/黑名單/灰名單機制
- 動態角色分配
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.config.feed_roles import get_all_feeds_for_category, CATEGORY_ROLES
from app.config.topic_config import get_topic_config
from app.models.topic import Category

logger = logging.getLogger(__name__)


class HealthLevel(Enum):
    """健康等級"""
    HEALTHY = 0       # 健康
    LEVEL_1 = 1       # 臨時暫停（1小時內連續失敗3次）
    LEVEL_2 = 2       # 短期暫停（24小時內失敗率>30%）
    LEVEL_3 = 3       # 待替換（7天內失敗率>50%）
    LEVEL_4 = 4       # 永久停用


class SourceListType(Enum):
    """來源名單類型"""
    WHITELIST = "whitelist"    # 白名單：高優先級
    BLACKLIST = "blacklist"    # 黑名單：禁用
    GREYLIST = "greylist"      # 灰名單：觀察中
    NORMAL = "normal"          # 正常來源


class FeedHealthService:
    """Feed 健康監控服務 v4.0 - 支援分級監控"""
    
    def __init__(self, repository: Optional[FeedHealthRepository] = None):
        """
        初始化服務
        
        Args:
            repository: FeedHealthRepository 實例（可選，如果不提供則創建新實例）
        """
        self.repository = repository or FeedHealthRepository()
        self.config = get_topic_config()
        
        # 載入來源名單
        self._whitelist: List[str] = []
        self._blacklist: List[str] = []
        self._greylist: List[str] = []
        self._load_source_lists()
    
    def _load_source_lists(self):
        """載入來源名單"""
        try:
            lists_config = self.config.get_rss_source_lists_config()
            
            # 載入黑名單
            blacklist_config = lists_config.get("blacklist", {})
            if blacklist_config.get("enabled", True):
                self._blacklist = blacklist_config.get("sources", [])
            
            logger.info(f"來源名單載入完成: 白名單={len(self._whitelist)}, 黑名單={len(self._blacklist)}, 灰名單={len(self._greylist)}")
        except Exception as e:
            logger.warning(f"載入來源名單失敗: {e}")
    
    # ============================================
    # Phase 1: 來源名單管理
    # ============================================
    
    def get_source_list_type(self, feed_url: str) -> SourceListType:
        """
        取得來源的名單類型
        
        Args:
            feed_url: Feed URL
            
        Returns:
            來源名單類型
        """
        if feed_url in self._blacklist:
            return SourceListType.BLACKLIST
        if feed_url in self._whitelist:
            return SourceListType.WHITELIST
        if feed_url in self._greylist:
            return SourceListType.GREYLIST
        return SourceListType.NORMAL
    
    def add_to_whitelist(self, feed_url: str) -> bool:
        """加入白名單"""
        if feed_url not in self._whitelist:
            self._whitelist.append(feed_url)
            # 從其他名單移除
            if feed_url in self._blacklist:
                self._blacklist.remove(feed_url)
            if feed_url in self._greylist:
                self._greylist.remove(feed_url)
            logger.info(f"已將 {feed_url} 加入白名單")
            return True
        return False
    
    def add_to_blacklist(self, feed_url: str) -> bool:
        """加入黑名單"""
        if feed_url not in self._blacklist:
            self._blacklist.append(feed_url)
            # 從其他名單移除
            if feed_url in self._whitelist:
                self._whitelist.remove(feed_url)
            if feed_url in self._greylist:
                self._greylist.remove(feed_url)
            logger.info(f"已將 {feed_url} 加入黑名單")
            return True
        return False
    
    def add_to_greylist(self, feed_url: str) -> bool:
        """加入灰名單"""
        if feed_url not in self._greylist:
            self._greylist.append(feed_url)
            # 從白名單移除（黑名單優先）
            if feed_url in self._whitelist:
                self._whitelist.remove(feed_url)
            logger.info(f"已將 {feed_url} 加入灰名單")
            return True
        return False
    
    def remove_from_lists(self, feed_url: str) -> bool:
        """從所有名單中移除"""
        removed = False
        if feed_url in self._whitelist:
            self._whitelist.remove(feed_url)
            removed = True
        if feed_url in self._blacklist:
            self._blacklist.remove(feed_url)
            removed = True
        if feed_url in self._greylist:
            self._greylist.remove(feed_url)
            removed = True
        return removed
    
    # ============================================
    # Phase 1: 分級健康監控 (Level 1-4)
    # ============================================
    
    async def get_health_level(self, feed_url: str) -> HealthLevel:
        """
        取得 Feed 的健康等級
        
        Args:
            feed_url: Feed URL
            
        Returns:
            健康等級 (Level 0-4)
        """
        # 黑名單直接返回 Level 4
        if self.get_source_list_type(feed_url) == SourceListType.BLACKLIST:
            return HealthLevel.LEVEL_4
        
        # 白名單有豁免權，但仍需檢查 Level 1-2
        is_whitelisted = self.get_source_list_type(feed_url) == SourceListType.WHITELIST
        whitelist_config = self.config.get_whitelist_config()
        immune_levels = whitelist_config.get("immune_to_levels", [3, 4])
        
        # 檢查 Level 4（14天失敗率>70%）
        if not is_whitelisted or 4 not in immune_levels:
            level_4_config = self.config.get_health_level_config(4)
            threshold = level_4_config.get("failure_rate_threshold", 0.70)
            days = level_4_config.get("time_window_days", 14)
            failure_rate = await self._get_failure_rate(feed_url, days=days)
            if failure_rate >= threshold:
                return HealthLevel.LEVEL_4
        
        # 檢查 Level 3（7天失敗率>50%）
        if not is_whitelisted or 3 not in immune_levels:
            level_3_config = self.config.get_health_level_config(3)
            threshold = level_3_config.get("failure_rate_threshold", 0.50)
            days = level_3_config.get("time_window_days", 7)
            failure_rate = await self._get_failure_rate(feed_url, days=days)
            if failure_rate >= threshold:
                return HealthLevel.LEVEL_3
        
        # 檢查 Level 2（24小時失敗率>30%）
        level_2_config = self.config.get_health_level_config(2)
        threshold = level_2_config.get("failure_rate_threshold", 0.30)
        hours = level_2_config.get("time_window_hours", 24)
        failure_rate = await self._get_failure_rate(feed_url, hours=hours)
        if failure_rate >= threshold:
            return HealthLevel.LEVEL_2
        
        # 檢查 Level 1（1小時內連續失敗3次）
        level_1_config = self.config.get_health_level_config(1)
        failure_count = level_1_config.get("failure_count", 3)
        hours = level_1_config.get("time_window_hours", 1)
        consecutive_failures = await self._get_consecutive_failures(feed_url, hours=hours)
        if consecutive_failures >= failure_count:
            return HealthLevel.LEVEL_1
        
        return HealthLevel.HEALTHY
    
    async def _get_failure_rate(
        self,
        feed_url: str,
        hours: Optional[int] = None,
        days: Optional[int] = None
    ) -> float:
        """計算時間範圍內的失敗率"""
        try:
            if days:
                since = datetime.utcnow() - timedelta(days=days)
            elif hours:
                since = datetime.utcnow() - timedelta(hours=hours)
            else:
                since = datetime.utcnow() - timedelta(hours=24)
            
            # 從 repository 取得統計
            stats = await self.repository.get_feed_stats(feed_url, since=since)
            total = stats.get("total", 0)
            failures = stats.get("failures", 0)
            
            if total == 0:
                return 0.0
            
            return failures / total
        except Exception as e:
            logger.warning(f"計算失敗率失敗 ({feed_url}): {e}")
            return 0.0
    
    async def _get_consecutive_failures(self, feed_url: str, hours: int = 1) -> int:
        """計算連續失敗次數"""
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            return await self.repository.get_consecutive_failures(feed_url, since=since)
        except Exception as e:
            logger.warning(f"計算連續失敗次數失敗 ({feed_url}): {e}")
            return 0
    
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
            
            # Phase 1: 檢查是否需要加入灰名單
            health_level = await self.get_health_level(feed_url)
            if health_level == HealthLevel.LEVEL_3:
                self.add_to_greylist(feed_url)
                logger.warning(f"Feed {feed_url} 達到 Level 3，已加入灰名單")
    
    async def should_skip_feed(self, feed_url: str) -> bool:
        """
        檢查是否應該跳過此 Feed（基於健康狀態）
        
        Args:
            feed_url: Feed URL
            
        Returns:
            True 如果應該跳過
        """
        # 黑名單永遠跳過
        if self.get_source_list_type(feed_url) == SourceListType.BLACKLIST:
            return True
        
        # 檢查健康等級
        health_level = await self.get_health_level(feed_url)
        
        # Level 1-4 都需要暫停
        if health_level.value >= 1:
            return True
        
        return False
    
    def get_feed_weight(self, feed_url: str, base_weight: float = 1.0) -> float:
        """
        取得 Feed 的權重（灰名單會降低權重）
        
        Args:
            feed_url: Feed URL
            base_weight: 基礎權重
            
        Returns:
            調整後的權重
        """
        list_type = self.get_source_list_type(feed_url)
        
        if list_type == SourceListType.BLACKLIST:
            return 0.0
        
        if list_type == SourceListType.WHITELIST:
            return base_weight * 1.2  # 白名單提高 20%
        
        if list_type == SourceListType.GREYLIST:
            greylist_config = self.config.get_greylist_config()
            reduction = greylist_config.get("weight_reduction", 0.5)
            return base_weight * reduction
        
        return base_weight
    
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


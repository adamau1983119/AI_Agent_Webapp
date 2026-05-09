"""
Feed 健康監控服務 v4.0
提供 Feed 健康狀態的業務邏輯層

Phase 1 完成功能：
- Level 1-4 分級健康監控（含自動恢復機制）
- 白名單/黑名單/灰名單機制（DB 持久化）
- 動態角色分配（根據健康度調整）
- 多樣性門檻各分類不同
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.services.repositories.feed_health_repository import FeedHealthRepository
from app.services.repositories.source_list_repository import SourceListRepository
from app.config.feed_roles import get_all_feeds_for_category, CATEGORY_ROLES, get_roles_for_category, get_role_distribution
from app.config.topic_config import get_topic_config
from app.models.topic import Category

logger = logging.getLogger(__name__)


class HealthLevel(Enum):
    """健康等級"""
    HEALTHY = 0       # 健康
    LEVEL_1 = 1       # 臨時暫停（1小時內連續失敗3次）→ 暫停 1 小時
    LEVEL_2 = 2       # 短期暫停（24小時內失敗≥5次或失敗率>30%）→ 暫停 24 小時
    LEVEL_3 = 3       # 待替換（7天內失敗率>50%）→ 標記灰名單
    LEVEL_4 = 4       # 永久停用（30天無成功）→ 自動停用


class SourceListType(Enum):
    """來源名單類型"""
    WHITELIST = "whitelist"    # 白名單：高優先級
    BLACKLIST = "blacklist"    # 黑名單：禁用
    GREYLIST = "greylist"      # 灰名單：觀察中
    NORMAL = "normal"          # 正常來源


class FeedHealthService:
    """Feed 健康監控服務 v4.0 - 支援分級監控 + DB 持久化"""
    
    def __init__(
        self,
        repository: Optional[FeedHealthRepository] = None,
        source_list_repo: Optional[SourceListRepository] = None
    ):
        """
        初始化服務
        
        Args:
            repository: FeedHealthRepository 實例
            source_list_repo: SourceListRepository 實例（DB 持久化）
        """
        self.repository = repository or FeedHealthRepository()
        self.source_list_repo = source_list_repo or SourceListRepository()
        self.config = get_topic_config()
        
        # 記憶體快取（減少 DB 查詢）
        self._whitelist_cache: List[str] = []
        self._blacklist_cache: List[str] = []
        self._greylist_cache: List[str] = []
        self._cache_loaded = False
    
    async def _ensure_cache(self):
        """確保快取已載入"""
        if not self._cache_loaded:
            await self._load_source_lists()
    
    async def _load_source_lists(self):
        """從 DB 載入來源名單到快取"""
        try:
            self._whitelist_cache = await self.source_list_repo.get_whitelist_urls()
            self._blacklist_cache = await self.source_list_repo.get_blacklist_urls()
            self._greylist_cache = await self.source_list_repo.get_greylist_urls()
            self._cache_loaded = True
            
            logger.info(
                f"來源名單載入完成: 白名單={len(self._whitelist_cache)}, "
                f"黑名單={len(self._blacklist_cache)}, 灰名單={len(self._greylist_cache)}"
            )
        except Exception as e:
            logger.warning(f"載入來源名單失敗（使用空快取）: {e}")
            self._cache_loaded = True  # 避免重複嘗試
    
    def _invalidate_cache(self):
        """清除快取（在名單變更後）"""
        self._cache_loaded = False
    
    # ============================================
    # Phase 1: 來源名單管理（DB 持久化）
    # ============================================
    
    async def get_source_list_type(self, feed_url: str) -> SourceListType:
        """
        取得來源的名單類型
        
        Args:
            feed_url: Feed URL
            
        Returns:
            來源名單類型
        """
        await self._ensure_cache()
        
        if feed_url in self._blacklist_cache:
            return SourceListType.BLACKLIST
        if feed_url in self._whitelist_cache:
            return SourceListType.WHITELIST
        if feed_url in self._greylist_cache:
            return SourceListType.GREYLIST
        return SourceListType.NORMAL
    
    async def add_to_whitelist(self, feed_url: str, reason: str = "") -> bool:
        """加入白名單（持久化到 DB）"""
        success = await self.source_list_repo.add_to_whitelist(feed_url, reason)
        if success:
            self._invalidate_cache()
        return success
    
    async def add_to_blacklist(self, feed_url: str, reason: str = "") -> bool:
        """加入黑名單（持久化到 DB）"""
        success = await self.source_list_repo.add_to_blacklist(feed_url, reason)
        if success:
            self._invalidate_cache()
        return success
    
    async def add_to_greylist(self, feed_url: str, reason: str = "") -> bool:
        """加入灰名單（持久化到 DB）"""
        success = await self.source_list_repo.add_to_greylist(feed_url, reason)
        if success:
            self._invalidate_cache()
        return success
    
    async def remove_from_lists(self, feed_url: str) -> bool:
        """從所有名單中移除（持久化到 DB）"""
        success = await self.source_list_repo.remove_from_list(feed_url)
        if success:
            self._invalidate_cache()
        return success
    
    async def get_whitelist(self) -> List[Dict[str, Any]]:
        """取得白名單詳情"""
        return await self.source_list_repo.get_whitelist()
    
    async def get_blacklist(self) -> List[Dict[str, Any]]:
        """取得黑名單詳情"""
        return await self.source_list_repo.get_blacklist()
    
    async def get_greylist(self) -> List[Dict[str, Any]]:
        """取得灰名單詳情"""
        return await self.source_list_repo.get_greylist()
    
    async def get_all_lists(self) -> Dict[str, Any]:
        """取得所有名單"""
        return await self.source_list_repo.get_all_lists()
    
    # ============================================
    # Phase 1: 分級健康監控 (Level 1-4) + 自動恢復
    # ============================================
    
    async def get_health_level(self, feed_url: str) -> HealthLevel:
        """
        取得 Feed 的健康等級
        
        Level 1: 1 小時內連續失敗 3 次 → 暫停 1 小時
        Level 2: 24 小時內失敗 ≥5 次或失敗率 >30% → 暫停 24 小時
        Level 3: 7 天內失敗率 >50% → 標記待替換
        Level 4: 30 天無成功 → 自動停用
        
        Args:
            feed_url: Feed URL
            
        Returns:
            健康等級 (Level 0-4)
        """
        # 黑名單直接返回 Level 4
        list_type = await self.get_source_list_type(feed_url)
        if list_type == SourceListType.BLACKLIST:
            return HealthLevel.LEVEL_4
        
        # 白名單有豁免權，但仍需檢查 Level 1-2
        is_whitelisted = list_type == SourceListType.WHITELIST
        whitelist_config = self.config.get_whitelist_config()
        immune_levels = whitelist_config.get("immune_to_levels", [3, 4])
        
        # 檢查 Level 4（30 天無成功 → 自動停用）
        if not is_whitelisted or 4 not in immune_levels:
            has_success_30d = await self._has_success_in_period(feed_url, days=30)
            # 只有在有記錄但沒有成功的情況下才標記 Level 4
            stats_30d = await self._get_failure_rate(feed_url, days=30)
            has_records = await self._has_records_in_period(feed_url, days=30)
            if has_records and not has_success_30d:
                return HealthLevel.LEVEL_4
        
        # 檢查 Level 3（7天失敗率>50%）
        if not is_whitelisted or 3 not in immune_levels:
            level_3_config = self.config.get_health_level_config(3)
            threshold = level_3_config.get("failure_rate_threshold", 0.50)
            days = level_3_config.get("time_window_days", 7)
            failure_rate = await self._get_failure_rate(feed_url, days=days)
            if failure_rate >= threshold:
                return HealthLevel.LEVEL_3
        
        # 檢查 Level 2（24小時內失敗≥5次或失敗率>30%）
        level_2_config = self.config.get_health_level_config(2)
        threshold = level_2_config.get("failure_rate_threshold", 0.30)
        hours = level_2_config.get("time_window_hours", 24)
        failure_rate = await self._get_failure_rate(feed_url, hours=hours)
        
        # 額外檢查：24 小時內失敗次數 ≥5
        stats_24h = await self.repository.get_feed_stats(
            feed_url, since=datetime.utcnow() - timedelta(hours=hours)
        )
        failure_count_24h = stats_24h.get("failures", 0)
        
        if failure_rate >= threshold or failure_count_24h >= 5:
            return HealthLevel.LEVEL_2
        
        # 檢查 Level 1（1小時內連續失敗3次）
        level_1_config = self.config.get_health_level_config(1)
        failure_count = level_1_config.get("failure_count", 3)
        hours_l1 = level_1_config.get("time_window_hours", 1)
        consecutive_failures = await self._get_consecutive_failures(feed_url, hours=hours_l1)
        if consecutive_failures >= failure_count:
            return HealthLevel.LEVEL_1
        
        return HealthLevel.HEALTHY
    
    async def _has_success_in_period(self, feed_url: str, days: int) -> bool:
        """檢查指定時間範圍內是否有成功記錄"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            stats = await self.repository.get_feed_stats(feed_url, since=since)
            return stats.get("successes", 0) > 0
        except Exception as e:
            logger.warning(f"檢查成功記錄失敗 ({feed_url}): {e}")
            return True  # 出錯時假設有成功
    
    async def _has_records_in_period(self, feed_url: str, days: int) -> bool:
        """檢查指定時間範圍內是否有任何記錄"""
        try:
            since = datetime.utcnow() - timedelta(days=days)
            stats = await self.repository.get_feed_stats(feed_url, since=since)
            return stats.get("total", 0) > 0
        except Exception as e:
            logger.warning(f"檢查記錄失敗 ({feed_url}): {e}")
            return False
    
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
    
    async def should_skip_feed(self, feed_url: str) -> bool:
        """
        檢查是否應該跳過此 Feed（基於健康狀態 + 暫停恢復機制）
        
        Level 1: 暫停 1 小時後自動恢復
        Level 2: 暫停 24 小時後自動恢復（需連續6小時無失敗）
        Level 3+: 需人工處理
        
        Args:
            feed_url: Feed URL
            
        Returns:
            True 如果應該跳過
        """
        # 黑名單永遠跳過
        list_type = await self.get_source_list_type(feed_url)
        if list_type == SourceListType.BLACKLIST:
            return True

        # Repository 暫停旗標（連敗等機制標記為暫停時直接跳過抓取）
        if await self.repository.is_paused(feed_url):
            return True

        health_level = await self.get_health_level(feed_url)
        
        if health_level == HealthLevel.HEALTHY:
            return False
        
        # Level 1: 檢查暫停 1 小時是否已過
        if health_level == HealthLevel.LEVEL_1:
            level_1_config = self.config.get_health_level_config(1)
            pause_hours = level_1_config.get("pause_duration_hours", 1)
            auto_recover = level_1_config.get("auto_recover", True)
            
            if auto_recover:
                # 檢查最後一次失敗是否超過 pause_hours 小時
                since = datetime.utcnow() - timedelta(hours=pause_hours)
                recent_failures = await self._get_consecutive_failures(feed_url, hours=pause_hours)
                if recent_failures == 0:
                    # 暫停期間已過且無新失敗 → 自動恢復
                    return False
            
            return True
        
        # Level 2: 檢查暫停 24 小時是否已過
        if health_level == HealthLevel.LEVEL_2:
            level_2_config = self.config.get_health_level_config(2)
            pause_hours = level_2_config.get("pause_duration_hours", 6)
            auto_recover = level_2_config.get("auto_recover", True)
            
            if auto_recover:
                since = datetime.utcnow() - timedelta(hours=pause_hours)
                recent_failures = await self._get_consecutive_failures(feed_url, hours=pause_hours)
                if recent_failures == 0:
                    return False
            
            return True
        
        # Level 3-4 需要人工處理
        return True
    
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
                await self.add_to_greylist(feed_url, reason="Level 3: 7天失敗率>50%")
                logger.warning(f"Feed {feed_url} 達到 Level 3，已加入灰名單")
    
    def get_feed_weight(self, feed_url: str, base_weight: float = 1.0) -> float:
        """
        取得 Feed 的權重（同步方法，使用快取）
        
        Args:
            feed_url: Feed URL
            base_weight: 基礎權重
            
        Returns:
            調整後的權重
        """
        if feed_url in self._blacklist_cache:
            return 0.0
        
        if feed_url in self._whitelist_cache:
            return base_weight * 1.2  # 白名單提高 20%
        
        if feed_url in self._greylist_cache:
            greylist_config = self.config.get_greylist_config()
            reduction = greylist_config.get("weight_reduction", 0.5)
            return base_weight * reduction
        
        return base_weight
    
    # ============================================
    # Phase 1: 動態角色分配 (1.3.7)
    # ============================================
    
    async def get_dynamic_role_distribution(self, category: Category) -> Dict[str, int]:
        """
        根據健康度動態調整角色分配
        
        規則：
        - 如果某個角色的所有 Feed 都不健康，將其配額分配給健康的角色
        - 健康度高的角色可以獲得更多配額
        
        Args:
            category: 分類
            
        Returns:
            動態調整後的角色分配 {role_name: topic_count}
        """
        roles = get_roles_for_category(category)
        base_distribution = get_role_distribution(category)
        
        if not roles or not base_distribution:
            return base_distribution
        
        # 計算各角色的健康分數
        role_health: Dict[str, float] = {}
        healthy_roles: List[str] = []
        unhealthy_roles: List[str] = []
        
        for role_name, feeds in roles.items():
            if not feeds:
                continue
            
            role_scores = []
            for source_name, feed_url, weight in feeds:
                health_level = await self.get_health_level(feed_url)
                
                if health_level == HealthLevel.HEALTHY:
                    role_scores.append(1.0)
                elif health_level == HealthLevel.LEVEL_1:
                    role_scores.append(0.5)
                elif health_level == HealthLevel.LEVEL_2:
                    role_scores.append(0.2)
                else:
                    role_scores.append(0.0)
            
            avg_score = sum(role_scores) / len(role_scores) if role_scores else 0.0
            role_health[role_name] = avg_score
            
            if avg_score >= 0.3:
                healthy_roles.append(role_name)
            else:
                unhealthy_roles.append(role_name)
        
        # 動態調整分配
        dynamic_distribution = base_distribution.copy()
        
        if not healthy_roles:
            # 所有角色都不健康，保持原分配
            return dynamic_distribution
        
        # 將不健康角色的配額重新分配給健康角色
        redistributed = 0
        for role in unhealthy_roles:
            if role in dynamic_distribution:
                redistributed += dynamic_distribution[role]
                dynamic_distribution[role] = 0
        
        if redistributed > 0 and healthy_roles:
            # 按健康度比例分配
            total_health = sum(role_health.get(r, 0) for r in healthy_roles)
            
            for role in healthy_roles:
                if total_health > 0:
                    share = (role_health.get(role, 0) / total_health) * redistributed
                    dynamic_distribution[role] = dynamic_distribution.get(role, 0) + int(round(share))
                else:
                    # 平均分配
                    share = redistributed / len(healthy_roles)
                    dynamic_distribution[role] = dynamic_distribution.get(role, 0) + int(round(share))
        
        logger.info(f"動態角色分配 ({category.value}): {dynamic_distribution}")
        return dynamic_distribution
    
    # ============================================
    # Phase 1: 多樣性門檻 (1.3.8)
    # ============================================
    
    def get_diversity_threshold(self, category: str) -> Dict[str, Any]:
        """
        取得各分類的多樣性門檻
        
        Fashion: 0.65
        Food: 0.55
        Trend: 0.75
        
        Args:
            category: 分類名稱
            
        Returns:
            多樣性門檻配置
        """
        return self.config.get_diversity_threshold(category)
    
    def check_diversity(self, category: str, diversity_score: float) -> Dict[str, Any]:
        """
        檢查多樣性是否達標
        
        Args:
            category: 分類名稱
            diversity_score: 多樣性分數
            
        Returns:
            檢查結果
        """
        threshold = self.get_diversity_threshold(category)
        min_score = threshold.get("min_score", 0.6)
        
        passed = diversity_score >= min_score
        
        return {
            "category": category,
            "diversity_score": diversity_score,
            "min_score": min_score,
            "passed": passed,
            "message": f"{'通過' if passed else '未通過'}多樣性門檻 ({min_score})"
        }
    
    # ============================================
    # 健康報告相關
    # ============================================
    
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
        """
        is_paused = await self.repository.is_paused(feed_url)
        reliability = await self.repository.get_reliability_score(feed_url)
        recent_records = await self.repository.get_health_report(feed_url, limit=5)
        health_level = await self.get_health_level(feed_url)
        list_type = await self.get_source_list_type(feed_url)
        
        health_score = self.calculate_health_score({
            "reliability_score": reliability,
            "is_paused": is_paused
        })
        
        return {
            "feed_url": feed_url,
            "health_score": health_score,
            "health_status": self.get_health_status(health_score),
            "health_level": health_level.value,
            "health_level_name": health_level.name,
            "list_type": list_type.value,
            "reliability_score": reliability,
            "is_paused": is_paused,
            "recent_records": recent_records,
            "checked_at": datetime.utcnow()
        }
    
    async def get_category_health(self, category: Category) -> Dict[str, Any]:
        """
        獲取分類下所有 Feed 的健康狀態
        """
        feeds = get_all_feeds_for_category(category)
        feed_health_list = []
        
        for source_name, feed_url, weight in feeds:
            health = await self.get_feed_health(feed_url)
            health["source_name"] = source_name
            health["weight"] = weight
            feed_health_list.append(health)
        
        total_feeds = len(feed_health_list)
        healthy_count = sum(1 for h in feed_health_list if h["health_status"] == "healthy")
        paused_count = sum(1 for h in feed_health_list if h["is_paused"])
        avg_score = sum(h["health_score"] for h in feed_health_list) / total_feeds if total_feeds > 0 else 100
        
        # 動態角色分配
        dynamic_distribution = await self.get_dynamic_role_distribution(category)
        
        # 多樣性門檻
        diversity_threshold = self.get_diversity_threshold(category.value)
        
        return {
            "category": category.value,
            "total_feeds": total_feeds,
            "healthy_feeds": healthy_count,
            "paused_feeds": paused_count,
            "average_health_score": round(avg_score, 2),
            "overall_status": self.get_health_status(int(avg_score)),
            "dynamic_role_distribution": dynamic_distribution,
            "diversity_threshold": diversity_threshold,
            "feeds": feed_health_list,
            "generated_at": datetime.utcnow()
        }
    
    async def get_all_categories_health(self) -> Dict[str, Any]:
        """
        獲取所有分類的健康狀態
        """
        categories_health = {}
        
        for category in [Category.FASHION, Category.FOOD, Category.TREND]:
            categories_health[category.value] = await self.get_category_health(category)
        
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
        """獲取統計摘要"""
        return await self.repository.get_stats_summary()
    
    async def get_problematic_feeds(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """獲取有問題的 Feed 列表（可靠度低於閾值）"""
        all_health = await self.repository.get_all_feed_health()
        
        problematic = [
            h for h in all_health
            if h.get("reliability_score", 1.0) < threshold or h.get("is_paused", False)
        ]
        
        return sorted(problematic, key=lambda x: x.get("reliability_score", 0))


# 創建全域實例
feed_health_service = FeedHealthService()

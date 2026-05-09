"""
Phase 2 測試 - Feed 健康監控
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from app.services.feed_health_service import FeedHealthService


class TestFeedHealthService:
    """Feed 健康服務測試"""
    
    def setup_method(self):
        """每個測試前初始化"""
        self.mock_repo = MagicMock()
        self.mock_source_list = MagicMock()
        # 非同步方法須為 AsyncMock，否則 await 會對 MagicMock 報錯
        self.mock_repo.get_feed_stats = AsyncMock(
            return_value={"total": 0, "failures": 0, "successes": 0}
        )
        self.mock_repo.get_consecutive_failures = AsyncMock(return_value=0)
        self.mock_repo.record_success = AsyncMock()
        self.mock_repo.record_failure = AsyncMock()
        self.mock_repo.is_paused = AsyncMock(return_value=False)
        self.mock_repo.get_reliability_score = AsyncMock(return_value=0.92)
        self.mock_repo.get_health_report = AsyncMock(return_value=[])
        self.mock_source_list.get_whitelist_urls = AsyncMock(return_value=[])
        self.mock_source_list.get_blacklist_urls = AsyncMock(return_value=[])
        self.mock_source_list.get_greylist_urls = AsyncMock(return_value=[])

        self.service = FeedHealthService(self.mock_repo, self.mock_source_list)
    
    def test_calculate_health_score_healthy(self):
        """測試健康 Feed 的分數計算"""
        metrics = {
            "reliability_score": 0.95,
            "is_paused": False
        }
        
        score = self.service.calculate_health_score(metrics)
        
        assert score == 95
    
    def test_calculate_health_score_paused(self):
        """測試暫停 Feed 的分數計算"""
        metrics = {
            "reliability_score": 0.95,
            "is_paused": True
        }
        
        score = self.service.calculate_health_score(metrics)
        
        assert score == 0
    
    def test_calculate_health_score_degraded(self):
        """測試降級 Feed 的分數計算"""
        metrics = {
            "reliability_score": 0.75,
            "is_paused": False
        }
        
        score = self.service.calculate_health_score(metrics)
        
        assert score == 75
    
    def test_get_health_status_healthy(self):
        """測試健康狀態判斷 - healthy"""
        assert self.service.get_health_status(95) == "healthy"
        assert self.service.get_health_status(90) == "healthy"
    
    def test_get_health_status_degraded(self):
        """測試健康狀態判斷 - degraded"""
        assert self.service.get_health_status(80) == "degraded"
        assert self.service.get_health_status(70) == "degraded"
    
    def test_get_health_status_warning(self):
        """測試健康狀態判斷 - warning"""
        assert self.service.get_health_status(60) == "warning"
        assert self.service.get_health_status(50) == "warning"
    
    def test_get_health_status_unhealthy(self):
        """測試健康狀態判斷 - unhealthy"""
        assert self.service.get_health_status(40) == "unhealthy"
        assert self.service.get_health_status(10) == "unhealthy"
    
    def test_get_health_status_paused(self):
        """測試健康狀態判斷 - paused"""
        assert self.service.get_health_status(0) == "paused"
    
    @pytest.mark.asyncio
    async def test_record_fetch_result_success(self):
        """測試記錄成功抓取結果"""
        await self.service.record_fetch_result(
            feed_url="https://vogue.com/feed",
            source_name="Vogue",
            success=True
        )
        
        self.mock_repo.record_success.assert_called_once_with(
            "https://vogue.com/feed",
            "Vogue"
        )
    
    @pytest.mark.asyncio
    async def test_record_fetch_result_failure(self):
        """測試記錄失敗抓取結果"""
        await self.service.record_fetch_result(
            feed_url="https://vogue.com/feed",
            source_name="Vogue",
            success=False,
            error="TimeoutError"
        )
        
        self.mock_repo.record_failure.assert_called_once_with(
            "https://vogue.com/feed",
            "TimeoutError",
            "Vogue"
        )
    
    @pytest.mark.asyncio
    async def test_should_skip_feed_paused(self):
        """測試暫停的 Feed 應該被跳過"""
        self.mock_repo.is_paused = AsyncMock(return_value=True)

        result = await self.service.should_skip_feed("https://vogue.com/feed")
        
        assert result == True
    
    @pytest.mark.asyncio
    async def test_should_skip_feed_active(self):
        """測試活躍的 Feed 不應該被跳過"""
        self.mock_repo.is_paused = AsyncMock(return_value=False)

        result = await self.service.should_skip_feed("https://vogue.com/feed")
        
        assert result == False
    
    @pytest.mark.asyncio
    async def test_get_feed_health(self):
        """測試獲取單一 Feed 健康狀態"""
        result = await self.service.get_feed_health("https://vogue.com/feed")
        
        assert "feed_url" in result
        assert "health_score" in result
        assert "health_status" in result
        assert "reliability_score" in result
        assert "is_paused" in result
        assert result["health_score"] == 92
        assert result["health_status"] == "healthy"


class TestFeedHealthRepository:
    """Feed 健康 Repository 測試（使用 mock）"""
    
    @pytest.mark.asyncio
    async def test_is_paused_after_3_failures(self):
        """測試連續 3 次失敗後應該暫停"""
        from app.services.repositories.feed_health_repository import FeedHealthRepository
        
        # 這個測試需要 MongoDB 連接，使用 mock
        with patch.object(FeedHealthRepository, '_get_collection') as mock_collection:
            mock_col = MagicMock()
            mock_col.count_documents = AsyncMock(return_value=3)
            mock_col.find_one = AsyncMock(return_value=None)
            mock_collection.return_value = mock_col
            
            repo = FeedHealthRepository()
            repo._indexes_created = True
            
            result = await repo.is_paused("https://test.com/feed")
            
            assert result == True
    
    @pytest.mark.asyncio
    async def test_is_paused_less_than_3_failures(self):
        """測試少於 3 次失敗不應該暫停"""
        from app.services.repositories.feed_health_repository import FeedHealthRepository
        
        with patch.object(FeedHealthRepository, '_get_collection') as mock_collection:
            mock_col = MagicMock()
            mock_col.count_documents = AsyncMock(return_value=2)
            mock_col.find_one = AsyncMock(return_value=None)
            mock_collection.return_value = mock_col
            
            repo = FeedHealthRepository()
            repo._indexes_created = True
            
            result = await repo.is_paused("https://test.com/feed")
            
            assert result == False
    
    @pytest.mark.asyncio
    async def test_reliability_score_calculation(self):
        """測試可靠度分數計算"""
        from app.services.repositories.feed_health_repository import FeedHealthRepository
        
        with patch.object(FeedHealthRepository, '_get_collection') as mock_collection:
            mock_col = MagicMock()
            # 10 次請求，8 次成功
            mock_col.count_documents = AsyncMock(side_effect=[10, 8])
            mock_collection.return_value = mock_col
            
            repo = FeedHealthRepository()
            repo._indexes_created = True
            
            result = await repo.get_reliability_score("https://test.com/feed")
            
            assert result == 0.8


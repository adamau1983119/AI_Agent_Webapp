"""
Phase 3 測試 - Feed Health API
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime


class TestFeedsHealthAPI:
    """Feed Health API 測試"""
    
    @pytest.fixture
    def mock_health_service(self):
        """Mock FeedHealthService"""
        with patch('app.api.v1.feeds.health_service') as mock:
            yield mock
    
    @pytest.fixture
    def mock_health_repo(self):
        """Mock FeedHealthRepository"""
        with patch('app.api.v1.feeds.health_repo') as mock:
            yield mock
    
    def test_get_all_feeds_health_endpoint_exists(self):
        """測試 /feeds/health 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/health" in routes or "/health" in routes
    
    def test_get_category_health_endpoint_exists(self):
        """測試 /feeds/health/{category} 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/health/{category}" in routes or "/health/{category}" in routes
    
    def test_get_stats_endpoint_exists(self):
        """測試 /feeds/stats 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/stats" in routes or "/stats" in routes
    
    def test_get_diversity_report_endpoint_exists(self):
        """測試 /feeds/diversity-report 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/diversity-report" in routes or "/diversity-report" in routes
    
    def test_pause_endpoint_exists(self):
        """測試 /feeds/pause 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/pause" in routes or "/pause" in routes
    
    def test_resume_endpoint_exists(self):
        """測試 /feeds/resume 端點存在"""
        from app.api.v1.feeds import router
        
        routes = [route.path for route in router.routes]
        assert "/feeds/resume" in routes or "/resume" in routes


class TestFeedsAPIResponses:
    """Feed API 響應測試"""
    
    @pytest.mark.asyncio
    async def test_get_all_feeds_health_response(self):
        """測試 /feeds/health 響應格式"""
        from app.api.v1.feeds import get_all_feeds_health
        from unittest.mock import AsyncMock, patch
        
        mock_data = {
            "summary": {
                "total_feeds": 30,
                "healthy_feeds": 25,
                "paused_feeds": 2,
                "overall_health_rate": 0.83
            },
            "categories": {
                "fashion": {"total_feeds": 10, "healthy_feeds": 8},
                "food": {"total_feeds": 10, "healthy_feeds": 9},
                "trend": {"total_feeds": 10, "healthy_feeds": 8},
            },
            "generated_at": datetime.utcnow()
        }
        
        with patch('app.api.v1.feeds.health_service.get_all_categories_health', new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_all_feeds_health()
        
        assert result["success"] == True
        assert "data" in result
    
    @pytest.mark.asyncio
    async def test_get_category_health_fashion(self):
        """測試 /feeds/health/fashion 響應"""
        from app.api.v1.feeds import get_category_feeds_health
        from unittest.mock import AsyncMock, patch
        
        mock_data = {
            "category": "fashion",
            "total_feeds": 10,
            "healthy_feeds": 8,
            "paused_feeds": 1,
            "average_health_score": 85.5,
            "overall_status": "degraded",
            "feeds": [],
            "generated_at": datetime.utcnow()
        }
        
        with patch('app.api.v1.feeds.health_service.get_category_health', new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_category_feeds_health("fashion")
        
        assert result["success"] == True
        assert result["data"]["category"] == "fashion"
    
    @pytest.mark.asyncio
    async def test_get_category_health_invalid_category(self):
        """測試無效分類返回錯誤"""
        from app.api.v1.feeds import get_category_feeds_health
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await get_category_feeds_health("invalid_category")
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_stats_response(self):
        """測試 /feeds/stats 響應格式"""
        from app.api.v1.feeds import get_feeds_stats
        from unittest.mock import AsyncMock, patch
        
        mock_data = {
            "last_hour": {
                "total_requests": 100,
                "failures": 5,
                "success_rate": 0.95
            },
            "last_24_hours": {
                "total_requests": 2400,
                "failures": 120,
                "success_rate": 0.95
            },
            "feeds": {
                "total_tracked": 30,
                "healthy": 25,
                "degraded": 3,
                "unhealthy": 1,
                "paused": 1
            },
            "generated_at": datetime.utcnow()
        }
        
        with patch('app.api.v1.feeds.health_service.get_stats_summary', new_callable=AsyncMock) as mock:
            mock.return_value = mock_data
            result = await get_feeds_stats()
        
        assert result["success"] == True
        assert "last_hour" in result["data"]
        assert "last_24_hours" in result["data"]
        assert "feeds" in result["data"]
    
    @pytest.mark.asyncio
    async def test_pause_feed(self):
        """測試暫停 Feed"""
        from app.api.v1.feeds import pause_feed
        from unittest.mock import AsyncMock, patch
        
        mock_repo = AsyncMock()
        mock_repo.record_failure = AsyncMock()
        
        with patch('app.api.v1.feeds.health_repo', mock_repo):
            result = await pause_feed(
                feed_url="https://vogue.com/feed",
                reason="Manual test"
            )
        
        assert result["success"] == True
        assert result["data"]["is_paused"] == True
        # 應該記錄 3 次失敗以觸發暫停
        assert mock_repo.record_failure.call_count == 3
    
    @pytest.mark.asyncio
    async def test_resume_feed(self):
        """測試恢復 Feed"""
        from app.api.v1.feeds import resume_feed
        from unittest.mock import AsyncMock, patch
        
        mock_repo = AsyncMock()
        mock_repo.record_success = AsyncMock()
        mock_repo.is_paused = AsyncMock(return_value=False)
        
        with patch('app.api.v1.feeds.health_repo', mock_repo):
            result = await resume_feed(feed_url="https://vogue.com/feed")
        
        assert result["success"] == True
        mock_repo.record_success.assert_called_once()


"""
Phase 1.1 測試 - RSS Feed 角色分配
"""
import pytest
from app.config.feed_roles import (
    FASHION_ROLES,
    FOOD_ROLES,
    TREND_ROLES,
    get_roles_for_category,
    get_role_distribution,
    get_source_weight,
    get_all_feeds_for_category,
    DEFAULT_ROLE_DISTRIBUTION,
)
from app.models.topic import Category


class TestFeedRoles:
    """Feed 角色配置測試"""
    
    def test_fashion_roles_exist(self):
        """測試 Fashion 角色配置存在"""
        assert len(FASHION_ROLES) >= 5
        assert "authority" in FASHION_ROLES
        assert "streetwear" in FASHION_ROLES
        assert "asian" in FASHION_ROLES
        assert "industry" in FASHION_ROLES
        assert "practical" in FASHION_ROLES
    
    def test_food_roles_exist(self):
        """測試 Food 角色配置存在"""
        assert len(FOOD_ROLES) >= 5
        assert "mainstream" in FOOD_ROLES
        assert "professional" in FOOD_ROLES
        assert "cultural" in FOOD_ROLES
        assert "healthy" in FOOD_ROLES
        assert "casual" in FOOD_ROLES
    
    def test_trend_roles_exist(self):
        """測試 Trend 角色配置存在"""
        assert len(TREND_ROLES) >= 5
        assert "tech" in TREND_ROLES
        assert "science" in TREND_ROLES
        assert "culture" in TREND_ROLES
        assert "innovation" in TREND_ROLES
        assert "lifestyle" in TREND_ROLES
    
    def test_each_role_has_feeds(self):
        """測試每個角色都有 Feed"""
        for role, feeds in FASHION_ROLES.items():
            assert len(feeds) >= 1, f"Fashion role '{role}' has no feeds"
            for name, url, weight in feeds:
                assert len(name) > 0
                assert url.startswith("http")
                assert 0 <= weight <= 1
        
        for role, feeds in FOOD_ROLES.items():
            assert len(feeds) >= 1, f"Food role '{role}' has no feeds"
        
        for role, feeds in TREND_ROLES.items():
            assert len(feeds) >= 1, f"Trend role '{role}' has no feeds"


class TestGetRolesForCategory:
    """獲取分類角色測試"""
    
    def test_get_fashion_roles(self):
        """測試獲取 Fashion 角色"""
        roles = get_roles_for_category(Category.FASHION)
        
        assert roles == FASHION_ROLES
    
    def test_get_food_roles(self):
        """測試獲取 Food 角色"""
        roles = get_roles_for_category(Category.FOOD)
        
        assert roles == FOOD_ROLES
    
    def test_get_trend_roles(self):
        """測試獲取 Trend 角色"""
        roles = get_roles_for_category(Category.TREND)
        
        assert roles == TREND_ROLES


class TestGetRoleDistribution:
    """獲取角色分配比例測試"""
    
    def test_fashion_distribution_sums_to_10(self):
        """測試 Fashion 分配總和為 10"""
        distribution = get_role_distribution(Category.FASHION)
        
        total = sum(distribution.values())
        assert total == 10
    
    def test_food_distribution_sums_to_10(self):
        """測試 Food 分配總和為 10"""
        distribution = get_role_distribution(Category.FOOD)
        
        total = sum(distribution.values())
        assert total == 10
    
    def test_trend_distribution_sums_to_10(self):
        """測試 Trend 分配總和為 10"""
        distribution = get_role_distribution(Category.TREND)
        
        total = sum(distribution.values())
        assert total == 10
    
    def test_each_role_has_at_least_1(self):
        """測試每個角色至少分配 1 個"""
        for category in [Category.FASHION, Category.FOOD, Category.TREND]:
            distribution = get_role_distribution(category)
            for role, count in distribution.items():
                assert count >= 1, f"Role '{role}' in {category.value} has count {count}"


class TestGetSourceWeight:
    """獲取來源權重測試"""
    
    def test_vogue_weight_tier_s(self):
        """測試 Vogue 權重為 Tier S"""
        weight = get_source_weight("Vogue")
        
        assert weight >= 0.95
    
    def test_hypebeast_weight_tier_a(self):
        """測試 Hypebeast 權重為 Tier A"""
        weight = get_source_weight("Hypebeast")
        
        assert 0.8 <= weight <= 0.9
    
    def test_unknown_source_default_weight(self):
        """測試未知來源返回預設權重"""
        weight = get_source_weight("Unknown Random Blog")
        
        assert weight == 0.5
    
    def test_partial_match(self):
        """測試部分匹配（來源名稱包含已知來源）"""
        weight = get_source_weight("Vogue International")
        
        assert weight >= 0.95


class TestGetAllFeedsForCategory:
    """獲取分類所有 Feed 測試"""
    
    def test_fashion_has_multiple_feeds(self):
        """測試 Fashion 有多個 Feed"""
        feeds = get_all_feeds_for_category(Category.FASHION)
        
        assert len(feeds) >= 10
    
    def test_food_has_multiple_feeds(self):
        """測試 Food 有多個 Feed"""
        feeds = get_all_feeds_for_category(Category.FOOD)
        
        assert len(feeds) >= 5
    
    def test_trend_has_multiple_feeds(self):
        """測試 Trend 有多個 Feed"""
        feeds = get_all_feeds_for_category(Category.TREND)
        
        assert len(feeds) >= 10
    
    def test_no_single_source_monopoly(self):
        """測試沒有單一來源壟斷（每個分類 >= 5 個不同來源）"""
        for category in [Category.FASHION, Category.FOOD, Category.TREND]:
            feeds = get_all_feeds_for_category(category)
            sources = set(name for name, url, weight in feeds)
            
            assert len(sources) >= 5, f"Category {category.value} has only {len(sources)} unique sources"


"""
Phase 1.2 + 1.3 測試 - 文章評分服務 + 多樣性指標
"""
import pytest
from datetime import datetime, timedelta
from app.services.scoring_service import ScoringService, DiversityScorer
from app.models.topic import Category


class TestScoringService:
    """文章評分服務測試"""
    
    def setup_method(self):
        """每個測試前初始化"""
        self.scorer = ScoringService()
    
    def test_compute_score_new_article(self, sample_article):
        """測試新文章（< 1 小時）應該得到高分"""
        # 設置發布時間為 30 分鐘前
        sample_article["published"] = datetime.utcnow() - timedelta(minutes=30)
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert "score" in result
        assert "score_breakdown" in result
        assert result["score_breakdown"]["time"] >= 0.9  # 時效性高分
        assert result["score"] > 0.5  # 總分應該不低
    
    def test_compute_score_old_article(self, sample_article):
        """測試舊文章（> 48 小時）應該得到低分"""
        # 設置發布時間為 72 小時前
        sample_article["published"] = datetime.utcnow() - timedelta(hours=72)
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["time"] <= 0.3  # 時效性低分
    
    def test_source_weight_tier_s(self, sample_article):
        """測試 Tier S 來源（Vogue）應該得到高分"""
        sample_article["source"] = "Vogue"
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["source"] >= 0.95  # Vogue 是 Tier S
    
    def test_source_weight_unknown(self, sample_article):
        """測試未知來源應該得到中等分數"""
        sample_article["source"] = "Unknown Blog"
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["source"] == 0.5  # 未知來源預設 0.5
    
    def test_completeness_with_image(self, sample_article):
        """測試有圖片的文章完整度分數"""
        sample_article["images"] = ["image1.jpg", "image2.jpg"]
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["completeness"] >= 0.4  # 有圖片加分
    
    def test_completeness_without_image(self, sample_article):
        """測試無圖片的文章完整度分數"""
        sample_article["images"] = []
        sample_article["summary"] = ""
        sample_article["original_content"] = ""
        sample_article["keywords"] = []
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["completeness"] == 0.0
    
    def test_relevance_keyword_match(self, sample_article):
        """測試關鍵字匹配的相關度分數"""
        sample_article["title"] = "Fashion trends and style guide"
        sample_article["summary"] = "Latest fashion style and trend news"
        
        result = self.scorer.compute_score(sample_article, Category.FASHION)
        
        assert result["score_breakdown"]["relevance"] > 0  # 有匹配關鍵字
    
    def test_update_weights(self):
        """測試更新權重功能"""
        original_time_weight = self.scorer.weights["time"]
        
        self.scorer.update_weights({"time": 0.5})
        
        # 權重會被正規化，但相對比例應該改變
        assert self.scorer.weights["time"] != original_time_weight


class TestDiversityScorer:
    """多樣性評分測試"""
    
    def test_diversity_score_single_source(self, single_source_topics):
        """測試單一來源的多樣性分數應該很低"""
        score = DiversityScorer.calculate_diversity_score(single_source_topics)
        
        # 10 篇全來自同一來源，分數應該很低
        assert score <= 0.1
    
    def test_diversity_score_all_unique(self):
        """測試所有來源唯一的多樣性分數應該為 1.0"""
        topics = [
            {"source_name": f"Source_{i}"} for i in range(10)
        ]
        
        score = DiversityScorer.calculate_diversity_score(topics)
        
        assert score == 1.0
    
    def test_diversity_score_mixed(self, sample_topics):
        """測試混合來源的多樣性分數"""
        score = DiversityScorer.calculate_diversity_score(sample_topics)
        
        # 10 篇來自 9 個不同來源，分數應該很高
        assert score >= 0.6
        assert score <= 1.0
    
    def test_diversity_score_empty_list(self):
        """測試空列表的多樣性分數"""
        score = DiversityScorer.calculate_diversity_score([])
        
        assert score == 0.0
    
    def test_diversity_report(self, sample_topics):
        """測試多樣性報告功能"""
        report = DiversityScorer.get_diversity_report(sample_topics)
        
        assert "score" in report
        assert "total_topics" in report
        assert "unique_sources" in report
        assert "source_distribution" in report
        assert "status" in report
        assert "passed" in report
        
        assert report["total_topics"] == 10
        assert report["unique_sources"] >= 5
        assert report["passed"] == True  # score >= 0.6
    
    def test_diversity_report_fail_threshold(self, single_source_topics):
        """測試未通過閾值的多樣性報告"""
        report = DiversityScorer.get_diversity_report(single_source_topics)
        
        assert report["passed"] == False  # score < 0.6
        assert report["status"] == "poor"


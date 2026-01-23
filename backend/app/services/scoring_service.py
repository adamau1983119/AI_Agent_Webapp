"""
文章評分服務
根據時效性、來源信任度、完整度、相關度計算文章分數
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import Counter

from app.models.topic import Category
from app.config.feed_roles import get_source_weight

logger = logging.getLogger(__name__)


# 評分權重配置
SCORING_WEIGHTS = {
    "time": 0.4,        # 時效性 40%
    "source": 0.3,      # 來源信任度 30%
    "completeness": 0.2, # 完整度 20%
    "relevance": 0.1,   # 相關度 10%
}

# 分類關鍵字（用於相關度計算）
CATEGORY_KEYWORDS = {
    Category.FASHION: [
        "fashion", "style", "trend", "designer", "runway", "collection",
        "時尚", "潮流", "設計師", "時裝", "穿搭", "服飾",
        "outfit", "wardrobe", "couture", "streetwear", "luxury"
    ],
    Category.FOOD: [
        "food", "recipe", "restaurant", "chef", "cuisine", "cooking",
        "美食", "食譜", "餐廳", "料理", "烹飪", "小吃",
        "dining", "gourmet", "ingredient", "dish", "flavor"
    ],
    Category.TREND: [
        "tech", "technology", "ai", "innovation", "startup", "digital",
        "科技", "技術", "創新", "趨勢", "發展", "智能",
        "future", "research", "data", "software", "hardware"
    ],
}


class ScoringService:
    """文章評分服務"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化評分服務
        
        Args:
            weights: 自定義權重配置，如果為 None 則使用預設值
        """
        self.weights = weights or SCORING_WEIGHTS.copy()
    
    def compute_score(
        self,
        article: Dict[str, Any],
        category: Category
    ) -> Dict[str, Any]:
        """
        計算文章總分
        
        Args:
            article: 文章數據（包含 title, published, source, images 等）
            category: 文章分類
            
        Returns:
            包含 score 和 score_breakdown 的字典
        """
        time_score = self._compute_time_score(article)
        source_score = self._compute_source_score(article)
        completeness_score = self._compute_completeness_score(article)
        relevance_score = self._compute_relevance_score(article, category)
        
        # 計算加權總分
        total_score = (
            self.weights["time"] * time_score +
            self.weights["source"] * source_score +
            self.weights["completeness"] * completeness_score +
            self.weights["relevance"] * relevance_score
        )
        
        return {
            "score": round(total_score, 4),
            "score_breakdown": {
                "time": round(time_score, 4),
                "source": round(source_score, 4),
                "completeness": round(completeness_score, 4),
                "relevance": round(relevance_score, 4),
            }
        }
    
    def _compute_time_score(self, article: Dict[str, Any]) -> float:
        """
        計算時效性分數
        
        - 1 小時內: 1.0
        - 6 小時內: 0.9
        - 24 小時內: 0.7
        - 48 小時內: 0.5
        - 超過 48 小時: 0.2
        """
        import time as time_module
        
        published = article.get("published") or article.get("fetched_at")
        
        if not published:
            return 0.5  # 無發布時間，給中等分數
        
        try:
            # 處理 time.struct_time 格式（feedparser 返回的格式）
            if isinstance(published, time_module.struct_time):
                published = datetime(*published[:6])
            # 處理字符串格式
            elif isinstance(published, str):
                try:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except:
                    return 0.5
            # 確保是 datetime 對象
            elif not isinstance(published, datetime):
                return 0.5
            
            now = datetime.utcnow()
            
            # 處理時區
            if hasattr(published, 'tzinfo') and published.tzinfo:
                now = now.replace(tzinfo=published.tzinfo)
            
            age = now - published
            hours = age.total_seconds() / 3600
            
            if hours <= 1:
                return 1.0
            elif hours <= 6:
                return 0.9
            elif hours <= 24:
                return 0.7
            elif hours <= 48:
                return 0.5
            else:
                return 0.2
        except Exception as e:
            logger.warning(f"計算時效性分數失敗: {e}")
            return 0.5
    
    def _compute_source_score(self, article: Dict[str, Any]) -> float:
        """
        計算來源信任度分數
        根據 feed_roles.py 中定義的來源權重
        """
        source_name = article.get("source") or article.get("source_name", "")
        return get_source_weight(source_name)
    
    def _compute_completeness_score(self, article: Dict[str, Any]) -> float:
        """
        計算完整度分數
        
        - 有圖片: +0.4
        - 有摘要: +0.3
        - 有原始內容: +0.2
        - 有關鍵字: +0.1
        """
        score = 0.0
        
        # 檢查圖片
        images = article.get("images", [])
        if images and len(images) > 0:
            score += 0.4
        
        # 檢查摘要
        summary = article.get("summary") or article.get("description", "")
        if summary and len(summary) > 20:
            score += 0.3
        
        # 檢查原始內容
        content = article.get("original_content") or article.get("content", "")
        if content and len(content) > 100:
            score += 0.2
        
        # 檢查關鍵字
        keywords = article.get("keywords", [])
        if keywords and len(keywords) > 0:
            score += 0.1
        
        return score
    
    def _compute_relevance_score(
        self,
        article: Dict[str, Any],
        category: Category
    ) -> float:
        """
        計算相關度分數
        根據標題和摘要中包含的分類關鍵字數量
        """
        keywords = CATEGORY_KEYWORDS.get(category, [])
        if not keywords:
            return 0.5
        
        # 組合文本進行檢查
        title = article.get("title", "").lower()
        summary = (article.get("summary") or article.get("description", "")).lower()
        text = f"{title} {summary}"
        
        # 計算匹配的關鍵字數量
        matches = sum(1 for kw in keywords if kw.lower() in text)
        
        # 正規化分數 (最多匹配 5 個關鍵字得滿分)
        return min(matches / 5, 1.0)
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """
        更新評分權重
        
        Args:
            new_weights: 新的權重配置（只更新提供的鍵）
        """
        for key, value in new_weights.items():
            if key in self.weights:
                self.weights[key] = value
        
        # 正規化權重，確保總和為 1
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
        
        logger.info(f"評分權重已更新: {self.weights}")


class DiversityScorer:
    """多樣性評分服務"""
    
    @staticmethod
    def calculate_diversity_score(topics: List[Dict[str, Any]]) -> float:
        """
        計算來源多樣性分數
        
        公式: diversity_score = 1 - (max_ratio - avg_ratio)
        
        範例:
        - 10 篇全來自 Vogue → score ≈ 0.0
        - 10 篇來自 5 個來源各 2 篇 → score ≈ 0.8
        - 10 篇來自 10 個不同來源 → score = 1.0
        
        Args:
            topics: 主題列表
            
        Returns:
            多樣性分數 (0.0 - 1.0)
        """
        if not topics:
            return 0.0
        
        # 收集所有來源名稱
        sources = []
        for topic in topics:
            source_name = topic.get("source") or topic.get("source_name")
            if source_name:
                sources.append(source_name)
        
        if not sources:
            return 0.0
        
        # 計算來源分布
        counts = Counter(sources)
        num_sources = len(counts)
        total_topics = len(sources)
        
        if num_sources == 0:
            return 0.0
        
        # 如果只有 1 個來源，分數為 0.0
        if num_sources == 1:
            return 0.0
        
        # 計算最大來源佔比和平均佔比
        max_ratio = max(counts.values()) / total_topics
        avg_ratio = 1 / num_sources
        
        # 計算多樣性分數
        score = max(0, 1 - (max_ratio - avg_ratio))
        
        return round(score, 4)
    
    @staticmethod
    def get_diversity_report(topics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成多樣性報告
        
        Args:
            topics: 主題列表
            
        Returns:
            包含多樣性分析的報告
        """
        if not topics:
            return {
                "score": 0.0,
                "total_topics": 0,
                "unique_sources": 0,
                "source_distribution": {},
                "status": "no_data"
            }
        
        # 收集來源
        sources = []
        for topic in topics:
            source_name = topic.get("source") or topic.get("source_name", "Unknown")
            sources.append(source_name)
        
        counts = Counter(sources)
        score = DiversityScorer.calculate_diversity_score(topics)
        
        # 判斷狀態
        if score >= 0.8:
            status = "excellent"
        elif score >= 0.6:
            status = "good"
        elif score >= 0.4:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "score": score,
            "total_topics": len(topics),
            "unique_sources": len(counts),
            "source_distribution": dict(counts),
            "max_source": counts.most_common(1)[0] if counts else None,
            "status": status,
            "passed": score >= 0.6  # 驗收標準：>= 0.6
        }


"""
智能圖片匹配服務 (Phase 5B)
根據關鍵字匹配度、來源信任度、圖片品質和來源多樣性計算圖片分數
"""
import logging
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime

from app.config.feed_roles import get_source_weight

logger = logging.getLogger(__name__)


# 圖片評分權重配置
IMAGE_SCORING_WEIGHTS = {
    "keyword": 0.40,    # 關鍵字匹配 40%
    "trust": 0.25,      # 來源信任度 25%
    "quality": 0.15,    # 圖片品質 15%
    "diversity": 0.20,  # 來源多樣性 20%
}

# 來源信任度層級
SOURCE_TRUST_TIERS = {
    # Tier S (1.0) - 權威來源
    "vogue": 1.0,
    "elle": 1.0,
    "nyt": 1.0,
    "nytimes": 1.0,
    "bbc": 1.0,
    "business of fashion": 0.95,
    "bof": 0.95,
    
    # Tier A (0.85-0.9) - 專業來源
    "techcrunch": 0.9,
    "the verge": 0.9,
    "wired": 0.9,
    "hypebeast": 0.85,
    "wwd": 0.85,
    "eater": 0.85,
    "bon appetit": 0.85,
    
    # Tier B (0.6-0.8) - 外部圖片庫
    "unsplash": 0.7,
    "pexels": 0.7,
    "pixabay": 0.65,
    "google": 0.6,
    
    # Tier C (0.4-0.5) - 未知來源
    "unknown": 0.5,
}


class KeywordExtractor:
    """關鍵字提取器"""
    
    # 停用詞列表
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "and", "but", "or", "nor", "so", "yet", "both", "either", "neither",
        "not", "only", "same", "than", "too", "very", "just", "also",
        "的", "是", "在", "和", "了", "有", "這", "那", "與", "為",
    }
    
    @classmethod
    def extract_from_title(cls, title: str) -> List[str]:
        """從標題提取關鍵字"""
        if not title:
            return []
        
        # 提取英文單詞（3+ 字元）
        english_words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
        english_keywords = [w for w in english_words if w not in cls.STOP_WORDS]
        
        # 提取中文詞（2-4 字）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', title)
        chinese_keywords = [w for w in chinese_words if w not in cls.STOP_WORDS]
        
        # 合併並去重
        all_keywords = list(set(english_keywords + chinese_keywords))
        return all_keywords[:10]  # 最多返回 10 個關鍵字
    
    @classmethod
    def extract_from_content(cls, content: str) -> List[str]:
        """從內容提取關鍵字（更全面）"""
        if not content:
            return []
        
        # 限制內容長度
        content = content[:2000]
        
        # 提取英文單詞
        english_words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_counts = {}
        for word in english_words:
            if word not in cls.STOP_WORDS:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # 按頻率排序取前 15 個
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        english_keywords = [w[0] for w in sorted_words[:15]]
        
        # 提取中文詞
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', content)
        chinese_counts = {}
        for word in chinese_words:
            if word not in cls.STOP_WORDS:
                chinese_counts[word] = chinese_counts.get(word, 0) + 1
        
        sorted_chinese = sorted(chinese_counts.items(), key=lambda x: x[1], reverse=True)
        chinese_keywords = [w[0] for w in sorted_chinese[:10]]
        
        return english_keywords + chinese_keywords
    
    @classmethod
    def extract_entities(cls, text: str) -> List[str]:
        """提取專有名詞（品牌、人名、地名）"""
        if not text:
            return []
        
        # 簡單的大寫字母開頭單詞作為專有名詞
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # 去重並限制數量
        return list(set(entities))[:10]


class ImageMatcher:
    """智能圖片匹配服務"""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        初始化圖片匹配器
        
        Args:
            weights: 自定義權重配置
        """
        self.weights = weights or IMAGE_SCORING_WEIGHTS.copy()
        self.keyword_extractor = KeywordExtractor()
    
    async def match_images(
        self,
        topic: Dict[str, Any],
        candidate_images: List[Dict[str, Any]],
        target_count: int = 10
    ) -> List[Dict[str, Any]]:
        """
        為主題匹配最佳圖片
        
        Args:
            topic: 主題數據（包含 title, content, sources 等）
            candidate_images: 候選圖片列表
            target_count: 目標圖片數量
            
        Returns:
            排序後的最佳圖片列表（包含分數）
        """
        if not candidate_images:
            return []
        
        # 提取關鍵字
        keywords = self._extract_all_keywords(topic)
        logger.info(f"提取關鍵字: {keywords[:10]}...")
        
        # 計算每張圖片的分數
        scored_images = []
        selected_sources: Set[str] = set()
        
        # 第一輪：計算基礎分數（不含多樣性）
        for image in candidate_images:
            base_score = self._compute_base_score(image, keywords)
            scored_images.append({
                **image,
                "base_score": base_score,
                "score": 0,  # 稍後計算
                "score_breakdown": {},
            })
        
        # 按基礎分數排序
        scored_images.sort(key=lambda x: x["base_score"], reverse=True)
        
        # 第二輪：加入多樣性加權，選擇最終圖片
        final_images = []
        for image in scored_images:
            if len(final_images) >= target_count:
                break
            
            # 計算多樣性加分
            diversity_bonus = self._compute_diversity_bonus(image, selected_sources)
            
            # 計算最終分數
            keyword_score = self._compute_keyword_score(image, keywords)
            trust_score = self._compute_trust_score(image)
            quality_score = self._compute_quality_score(image)
            
            total_score = (
                self.weights["keyword"] * keyword_score +
                self.weights["trust"] * trust_score +
                self.weights["quality"] * quality_score +
                self.weights["diversity"] * diversity_bonus
            )
            
            image["score"] = round(total_score, 4)
            image["score_breakdown"] = {
                "keyword": round(keyword_score, 4),
                "trust": round(trust_score, 4),
                "quality": round(quality_score, 4),
                "diversity": round(diversity_bonus, 4),
            }
            image["matched_keywords"] = self._get_matched_keywords(image, keywords)
            
            final_images.append(image)
            
            # 記錄已選擇的來源
            source = image.get("source", "unknown")
            selected_sources.add(source)
        
        # 按最終分數重新排序
        final_images.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"匹配完成，選擇 {len(final_images)} 張圖片")
        return final_images
    
    def _extract_all_keywords(self, topic: Dict[str, Any]) -> List[str]:
        """從主題提取所有關鍵字"""
        keywords = []
        
        # 從標題提取
        title = topic.get("title", "")
        keywords.extend(self.keyword_extractor.extract_from_title(title))
        
        # 從原始標題提取
        original_title = topic.get("original_title", "")
        if original_title and original_title != title:
            keywords.extend(self.keyword_extractor.extract_from_title(original_title))
        
        # 從內容提取
        content = topic.get("content", "") or topic.get("description", "")
        if content:
            keywords.extend(self.keyword_extractor.extract_from_content(content))
        
        # 從來源提取
        for source in topic.get("sources", []):
            source_keywords = source.get("keywords", [])
            keywords.extend(source_keywords)
        
        # 提取專有名詞
        full_text = f"{title} {original_title} {content}"
        entities = self.keyword_extractor.extract_entities(full_text)
        keywords.extend(entities)
        
        # 去重並返回
        return list(set(keywords))
    
    def _compute_base_score(
        self,
        image: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """計算基礎分數（不含多樣性）"""
        keyword_score = self._compute_keyword_score(image, keywords)
        trust_score = self._compute_trust_score(image)
        quality_score = self._compute_quality_score(image)
        
        # 基礎分數 = 80% 的權重
        return (
            0.5 * keyword_score +
            0.3 * trust_score +
            0.2 * quality_score
        )
    
    def _compute_keyword_score(
        self,
        image: Dict[str, Any],
        keywords: List[str]
    ) -> float:
        """
        計算關鍵字匹配分數
        
        檢查圖片的 alt、caption、filename 是否包含關鍵字
        """
        if not keywords:
            return 0.5
        
        # 組合所有可檢查的文本
        alt = image.get("alt", "").lower()
        caption = image.get("caption", "").lower()
        filename = image.get("filename", "").lower()
        url = image.get("url", "").lower()
        
        text = f"{alt} {caption} {filename} {url}"
        
        # 計算匹配數量
        matches = sum(1 for kw in keywords if kw.lower() in text)
        
        # 正規化（最多匹配 5 個關鍵字得滿分）
        return min(matches / 5, 1.0)
    
    def _compute_trust_score(self, image: Dict[str, Any]) -> float:
        """計算來源信任度分數"""
        source = image.get("source", "").lower()
        
        # 查找匹配的來源
        for source_name, trust in SOURCE_TRUST_TIERS.items():
            if source_name in source:
                return trust
        
        return SOURCE_TRUST_TIERS["unknown"]
    
    def _compute_quality_score(self, image: Dict[str, Any]) -> float:
        """
        計算圖片品質分數
        
        - 解析度 >= 1920: 1.0
        - 解析度 >= 1200: 0.8
        - 解析度 >= 800: 0.6
        - 解析度 < 800: 0.3
        """
        width = image.get("width", 0)
        height = image.get("height", 0)
        
        # 使用較大的維度
        max_dimension = max(width, height)
        
        if max_dimension >= 1920:
            return 1.0
        elif max_dimension >= 1200:
            return 0.8
        elif max_dimension >= 800:
            return 0.6
        elif max_dimension > 0:
            return 0.3
        else:
            # 無解析度信息，給中等分數
            return 0.5
    
    def _compute_diversity_bonus(
        self,
        image: Dict[str, Any],
        selected_sources: Set[str]
    ) -> float:
        """
        計算多樣性加分
        
        - 如果圖片來源與已選圖片不同 → 1.0
        - 如果圖片來源與已選圖片相同 → 0.0
        """
        source = image.get("source", "unknown")
        
        if source not in selected_sources:
            return 1.0
        else:
            return 0.0
    
    def _get_matched_keywords(
        self,
        image: Dict[str, Any],
        keywords: List[str]
    ) -> List[str]:
        """獲取匹配到的關鍵字列表"""
        alt = image.get("alt", "").lower()
        caption = image.get("caption", "").lower()
        filename = image.get("filename", "").lower()
        url = image.get("url", "").lower()
        
        text = f"{alt} {caption} {filename} {url}"
        
        matched = [kw for kw in keywords if kw.lower() in text]
        return matched[:5]  # 最多返回 5 個
    
    def generate_caption(
        self,
        image: Dict[str, Any],
        topic: Dict[str, Any]
    ) -> str:
        """
        為圖片生成標題/說明
        
        Args:
            image: 圖片數據
            topic: 主題數據
            
        Returns:
            生成的標題
        """
        # 優先使用圖片自帶的 caption
        if image.get("caption"):
            return image["caption"]
        
        # 其次使用 alt 文字
        if image.get("alt"):
            return image["alt"]
        
        # 使用主題標題和來源生成
        topic_title = topic.get("title", "")
        source = image.get("source", "")
        
        if topic_title and source:
            return f"{topic_title} - {source}"
        elif topic_title:
            return topic_title
        elif source:
            return f"Image from {source}"
        else:
            return "Related Image"


# 創建全域實例
image_matcher = ImageMatcher()


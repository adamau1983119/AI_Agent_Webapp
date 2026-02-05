"""
HashtagExtractor (Phase 6.5)
從文章標題和內容提取 Hashtags
結合正則提取和 AI 生成
"""
from typing import List, Set, Optional, Dict, Any
import re
import logging
from app.config.brands import (
    ALL_BRANDS,
    BRANDS_BY_CATEGORY,
    STOP_WORDS,
    get_brands_for_category,
    is_stop_word,
)

logger = logging.getLogger(__name__)


class HashtagExtractor:
    """
    Hashtag 提取器 (Phase 6.5)
    
    提取策略：
    1. 正則提取已有的 #hashtag
    2. 正則提取專有名詞（大寫開頭）
    3. 匹配品牌名稱
    4. AI 生成補充（可選）
    5. 過濾和去重
    """
    
    # 正則模式
    HASHTAG_PATTERN = re.compile(r'#(\w+)', re.UNICODE)
    PROPER_NOUN_PATTERN = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b')
    CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]+')
    
    def __init__(
        self,
        category: Optional[str] = None,
        max_hashtags: int = 15,
        use_ai: bool = False,
        ai_service: Any = None
    ):
        """
        初始化提取器
        
        Args:
            category: 文章分類（用於選擇品牌列表）
            max_hashtags: 最大 hashtag 數量
            use_ai: 是否使用 AI 生成
            ai_service: AI 服務實例
        """
        self.category = category
        self.max_hashtags = max_hashtags
        self.use_ai = use_ai
        self.ai_service = ai_service
        
        # 根據分類選擇品牌列表
        if category:
            self.brands = get_brands_for_category(category)
        else:
            self.brands = ALL_BRANDS
    
    def extract(
        self,
        title: str,
        content: Optional[str] = None,
        existing_keywords: Optional[List[str]] = None
    ) -> List[str]:
        """
        提取 Hashtags
        
        Args:
            title: 文章標題
            content: 文章內容（可選）
            existing_keywords: 已有的關鍵字（可選）
            
        Returns:
            Hashtag 列表
        """
        hashtags: Set[str] = set()
        
        # 1. 添加已有的關鍵字
        if existing_keywords:
            for kw in existing_keywords:
                if self._is_valid_hashtag(kw):
                    hashtags.add(self._normalize(kw))
        
        # 2. 提取已有的 #hashtag
        existing = self._extract_existing_hashtags(title)
        hashtags.update(existing)
        if content:
            existing = self._extract_existing_hashtags(content)
            hashtags.update(existing)
        
        # 3. 提取專有名詞
        proper_nouns = self._extract_proper_nouns(title)
        hashtags.update(proper_nouns)
        if content:
            proper_nouns = self._extract_proper_nouns(content[:1000])  # 只處理前 1000 字
            hashtags.update(proper_nouns)
        
        # 4. 匹配品牌名稱
        brands = self._extract_brands(title)
        hashtags.update(brands)
        if content:
            brands = self._extract_brands(content[:1000])
            hashtags.update(brands)
        
        # 5. AI 生成補充（如果啟用且數量不足）
        if self.use_ai and len(hashtags) < 5:
            ai_hashtags = self._extract_by_ai(title, content)
            hashtags.update(ai_hashtags)
        
        # 6. 過濾和去重
        filtered = self._filter_and_dedupe(list(hashtags))
        
        # 7. 限制數量
        return filtered[:self.max_hashtags]
    
    def _extract_existing_hashtags(self, text: str) -> Set[str]:
        """
        提取已有的 #hashtag
        """
        if not text:
            return set()
        
        matches = self.HASHTAG_PATTERN.findall(text)
        return {self._normalize(m) for m in matches if self._is_valid_hashtag(m)}
    
    def _extract_proper_nouns(self, text: str) -> Set[str]:
        """
        提取專有名詞（大寫開頭的詞）
        """
        if not text:
            return set()
        
        hashtags = set()
        
        # 英文專有名詞
        matches = self.PROPER_NOUN_PATTERN.findall(text)
        for match in matches:
            # 移除空格，合併為單一 hashtag
            normalized = match.replace(" ", "")
            if self._is_valid_hashtag(normalized):
                hashtags.add(normalized)
        
        # 中文詞彙（簡單提取）
        chinese_matches = self.CHINESE_PATTERN.findall(text)
        for match in chinese_matches:
            if len(match) >= 2 and len(match) <= 10:
                hashtags.add(match)
        
        return hashtags
    
    def _extract_brands(self, text: str) -> Set[str]:
        """
        匹配品牌名稱
        """
        if not text:
            return set()
        
        hashtags = set()
        text_lower = text.lower()
        
        for brand in self.brands:
            # 不區分大小寫匹配
            if brand.lower() in text_lower:
                # 使用原始大小寫
                hashtags.add(brand.replace(" ", ""))
        
        return hashtags
    
    def _extract_by_ai(
        self,
        title: str,
        content: Optional[str] = None
    ) -> Set[str]:
        """
        使用 AI 生成 Hashtags
        """
        if not self.ai_service:
            return set()
        
        try:
            # 構建提示
            text = title
            if content:
                text += "\n\n" + content[:500]
            
            prompt = f"""
            請為以下文章提取 5-10 個適合的 hashtags。
            要求：
            1. 提取品牌名稱、人名、地點
            2. 提取主題關鍵字
            3. 不要包含太泛泛的詞（如 "fashion", "news"）
            4. 每個 hashtag 用逗號分隔
            
            文章：
            {text}
            
            Hashtags：
            """
            
            # 調用 AI 服務
            response = self.ai_service.generate(prompt)
            
            # 解析回應
            if response:
                tags = [t.strip().replace("#", "") for t in response.split(",")]
                return {self._normalize(t) for t in tags if self._is_valid_hashtag(t)}
                
        except Exception as e:
            logger.warning(f"AI hashtag extraction failed: {e}")
        
        return set()
    
    def _filter_and_dedupe(self, hashtags: List[str]) -> List[str]:
        """
        過濾和去重
        """
        filtered = []
        seen_lower = set()
        
        for tag in hashtags:
            tag_lower = tag.lower()
            
            # 跳過已見過的（不區分大小寫）
            if tag_lower in seen_lower:
                continue
            
            # 跳過停用詞
            if is_stop_word(tag):
                continue
            
            # 跳過太短或太長的
            if len(tag) < 2 or len(tag) > 30:
                continue
            
            seen_lower.add(tag_lower)
            filtered.append(tag)
        
        # 按長度排序（較長的通常更具體）
        filtered.sort(key=lambda x: (-len(x), x))
        
        return filtered
    
    def _is_valid_hashtag(self, text: str) -> bool:
        """
        檢查是否為有效的 hashtag
        """
        if not text:
            return False
        
        # 長度檢查
        if len(text) < 2 or len(text) > 30:
            return False
        
        # 停用詞檢查
        if is_stop_word(text):
            return False
        
        # 純數字檢查
        if text.isdigit():
            return False
        
        return True
    
    def _normalize(self, text: str) -> str:
        """
        正規化 hashtag
        """
        # 移除 # 符號
        text = text.replace("#", "")
        
        # 移除特殊字符（保留字母、數字、中文）
        text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        
        return text


# 便捷函數
def extract_hashtags(
    title: str,
    content: Optional[str] = None,
    category: Optional[str] = None,
    max_hashtags: int = 15
) -> List[str]:
    """
    便捷函數：提取 hashtags
    
    Args:
        title: 文章標題
        content: 文章內容
        category: 分類
        max_hashtags: 最大數量
        
    Returns:
        Hashtag 列表
    """
    extractor = HashtagExtractor(
        category=category,
        max_hashtags=max_hashtags,
        use_ai=False
    )
    return extractor.extract(title, content)


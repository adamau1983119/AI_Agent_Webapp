"""
內容去重服務
用於檢測和過濾重複的 RSS 內容，降低重複率

功能：
1. 精確匹配（MD5 哈希）
2. 模糊匹配（相似度檢測）
3. 快取管理（避免重複計算）
"""
import hashlib
import logging
import re
from typing import List, Set, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from collections import deque

logger = logging.getLogger(__name__)


class ContentDeduplicator:
    """
    內容去重器
    
    使用兩層檢測：
    1. 精確匹配：MD5 哈希比對（O(1) 查詢）
    2. 模糊匹配：字串相似度（O(n) 但只檢查最近 N 條）
    """
    
    def __init__(
        self,
        db=None,
        similarity_threshold: float = 0.85,
        cache_size: int = 5000,
        recent_check_limit: int = 500
    ):
        """
        初始化去重器
        
        Args:
            db: MongoDB 資料庫實例（可選，用於持久化）
            similarity_threshold: 相似度門檻（0-1），預設 0.85
            cache_size: 哈希快取大小
            recent_check_limit: 模糊匹配只檢查最近 N 條
        """
        self.db = db
        self.similarity_threshold = similarity_threshold
        self.cache_size = cache_size
        self.recent_check_limit = recent_check_limit
        
        # 快取
        self.title_hashes: Set[str] = set()
        self.recent_titles: deque = deque(maxlen=cache_size)
        self.stats = {
            "checked": 0,
            "exact_duplicates": 0,
            "similar_duplicates": 0,
            "unique": 0
        }
        
        self._initialized = False
    
    async def initialize(self):
        """
        從資料庫載入最近的標題到快取
        """
        if self._initialized:
            return
        
        if self.db is not None:
            try:
                cutoff = datetime.utcnow() - timedelta(hours=48)
                
                # 載入最近 48 小時的標題
                cursor = self.db.topics.find(
                    {"created_at": {"$gte": cutoff}},
                    {"title": 1, "_id": 0}
                ).sort("created_at", -1).limit(self.cache_size)
                
                async for doc in cursor:
                    title = doc.get("title", "")
                    if title:
                        self.title_hashes.add(self._hash_title(title))
                        self.recent_titles.append(title)
                
                logger.info(f"去重快取初始化完成: {len(self.title_hashes)} 個標題")
                
            except Exception as e:
                logger.warning(f"初始化去重快取失敗: {e}")
        
        self._initialized = True
    
    def _normalize_title(self, title: str) -> str:
        """
        標準化標題（移除標點、空格、轉小寫）
        """
        # 移除特殊字符
        normalized = re.sub(r'[^\w\s\u4e00-\u9fff]', '', title)
        # 移除多餘空格
        normalized = ' '.join(normalized.split())
        # 轉小寫（英文）
        normalized = normalized.lower()
        return normalized
    
    def _hash_title(self, title: str) -> str:
        """
        生成標題的 MD5 哈希
        """
        normalized = self._normalize_title(title)
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _compute_similarity(self, title1: str, title2: str) -> float:
        """
        計算兩個標題的相似度（0-1）
        
        使用 SequenceMatcher，對中英文都有效
        """
        norm1 = self._normalize_title(title1)
        norm2 = self._normalize_title(title2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    async def is_duplicate(
        self,
        title: str,
        check_similar: bool = True
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        檢查標題是否重複
        
        Args:
            title: 要檢查的標題
            check_similar: 是否進行模糊匹配（較慢）
            
        Returns:
            (is_duplicate, reason, similar_title)
            - is_duplicate: 是否重複
            - reason: 重複原因（"exact_match" 或 "similar_match"）
            - similar_title: 相似的標題（僅模糊匹配時）
        """
        if not self._initialized:
            await self.initialize()
        
        self.stats["checked"] += 1
        
        # 空標題直接跳過
        if not title or len(title.strip()) < 5:
            return False, None, None
        
        # Step 1: 精確匹配（哈希）
        title_hash = self._hash_title(title)
        if title_hash in self.title_hashes:
            self.stats["exact_duplicates"] += 1
            logger.debug(f"精確重複: {title[:30]}...")
            return True, "exact_match", None
        
        # Step 2: 模糊匹配（相似度）
        if check_similar:
            # 只檢查最近 N 條，避免效能問題
            recent_to_check = list(self.recent_titles)[-self.recent_check_limit:]
            
            for existing_title in recent_to_check:
                similarity = self._compute_similarity(title, existing_title)
                
                if similarity >= self.similarity_threshold:
                    self.stats["similar_duplicates"] += 1
                    logger.debug(
                        f"相似重複 ({similarity:.0%}): "
                        f"{title[:25]}... ≈ {existing_title[:25]}..."
                    )
                    return True, f"similar_match_{similarity:.0%}", existing_title
        
        # 不重複，加入快取
        self.title_hashes.add(title_hash)
        self.recent_titles.append(title)
        self.stats["unique"] += 1
        
        return False, None, None
    
    async def batch_check(
        self,
        titles: List[str],
        check_similar: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批次檢查多個標題
        
        Args:
            titles: 標題列表
            check_similar: 是否進行模糊匹配
            
        Returns:
            [{
                "title": str,
                "is_duplicate": bool,
                "reason": str,
                "similar_to": str
            }, ...]
        """
        results = []
        
        for title in titles:
            is_dup, reason, similar = await self.is_duplicate(title, check_similar)
            results.append({
                "title": title,
                "is_duplicate": is_dup,
                "reason": reason,
                "similar_to": similar
            })
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        獲取去重統計
        """
        total = self.stats["checked"]
        duplicates = self.stats["exact_duplicates"] + self.stats["similar_duplicates"]
        
        return {
            "total_checked": total,
            "exact_duplicates": self.stats["exact_duplicates"],
            "similar_duplicates": self.stats["similar_duplicates"],
            "unique": self.stats["unique"],
            "duplicate_rate": f"{(duplicates / total * 100):.1f}%" if total > 0 else "0%",
            "cache_size": len(self.title_hashes),
            "recent_titles_count": len(self.recent_titles),
            "similarity_threshold": self.similarity_threshold
        }
    
    def reset_stats(self):
        """重置統計"""
        self.stats = {
            "checked": 0,
            "exact_duplicates": 0,
            "similar_duplicates": 0,
            "unique": 0
        }
    
    def clear_cache(self):
        """清空快取"""
        self.title_hashes.clear()
        self.recent_titles.clear()
        self._initialized = False
        logger.info("去重快取已清空")


class ContentDeduplicationService:
    """
    內容去重服務（整合到收集流程）
    """
    
    def __init__(self, db=None):
        self.db = db
        self.deduplicator = ContentDeduplicator(db=db)
    
    async def filter_duplicates(
        self,
        topics: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        過濾重複的主題
        
        Args:
            topics: 主題列表
            
        Returns:
            (unique_topics, duplicate_topics)
        """
        await self.deduplicator.initialize()
        
        unique = []
        duplicates = []
        
        for topic in topics:
            title = topic.get("title", "")
            is_dup, reason, similar = await self.deduplicator.is_duplicate(title)
            
            if is_dup:
                topic["_duplicate_reason"] = reason
                topic["_similar_to"] = similar
                duplicates.append(topic)
            else:
                unique.append(topic)
        
        # 記錄統計
        logger.info(
            f"去重完成: {len(unique)} 唯一, {len(duplicates)} 重複 "
            f"(重複率: {len(duplicates) / len(topics) * 100:.1f}%)"
        )
        
        return unique, duplicates
    
    async def check_before_save(
        self,
        title: str,
        category: str = None
    ) -> bool:
        """
        保存前檢查是否重複
        
        Args:
            title: 標題
            category: 類別（可選，用於分類檢查）
            
        Returns:
            True 如果可以保存（不重複），False 如果應跳過（重複）
        """
        is_dup, reason, _ = await self.deduplicator.is_duplicate(title)
        return not is_dup
    
    def get_stats(self) -> Dict[str, Any]:
        """獲取統計"""
        return self.deduplicator.get_stats()


# 全局實例（方便在收集器中使用）
_dedup_service: Optional[ContentDeduplicationService] = None


def get_deduplication_service(db=None) -> ContentDeduplicationService:
    """
    獲取去重服務單例
    """
    global _dedup_service
    
    if _dedup_service is None:
        _dedup_service = ContentDeduplicationService(db=db)
    
    return _dedup_service


async def reset_deduplication_service():
    """
    重置去重服務（用於測試或手動清理）
    """
    global _dedup_service
    
    if _dedup_service is not None:
        _dedup_service.deduplicator.clear_cache()
        _dedup_service = None


"""
Redis 快取服務
提供搜尋結果快取和熱門查詢統計功能
"""
from typing import Optional, Dict, Any, List
import json
import hashlib
import logging
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from app.config_module import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis 快取服務"""
    
    def __init__(self):
        self.redis_client: Optional[Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.enabled = settings.REDIS_ENABLED
    
    async def connect(self):
        """連接到 Redis"""
        if not self.enabled:
            logger.info("Redis 快取已禁用")
            return
        
        try:
            # 建立連接池
            self.pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=settings.REDIS_DECODE_RESPONSES
            )
            
            # 建立 Redis 客戶端
            self.redis_client = Redis(connection_pool=self.pool)
            
            # 測試連接
            await self.redis_client.ping()
            logger.info(f"✅ Redis 連接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.warning(f"Redis 連接失敗: {e}，將跳過快取功能")
            self.enabled = False
            self.redis_client = None
    
    async def disconnect(self):
        """斷開 Redis 連接"""
        if self.redis_client:
            await self.redis_client.close()
        if self.pool:
            await self.pool.disconnect()
    
    def _build_cache_key(
        self,
        query: str,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        role: str = "guest"
    ) -> str:
        """
        建立快取 key
        
        Args:
            query: 搜尋關鍵字
            category: 分類
            page: 頁碼
            limit: 每頁數量
            role: 用戶角色
            
        Returns:
            快取 key
        """
        # 建立唯一標識符
        key_parts = [query, category or "", str(page), str(limit), role]
        key_string = ":".join(key_parts)
        
        # 使用 MD5 hash 縮短 key 長度
        query_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"search:{query_hash}:{category or 'all'}:{page}:{limit}:{role}"
    
    async def get_cache(
        self,
        query: str,
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        role: str = "guest"
    ) -> Optional[Dict[str, Any]]:
        """
        從快取獲取搜尋結果
        
        Args:
            query: 搜尋關鍵字
            category: 分類
            page: 頁碼
            limit: 每頁數量
            role: 用戶角色
            
        Returns:
            快取結果，如果不存在則返回 None
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._build_cache_key(query, category, page, limit, role)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"快取命中: {cache_key}")
                return json.loads(cached_data)
            else:
                logger.debug(f"快取未命中: {cache_key}")
                return None
        except Exception as e:
            logger.warning(f"讀取快取失敗: {e}，繼續查詢資料庫")
            return None
    
    async def set_cache(
        self,
        query: str,
        result: Dict[str, Any],
        category: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
        role: str = "guest",
        ttl: int = 300  # 5 分鐘
    ):
        """
        將搜尋結果寫入快取
        
        Args:
            query: 搜尋關鍵字
            result: 搜尋結果
            category: 分類
            page: 頁碼
            limit: 每頁數量
            role: 用戶角色
            ttl: 快取過期時間（秒）
        """
        if not self.enabled or not self.redis_client:
            return
        
        try:
            cache_key = self._build_cache_key(query, category, page, limit, role)
            await self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result, ensure_ascii=False, default=str)
            )
            logger.debug(f"快取寫入成功: {cache_key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"寫入快取失敗: {e}")
    
    async def increment_hot_query(self, query: str, increment: int = 1):
        """
        增加熱門查詢統計
        
        Args:
            query: 搜尋關鍵字
            increment: 增加數量
        """
        if not self.enabled or not self.redis_client:
            return
        
        try:
            hot_queries_key = "hot:queries"
            await self.redis_client.zincrby(hot_queries_key, increment, query)
            
            # 設定 TTL（1 小時）
            await self.redis_client.expire(hot_queries_key, 3600)
        except Exception as e:
            logger.warning(f"更新熱門查詢統計失敗: {e}")
    
    async def get_hot_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        獲取熱門查詢列表
        
        Args:
            limit: 返回數量
            
        Returns:
            熱門查詢列表，格式：[{"query": "...", "count": 123}, ...]
        """
        if not self.enabled or not self.redis_client:
            return []
        
        try:
            hot_queries_key = "hot:queries"
            # 獲取分數最高的查詢（降序）
            queries = await self.redis_client.zrevrange(
                hot_queries_key,
                0,
                limit - 1,
                withscores=True
            )
            
            result = []
            for query, score in queries:
                result.append({
                    "query": query,
                    "count": int(score)
                })
            
            return result
        except Exception as e:
            logger.warning(f"獲取熱門查詢失敗: {e}")
            return []
    
    async def clear_cache(self, pattern: str = "search:*") -> int:
        """
        清除快取（管理員功能）
        
        Args:
            pattern: 快取 key 模式（預設清除所有搜尋快取）
            
        Returns:
            清除的快取數量
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            deleted_count = 0
            cursor = 0
            
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor,
                    match=pattern,
                    count=100
                )
                
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                    deleted_count += deleted
                
                if cursor == 0:
                    break
            
            logger.info(f"清除快取完成: 刪除 {deleted_count} 個 key（模式: {pattern}）")
            return deleted_count
        except Exception as e:
            logger.error(f"清除快取失敗: {e}")
            return 0
    
    async def invalidate_topic_cache(self, topic_id: Optional[str] = None):
        """
        使主題相關的快取失效（當主題新增/更新時調用）
        
        Args:
            topic_id: 主題 ID（如果提供，只清除相關快取；否則清除所有搜尋快取）
        """
        if topic_id:
            # 清除特定主題相關的快取（可以根據實際需求實作更精細的清除邏輯）
            await self.clear_cache("search:*")
        else:
            # 清除所有搜尋快取
            await self.clear_cache("search:*")


# 全域快取服務實例
cache_service = CacheService()


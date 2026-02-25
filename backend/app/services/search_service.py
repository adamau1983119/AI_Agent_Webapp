"""
搜尋服務
提供主題搜尋功能，支援中文全文搜尋、權限控制和結果過濾
整合 Redis 快取和 Elasticsearch
"""
from typing import Optional, List, Dict, Any, Literal
from enum import Enum
import re
import logging
from app.models.topic import Category
from app.services.repositories.topic_repository import TopicRepository
from app.services.cache_service import cache_service
from app.services.elasticsearch_service import es_service

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """用戶角色"""
    GUEST = "guest"
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


def sanitize_query(query: str, error_key_prefix: str = "topic") -> str:
    """
    清理和驗證查詢字串
    
    Args:
        query: 原始查詢字串
        error_key_prefix: 錯誤訊息鍵前綴（用於 i18n）
    
    Returns:
        清理後的查詢字串
    
    Raises:
        ValueError: 如果查詢字串無效（錯誤訊息為 i18n 鍵）
    """
    if not query or not isinstance(query, str):
        raise ValueError(f"{error_key_prefix}.invalid_query:error=Query string cannot be empty")
    
    # 移除前後空白
    query = query.strip()
    
    # 驗證長度
    if len(query) < 2:
        raise ValueError(f"{error_key_prefix}.query_too_short")
    if len(query) > 100:
        raise ValueError(f"{error_key_prefix}.query_too_long")
    
    # 移除危險字符（MongoDB 正則表達式特殊字符需要轉義，但這裡我們先清理明顯的危險字符）
    # 保留中文字符、英文字母、數字、空格和常見標點符號
    # 移除可能導致注入的字符
    dangerous_chars = ['$', '{', '}', '\\']
    for char in dangerous_chars:
        query = query.replace(char, '')
    
    return query


def filter_results_by_role(
    results: List[Dict[str, Any]], 
    role: UserRole = UserRole.GUEST
) -> List[Dict[str, Any]]:
    """
    根據用戶角色過濾結果欄位
    
    Args:
        results: 原始結果列表
        role: 用戶角色
        
    Returns:
        過濾後的結果列表
    """
    filtered_results = []
    
    for result in results:
        filtered_result = {}
        
        if role == UserRole.GUEST:
            # 訪客：只能看標題和摘要
            filtered_result["id"] = result.get("id")
            filtered_result["title"] = result.get("title")
            filtered_result["summary"] = result.get("summary") or result.get("description")
            filtered_result["category"] = result.get("category")
        
        elif role == UserRole.USER:
            # 普通用戶：標題、摘要、來源 URL、預覽圖片
            filtered_result["id"] = result.get("id")
            filtered_result["title"] = result.get("title")
            filtered_result["summary"] = result.get("summary") or result.get("description")
            filtered_result["category"] = result.get("category")
            
            # 提取來源 URL
            if "source" in result:
                if isinstance(result["source"], dict):
                    filtered_result["source_url"] = result["source"].get("url")
                elif isinstance(result["source"], str):
                    filtered_result["source_url"] = result["source"]
            
            # 提取預覽圖片
            if "preview_images" in result and result["preview_images"]:
                filtered_result["preview_image"] = result["preview_images"][0] if result["preview_images"] else None
            elif "images" in result and result["images"]:
                if isinstance(result["images"], dict) and "preview" in result["images"]:
                    preview = result["images"]["preview"]
                    filtered_result["preview_image"] = preview[0] if preview else None
        
        elif role == UserRole.PREMIUM:
            # 付費用戶：所有欄位（除了 metadata）
            filtered_result = {k: v for k, v in result.items() if k != "metadata"}
        
        elif role == UserRole.ADMIN:
            # 管理員：所有欄位（包括 metadata）
            filtered_result = result.copy()
        
        filtered_results.append(filtered_result)
    
    return filtered_results


class SearchService:
    """搜尋服務"""
    
    def __init__(self, db=None):
        self.topic_repo = TopicRepository(db=db)
    
    async def search_topics(
        self,
        query: str,
        category: Optional[Category] = None,
        page: int = 1,
        limit: int = 10,
        role: UserRole = UserRole.GUEST
    ) -> Dict[str, Any]:
        """
        搜尋主題（整合 Redis 快取和 Elasticsearch）
        
        Args:
            query: 搜尋關鍵字（必填，2-100字元）
            category: 分類篩選（可選）
            page: 頁碼（1-100，預設1）
            limit: 每頁數量（1-50，預設10）
            role: 用戶角色（預設guest）
            
        Returns:
            搜尋結果字典，包含：
            - source: 資料來源（"es"/"db"/"cache"）
            - results: 結果列表
            - pagination: 分頁資訊
        """
        # 清理和驗證查詢字串
        try:
            query = sanitize_query(query, "topic")
        except ValueError as e:
            # 如果錯誤訊息是 i18n 鍵，直接傳遞；否則包裝為通用錯誤
            error_msg = str(e)
            if not error_msg.startswith("topic."):
                raise ValueError(f"topic.invalid_query:error={error_msg}")
            raise
        
        # 驗證分頁參數
        if page < 1 or page > 100:
            raise ValueError("topic.page_invalid")
        if limit < 1 or limit > 50:
            raise ValueError("topic.limit_invalid")
        
        category_str = category.value if category and hasattr(category, 'value') else (category if category else None)
        role_str = role.value if hasattr(role, 'value') else role
        
        # 1. 檢查 Redis 快取
        cached_result = await cache_service.get_cache(
            query=query,
            category=category_str,
            page=page,
            limit=limit,
            role=role_str
        )
        
        if cached_result:
            logger.info(f"快取命中: '{query}' (role: {role_str})")
            # 更新熱門查詢統計
            await cache_service.increment_hot_query(query)
            return cached_result
        
        # 2. 快取未命中，執行搜尋
        source = "db"
        topics = []
        total = 0
        
        # 2.1 嘗試使用 Elasticsearch（如果啟用）
        if es_service.enabled and es_service.es_client:
            try:
                es_result = await es_service.search(
                    query=query,
                    category=category_str,
                    page=page,
                    limit=limit
                )
                topics = es_result["results"]
                total = es_result["total"]
                source = "es"
                logger.info(f"Elasticsearch 搜尋成功: '{query}', 找到 {total} 筆結果")
            except Exception as e:
                logger.warning(f"Elasticsearch 搜尋失敗: {e}，回退到 MongoDB")
                # 回退到 MongoDB
                source = "db"
        
        # 2.2 如果 Elasticsearch 未啟用或失敗，使用 MongoDB
        if source == "db" or not topics:
            try:
                filter_query: Dict[str, Any] = {}
                
                # 分類篩選
                if category:
                    filter_query["category"] = category_str
                
                # 只搜尋已發布的主題（排除已刪除的）
                filter_query["status"] = {"$ne": "deleted"}
                
                # 中文全文搜尋：搜尋標題、摘要、內容
                escaped_query = re.escape(query)
                search_pattern = {
                    "$or": [
                        {"title": {"$regex": escaped_query, "$options": "i"}},
                        {"summary": {"$regex": escaped_query, "$options": "i"}},
                        {"description": {"$regex": escaped_query, "$options": "i"}},
                        {"content": {"$regex": escaped_query, "$options": "i"}},
                    ]
                }
                filter_query.update(search_pattern)
                
                # 計算跳過數量
                skip = (page - 1) * limit
                
                # 建立排序條件
                sort_list = [("generated_at", -1)]
                
                # 執行查詢
                topics = await self.topic_repo.find_many(
                    filter=filter_query,
                    skip=skip,
                    limit=limit,
                    sort=sort_list
                )
                total = await self.topic_repo.count(filter=filter_query)
                
                logger.info(f"MongoDB 搜尋成功: '{query}', 找到 {total} 筆結果")
            except Exception as e:
                logger.error(f"MongoDB 搜尋失敗: {e}", exc_info=True)
                # 如果資料庫連接失敗，返回空結果而不是拋出異常
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    logger.warning(f"資料庫連接問題，返回空搜尋結果: {e}")
                    topics = []
                    total = 0
                else:
                    # 將錯誤訊息包裝為 i18n 鍵
                    raise Exception(f"topic.search_error:error={str(e)}")
        
        # 3. 根據角色過濾結果
        filtered_topics = filter_results_by_role(topics, role)
        
        # 4. 計算總頁數
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        
        # 5. 建立結果
        result = {
            "source": source,
            "results": filtered_topics,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": total_pages
            }
        }
        
        # 6. 寫入快取（TTL: 5分鐘）
        await cache_service.set_cache(
            query=query,
            result=result,
            category=category_str,
            page=page,
            limit=limit,
            role=role_str,
            ttl=300
        )
        
        # 7. 更新熱門查詢統計
        await cache_service.increment_hot_query(query)
        
        return result
    
    async def check_url_exists(self, url: str) -> Dict[str, Any]:
        """
        檢查原文 URL 是否已收錄
        
        Args:
            url: 原文 URL
            
        Returns:
            包含 exists 和 topic（如果存在）的字典
        """
        if not url or not isinstance(url, str):
            return {"exists": False, "topic": None}
        
        # 清理 URL
        url = url.strip()
        if not url:
            return {"exists": False, "topic": None}
        
        # 搜尋 source.url 欄位（支援多種資料結構）
        filter_query = {
            "$or": [
                {"source.url": url},
                {"sources.url": url},
                {"sources": {"$elemMatch": {"url": url}}},
                {"source": url}  # 如果 source 是字符串
            ]
        }
        
        try:
            topic = await self.topic_repo.find_one(filter=filter_query)
            if topic:
                # 提取來源 URL
                source_url = url
                if isinstance(topic.get("source"), dict):
                    source_url = topic["source"].get("url", url)
                elif isinstance(topic.get("source"), str):
                    source_url = topic.get("source", url)
                
                # 提取預覽圖片
                preview_image = None
                if topic.get("preview_images") and isinstance(topic["preview_images"], list):
                    preview_image = topic["preview_images"][0] if topic["preview_images"] else None
                elif topic.get("images") and isinstance(topic["images"], dict):
                    if topic["images"].get("preview") and isinstance(topic["images"]["preview"], list):
                        preview_image = topic["images"]["preview"][0] if topic["images"]["preview"] else None
                
                # 只返回基本資訊
                return {
                    "exists": True,
                    "topic": {
                        "id": topic.get("id"),
                        "title": topic.get("title"),
                        "summary": topic.get("summary") or topic.get("description"),
                        "source_url": source_url,
                        "preview_image": preview_image
                    }
                }
            else:
                return {"exists": False, "topic": None}
        except Exception as e:
            logger.error(f"檢查 URL 是否存在時發生錯誤: {e}")
            return {"exists": False, "topic": None}


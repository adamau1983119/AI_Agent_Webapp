"""
Google Custom Search 圖片服務（需要 API Key）
使用 Google Custom Search API 搜尋圖片
"""
import httpx
from typing import List, Dict, Any
from app.services.images.base import ImageServiceBase
from app.services.images.exceptions import ImageSearchError, ErrorCode
from app.config import settings
from app.models.image import ImageSource
import logging

logger = logging.getLogger(__name__)


class GoogleCustomSearchService(ImageServiceBase):
    """Google Custom Search 圖片服務（需要 API Key）"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_API_KEY', '')
        self.search_engine_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', '')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        # 初始化時驗證配置
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search API Key 或 Search Engine ID 未設定")
        else:
            logger.info("✅ Google Custom Search 服務已初始化")
    
    async def search_images(
        self,
        keywords: str,
        page: int = 1,
        limit: int = 20,
        trace_id: str = ""
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片（使用 Google Custom Search API）
        
        Args:
            keywords: 搜尋關鍵字
            page: 頁碼（Google 限制每頁最多 10 張）
            limit: 每頁數量（最多 10）
            trace_id: 追蹤 ID
            
        Returns:
            圖片列表
            
        Raises:
            ImageSearchError: 當搜尋失敗時
        """
        # 驗證配置
        if not self.api_key or not self.search_engine_id:
            raise ImageSearchError(
                ErrorCode.INVALID_CONFIG,
                "google_custom_search",
                "GOOGLE_API_KEY 或 GOOGLE_SEARCH_ENGINE_ID 未設定"
            )
        
        limit = min(limit, 10)  # Google 限制每頁最多 10 張
        
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": keywords,
            "searchType": "image",  # 關鍵：必須指定為圖片搜尋
            "num": limit,
            "start": (page - 1) * limit + 1,  # Google 的 start 從 1 開始
            "safe": "active",  # 安全搜尋
        }
        
        # 記錄請求（隱藏 API Key）
        safe_params = {k: v for k, v in params.items() if k != "key"}
        logger.info(f"[{trace_id}] Google Custom Search 請求: {safe_params}")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                
                # 記錄響應狀態
                logger.info(f"[{trace_id}] Google Custom Search 響應: status={response.status_code}")
                
                # 處理不同狀態碼
                if response.status_code == 429:
                    logger.warning(f"[{trace_id}] Google Custom Search API 配額已用完")
                    raise ImageSearchError(
                        ErrorCode.RATE_LIMIT,
                        "google_custom_search",
                        "API 配額已用完",
                        {"status_code": 429}
                    )
                
                if response.status_code == 403:
                    logger.error(f"[{trace_id}] Google Custom Search API Key 無效或權限不足")
                    raise ImageSearchError(
                        ErrorCode.INVALID_CONFIG_OR_PERMISSION,
                        "google_custom_search",
                        "API Key 無效或權限不足",
                        {"status_code": 403}
                    )
                
                if response.status_code >= 500:
                    logger.error(f"[{trace_id}] Google Custom Search 上游服務錯誤: {response.status_code}")
                    raise ImageSearchError(
                        ErrorCode.UPSTREAM_ERROR,
                        "google_custom_search",
                        f"上游服務錯誤: {response.status_code}",
                        {"status_code": response.status_code}
                    )
                
                if response.status_code != 200:
                    logger.warning(f"[{trace_id}] Google Custom Search HTTP 錯誤: {response.status_code}")
                    raise ImageSearchError(
                        ErrorCode.HTTP_ERROR,
                        "google_custom_search",
                        f"HTTP 錯誤: {response.status_code}",
                        {"status_code": response.status_code}
                    )
                
                response.raise_for_status()
                data = response.json()
                
                # 記錄搜尋資訊
                search_info = data.get("searchInformation", {})
                total_results = search_info.get("totalResults", "0")
                logger.info(f"[{trace_id}] Google Custom Search 結果: totalResults={total_results}, items={len(data.get('items', []))}")
                
                items = data.get("items", [])
                
                # 轉換為統一格式，過濾非圖片結果
                result = []
                for item in items:
                    link = item.get("link", "")
                    mime = item.get("mime", "")
                    
                    # 只保留有效的連結
                    if not link:
                        continue
                    
                    # 如果 mime 存在且不是圖片類型，跳過
                    # 但如果 mime 為空，我們仍然保留（因為 searchType=image 應該確保都是圖片）
                    if mime and not mime.startswith("image/"):
                        logger.debug(f"[{trace_id}] 跳過非圖片結果: {link} (mime={mime})")
                        continue
                    
                    # 檢查連結是否看起來像圖片 URL
                    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
                    is_image_url = any(link.lower().endswith(ext) for ext in image_extensions)
                    
                    # 如果 mime 為空且 URL 也不像圖片，跳過
                    if not mime and not is_image_url:
                        # 但對於 Google Custom Search，如果 searchType=image，我們應該信任結果
                        # 所以這裡我們仍然保留
                        pass
                    
                    result.append({
                        "id": f"google_{hash(link) % 1000000}",
                        "url": link,
                        "thumbnail_url": item.get("image", {}).get("thumbnailLink", link),
                        "width": item.get("image", {}).get("width", 0),
                        "height": item.get("image", {}).get("height", 0),
                        "title": item.get("title", ""),
                        "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
                        "photographer": item.get("displayLink", ""),
                        "photographer_url": item.get("image", {}).get("contextLink", ""),
                        "license": "Unknown",  # Google 不提供授權資訊
                        "keywords": [keywords],
                    })
                
                if not result:
                    logger.warning(f"[{trace_id}] Google Custom Search 過濾後無圖片結果: 原始 items={len(items)}, totalResults={total_results}")
                    # 不要拋出異常，讓 ImageServiceManager 嘗試下一個服務
                    # 但記錄詳細資訊以便診斷
                    raise ImageSearchError(
                        ErrorCode.NO_RESULTS,
                        "google_custom_search",
                        f"查詢無圖片結果（原始結果: {len(items)} 個，總結果數: {total_results}）",
                        {"total_results": total_results, "items_count": len(items)}
                    )
                
                logger.info(f"[{trace_id}] ✅ Google Custom Search 成功: 返回 {len(result)} 張圖片")
                return result
                
        except ImageSearchError:
            raise
        except httpx.TimeoutException:
            logger.error(f"[{trace_id}] Google Custom Search 請求超時")
            raise ImageSearchError(
                ErrorCode.TIMEOUT_ERROR,
                "google_custom_search",
                "請求超時",
                {"timeout": 10.0}
            )
        except Exception as e:
            logger.exception(f"[{trace_id}] Google Custom Search 發生未處理異常")
            raise ImageSearchError(
                ErrorCode.UNKNOWN_ERROR,
                "google_custom_search",
                f"未知錯誤: {str(e)}",
                {"exception_type": type(e).__name__}
            )
    
    async def get_image_info(self, image_id: str) -> Dict[str, Any]:
        """
        根據 ID 獲取圖片詳情
        
        Args:
            image_id: 圖片 ID（格式：google_xxx）
            
        Returns:
            圖片詳情
        """
        # Google Custom Search 不支援根據 ID 獲取圖片
        # 這裡返回一個基本結構
        return {
            "id": image_id,
            "url": "",
            "source": ImageSource.GOOGLE_CUSTOM_SEARCH.value,
            "license": "Unknown",
        }


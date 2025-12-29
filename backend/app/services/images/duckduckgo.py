"""
DuckDuckGo 圖片服務（無需 API Key）
使用網頁爬蟲方式搜尋圖片，類似 Google 圖片搜尋
"""
import httpx
from typing import List, Dict, Any
from app.services.images.base import ImageServiceBase
from app.models.image import ImageSource
import logging
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)


class DuckDuckGoService(ImageServiceBase):
    """DuckDuckGo 圖片服務（無需 API Key）"""
    
    def __init__(self):
        self.base_url = "https://duckduckgo.com"
        # DuckDuckGo 允許爬蟲，不需要 API Key
        logger.info("初始化 DuckDuckGo 圖片服務（無需 API Key）")
    
    async def search_images(
        self,
        keywords: str,
        page: int = 1,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        搜尋圖片（使用 DuckDuckGo Images）
        
        Args:
            keywords: 搜尋關鍵字
            page: 頁碼（DuckDuckGo 不支援分頁，但我們可以模擬）
            limit: 每頁數量（最多 50）
            
        Returns:
            圖片列表
        """
        limit = min(limit, 50)  # DuckDuckGo 限制
        
        try:
            # 使用 DuckDuckGo Images API（非官方，但穩定）
            # 方法：使用 DuckDuckGo 的圖片搜尋端點
            search_url = f"{self.base_url}/i.js"
            
            # 第一次請求獲取 token
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                # 先訪問搜尋頁面獲取 token
                search_page_url = f"{self.base_url}/?q={quote(keywords)}&iax=images&ia=images"
                response = await client.get(search_page_url)
                
                # 從 HTML 中提取 vqd token（DuckDuckGo 需要的認證 token）
                html_content = response.text
                vqd_match = re.search(r'vqd="([^"]+)"', html_content)
                if not vqd_match:
                    # 如果找不到 vqd，嘗試另一種方式
                    vqd_match = re.search(r'vqd=([^&]+)', html_content)
                
                vqd = vqd_match.group(1) if vqd_match else ""
                
                if not vqd:
                    logger.warning("無法獲取 DuckDuckGo vqd token，嘗試直接搜尋...")
                    # 如果無法獲取 token，使用簡化方法
                    return await self._search_images_simple(keywords, limit)
                
                # 使用 token 搜尋圖片
                params = {
                    "q": keywords,
                    "o": "json",
                    "p": "1" if page == 1 else str(page),
                    "s": str((page - 1) * limit),  # 起始位置
                    "vqd": vqd,
                    "f": ",,,",
                    "u": "bing",
                }
                
                response = await client.get(search_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    images = data.get("results", [])
                    
                    # 轉換為統一格式
                    result = []
                    for img in images[:limit]:
                        result.append({
                            "id": f"ddg_{img.get('image', '')[:50]}",  # 使用 URL 的一部分作為 ID
                            "url": img.get("image", ""),
                            "thumbnail_url": img.get("thumbnail", img.get("image", "")),
                            "width": img.get("width", 0),
                            "height": img.get("height", 0),
                            "title": img.get("title", ""),
                            "source": ImageSource.DUCKDUCKGO.value,
                            "photographer": img.get("title", "").split(" - ")[0] if " - " in img.get("title", "") else "",
                            "photographer_url": "",
                            "license": "Unknown",  # DuckDuckGo 不提供授權資訊
                            "keywords": [keywords],
                        })
                    
                    logger.info(f"✅ DuckDuckGo 搜尋成功，找到 {len(result)} 張圖片")
                    return result
                else:
                    logger.warning(f"DuckDuckGo API 返回錯誤，嘗試簡化方法...")
                    return await self._search_images_simple(keywords, limit)
                    
        except Exception as e:
            logger.error(f"DuckDuckGo 搜尋失敗: {e}")
            # 如果 API 方法失敗，嘗試簡化方法
            try:
                return await self._search_images_simple(keywords, limit)
            except Exception as e2:
                logger.error(f"DuckDuckGo 簡化搜尋也失敗: {e2}")
                raise
    
    async def _search_images_simple(self, keywords: str, limit: int) -> List[Dict[str, Any]]:
        """
        簡化搜尋方法（使用 duckduckgo-images-api 庫）
        這是一個備援方法，如果 API 方法失敗時使用
        """
        try:
            # 嘗試使用 duckduckgo-images-api 庫
            try:
                from duckduckgo_images import DDGS
                
                ddgs = DDGS()
                results = ddgs.images(
                    keywords=keywords,
                    max_results=limit,
                    safesearch='moderate'
                )
                
                result = []
                for img in results:
                    if img.get("image"):
                        result.append({
                            "id": f"ddg_{hash(img.get('image', '')) % 1000000}",
                            "url": img.get("image", ""),
                            "thumbnail_url": img.get("thumbnail", img.get("image", "")),
                            "width": img.get("width", 0),
                            "height": img.get("height", 0),
                            "title": img.get("title", keywords),
                            "source": ImageSource.DUCKDUCKGO.value,
                            "photographer": img.get("title", "").split(" - ")[0] if " - " in img.get("title", "") else "",
                            "photographer_url": "",
                            "license": "Unknown",
                            "keywords": [keywords],
                        })
                
                logger.info(f"✅ DuckDuckGo 簡化搜尋成功，找到 {len(result)} 張圖片")
                return result
                
            except ImportError:
                logger.warning("duckduckgo-images-api 庫未安裝，使用 HTML 解析方法...")
                # 如果庫未安裝，使用 HTML 解析方法
                return await self._search_images_html(keywords, limit)
                
        except Exception as e:
            logger.error(f"DuckDuckGo 簡化搜尋失敗: {e}")
            # 如果所有方法都失敗，嘗試 HTML 解析
            try:
                return await self._search_images_html(keywords, limit)
            except Exception as e2:
                logger.error(f"DuckDuckGo HTML 解析也失敗: {e2}")
                raise
    
    async def _search_images_html(self, keywords: str, limit: int) -> List[Dict[str, Any]]:
        """
        HTML 解析方法（最後備援）
        """
        try:
            search_url = f"{self.base_url}/?q={quote(keywords)}&iax=images&ia=images"
            
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(search_url, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                
                html = response.text
                
                # 從 HTML 中提取圖片 URL
                # DuckDuckGo 的圖片 URL 通常在 data-src 或 src 屬性中
                image_patterns = [
                    r'data-src="([^"]+)"',
                    r'src="([^"]+\.(?:jpg|jpeg|png|gif|webp))"',
                    r'data-image="([^"]+)"',
                ]
                
                result = []
                seen_urls = set()
                
                for pattern in image_patterns:
                    matches = re.findall(pattern, html)
                    for url in matches:
                        if url and url.startswith("http") and url not in seen_urls:
                            # 過濾掉一些無關的 URL
                            if any(skip in url.lower() for skip in ['logo', 'icon', 'button', 'avatar']):
                                continue
                            seen_urls.add(url)
                            result.append({
                                "id": f"ddg_{hash(url) % 1000000}",
                                "url": url,
                                "thumbnail_url": url,
                                "width": 0,
                                "height": 0,
                                "title": keywords,
                                "source": ImageSource.DUCKDUCKGO.value,
                                "photographer": "",
                                "photographer_url": "",
                                "license": "Unknown",
                                "keywords": [keywords],
                            })
                            
                            if len(result) >= limit:
                                break
                    
                    if len(result) >= limit:
                        break
                
                logger.info(f"✅ DuckDuckGo HTML 解析成功，找到 {len(result)} 張圖片")
                return result
                
        except Exception as e:
            logger.error(f"DuckDuckGo HTML 解析失敗: {e}")
            raise
    
    async def get_image_info(self, image_id: str) -> Dict[str, Any]:
        """
        根據 ID 獲取圖片詳情
        
        Args:
            image_id: 圖片 ID（格式：ddg_xxx）
            
        Returns:
            圖片詳情
        """
        # DuckDuckGo 不支援根據 ID 獲取圖片
        # 這裡返回一個基本結構
        return {
            "id": image_id,
            "url": "",
            "source": ImageSource.DUCKDUCKGO.value,
            "license": "Unknown",
        }


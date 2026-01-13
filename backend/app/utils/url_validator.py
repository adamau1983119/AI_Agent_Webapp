"""
URL 驗證工具
用於驗證和過濾圖片 URL，過濾掉無法直接訪問的 URL（如 TikTok/Instagram crawler URL）
"""
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def is_direct_image_url(url: str) -> bool:
    """
    檢查 URL 是否為直接的圖片文件 URL
    
    Args:
        url: 要檢查的 URL
        
    Returns:
        True 如果是直接的圖片 URL，False 否則
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # 檢查 URL 結尾是否為圖片格式（支援查詢參數）
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg']
    for ext in image_extensions:
        # 匹配 .ext 或 .ext?xxx 格式
        if re.search(rf"\.{ext[1:]}(\?.*)?$", url_lower):
            return True
    
    return False


def is_crawler_url(url: str) -> bool:
    """
    檢查 URL 是否為 crawler URL（如 TikTok/Instagram API 端點）
    
    Args:
        url: 要檢查的 URL
        
    Returns:
        True 如果是 crawler URL，False 否則
    """
    if not url or not isinstance(url, str):
        return False
    
    url_lower = url.lower()
    
    # TikTok crawler URL 模式
    tiktok_patterns = [
        r"tiktok\.com/api/img/",
        r"tiktok\.com/api/.*itemid",
    ]
    
    # Instagram crawler URL 模式
    instagram_patterns = [
        r"lookaside\.instagram\.com/seo/google_widget/crawler/",
        r"instagram\.com/seo/google_widget/",
    ]
    
    # 檢查是否匹配任何 crawler 模式
    all_patterns = tiktok_patterns + instagram_patterns
    for pattern in all_patterns:
        if re.search(pattern, url_lower):
            return True
    
    return False


def is_valid_image_url(url: str, mime: str = None) -> bool:
    """
    檢查 URL 是否為有效的圖片 URL
    
    Args:
        url: 要檢查的 URL
        mime: MIME 類型（可選）
        
    Returns:
        True 如果是有效的圖片 URL，False 否則
    """
    if not url or not isinstance(url, str):
        return False
    
    # 如果是 crawler URL，則無效
    if is_crawler_url(url):
        return False
    
    # 如果是直接的圖片 URL，則有效
    if is_direct_image_url(url):
        return True
    
    # 如果 MIME 類型是 image/*，則有效
    if mime and isinstance(mime, str) and mime.startswith("image/"):
        return True
    
    return False


def filter_image_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    過濾圖片搜尋結果，只保留可直接訪問的圖片
    
    Args:
        items: 圖片搜尋結果列表（每個項目包含 link, mime 等欄位）
        
    Returns:
        過濾後的圖片列表
    """
    if not items:
        return []
    
    filtered_results = []
    filtered_count = 0
    
    for item in items:
        link = item.get("link", "")
        mime = item.get("mime", "")
        
        # 如果沒有 link，跳過
        if not link:
            filtered_count += 1
            continue
        
        # 檢查是否為有效的圖片 URL
        if is_valid_image_url(link, mime):
            filtered_results.append(item)
        else:
            filtered_count += 1
            logger.debug(f"過濾掉無效圖片 URL: {link} (mime={mime})")
    
    if filtered_count > 0:
        logger.info(f"URL 過濾: 原始結果 {len(items)} 個，過濾後 {len(filtered_results)} 個，過濾掉 {filtered_count} 個")
    
    return filtered_results


def get_image_url_priority(url: str, mime: str = None) -> int:
    """
    獲取圖片 URL 的優先級（用於排序）
    優先級越高，越應該優先使用
    
    Args:
        url: 圖片 URL
        mime: MIME 類型（可選）
        
    Returns:
        優先級分數（0-100）
    """
    if not is_valid_image_url(url, mime):
        return 0
    
    priority = 50  # 基礎分數
    
    # 直接的圖片 URL 優先級更高
    if is_direct_image_url(url):
        priority += 30
    
    # 如果 MIME 類型明確，優先級更高
    if mime and mime.startswith("image/"):
        priority += 20
    
    # 常見的圖片格式優先級更高
    url_lower = url.lower()
    if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png']):
        priority += 10
    
    return min(priority, 100)


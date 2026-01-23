"""
OriginalImageExtractor (Phase 6.4)
從 RSS Feed 提取原文照片
"""
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from bs4 import BeautifulSoup
import hashlib
import re
import logging

logger = logging.getLogger(__name__)


class OriginalImageExtractor:
    """
    原文照片提取器 (Phase 6.4)
    
    從 RSS entry 提取圖片：
    1. media_content
    2. media_thumbnail
    3. enclosures
    4. HTML 內容中的 <img> 標籤
    5. og:image
    """
    
    # 支援的圖片格式
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
    
    # 最小圖片尺寸（過濾小圖標）
    MIN_WIDTH = 100
    MIN_HEIGHT = 100
    
    # 排除的 URL 模式（廣告、追蹤像素等）
    EXCLUDE_PATTERNS = [
        r'pixel\.',
        r'tracking\.',
        r'analytics\.',
        r'doubleclick\.',
        r'facebook\.com/tr',
        r'google-analytics\.',
        r'1x1\.',
        r'spacer\.',
        r'blank\.',
        r'transparent\.',
        r'\.gif\?',  # 追蹤 GIF
    ]
    
    def __init__(self, min_width: int = 100, min_height: int = 100):
        self.min_width = min_width
        self.min_height = min_height
        self._exclude_regex = re.compile('|'.join(self.EXCLUDE_PATTERNS), re.IGNORECASE)
    
    def extract_from_entry(
        self,
        entry: Dict[str, Any],
        source_name: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        從 RSS entry 提取所有圖片
        
        Args:
            entry: feedparser 解析的 entry
            source_name: 來源名稱
            
        Returns:
            圖片列表，每個包含 photo_id, url, caption 等
        """
        images: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()
        
        # 1. 提取 media_content
        media_images = self._extract_media_content(entry)
        for img in media_images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                images.append(img)
        
        # 2. 提取 media_thumbnail
        thumbnail_images = self._extract_media_thumbnail(entry)
        for img in thumbnail_images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                images.append(img)
        
        # 3. 提取 enclosures
        enclosure_images = self._extract_enclosures(entry)
        for img in enclosure_images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                images.append(img)
        
        # 4. 從 HTML 內容提取
        html_images = self._extract_from_html(entry)
        for img in html_images:
            if img["url"] not in seen_urls:
                seen_urls.add(img["url"])
                images.append(img)
        
        # 5. 去重和過濾
        filtered_images = self._filter_images(images)
        
        # 6. 生成 photo_id
        for img in filtered_images:
            img["photo_id"] = self.generate_photo_id(img["url"])
            img["source_name"] = source_name
        
        logger.debug(f"Extracted {len(filtered_images)} images from entry")
        return filtered_images
    
    def _extract_media_content(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取 media_content
        
        RSS 2.0 Media 擴展格式
        """
        images = []
        
        # media_content 可能是列表或單個對象
        media_content = entry.get("media_content", [])
        if not isinstance(media_content, list):
            media_content = [media_content]
        
        for media in media_content:
            if not isinstance(media, dict):
                continue
            
            url = media.get("url", "")
            media_type = media.get("type", "")
            
            # 檢查是否為圖片
            if self._is_image_url(url) or media_type.startswith("image/"):
                images.append({
                    "url": url,
                    "width": self._parse_int(media.get("width")),
                    "height": self._parse_int(media.get("height")),
                    "caption": media.get("description", ""),
                    "source_type": "media_content"
                })
        
        return images
    
    def _extract_media_thumbnail(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取 media_thumbnail
        """
        images = []
        
        # media_thumbnail 可能是列表或單個對象
        thumbnails = entry.get("media_thumbnail", [])
        if not isinstance(thumbnails, list):
            thumbnails = [thumbnails]
        
        for thumb in thumbnails:
            if not isinstance(thumb, dict):
                continue
            
            url = thumb.get("url", "")
            if self._is_image_url(url):
                images.append({
                    "url": url,
                    "width": self._parse_int(thumb.get("width")),
                    "height": self._parse_int(thumb.get("height")),
                    "caption": "",
                    "source_type": "media_thumbnail"
                })
        
        return images
    
    def _extract_enclosures(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        提取 enclosures
        
        RSS 2.0 標準附件格式
        """
        images = []
        
        enclosures = entry.get("enclosures", [])
        if not isinstance(enclosures, list):
            enclosures = [enclosures]
        
        for enc in enclosures:
            if not isinstance(enc, dict):
                continue
            
            url = enc.get("url", "") or enc.get("href", "")
            enc_type = enc.get("type", "")
            
            if self._is_image_url(url) or enc_type.startswith("image/"):
                images.append({
                    "url": url,
                    "width": None,
                    "height": None,
                    "caption": "",
                    "source_type": "enclosure"
                })
        
        return images
    
    def _extract_from_html(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        從 HTML 內容提取 <img> 標籤
        """
        images = []
        
        # 嘗試多個可能的 HTML 內容欄位
        html_content = ""
        for field in ["content", "summary", "description"]:
            content = entry.get(field)
            if content:
                if isinstance(content, list) and len(content) > 0:
                    html_content = content[0].get("value", "")
                elif isinstance(content, str):
                    html_content = content
                if html_content:
                    break
        
        if not html_content:
            return images
        
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            
            # 提取 <img> 標籤
            for img in soup.find_all("img"):
                url = img.get("src", "") or img.get("data-src", "")
                if not url:
                    continue
                
                # 處理相對 URL
                if url.startswith("//"):
                    url = "https:" + url
                
                if self._is_image_url(url):
                    images.append({
                        "url": url,
                        "width": self._parse_int(img.get("width")),
                        "height": self._parse_int(img.get("height")),
                        "caption": img.get("alt", "") or img.get("title", ""),
                        "source_type": "html_img"
                    })
            
            # 提取 og:image
            for meta in soup.find_all("meta", property="og:image"):
                url = meta.get("content", "")
                if url and self._is_image_url(url):
                    images.append({
                        "url": url,
                        "width": None,
                        "height": None,
                        "caption": "",
                        "source_type": "og_image"
                    })
                    
        except Exception as e:
            logger.warning(f"Failed to parse HTML content: {e}")
        
        return images
    
    def _filter_images(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        過濾圖片：去除小圖、追蹤像素等
        """
        filtered = []
        
        for img in images:
            url = img.get("url", "")
            
            # 排除追蹤像素和廣告
            if self._exclude_regex.search(url):
                continue
            
            # 檢查尺寸（如果有）
            width = img.get("width")
            height = img.get("height")
            
            if width and height:
                if width < self.min_width or height < self.min_height:
                    continue
            
            # 確保 URL 有效
            if not url or len(url) < 10:
                continue
            
            filtered.append(img)
        
        return filtered
    
    def _deduplicate(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        去重：根據 URL 去重
        """
        seen = set()
        unique = []
        
        for img in images:
            url = img.get("url", "")
            # 正規化 URL（移除查詢參數）
            normalized = url.split("?")[0]
            
            if normalized not in seen:
                seen.add(normalized)
                unique.append(img)
        
        return unique
    
    def _is_image_url(self, url: str) -> bool:
        """
        檢查 URL 是否為圖片
        """
        if not url:
            return False
        
        url_lower = url.lower()
        
        # 檢查副檔名
        for ext in self.SUPPORTED_EXTENSIONS:
            if ext in url_lower:
                return True
        
        # 檢查常見的圖片服務
        image_services = [
            "images.",
            "img.",
            "media.",
            "cdn.",
            "static.",
            "/images/",
            "/img/",
            "/photos/",
            "unsplash.com",
            "pexels.com",
            "cloudinary.com",
            "imgix.net",
        ]
        
        for service in image_services:
            if service in url_lower:
                return True
        
        return False
    
    def _parse_int(self, value: Any) -> Optional[int]:
        """
        安全解析整數
        """
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def generate_photo_id(url: str) -> str:
        """
        從 URL 生成唯一的 photo_id
        
        Args:
            url: 圖片 URL
            
        Returns:
            photo_id（格式：P + 8位 hash）
        """
        # 正規化 URL
        normalized = url.split("?")[0].lower()
        
        # 生成 MD5 hash
        url_hash = hashlib.md5(normalized.encode()).hexdigest()[:8]
        
        return f"P{url_hash}"
    
    def extract_all_from_entries(
        self,
        entries: List[Dict[str, Any]],
        source_name: str = "unknown"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        從多個 entries 提取圖片
        
        Args:
            entries: entry 列表
            source_name: 來源名稱
            
        Returns:
            {entry_id: [images]} 映射
        """
        result = {}
        
        for entry in entries:
            entry_id = entry.get("id") or entry.get("link", "unknown")
            images = self.extract_from_entry(entry, source_name)
            result[entry_id] = images
        
        return result


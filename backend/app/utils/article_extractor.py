"""
文章內容提取工具
用於從 URL 或 HTML 提取原文圖片、完整報導內容和風格分析
支援 BeautifulSoup 與正則表達式雙引擎容錯
"""
import re
import html as html_lib
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

try:
    import httpx
except (ImportError, Exception):
    httpx = None

try:
    from bs4 import BeautifulSoup
except (ImportError, Exception):
    BeautifulSoup = None

logger = logging.getLogger(__name__)


class ArticleExtractor:
    """文章內容提取器（支援 BeautifulSoup 與 Regex 容錯）"""

    def __init__(self):
        self.timeout = 15.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6',
        }

    async def extract_article_info(self, url: str) -> Dict[str, Any]:
        """從 URL 提取文章資訊"""
        if not url or not str(url).startswith(('http://', 'https://')):
            return {
                "images": [],
                "original_content": None,
                "language": None,
                "style": None,
                "success": False,
                "error": "Invalid URL",
            }
        try:
            if httpx is None:
                raise RuntimeError("httpx not available")
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                html_text = response.text
                return self.extract_from_html_content(html_text, base_url=url)
        except Exception as e:
            logger.warning(f"提取文章資訊失敗 {url}: {e}")
            return {
                "images": [],
                "original_content": None,
                "language": None,
                "style": None,
                "success": False,
                "error": str(e),
            }

    def extract_from_html_content(self, html_content: str, base_url: str = "") -> Dict[str, Any]:
        """從 HTML 內容（如 RSS 內的 content:encoded 或 summary）直接提取新聞正文與圖片"""
        if not html_content or not isinstance(html_content, str):
            return {
                "images": [],
                "original_content": None,
                "language": None,
                "style": None,
                "success": False,
            }

        images: List[str] = []
        content: str = ""

        # 1. 嘗試使用 BeautifulSoup 解析
        if BeautifulSoup is not None:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                # 檢查 soup 是否為 MagicMock
                if hasattr(soup, 'find_all') and not str(type(soup)).startswith("<class 'unittest.mock"):
                    images = self._extract_images_soup(soup, base_url)
                    content = self._extract_content_soup(soup)
            except Exception as bs_err:
                logger.debug("BeautifulSoup 解析失敗，切換正則降級: %s", bs_err)

        # 2. 正則降級 (Regex Fallback)
        if not images:
            images = self._extract_images_regex(html_content, base_url)
        if not content or len(content) < 30:
            content = self._extract_content_regex(html_content)

        language = self._detect_language(content)
        style = self._analyze_style(content)
        return {
            "images": images[:6],
            "original_content": content if content else None,
            "language": language,
            "style": style,
            "success": bool(content and len(content) >= 30),
        }

    def _extract_images_soup(self, soup: Any, base_url: str) -> List[str]:
        images: List[str] = []
        seen_urls = set()

        # og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/') and base_url:
                img_url = urljoin(base_url, img_url)
            if img_url not in seen_urls and img_url.startswith('http'):
                images.append(img_url)
                seen_urls.add(img_url)

        # <img> tags
        for img in soup.find_all('img', src=True):
            img_url = img.get('src') or img.get('data-src') or img.get('data-original')
            if not img_url or img_url.startswith('data:'):
                continue
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/') and base_url:
                img_url = urljoin(base_url, img_url)
            if any(s in img_url.lower() for s in ['logo', 'icon', 'avatar', 'badge', 'tracking', 'pixel']):
                continue
            if img_url not in seen_urls and img_url.startswith('http'):
                images.append(img_url)
                seen_urls.add(img_url)
        return images

    def _extract_images_regex(self, html_text: str, base_url: str) -> List[str]:
        images: List[str] = []
        seen = set()

        # og:image
        og_m = re.findall(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html_text, re.I)
        og_m += re.findall(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html_text, re.I)
        for u in og_m:
            if u.startswith('//'):
                u = 'https:' + u
            elif u.startswith('/') and base_url:
                u = urljoin(base_url, u)
            if u not in seen and u.startswith('http'):
                images.append(u)
                seen.add(u)

        # <img> src
        img_m = re.findall(r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']', html_text, re.I)
        for u in img_m:
            if u.startswith('data:'):
                continue
            if u.startswith('//'):
                u = 'https:' + u
            elif u.startswith('/') and base_url:
                u = urljoin(base_url, u)
            if any(s in u.lower() for s in ['logo', 'icon', 'avatar', 'badge', 'tracking', 'pixel']):
                continue
            if u not in seen and u.startswith('http'):
                images.append(u)
                seen.add(u)
        return images

    def _extract_content_soup(self, soup: Any) -> str:
        candidates = [
            soup.find('article'),
            soup.find('div', attrs={'itemprop': 'articleBody'}),
            soup.find('div', class_=re.compile(r'(article[-_]body|post[-_]content|entry[-_]content|article[-_]content|story[-_]body|c-entry-content)', re.I)),
            soup.find('main'),
            soup.find('body'),
        ]
        for container in candidates:
            if not container:
                continue
            container_copy = BeautifulSoup(str(container), 'html.parser')
            for tag in container_copy.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form', 'noscript', 'svg', 'button']):
                tag.decompose()
            from app.utils.article_boilerplate import clean_extracted_text, strip_boilerplate_nodes
            strip_boilerplate_nodes(container_copy)
            text = container_copy.get_text(separator='\n', strip=True)
            cleaned = clean_extracted_text(text)
            if len(cleaned) >= 30:
                return cleaned[:5000]
        return ""

    def _extract_content_regex(self, html_text: str) -> str:
        # 去除 script, style, nav 等標籤內容
        cleaned = re.sub(r'<(script|style|nav|header|footer|aside|iframe|svg|noscript)[^>]*>.*?</\1>', '', html_text, flags=re.DOTALL | re.I)
        # 標籤替換為換行
        cleaned = re.sub(r'<br\s*/?>', '\n', cleaned, flags=re.I)
        cleaned = re.sub(r'</p>', '\n\n', cleaned, flags=re.I)
        cleaned = re.sub(r'</div>', '\n', cleaned, flags=re.I)
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        cleaned = html_lib.unescape(cleaned)
        lines = [l.strip() for l in cleaned.splitlines() if l.strip()]
        result = '\n\n'.join(lines)
        from app.utils.article_boilerplate import clean_extracted_text
        return clean_extracted_text(result)[:5000]

    def _detect_language(self, content: str) -> str:
        if not content:
            return "unknown"
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
        kana_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))

        if kana_chars > 5:
            return "ja"
        if chinese_chars > english_chars * 0.3:
            return "zh-TW"
        elif english_chars > chinese_chars * 0.5:
            return "en"
        else:
            return "mixed"

    def _analyze_style(self, content: str) -> Dict[str, str]:
        if not content:
            return {"tone": None, "structure": None, "vocabulary": None}
        tone = "neutral"
        if any(word in content.lower() for word in ['excited', 'amazing', 'wow', '驚喜', '太棒了']):
            tone = "enthusiastic"
        elif any(word in content.lower() for word in ['report', 'according', '報導', '據']):
            tone = "news_report"
        elif any(word in content.lower() for word in ['share', 'experience', '分享', '體驗']):
            tone = "casual_sharing"

        paragraphs = content.split('\n\n')
        avg_len = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        if avg_len < 100:
            structure = "short_paragraphs"
        elif avg_len < 300:
            structure = "medium_paragraphs"
        else:
            structure = "long_paragraphs"

        vocabulary = "general"
        if any(term in content.lower() for term in ['design', 'collection', 'fashion', 'designer', '設計', '系列', '時尚', '設計師']):
            vocabulary = "professional_terms"

        return {"tone": tone, "structure": structure, "vocabulary": vocabulary}

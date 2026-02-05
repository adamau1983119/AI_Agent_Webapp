"""
文章內容提取工具
用於從 URL 提取原文圖片、內容和風格分析
"""
import re
import httpx
import logging
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class ArticleExtractor:
    """文章內容提取器"""
    
    def __init__(self):
        self.timeout = 15.0
    
    async def extract_article_info(self, url: str) -> Dict[str, Any]:
        """
        從 URL 提取文章資訊
        
        Args:
            url: 文章 URL
            
        Returns:
            包含 images, content, language, style 的字典
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # 提取圖片
                images = self._extract_images(soup, url)
                
                # 提取內容
                content = self._extract_content(soup)
                
                # 檢測語言
                language = self._detect_language(content)
                
                # 分析風格
                style = self._analyze_style(content)
                
                return {
                    "images": images,
                    "original_content": content,
                    "language": language,
                    "style": style,
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"提取文章資訊失敗 {url}: {e}")
            return {
                "images": [],
                "original_content": None,
                "language": None,
                "style": None,
                "success": False,
                "error": str(e)
            }
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取文章圖片"""
        images = []
        seen_urls = set()
        
        # 1. 提取 og:image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            img_url = og_image['content']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(base_url, img_url)
            if img_url not in seen_urls:
                images.append(img_url)
                seen_urls.add(img_url)
        
        # 2. 提取 twitter:image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            img_url = twitter_image['content']
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(base_url, img_url)
            if img_url not in seen_urls:
                images.append(img_url)
                seen_urls.add(img_url)
        
        # 3. 提取 <img> 標籤中的圖片（優先提取 article 內的圖片）
        article_tag = soup.find('article') or soup.find('main') or soup.find('body')
        if article_tag:
            img_tags = article_tag.find_all('img', src=True)
            for img in img_tags[:5]:  # 最多提取5張
                img_url = img.get('src') or img.get('data-src')
                if not img_url:
                    continue
                
                # 處理相對 URL
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = urljoin(base_url, img_url)
                
                # 過濾掉小圖標和 logo
                if any(skip in img_url.lower() for skip in ['logo', 'icon', 'avatar', 'button', 'badge']):
                    continue
                
                # 過濾掉 data URI
                if img_url.startswith('data:'):
                    continue
                
                if img_url not in seen_urls and img_url.startswith('http'):
                    images.append(img_url)
                    seen_urls.add(img_url)
        
        return images[:5]  # 最多返回5張圖片
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取文章內容"""
        # 優先從 article 標籤提取
        article_tag = soup.find('article')
        if article_tag:
            # 移除 script 和 style 標籤
            for tag in article_tag.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            text = article_tag.get_text(separator='\n', strip=True)
            if text and len(text) > 100:
                return text[:5000]  # 限制長度
        
        # 如果沒有 article 標籤，嘗試從 main 標籤提取
        main_tag = soup.find('main')
        if main_tag:
            for tag in main_tag.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            text = main_tag.get_text(separator='\n', strip=True)
            if text and len(text) > 100:
                return text[:5000]
        
        # 最後嘗試從 body 提取（但會更不準確）
        body_tag = soup.find('body')
        if body_tag:
            for tag in body_tag.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            text = body_tag.get_text(separator='\n', strip=True)
            if text and len(text) > 100:
                return text[:5000]
        
        return ""
    
    def _detect_language(self, content: str) -> str:
        """檢測語言（簡化版）"""
        if not content:
            return "unknown"
        
        # 簡單的語言檢測：統計中文字符和英文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fa5]', content))
        english_chars = len(re.findall(r'[a-zA-Z]', content))
        
        if chinese_chars > english_chars * 0.5:
            return "zh"
        elif english_chars > chinese_chars * 0.5:
            return "en"
        else:
            return "mixed"
    
    def _analyze_style(self, content: str) -> Dict[str, str]:
        """分析文章風格"""
        if not content:
            return {
                "tone": None,
                "structure": None,
                "vocabulary": None
            }
        
        # 分析語調
        tone = "neutral"
        if any(word in content.lower() for word in ['excited', 'amazing', 'wow', '驚喜', '太棒了']):
            tone = "enthusiastic"
        elif any(word in content.lower() for word in ['report', 'according', '報導', '據']):
            tone = "news_report"
        elif any(word in content.lower() for word in ['share', 'experience', '分享', '體驗']):
            tone = "casual_sharing"
        
        # 分析結構
        paragraphs = content.split('\n')
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        if avg_paragraph_length < 100:
            structure = "short_paragraphs"
        elif avg_paragraph_length < 300:
            structure = "medium_paragraphs"
        else:
            structure = "long_paragraphs"
        
        # 分析詞彙
        vocabulary = "general"
        professional_terms = ['design', 'collection', 'fashion', 'designer', '設計', '系列', '時尚', '設計師']
        if any(term in content.lower() for term in professional_terms):
            vocabulary = "professional_terms"
        
        return {
            "tone": tone,
            "structure": structure,
            "vocabulary": vocabulary
        }


"""
DeepSeek AI 服務
使用 OpenAI 兼容的 API 接口
"""
import httpx
import json
from typing import Optional, Dict, Any
from app.services.ai.base import AIServiceBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DeepSeekService(AIServiceBase):
    """DeepSeek 服務（OpenAI 兼容）"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL
        self.base_url = settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com/v1/chat/completions"
    
    def _build_prompt(self, topic_title: str, topic_category: str, keywords: list[str], content_type: str, target: str) -> str:
        """
        建立 Prompt
        
        Args:
            topic_title: 主題標題
            topic_category: 主題分類
            keywords: 關鍵字列表
            content_type: 內容類型（article/script）
            target: 目標（長度或時長）
            
        Returns:
            Prompt 字串
        """
        if content_type == "article":
            from app.prompts.article_prompt import build_article_prompt
            return build_article_prompt(topic_title, topic_category, keywords, int(target))
        else:  # script
            from app.prompts.script_prompt import build_script_prompt
            return build_script_prompt(topic_title, topic_category, keywords, int(target))
    
    async def _call_api(self, prompt: str) -> str:
        """
        調用 DeepSeek API（OpenAI 兼容格式）
        
        Args:
            prompt: Prompt 內容
            
        Returns:
            AI 生成的回應
        """
        if not self.api_key:
            logger.error("❌ DeepSeek API Key 未設定 - 請檢查 Railway 環境變數 DEEPSEEK_API_KEY")
            raise ValueError("DeepSeek API Key 未設定")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            logger.info(f"調用 DeepSeek API: {self.base_url}, Model: {self.model}")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # 解析 OpenAI 兼容格式的回應
                if "choices" in result and len(result["choices"]) > 0:
                    message = result["choices"][0].get("message", {})
                    content = message.get("content", "")
                    if content:
                        return content
                
                raise ValueError(f"API 回應格式錯誤: {result}")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API 調用失敗: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"DeepSeek API 調用失敗: {e.response.status_code}")
        except Exception as e:
            logger.error(f"調用 DeepSeek API 時發生錯誤: {e}")
            raise
    
    async def generate_article(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        length: int = 500
    ) -> str:
        """生成短文"""
        prompt = self._build_prompt(topic_title, topic_category, keywords, "article", str(length))
        return await self._call_api(prompt)
    
    async def generate_script(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        duration: int = 30
    ) -> str:
        """生成腳本"""
        prompt = self._build_prompt(topic_title, topic_category, keywords, "script", str(duration))
        return await self._call_api(prompt)
    
    async def generate_both(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        article_length: int = 500,
        script_duration: int = 30
    ) -> Dict[str, str]:
        """同時生成短文和腳本"""
        article_prompt = self._build_prompt(topic_title, topic_category, keywords, "article", str(article_length))
        script_prompt = self._build_prompt(topic_title, topic_category, keywords, "script", str(script_duration))
        
        article = await self._call_api(article_prompt)
        script = await self._call_api(script_prompt)
        
        return {
            "article": article,
            "script": script
        }


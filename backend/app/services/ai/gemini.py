"""
Google Gemini AI 服務
適用於香港及國際用戶
"""
import google.generativeai as genai
from typing import Dict, Any
from app.services.ai.base import AIServiceBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiService(AIServiceBase):
    """Google Gemini 服務"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-pro"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未設定")
        
        # 配置 Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
    
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
    
    async def generate_article(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        length: int = 500
    ) -> str:
        """生成短文"""
        try:
            prompt = self._build_prompt(topic_title, topic_category, keywords, "article", str(length))
            
            # 使用 Gemini 生成
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": length * 2,  # 估算 token 數量
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini 生成短文失敗: {e}")
            raise
    
    async def generate_script(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        duration: int = 30
    ) -> str:
        """生成腳本"""
        try:
            prompt = self._build_prompt(topic_title, topic_category, keywords, "script", str(duration))
            
            # 使用 Gemini 生成
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": duration * 17 * 2,  # 估算 token 數量
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini 生成腳本失敗: {e}")
            raise
    
    async def generate_both(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        article_length: int = 500,
        script_duration: int = 30
    ) -> Dict[str, str]:
        """同時生成短文和腳本"""
        article = await self.generate_article(topic_title, topic_category, keywords, article_length)
        script = await self.generate_script(topic_title, topic_category, keywords, script_duration)
        
        return {
            "article": article,
            "script": script
        }

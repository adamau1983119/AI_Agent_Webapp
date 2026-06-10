"""
DeepSeek AI 服務
使用 OpenAI 兼容的 API 接口
"""
import httpx
from typing import Optional, Dict, Any
from app.services.ai.base import AIServiceBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DeepSeekService(AIServiceBase):
    """DeepSeek 服務（OpenAI 兼容）"""

    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = getattr(settings, "DEEPSEEK_MODEL_FLASH", None) or settings.DEEPSEEK_MODEL
        self.pro_model = getattr(settings, "DEEPSEEK_MODEL_PRO", "deepseek-v4-pro")
        self.base_url = settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com/v1/chat/completions"
        logger.info("DeepSeek Flash: %s | Pro: %s", self.model, self.pro_model)

    def _build_prompt(
        self, topic_title: str, topic_category: str, keywords: list[str], content_type: str, target: str
    ) -> str:
        if content_type == "article":
            from app.prompts.article_prompt import build_article_prompt
            return build_article_prompt(topic_title, topic_category, keywords, int(target))
        from app.prompts.script_prompt import build_script_prompt
        return build_script_prompt(topic_title, topic_category, keywords, int(target))

    def _resolve_max_tokens(self, model: Optional[str], max_tokens: Optional[int]) -> int:
        if max_tokens is not None:
            return max_tokens
        use_model = model or self.model
        is_pro = use_model == self.pro_model or "pro" in use_model.lower()
        if is_pro:
            return int(getattr(settings, "DEEPSEEK_PRO_MAX_TOKENS", 1500))
        return 2000

    async def _call_api(
        self, prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None
    ) -> str:
        use_model = model or self.model
        tokens = self._resolve_max_tokens(use_model, max_tokens)
        if not self.api_key:
            logger.error("DeepSeek API Key 未設定")
            raise ValueError("DeepSeek API Key 未設定")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": use_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": tokens,
        }

        try:
            logger.info("DeepSeek API model=%s max_tokens=%s", use_model, tokens)
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0].get("message", {}).get("content", "")
                    if content:
                        return content
                raise ValueError(f"API 回應格式錯誤: {result}")
        except httpx.HTTPStatusError as e:
            logger.error("DeepSeek API 失敗: %s - %s", e.response.status_code, e.response.text)
            raise ValueError(f"DeepSeek API 調用失敗: {e.response.status_code}")
        except Exception as e:
            logger.error("DeepSeek API 錯誤: %s", e)
            raise

    async def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """通用生成（預設 Flash）。"""
        return await self._call_api(prompt, model=model)

    async def generate_article(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        length: int = 500,
    ) -> str:
        prompt = self._build_prompt(topic_title, topic_category, keywords, "article", str(length))
        return await self._call_api(prompt, model=self.pro_model)

    async def generate_script(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        duration: int = 30,
    ) -> str:
        prompt = self._build_prompt(topic_title, topic_category, keywords, "script", str(duration))
        return await self._call_api(prompt)

    async def generate_both(
        self,
        topic_title: str,
        topic_category: str,
        keywords: list[str],
        article_length: int = 500,
        script_duration: int = 30,
    ) -> Dict[str, str]:
        article_prompt = self._build_prompt(
            topic_title, topic_category, keywords, "article", str(article_length)
        )
        script_prompt = self._build_prompt(
            topic_title, topic_category, keywords, "script", str(script_duration)
        )
        article = await self._call_api(article_prompt, model=self.pro_model)
        script = await self._call_api(script_prompt)
        return {"article": article, "script": script}

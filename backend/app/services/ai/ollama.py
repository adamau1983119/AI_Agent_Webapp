"""
Ollama 本地 AI 服務
適用於香港及無法使用雲端 AI 服務的用戶
"""
import httpx
from typing import Dict, Any
from app.services.ai.base import AIServiceBase
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OllamaService(AIServiceBase):
    """Ollama AI 服務（支援本地和雲端）"""
    
    def __init__(self):
        # 檢查是否使用雲端 API
        if settings.OLLAMA_API_KEY:
            # 使用雲端 API
            self.base_url = settings.OLLAMA_CLOUD_BASE_URL or "https://api.ollama.com"
            self.api_key = settings.OLLAMA_API_KEY
            self.use_cloud = True
            # 在初始化時設定完整 URL（避免在調用時重組）
            self.generate_url = f"{self.base_url}/generate"
            logger.info(f"使用 Ollama 雲端 API: {self.generate_url}")
        else:
            # 使用本地部署
            self.base_url = settings.OLLAMA_BASE_URL or "http://localhost:11434"
            self.api_key = None
            self.use_cloud = False
            # 在初始化時設定完整 URL
            self.generate_url = f"{self.base_url}/api/generate"
            logger.info(f"使用 Ollama 本地部署: {self.generate_url}")
            # 驗證本地服務是否運行
            self._verify_connection()
        
        self.model = settings.OLLAMA_MODEL or "llama2"
    
    def _verify_connection(self):
        """驗證 Ollama 服務是否運行"""
        if self.use_cloud:
            # 雲端 API 不需要驗證連接
            return
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
        except Exception as e:
            logger.warning(f"無法連接到 Ollama 服務 ({self.base_url})，請確保 Ollama 正在運行")
            logger.warning(f"錯誤: {e}")
            logger.info("請執行: ollama serve")
    
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
        調用 Ollama API（支援本地和雲端）
        
        Args:
            prompt: Prompt 內容
            
        Returns:
            AI 生成的回應
        """
        # 使用在 __init__ 時設定的完整 URL
        url = self.generate_url
        
        # 設定 Headers
        headers = {
            "Content-Type": "application/json"
        }
        if self.use_cloud:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 使用最簡請求格式（先測試基本連線）
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        # 如果需要，可以後續添加 options（確認基本連線成功後）
        # payload["options"] = {
        #     "temperature": 0.7,
        #     "num_predict": 2000,
        # }
        
        try:
            timeout = 120.0 if not self.use_cloud else 60.0  # 雲端通常較快
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                # 處理不同的回應格式
                if "response" in result:
                    return result["response"]
                elif "text" in result:
                    return result["text"]
                elif isinstance(result, str):
                    return result
                else:
                    logger.warning(f"未預期的回應格式: {result}")
                    return str(result)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API 調用失敗: {e.response.status_code} - {e.response.text}")
            if self.use_cloud:
                logger.error("請檢查 API Key 是否正確，或查看 Ollama 雲端服務狀態")
            raise
        except httpx.TimeoutException:
            logger.error("Ollama API 調用超時")
            if self.use_cloud:
                logger.error("請檢查網路連接或 Ollama 雲端服務狀態")
            else:
                logger.error("請檢查本地 Ollama 服務是否正常運行")
            raise
        except Exception as e:
            logger.error(f"調用 Ollama API 時發生錯誤: {e}")
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
        article = await self.generate_article(topic_title, topic_category, keywords, article_length)
        script = await self.generate_script(topic_title, topic_category, keywords, script_duration)
        
        return {
            "article": article,
            "script": script
        }

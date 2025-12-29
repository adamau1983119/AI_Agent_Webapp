"""
AI 服務工廠
根據配置選擇合適的 AI 服務
"""
import logging
from app.services.ai.base import AIServiceBase
from app.config import settings

logger = logging.getLogger(__name__)


class AIServiceFactory:
    """AI 服務工廠"""
    
    @staticmethod
    def get_service(service_name: str = None) -> AIServiceBase:
        """
        根據配置獲取 AI 服務實例
        
        Args:
            service_name: 服務名稱（可選，預設使用配置中的 AI_SERVICE）
            
        Returns:
            AI 服務實例
        """
        service_name = service_name or settings.AI_SERVICE
        
        if service_name in ["ollama", "ollama_cloud"]:
            from app.services.ai.ollama import OllamaService
            return OllamaService()
        elif service_name == "gemini":
            from app.services.ai.gemini import GeminiService
            return GeminiService()
        elif service_name == "openai":
            from app.services.ai.openai import OpenAIService
            return OpenAIService()
        else:  # 預設使用通義千問
            from app.services.ai.qwen import QwenService
            return QwenService()


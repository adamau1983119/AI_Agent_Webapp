"""
AI 服務工廠
根據配置選擇合適的 AI 服務
使用映射表方式，支援動態載入和擴展
"""
import logging
from app.services.ai.base import AIServiceBase
from app.config import settings

logger = logging.getLogger(__name__)


# AI 服務映射表
# 格式：服務名稱 -> (模組路徑, 類別名稱, API Key 環境變數名稱)
AI_SERVICES = {
    "qwen": {
        "module": "app.services.ai.qwen",
        "class": "QwenService",
        "api_key_env": "QWEN_API_KEY"
    },
    "openai": {
        "module": "app.services.ai.openai",
        "class": "OpenAIService",
        "api_key_env": "OPENAI_API_KEY"
    },
    "gemini": {
        "module": "app.services.ai.gemini",
        "class": "GeminiService",
        "api_key_env": "GEMINI_API_KEY"
    },
    "ollama": {
        "module": "app.services.ai.ollama",
        "class": "OllamaService",
        "api_key_env": None  # Ollama 本地服務不需要 API Key
    },
    "ollama_cloud": {
        "module": "app.services.ai.ollama",
        "class": "OllamaService",
        "api_key_env": "OLLAMA_API_KEY"
    },
    "deepseek": {
        "module": "app.services.ai.deepseek",
        "class": "DeepSeekService",
        "api_key_env": "DEEPSEEK_API_KEY"
    }
}


class AIServiceFactory:
    """AI 服務工廠（使用映射表方式）"""
    
    @staticmethod
    def get_service(service_name: str = None) -> AIServiceBase:
        """
        根據配置獲取 AI 服務實例（動態載入）
        
        Args:
            service_name: 服務名稱（可選，預設使用配置中的 AI_SERVICE）
            
        Returns:
            AI 服務實例
            
        Raises:
            ValueError: 如果服務不存在或載入失敗
        """
        service_name = service_name or settings.AI_SERVICE
        
        # 檢查服務是否存在於映射表
        if service_name not in AI_SERVICES:
            logger.warning(
                f"未知的 AI 服務: {service_name}，使用預設服務 deepseek"
            )
            service_name = "deepseek"
        
        service_config = AI_SERVICES[service_name]
        
        try:
            # 動態載入模組和類別
            module_path = service_config["module"]
            class_name = service_config["class"]
            
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            
            # 創建服務實例
            service_instance = service_class()
            
            logger.info(f"✅ 成功載入 AI 服務: {service_name} ({class_name})")
            return service_instance
            
        except ImportError as e:
            logger.error(f"無法載入 AI 服務模組 {service_config['module']}: {e}")
            raise ValueError(f"無法載入 AI 服務: {service_name} - {e}")
        except AttributeError as e:
            logger.error(f"AI 服務類別 {service_config['class']} 不存在: {e}")
            raise ValueError(f"AI 服務類別不存在: {service_name} - {e}")
        except Exception as e:
            logger.error(f"創建 AI 服務實例失敗: {service_name} - {e}")
            raise ValueError(f"創建 AI 服務實例失敗: {service_name} - {e}")
    
    @staticmethod
    def list_available_services() -> list[str]:
        """
        列出所有可用的 AI 服務名稱
        
        Returns:
            服務名稱列表
        """
        return list(AI_SERVICES.keys())
    
    @staticmethod
    def get_service_config(service_name: str) -> dict:
        """
        獲取服務配置資訊
        
        Args:
            service_name: 服務名稱
            
        Returns:
            服務配置字典，如果服務不存在則返回 None
        """
        return AI_SERVICES.get(service_name)


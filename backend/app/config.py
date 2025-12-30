"""
應用配置管理
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Union
import json


class Settings(BaseSettings):
    """應用設定"""
    
    # 應用配置
    APP_NAME: str = "AI Agent Webapp"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    AUTO_START_SCHEDULER: str = "false"  # 是否自動啟動排程服務（true/false）
    
    # 伺服器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB 配置
    # 本地 MongoDB: mongodb://localhost:27017
    # MongoDB Atlas: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ai_agent_webapp"
    
    # AI 服務配置
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"
    
    # 備援 AI 服務（可選）
    HUNYUAN_API_KEY: str = ""
    ERNIE_API_KEY: str = ""
    
    # OpenAI（替代方案，適用於香港/國際用戶）
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Google Gemini（推薦給香港用戶）
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-pro"
    
    # Ollama 本地 AI（推薦給無法使用雲端服務的用戶）
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"  # 官方支援的標準模型（雲端和本地都可用）
    
    # Ollama 雲端 API（使用 API Key）
    OLLAMA_API_KEY: str = ""
    OLLAMA_CLOUD_BASE_URL: str = "https://api.ollama.com"  # Ollama 雲端 API 端點（標準端點）
    
    # 選擇使用的 AI 服務（qwen, openai, gemini, ollama, ollama_cloud）
    AI_SERVICE: str = "qwen"  # 預設使用通義千問，香港用戶改為 "ollama" 或 "ollama_cloud"
    
    # 圖片服務配置
    UNSPLASH_ACCESS_KEY: str = ""
    PEXELS_API_KEY: str = ""
    PIXABAY_API_KEY: str = ""
    
    # Google Custom Search API（可選，需要 API Key）
    GOOGLE_API_KEY: str = ""
    GOOGLE_SEARCH_ENGINE_ID: str = ""  # Custom Search Engine ID
    
    # 安全配置
    # API Key 認證（可選，如果未設定則不啟用認證）
    API_KEY: str = ""
    
    # 請求限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # CORS 配置
    # 支援格式：
    # 1. JSON 格式: ["http://localhost:5173","http://localhost:3000"]
    # 2. 逗號分隔: http://localhost:5173,http://localhost:3000
    # 注意：生產環境需要包含 Vercel 前端 URL
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ai-agent-webapp-ten.vercel.app",  # Vercel 生產環境
    ]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析 CORS_ORIGINS，支援 JSON 和逗號分隔格式"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # 嘗試解析為 JSON
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # 如果不是 JSON，則按逗號分隔
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # 日誌配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全域設定實例
settings = Settings()


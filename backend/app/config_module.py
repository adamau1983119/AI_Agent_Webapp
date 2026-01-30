"""
應用配置管理
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
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
    
    # DeepSeek AI（OpenAI 兼容 API，推薦）
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"  # 或 "deepseek-chat-v3" 用於最新版本
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1/chat/completions"
    
    # 選擇使用的 AI 服務（qwen, openai, gemini, ollama, ollama_cloud, deepseek）
    AI_SERVICE: str = "deepseek"  # 預設使用 DeepSeek API（推薦）
    
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
    
    # ============================================
    # Phase 2: JWT 認證配置
    # ============================================
    JWT_SECRET: str = ""  # JWT 密鑰（必須設定）
    JWT_ALGORITHM: str = "HS256"  # JWT 演算法
    JWT_EXPIRE_MINUTES: int = 10080  # Token 過期時間（分鐘，預設 7 天）
    
    # ============================================
    # Phase 2: Google OAuth 配置
    # ============================================
    GOOGLE_OAUTH_CLIENT_ID: str = ""
    GOOGLE_OAUTH_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # ============================================
    # Phase 2: Gmail SMTP 配置
    # ============================================
    GMAIL_USER: str = ""
    GMAIL_APP_PASSWORD: str = ""
    
    # ============================================
    # Phase 2: 會員系統配置
    # ============================================
    MAX_USERS: int = 100  # 測試版最大用戶數（100 人限制）
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24  # Email 驗證連結過期時間（小時）
    PASSWORD_RESET_EXPIRE_HOURS: int = 24  # 密碼重設連結過期時間（小時）
    
    # ============================================
    # Phase 5: 社交平台配置
    # ============================================
    # 後端 URL（用於 OAuth 回調）
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    
    # Meta (Instagram + Facebook + Threads)
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    
    # TikTok（可選）
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""
    
    # 請求限流配置
    # 開發環境使用更寬鬆的限制，避免前端輪詢觸發速率限制
    RATE_LIMIT_PER_MINUTE: int = 60  # 預設值（生產環境）
    RATE_LIMIT_PER_HOUR: int = 1000  # 預設值（生產環境）
    
    @model_validator(mode='after')
    def adjust_rate_limit_for_environment(self):
        """根據環境調整速率限制"""
        # 開發環境使用更寬鬆的限制
        if self.ENVIRONMENT == 'development':
            # 只有在使用預設值時才調整（允許環境變數覆蓋）
            if self.RATE_LIMIT_PER_MINUTE == 60:
                object.__setattr__(self, 'RATE_LIMIT_PER_MINUTE', 300)
            if self.RATE_LIMIT_PER_HOUR == 1000:
                object.__setattr__(self, 'RATE_LIMIT_PER_HOUR', 5000)
        return self
    
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
    
    # Redis 配置（快取）
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""  # 可選
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_ENABLED: bool = True  # 是否啟用 Redis（如果 False，則跳過快取）
    
    # Elasticsearch 配置
    ELASTICSEARCH_HOSTS: str = "https://localhost:9200"  # 逗號分隔的多個主機（支援 http:// 或 https://）
    ELASTICSEARCH_INDEX: str = "topics"
    ELASTICSEARCH_TIMEOUT: int = 30  # 增加超時時間以適應 HTTPS
    ELASTICSEARCH_MAX_RETRIES: int = 3
    ELASTICSEARCH_ENABLED: bool = False  # 是否啟用 Elasticsearch（預設 False，使用 MongoDB）
    ELASTICSEARCH_USERNAME: str = "elastic"  # Elasticsearch 用戶名（8.x+ 版本需要）
    ELASTICSEARCH_PASSWORD: str = ""  # Elasticsearch 密碼（8.x+ 版本需要）
    ELASTICSEARCH_USE_SSL: bool = True  # 是否使用 SSL（如果 URL 是 https:// 會自動啟用）
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # 忽略未定義的環境變數，避免錯誤
    )


# 全域設定實例
settings = Settings()


"""
環境變數驗證器
在應用啟動時強制檢查所有關鍵環境變數，避免靜默失敗
"""
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class EnvironmentValidationError(Exception):
    """環境變數驗證錯誤"""
    pass


class EnvironmentValidator:
    """環境變數驗證器"""
    
    @staticmethod
    def validate_all() -> Dict[str, Any]:
        """
        驗證所有關鍵環境變數
        
        Returns:
            驗證結果字典，包含 errors 和 warnings
            
        Raises:
            EnvironmentValidationError: 如果關鍵環境變數缺失
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # 1. 檢查基本配置
        if not settings.ENVIRONMENT:
            errors.append("ENVIRONMENT 未設定")
        elif settings.ENVIRONMENT not in ["development", "production", "staging"]:
            warnings.append(f"ENVIRONMENT 值異常: {settings.ENVIRONMENT}")
        
        # 2. 檢查資料庫配置
        if not settings.MONGODB_URL:
            errors.append("MONGODB_URL 未設定（資料庫連接失敗）")
        elif settings.MONGODB_URL == "mongodb://localhost:27017":
            warnings.append("MONGODB_URL 使用預設值（localhost），生產環境應使用實際連接字串")
        
        # 3. 檢查排程服務配置
        auto_start = getattr(settings, 'AUTO_START_SCHEDULER', 'false').lower()
        if settings.ENVIRONMENT == "production" and auto_start != 'true':
            warnings.append(
                "生產環境下 AUTO_START_SCHEDULER 未設定為 true，"
                "排程服務可能不會自動啟動"
            )
        
        # 4. 檢查 AI 服務配置
        ai_service = settings.AI_SERVICE
        if not ai_service:
            errors.append("AI_SERVICE 未設定")
        else:
            # 檢查對應的 API Key
            if ai_service == "qwen":
                if not settings.QWEN_API_KEY:
                    errors.append("AI_SERVICE=qwen 但 QWEN_API_KEY 未設定")
            elif ai_service == "openai":
                if not settings.OPENAI_API_KEY:
                    errors.append("AI_SERVICE=openai 但 OPENAI_API_KEY 未設定")
            elif ai_service == "gemini":
                if not settings.GEMINI_API_KEY:
                    errors.append("AI_SERVICE=gemini 但 GEMINI_API_KEY 未設定")
            elif ai_service in ["ollama", "ollama_cloud"]:
                if ai_service == "ollama_cloud" and not settings.OLLAMA_API_KEY:
                    warnings.append("OLLAMA_API_KEY 未設定，ollama_cloud 服務可能無法使用")
                # ollama 本地服務不需要 API Key
        
        # 5. 檢查圖片服務配置
        image_services_configured = []
        if settings.UNSPLASH_ACCESS_KEY:
            image_services_configured.append("Unsplash")
        if settings.PEXELS_API_KEY:
            image_services_configured.append("Pexels")
        if settings.PIXABAY_API_KEY:
            image_services_configured.append("Pixabay")
        
        if not image_services_configured:
            errors.append(
                "所有圖片服務的 API Key 都未設定（UNSPLASH_ACCESS_KEY、"
                "PEXELS_API_KEY、PIXABAY_API_KEY），圖片搜尋將完全失敗"
            )
        else:
            logger.info(f"已配置的圖片服務: {', '.join(image_services_configured)}")
        
        # 6. 檢查 CORS 配置
        if not settings.CORS_ORIGINS:
            warnings.append("CORS_ORIGINS 未設定，可能導致前端無法連接")
        
        # 構建結果
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "environment": settings.ENVIRONMENT,
                "ai_service": settings.AI_SERVICE,
                "image_services_count": len(image_services_configured),
                "scheduler_auto_start": auto_start == 'true',
            }
        }
        
        # 記錄結果
        if errors:
            logger.error("=" * 60)
            logger.error("❌ 環境變數驗證失敗")
            logger.error("=" * 60)
            for error in errors:
                logger.error(f"  ❌ {error}")
            logger.error("=" * 60)
        
        if warnings:
            logger.warning("=" * 60)
            logger.warning("⚠️  環境變數警告")
            logger.warning("=" * 60)
            for warning in warnings:
                logger.warning(f"  ⚠️  {warning}")
            logger.warning("=" * 60)
        
        if result["valid"]:
            logger.info("✅ 環境變數驗證通過")
            logger.info(f"   - 環境: {settings.ENVIRONMENT}")
            logger.info(f"   - AI 服務: {settings.AI_SERVICE}")
            logger.info(f"   - 圖片服務: {len(image_services_configured)} 個已配置")
        
        # 如果有錯誤，拋出異常
        if errors:
            error_message = "\n".join([f"  - {e}" for e in errors])
            raise EnvironmentValidationError(
                f"環境變數配置不完整，請檢查以下項目：\n{error_message}"
            )
        
        return result
    
    @staticmethod
    def validate_ai_service() -> bool:
        """驗證 AI 服務配置"""
        ai_service = settings.AI_SERVICE
        
        if ai_service == "qwen":
            return bool(settings.QWEN_API_KEY)
        elif ai_service == "openai":
            return bool(settings.OPENAI_API_KEY)
        elif ai_service == "gemini":
            return bool(settings.GEMINI_API_KEY)
        elif ai_service in ["ollama", "ollama_cloud"]:
            if ai_service == "ollama_cloud":
                return bool(settings.OLLAMA_API_KEY)
            return True  # 本地 ollama 不需要 API Key
        
        return False
    
    @staticmethod
    def validate_image_services() -> bool:
        """驗證圖片服務配置"""
        return bool(
            settings.UNSPLASH_ACCESS_KEY or
            settings.PEXELS_API_KEY or
            settings.PIXABAY_API_KEY
        )
    
    @staticmethod
    def get_validation_summary() -> Dict[str, Any]:
        """取得驗證摘要（不拋出異常）"""
        try:
            return EnvironmentValidator.validate_all()
        except EnvironmentValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "summary": {}
            }


"""
健康檢查 API
"""
from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.database import check_connection
from app.utils.env_validator import EnvironmentValidator

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    # 檢查資料庫連接
    db_status = await check_connection()
    
    # 判斷整體狀態
    overall_status = "healthy" if db_status else "degraded"
    
    return {
        "status": overall_status,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    詳細健康檢查端點
    檢查資料庫、排程、AI 服務、圖片服務狀態
    """
    checks = {
        "database": False,
        "scheduler": False,
        "ai_service": False,
        "image_service": False,
    }
    
    details = {}
    
    # 1. 檢查資料庫
    try:
        db_status = await check_connection()
        checks["database"] = db_status
        details["database"] = {
            "status": "connected" if db_status else "disconnected",
            "url": settings.MONGODB_URL[:20] + "..." if settings.MONGODB_URL else None
        }
    except Exception as e:
        details["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 2. 檢查排程服務
    try:
        from app.services.automation.scheduler import SchedulerService
        scheduler_service = SchedulerService()
        checks["scheduler"] = scheduler_service.is_running
        details["scheduler"] = {
            "status": "running" if scheduler_service.is_running else "stopped",
            "auto_start": getattr(settings, 'AUTO_START_SCHEDULER', 'false').lower() == 'true',
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        details["scheduler"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 3. 檢查 AI 服務
    try:
        from app.services.ai.ai_service_factory import AIServiceFactory
        ai_service = AIServiceFactory.get_service(settings.AI_SERVICE)
        ai_valid = EnvironmentValidator.validate_ai_service()
        checks["ai_service"] = ai_valid
        details["ai_service"] = {
            "status": "configured" if ai_valid else "not_configured",
            "service": settings.AI_SERVICE,
            "api_key_set": ai_valid
        }
    except Exception as e:
        checks["ai_service"] = False
        details["ai_service"] = {
            "status": "error",
            "error": str(e),
            "service": settings.AI_SERVICE
        }
    
    # 4. 檢查圖片服務
    try:
        from app.services.images.image_service import ImageService
        image_service = ImageService()
        image_valid = EnvironmentValidator.validate_image_services()
        checks["image_service"] = image_valid
        
        image_details = {
            "status": "configured" if image_valid else "not_configured",
            "services": {}
        }
        
        # 檢查各個服務
        image_details["services"]["unsplash"] = {
            "configured": bool(settings.UNSPLASH_ACCESS_KEY)
        }
        image_details["services"]["pexels"] = {
            "configured": bool(settings.PEXELS_API_KEY)
        }
        image_details["services"]["pixabay"] = {
            "configured": bool(settings.PIXABAY_API_KEY)
        }
        
        details["image_service"] = image_details
    except Exception as e:
        checks["image_service"] = False
        details["image_service"] = {
            "status": "error",
            "error": str(e)
        }
    
    # 5. 環境變數驗證摘要
    try:
        validation_summary = EnvironmentValidator.get_validation_summary()
        details["environment_validation"] = validation_summary
    except Exception as e:
        details["environment_validation"] = {
            "error": str(e)
        }
    
    # 判斷整體狀態
    all_healthy = all(checks.values())
    overall_status = "healthy" if all_healthy else "degraded"
    
    return {
        "status": overall_status,
        "checks": checks,
        "details": details,
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


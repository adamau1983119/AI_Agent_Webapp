"""
健康檢查 API
"""
from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.database import check_connection

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


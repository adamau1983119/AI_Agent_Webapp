"""
FastAPI 應用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, check_connection
from app.middleware.auth import APIKeyMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用生命週期管理
    - 啟動時：連接 MongoDB、設定日誌
    - 關閉時：斷開 MongoDB 連接
    """
    # 啟動時執行
    # 設定日誌系統
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE if settings.ENVIRONMENT != "development" else None,
    )
    
    # 連接 MongoDB
    await connect_to_mongo()
    yield
    # 關閉時執行
    await close_mongo_connection()


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# 設定 CORS（安全策略）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# 添加請求限流中間件（在 CORS 之後）
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.RATE_LIMIT_PER_HOUR,
)

# 添加 API Key 認證中間件（在限流之後）
if settings.API_KEY:
    app.add_middleware(APIKeyMiddleware)


@app.get("/")
async def root():
    """根路徑"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    db_status = await check_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_status else "disconnected",
    }


# 註冊 API 路由
from app.api.v1 import topics, contents, images, user, health

app.include_router(health.router, prefix="/api/v1")
app.include_router(topics.router, prefix="/api/v1")
app.include_router(contents.router, prefix="/api/v1")
app.include_router(images.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


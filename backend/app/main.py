"""
FastAPI 應用入口
"""
from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, check_connection
from app.middleware.auth import APIKeyMiddleware
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import setup_logging

logger = logging.getLogger(__name__)


class CustomCORSMiddleware(BaseHTTPMiddleware):
    """自定義 CORS 中間件，確保 CORS header 正確設定"""
    
    async def dispatch(self, request: Request, call_next):
        # 獲取請求來源
        origin = request.headers.get("origin")
        
        # 解析允許的來源列表
        allowed_origins = settings.CORS_ORIGINS
        if isinstance(allowed_origins, str):
            allowed_origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
        elif not isinstance(allowed_origins, list):
            allowed_origins = list(allowed_origins) if allowed_origins else []
        
        # 如果沒有設定允許的來源，允許所有來源（開發環境）
        if not allowed_origins:
            allowed_origins = ["*"]
        
        # 處理 OPTIONS 預檢請求
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            # 對於預檢請求，總是設定 CORS header
            if "*" in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif origin and origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            elif origin:
                # 如果 origin 不在列表中，但仍然允許（開發環境）
                response.headers["Access-Control-Allow-Origin"] = origin
                logger.warning(f"⚠️ CORS: 允許未列出的來源 {origin}")
            else:
                # 沒有 origin header，使用第一個允許的來源
                if allowed_origins and allowed_origins[0] != "*":
                    response.headers["Access-Control-Allow-Origin"] = allowed_origins[0]
                else:
                    response.headers["Access-Control-Allow-Origin"] = "*"
            
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key, Accept"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            logger.debug(f"✅ CORS preflight 回應: {origin} -> {response.headers.get('Access-Control-Allow-Origin')}")
            return response
        
        # 處理實際請求
        response = await call_next(request)
        
        # 設定 CORS header（確保所有響應都有）
        if "*" in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
        elif origin and origin in allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        elif origin:
            # 開發環境：允許未列出的來源
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            logger.debug(f"⚠️ CORS: 允許未列出的來源 {origin}")
        else:
            # 沒有 origin，使用第一個允許的來源或 *
            if allowed_origins and allowed_origins[0] != "*":
                response.headers["Access-Control-Allow-Origin"] = allowed_origins[0]
            else:
                response.headers["Access-Control-Allow-Origin"] = "*"
        
        response.headers["Access-Control-Expose-Headers"] = "X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset"
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    應用生命週期管理
    - 啟動時：連接 MongoDB、設定日誌、啟動排程服務
    - 關閉時：斷開 MongoDB 連接、停止排程服務
    """
    # 啟動時執行
    # 設定日誌系統
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE if settings.ENVIRONMENT != "development" else None,
    )
    
    # 1. 環境變數驗證（強制檢查，缺失則阻止啟動）
    try:
        from app.utils.env_validator import EnvironmentValidator
        validation_result = EnvironmentValidator.validate_all()
        logger.info("✅ 環境變數驗證通過")
        if validation_result.get("warnings"):
            logger.warning(f"⚠️  發現 {len(validation_result['warnings'])} 個警告")
    except Exception as e:
        logger.error(f"❌ 環境變數驗證失敗: {e}")
        logger.error("應用程式啟動被阻止，請檢查環境變數配置")
        raise
    
    # 2. 詳細環境變數狀態日誌（僅在開發環境或 DEBUG 模式下顯示詳細資訊）
    # 在開發環境中，這些可選配置的缺失是正常的，使用 DEBUG 級別減少日誌噪音
    if settings.DEBUG or settings.ENVIRONMENT == "development":
        logger.debug("=== 啟動環境變數驗證（詳細） ===")
        logger.debug(f"AI_SERVICE: {settings.AI_SERVICE}")
        
        # DeepSeek 配置
        deepseek_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        if deepseek_key:
            logger.debug("✅ DEEPSEEK_API_KEY 存在")
        else:
            logger.debug("ℹ️ DEEPSEEK_API_KEY 未設定（可選，AI 功能將使用後備方案）")
        
        # Google Custom Search 配置
        google_key = getattr(settings, 'GOOGLE_API_KEY', '')
        if google_key:
            logger.debug("✅ GOOGLE_API_KEY 存在")
        else:
            logger.debug("ℹ️ GOOGLE_API_KEY 未設定（可選）")
        
        google_search_id = getattr(settings, 'GOOGLE_SEARCH_ENGINE_ID', '')
        if google_search_id:
            logger.debug("✅ GOOGLE_SEARCH_ENGINE_ID 存在")
        else:
            logger.debug("ℹ️ GOOGLE_SEARCH_ENGINE_ID 未設定（可選）")
        
        # 其他圖片服務配置
        unsplash_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '')
        if unsplash_key:
            logger.debug("✅ UNSPLASH_ACCESS_KEY 存在")
        else:
            logger.debug("ℹ️ UNSPLASH_ACCESS_KEY 未設定（可選，將使用 DuckDuckGo）")
        
        pexels_key = getattr(settings, 'PEXELS_API_KEY', '')
        if pexels_key:
            logger.debug("✅ PEXELS_API_KEY 存在")
        else:
            logger.debug("ℹ️ PEXELS_API_KEY 未設定（可選）")
        
        pixabay_key = getattr(settings, 'PIXABAY_API_KEY', '')
        if pixabay_key:
            logger.debug("✅ PIXABAY_API_KEY 存在")
        else:
            logger.debug("ℹ️ PIXABAY_API_KEY 未設定（可選）")
        
        logger.debug("=== 環境變數驗證完成 ===")
    else:
        # 生產環境：只記錄已配置的服務
        configured_services = []
        if getattr(settings, 'DEEPSEEK_API_KEY', ''):
            configured_services.append("DeepSeek")
        if getattr(settings, 'GOOGLE_API_KEY', ''):
            configured_services.append("Google Search")
        if getattr(settings, 'UNSPLASH_ACCESS_KEY', '') or getattr(settings, 'PEXELS_API_KEY', '') or getattr(settings, 'PIXABAY_API_KEY', ''):
            configured_services.append("Image Services")
        
        if configured_services:
            logger.info(f"已配置的服務: {', '.join(configured_services)}")
    
    # 連接 MongoDB（使用 app.state 存儲，避免全局變數不同步問題）
    try:
        logger.info("正在建立 MongoDB 連接...")
        sanitized_url = settings.MONGODB_URL[:50] + "..." if len(settings.MONGODB_URL) > 50 else settings.MONGODB_URL
        
        # 建立 MongoDB 客戶端
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=10,
        )
        
        # 測試連接
        await mongo_client.admin.command("ping")
        
        # 取得資料庫實例
        mongo_db = mongo_client[settings.MONGODB_DB_NAME]
        
        # 存儲到 app.state（這是 FastAPI 推薦的方式，避免全局變數不同步）
        # 使用 db 作為簡短別名，方便使用
        app.state.mongo_client = mongo_client
        app.state.mongo_db = mongo_db
        app.state.db = mongo_db  # 簡短別名，方便直接使用
        
        logger.info(f"✅ MongoDB 連接成功: {settings.MONGODB_DB_NAME}")
        logger.info(f"連接字串: {sanitized_url}")
        logger.info(f"資料庫實例 ID: {id(mongo_db)}")
        logger.info(f"app.state.db ID: {id(app.state.db)}")
        logger.info("✅ MongoDB 連接已存儲到 app.state.db，所有端點將使用同一個實例")
        
    except Exception as e:
        # 在開發環境中，連接失敗不會阻止啟動
        if settings.ENVIRONMENT == "development":
            logger.warning(f"⚠️ MongoDB 連接失敗（開發環境允許繼續）: {e}")
            logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
            app.state.mongo_client = None
            app.state.mongo_db = None
        else:
            # 生產環境必須有資料庫連接
            logger.critical(f"🚨 MongoDB 連接失敗，阻止系統啟動: {e}")
            raise
    
    # 調試：輸出 CORS 設定
    logger.info(f"CORS_ORIGINS 設定值: {settings.CORS_ORIGINS}")
    logger.info(f"CORS_ORIGINS 類型: {type(settings.CORS_ORIGINS)}")
    
    # 啟動排程服務（生產環境自動啟動，開發環境可手動啟動）
    scheduler_service = None
    scheduler_monitor = None
    
    # 檢查是否應該啟動排程服務
    # 生產環境或明確設定 AUTO_START_SCHEDULER=true 時啟動
    should_start_scheduler = (
        settings.ENVIRONMENT == "production" or 
        getattr(settings, 'AUTO_START_SCHEDULER', 'false').lower() == 'true'
    )
    
    if should_start_scheduler:
        try:
            from app.services.automation.scheduler import SchedulerService
            from app.services.automation.scheduler_monitor import SchedulerMonitor
            
            scheduler_service = SchedulerService()
            scheduler_service.start()
            logger.info("✅ 排程服務已啟動（生產環境）")
            
            # 啟動監控服務（僅生產環境）
            if settings.ENVIRONMENT == "production":
                scheduler_monitor = SchedulerMonitor(scheduler_service)
                # 在背景任務中啟動監控
                asyncio.create_task(scheduler_monitor.start_monitoring())
                logger.info("✅ 排程監控服務已啟動")
                
                # 確保今日主題已生成（啟動時檢查一次）
                asyncio.create_task(scheduler_monitor.ensure_today_topics())
        except Exception as e:
            logger.error(f"❌ 啟動排程服務失敗: {e}", exc_info=True)
    else:
        # 開發環境：記錄提示，可通過 API 手動啟動
        logger.info("ℹ️ 開發環境：排程服務未自動啟動")
        logger.info("   可通過 POST /api/v1/schedules/start 手動啟動")
        logger.info("   或使用 POST /api/v1/schedules/generate-today 立即生成今日主題")
    
    yield
    
    # 關閉時執行
    # 關閉 MongoDB 連接
    if hasattr(app.state, 'mongo_client') and app.state.mongo_client:
        try:
            app.state.mongo_client.close()
            logger.info("✅ MongoDB 連接已關閉")
        except Exception as e:
            logger.error(f"關閉 MongoDB 連接時發生錯誤: {e}")
    
    # 停止監控服務
    if scheduler_monitor:
        try:
            scheduler_monitor.stop_monitoring()
            logger.info("排程監控服務已停止")
        except Exception as e:
            logger.error(f"停止排程監控服務失敗: {e}")
    
    # 停止排程服務
    if scheduler_service:
        try:
            scheduler_service.stop()
            logger.info("排程服務已停止")
        except Exception as e:
            logger.error(f"停止排程服務失敗: {e}")
    
    # 斷開 MongoDB 連接
    await close_mongo_connection()


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# 設定 CORS（安全策略）
# 調試：輸出 CORS 設定
logger.info(f"設定 CORS，允許的來源: {settings.CORS_ORIGINS}")
logger.info(f"CORS_ORIGINS 類型: {type(settings.CORS_ORIGINS)}")

# 確保 CORS_ORIGINS 是列表格式
cors_origins_list = settings.CORS_ORIGINS
if isinstance(cors_origins_list, str):
    cors_origins_list = [origin.strip() for origin in cors_origins_list.split(',') if origin.strip()]
elif not isinstance(cors_origins_list, list):
    cors_origins_list = list(cors_origins_list) if cors_origins_list else []

logger.info(f"解析後的 CORS_ORIGINS: {cors_origins_list}")

# ⚠️ 重要：中間件執行順序（FastAPI 是後加先執行）
# 為了確保 CORS header 正確設定，CORSMiddleware 必須在 RateLimitMiddleware 之後添加
# 這樣當 RateLimitMiddleware 返回 429 時，CORSMiddleware 已經處理過請求

# 1. 先添加 API Key 認證中間件（最先執行）
if settings.API_KEY:
    app.add_middleware(APIKeyMiddleware)

# 2. 添加請求限流中間件（第二個執行）
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    requests_per_hour=settings.RATE_LIMIT_PER_HOUR,
)

# 3. 添加標準 CORS 中間件（FastAPI 內建，最後執行，確保所有響應都有 CORS header）
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list if cors_origins_list else ["*"],  # 如果為空，允許所有來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有方法（簡化配置）
    allow_headers=["*"],  # 允許所有 header（簡化配置）
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# 注意：移除 CustomCORSMiddleware，避免與 FastAPI CORSMiddleware 衝突
# FastAPI 的 CORSMiddleware 已經足夠處理所有 CORS 需求


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
    db_status, reason = await check_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "database": {
            "status": "connected" if db_status else "disconnected",
            "reason": reason if not db_status else None
        },
    }


# 註冊 API 路由
from app.api.v1 import topics, contents, images, user, health, schedules, interactions, recommendations, discover, validate, test_db

app.include_router(health.router, prefix="/api/v1")
app.include_router(test_db.router, prefix="/api/v1")  # 測試端點，用於驗證資料庫連接
app.include_router(topics.router, prefix="/api/v1")
app.include_router(contents.router, prefix="/api/v1")
app.include_router(images.router, prefix="/api/v1")  # 包含圖片代理端點 /api/v1/images/proxy
app.include_router(user.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(interactions.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(discover.router, prefix="/api/v1")
app.include_router(validate.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


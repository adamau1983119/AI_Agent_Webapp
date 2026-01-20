"""
MongoDB 資料庫連接管理
使用 FastAPI app.state 管理連接，避免全局變數不同步問題
"""
import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError
)
from app.config import settings
from fastapi import Request

# 設定日誌
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_database_from_request(request: Request) -> Optional[AsyncIOMotorDatabase]:
    """
    從 FastAPI Request 的 app.state 獲取資料庫實例
    
    這是推薦的方式，避免全局變數在不同模組實例間不同步的問題
    
    Args:
        request: FastAPI Request 對象
        
    Returns:
        AsyncIOMotorDatabase: 資料庫實例，如果未連接則返回 None
    """
    # 使用 app.state.db（與 main.py 中存儲的名稱一致）
    if hasattr(request.app.state, 'db') and request.app.state.db is not None:
        return request.app.state.db
    return None


async def get_database_dependency(request: Request) -> AsyncIOMotorDatabase:
    """
    FastAPI 依賴注入函數，用於獲取資料庫實例
    
    使用方式：
        @router.get("/endpoint")
        async def my_endpoint(db: AsyncIOMotorDatabase = Depends(get_database_dependency)):
            # 使用 db
            pass
    
    Args:
        request: FastAPI Request 對象
        
    Returns:
        AsyncIOMotorDatabase: 資料庫實例
        
    Raises:
        HTTPException: 如果資料庫未連接
    """
    from fastapi import HTTPException
    
    db = get_database_from_request(request)
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="資料庫未連接，請檢查 MongoDB 配置"
        )
    return db


def get_client_from_request(request: Request) -> Optional[AsyncIOMotorClient]:
    """
    從 FastAPI Request 的 app.state 獲取 MongoDB 客戶端實例
    
    Args:
        request: FastAPI Request 對象
        
    Returns:
        AsyncIOMotorClient: 客戶端實例，如果未連接則返回 None
    """
    # 使用 is not None 避免真值測試錯誤
    if hasattr(request.app.state, 'mongo_client') and request.app.state.mongo_client is not None:
        return request.app.state.mongo_client
    return None


async def check_connection_from_request(request: Request) -> tuple[bool, str]:
    """
    從 FastAPI Request 檢查 MongoDB 連接狀態
    
    Args:
        request: FastAPI Request 對象
        
    Returns:
        tuple[bool, str]: (是否連接, 錯誤原因或 "connected")
    """
    try:
        # 直接從 app.state 獲取（最簡單直接的方式）
        has_db = hasattr(request.app.state, 'db') and request.app.state.db is not None
        has_mongo_client = hasattr(request.app.state, 'mongo_client') and request.app.state.mongo_client is not None
        
        logger.debug(f"檢查 app.state: has_db={has_db}, has_mongo_client={has_mongo_client}")
        
        if not has_db or not has_mongo_client:
            reason = "資料庫客戶端未初始化（app.state.db 或 app.state.mongo_client 不存在）"
            logger.warning(f"MongoDB 連接檢查失敗: {reason}")
            return False, reason
        
        # 獲取實例
        client = request.app.state.mongo_client
        db = request.app.state.db
        
        logger.debug(f"資料庫實例 ID: {id(db)}, 客戶端 ID: {id(client)}")
        
        # 執行 ping 命令測試連接
        await client.admin.command("ping")
        logger.debug("MongoDB 連接健康檢查通過")
        return True, "connected"
    except ConnectionFailure as e:
        reason = f"連接失敗: {str(e)}"
        logger.warning(f"MongoDB 連接健康檢查失敗: {reason}")
        return False, reason
    except Exception as e:
        reason = f"未知錯誤: {type(e).__name__}: {str(e)}"
        logger.warning(f"MongoDB 連接健康檢查失敗: {reason}")
        return False, reason


# 保留舊的全局變數方式作為向後兼容（不推薦使用）
client: Optional[AsyncIOMotorClient] = None
database: Optional[AsyncIOMotorDatabase] = None
_connection_attempts = 0


def _validate_connection_string(url: str) -> bool:
    """
    驗證 MongoDB 連接字串格式
    
    Args:
        url: MongoDB 連接字串
        
    Returns:
        bool: 連接字串是否有效
    """
    if not url:
        logger.error("MongoDB 連接字串為空")
        return False
    
    # 檢查基本格式
    if not (url.startswith("mongodb://") or url.startswith("mongodb+srv://")):
        logger.error(f"MongoDB 連接字串格式錯誤，應以 mongodb:// 或 mongodb+srv:// 開頭")
        return False
    
    return True


def _sanitize_url_for_logging(url: str) -> str:
    """
    清理連接字串用於日誌記錄（隱藏密碼）
    
    Args:
        url: MongoDB 連接字串
        
    Returns:
        str: 清理後的連接字串
    """
    try:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(url)
        
        # 如果有用戶名和密碼，只顯示用戶名
        if parsed.username:
            # 只保留用戶名，密碼用 *** 替換
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            
            # 重建 URL
            sanitized = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return sanitized
        return url
    except Exception:
        # 如果解析失敗，返回前20個字符
        return url[:20] + "..." if len(url) > 20 else url


# 保留舊的連接函數作為向後兼容（不推薦使用）
async def connect_to_mongo(max_retries: int = 3, delay: int = 2):
    """
    舊版 MongoDB 連接函數（保留作為向後兼容）
    
    注意：推薦使用 app.state 方式，而不是全局變數
    """
    global client, database, _connection_attempts
    
    if not _validate_connection_string(settings.MONGODB_URL):
        error_msg = "MongoDB 連接字串格式無效"
        if settings.ENVIRONMENT == "development":
            logger.warning(f"⚠️ {error_msg}，開發環境允許繼續啟動")
            return None
        else:
            raise ConfigurationError(error_msg)
    
    sanitized_url = _sanitize_url_for_logging(settings.MONGODB_URL)
    _connection_attempts = 0
    
    for attempt in range(1, max_retries + 1):
        _connection_attempts = attempt
        try:
            logger.info(f"嘗試連接 MongoDB (第 {attempt}/{max_retries} 次)...")
            logger.debug(f"連接字串: {sanitized_url}")
            
            client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10,
            )
            
            await client.admin.command("ping")
            database = client[settings.MONGODB_DB_NAME]
            
            logger.info(f"✅ 成功連接到 MongoDB: {settings.MONGODB_DB_NAME}")
            logger.info(f"連接字串: {sanitized_url}")
            logger.info(f"連接嘗試次數: {attempt}")
            
            return database
            
        except OperationFailure as e:
            error_msg = str(e)
            if "authentication failed" in error_msg.lower() or "bad auth" in error_msg.lower():
                logger.error(f"❌ MongoDB 認證失敗 (第 {attempt} 次嘗試)")
                logger.error("可能原因：")
                logger.error("  1. 用戶名或密碼錯誤")
                logger.error("  2. 用戶權限不足")
                logger.error("  3. 資料庫名稱與用戶授權不一致")
                logger.error("  4. 連接字串中的特殊字符未正確 URL 編碼")
                
                if attempt < max_retries:
                    logger.info(f"等待 {delay} 秒後重試...")
                    await asyncio.sleep(delay)
                else:
                    if settings.ENVIRONMENT == "development":
                        logger.warning("⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動")
                        logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
                        client = None
                        database = None
                        return None
                    else:
                        logger.critical("🚨 生產環境：MongoDB 連接失敗，阻止系統啟動")
                        raise ConnectionFailure(f"MongoDB 認證失敗，已重試 {max_retries} 次: {str(e)}")
            else:
                logger.error(f"❌ MongoDB 操作失敗 (第 {attempt} 次嘗試): {str(e)}")
                if attempt < max_retries:
                    logger.info(f"等待 {delay} 秒後重試...")
                    await asyncio.sleep(delay)
                else:
                    if settings.ENVIRONMENT == "development":
                        logger.warning("⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動")
                        logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
                        client = None
                        database = None
                        return None
                    else:
                        raise OperationFailure(f"MongoDB 操作失敗，已重試 {max_retries} 次: {str(e)}")
                        
        except ServerSelectionTimeoutError as e:
            logger.error(f"❌ MongoDB 服務器選擇超時 (第 {attempt} 次嘗試): {str(e)}")
            if attempt < max_retries:
                logger.info(f"等待 {delay} 秒後重試...")
                await asyncio.sleep(delay)
            else:
                if settings.ENVIRONMENT == "development":
                    logger.warning("⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動")
                    logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
                    client = None
                    database = None
                    return None
                else:
                    raise ServerSelectionTimeoutError(f"MongoDB 服務器選擇超時，已重試 {max_retries} 次: {str(e)}")
                    
        except ConnectionFailure as e:
            logger.error(f"❌ MongoDB 連接失敗 (第 {attempt} 次嘗試): {str(e)}")
            if attempt < max_retries:
                logger.info(f"等待 {delay} 秒後重試...")
                await asyncio.sleep(delay)
            else:
                if settings.ENVIRONMENT == "development":
                    logger.warning("⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動")
                    logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
                    client = None
                    database = None
                    return None
                else:
                    logger.critical("🚨 生產環境：MongoDB 連接失敗，阻止系統啟動")
                    raise ConnectionFailure(f"MongoDB 連接失敗，已重試 {max_retries} 次: {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ MongoDB 連接發生未知錯誤 (第 {attempt} 次嘗試): {type(e).__name__}: {str(e)}")
            if attempt < max_retries:
                logger.info(f"等待 {delay} 秒後重試...")
                await asyncio.sleep(delay)
            else:
                if settings.ENVIRONMENT == "development":
                    logger.warning("⚠️ 開發環境：MongoDB 連接失敗，但允許系統繼續啟動")
                    logger.warning("⚠️ 注意：資料庫相關功能將無法使用")
                    client = None
                    database = None
                    return None
                else:
                    logger.critical("🚨 生產環境：MongoDB 連接失敗，阻止系統啟動")
                    raise ConnectionFailure(f"MongoDB 連接發生未知錯誤，已重試 {max_retries} 次: {str(e)}")


async def close_mongo_connection():
    """
    關閉 MongoDB 連接（舊版，保留作為向後兼容）
    """
    global client
    if client:
        client.close()
        logger.info("MongoDB 連接已關閉")


async def get_database() -> AsyncIOMotorDatabase:
    """
    取得資料庫實例（舊版，保留作為向後兼容）
    
    注意：推薦使用 get_database_from_request() 從 app.state 獲取
    
    Returns:
        AsyncIOMotorDatabase: 資料庫實例
        
    Raises:
        ConnectionFailure: 如果資料庫未連接
    """
    global database
    if database is None:
        # 在開發環境中，嘗試重新連接
        if settings.ENVIRONMENT == "development":
            logger.warning("資料庫未連接，嘗試重新連接...")
            try:
                await connect_to_mongo()
                if database is None:
                    raise ConnectionFailure("資料庫未連接，且重新連接失敗")
            except Exception as e:
                logger.error(f"重新連接失敗: {e}")
                raise ConnectionFailure(f"資料庫未連接，且重新連接失敗: {e}")
        else:
            raise ConnectionFailure("資料庫未連接，請先調用 connect_to_mongo()")
    
    return database


# 保留舊的檢查函數作為向後兼容
async def check_connection() -> tuple[bool, str]:
    """
    檢查 MongoDB 連接狀態（舊版，保留作為向後兼容）
    
    注意：推薦使用 check_connection_from_request() 從 app.state 檢查
    """
    global client, database
    try:
        if client is None or database is None:
            reason = "資料庫客戶端未初始化"
            logger.debug(f"MongoDB 連接檢查失敗: {reason}")
            return False, reason
        
        await client.admin.command("ping")
        logger.debug("MongoDB 連接健康檢查通過")
        return True, "connected"
    except ConnectionFailure as e:
        reason = f"連接失敗: {str(e)}"
        logger.warning(f"MongoDB 連接健康檢查失敗: {reason}")
        return False, reason
    except Exception as e:
        reason = f"未知錯誤: {type(e).__name__}: {str(e)}"
        logger.warning(f"MongoDB 連接健康檢查失敗: {reason}")
        return False, reason

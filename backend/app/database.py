"""
MongoDB 資料庫連接管理
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
import logging

# 設定日誌
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全域資料庫客戶端和資料庫實例
client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """
    連接到 MongoDB
    
    Raises:
        ConnectionFailure: 連接失敗時拋出異常
    """
    global client, database
    
    try:
        # 建立 MongoDB 客戶端
        client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 秒超時
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
        )
        
        # 測試連接
        await client.admin.command("ping")
        
        # 取得資料庫實例
        database = client[settings.MONGODB_DB_NAME]
        
        logger.info(f"成功連接到 MongoDB: {settings.MONGODB_DB_NAME}")
        logger.info(f"MongoDB URL: {settings.MONGODB_URL}")
        
        return database
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB 連接失敗: {e}")
        raise ConnectionFailure(f"無法連接到 MongoDB: {e}")
    except Exception as e:
        logger.error(f"MongoDB 連接發生未知錯誤: {e}")
        raise


async def close_mongo_connection():
    """
    關閉 MongoDB 連接
    """
    global client
    
    if client:
        client.close()
        logger.info("MongoDB 連接已關閉")


async def get_database() -> AsyncIOMotorDatabase:
    """
    取得資料庫實例
    
    Returns:
        AsyncIOMotorDatabase: 資料庫實例
        
    Raises:
        ConnectionFailure: 如果資料庫未連接
    """
    if database is None:
        raise ConnectionFailure("資料庫未連接，請先調用 connect_to_mongo()")
    
    return database


async def check_connection() -> bool:
    """
    檢查 MongoDB 連接狀態
    
    Returns:
        bool: 連接是否正常
    """
    try:
        if client is None:
            return False
        
        await client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB 連接檢查失敗: {e}")
        return False

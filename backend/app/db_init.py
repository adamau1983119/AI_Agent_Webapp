"""
資料庫初始化腳本
用於建立索引和初始資料
"""
import asyncio
import logging
from app.database import connect_to_mongo, get_database, close_mongo_connection
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_indexes():
    """
    建立資料庫索引
    """
    try:
        db = await get_database()
        
        # Topics 集合索引
        topics_collection = db["topics"]
        
        # 唯一索引：id
        await topics_collection.create_index([("id", 1)], unique=True)
        
        # 複合索引：category + status
        await topics_collection.create_index([("category", 1), ("status", 1)])
        
        # 時間排序索引：generated_at（降序）
        await topics_collection.create_index([("generated_at", -1)])
        
        # 複合索引：status + generated_at
        await topics_collection.create_index([("status", 1), ("generated_at", -1)])
        
        logger.info("✅ Topics 集合索引建立完成")
        
        # Contents 集合索引
        contents_collection = db["contents"]
        
        # 唯一索引：id
        await contents_collection.create_index([("id", 1)], unique=True)
        
        # 外鍵索引：topic_id
        await contents_collection.create_index([("topic_id", 1)])
        
        # 複合索引：topic_id + version
        await contents_collection.create_index([("topic_id", 1), ("version", -1)])
        
        logger.info("✅ Contents 集合索引建立完成")
        
        # Images 集合索引
        images_collection = db["images"]
        
        # 唯一索引：id
        await images_collection.create_index([("id", 1)], unique=True)
        
        # 複合索引：topic_id + order
        await images_collection.create_index([("topic_id", 1), ("order", 1)])
        
        # 來源索引：source
        await images_collection.create_index([("source", 1)])
        
        logger.info("✅ Images 集合索引建立完成")
        
        # UserPreferences 集合索引
        user_preferences_collection = db["user_preferences"]
        
        # 唯一索引：id
        await user_preferences_collection.create_index([("id", 1)], unique=True)
        
        logger.info("✅ UserPreferences 集合索引建立完成")
        
        # AuditLogs 集合索引
        audit_logs_collection = db["audit_logs"]
        
        # 唯一索引：id
        await audit_logs_collection.create_index([("id", 1)], unique=True)
        
        # 複合索引：topic_id + timestamp
        await audit_logs_collection.create_index([("topic_id", 1), ("timestamp", -1)])
        
        # 複合索引：action + timestamp
        await audit_logs_collection.create_index([("action", 1), ("timestamp", -1)])
        
        logger.info("✅ AuditLogs 集合索引建立完成")
        
        logger.info("🎉 所有索引建立完成！")
        
    except Exception as e:
        logger.error(f"❌ 建立索引時發生錯誤: {e}")
        raise


async def create_default_user_preferences():
    """
    建立預設使用者偏好設定
    """
    try:
        db = await get_database()
        user_preferences_collection = db["user_preferences"]
        
        # 檢查是否已存在預設使用者
        existing_user = await user_preferences_collection.find_one({"id": "user_default"})
        
        if existing_user:
            logger.info("✅ 預設使用者偏好已存在，跳過建立")
            return
        
        # 建立預設使用者偏好
        default_preferences = {
            "id": "user_default",
            "fashion_weight": 0.5,
            "food_weight": 0.3,
            "trend_weight": 0.2,
            "keywords": [],
            "excluded_keywords": [],
            "source_preferences": {
                "fashion": [],
                "food": [],
                "trend": []
            },
            "updated_at": None
        }
        
        await user_preferences_collection.insert_one(default_preferences)
        logger.info("✅ 預設使用者偏好建立完成")
        
    except Exception as e:
        logger.error(f"❌ 建立預設使用者偏好時發生錯誤: {e}")
        raise


async def init_database():
    """
    初始化資料庫
    """
    try:
        logger.info("開始初始化資料庫...")
        logger.info(f"資料庫名稱: {settings.MONGODB_DB_NAME}")
        logger.info(f"MongoDB URL: {settings.MONGODB_URL}")
        
        # 連接資料庫
        await connect_to_mongo()
        
        # 建立索引
        await create_indexes()
        
        # 建立預設使用者偏好
        await create_default_user_preferences()
        
        logger.info("✅ 資料庫初始化完成！")
        
    except Exception as e:
        logger.error(f"❌ 資料庫初始化失敗: {e}")
        raise
    finally:
        # 關閉連接
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(init_database())

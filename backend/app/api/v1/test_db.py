"""
資料庫測試端點
用於驗證 app.state.db 是否正常工作
"""
from fastapi import APIRouter, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/test", tags=["test"])


@router.get("/db")
async def test_db(request: Request):
    """
    測試資料庫連接和操作
    
    這是一個最小可行測試，確認 app.state.db 是否正常工作
    """
    try:
        # 直接從 app.state 獲取資料庫
        if not hasattr(request.app.state, 'db') or request.app.state.db is None:
            return {
                "status": "failed",
                "message": "app.state.db 未初始化",
                "has_db_attr": hasattr(request.app.state, 'db'),
                "db_value": None
            }
        
        db: AsyncIOMotorDatabase = request.app.state.db
        
        # 記錄實例 ID
        db_id = id(db)
        logger.info(f"測試端點 - 資料庫實例 ID: {db_id}")
        
        # 測試基本操作：計算 topics 集合的文檔數量
        topics_count = await db["topics"].count_documents({})
        
        # 測試連接：執行 ping
        await request.app.state.mongo_client.admin.command("ping")
        
        return {
            "status": "ok",
            "message": "資料庫連接和操作測試成功",
            "db_instance_id": db_id,
            "topics_count": topics_count,
            "database_name": db.name,
            "client_id": id(request.app.state.mongo_client) if hasattr(request.app.state, 'mongo_client') else None
        }
    except Exception as e:
        logger.error(f"測試資料庫時發生錯誤: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "資料庫測試失敗",
            "error": str(e),
            "error_type": type(e).__name__
        }


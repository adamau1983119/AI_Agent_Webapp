"""
測試 MongoDB 連接（簡化版）
"""
import asyncio
import sys
from app.database import connect_to_mongo, check_connection, close_mongo_connection
from app.config import settings


async def test():
    print("=" * 50)
    print("MongoDB 連接測試")
    print("=" * 50)
    print(f"MongoDB URL: {settings.MONGODB_URL[:60]}...")
    print(f"資料庫名稱: {settings.MONGODB_DB_NAME}")
    print("-" * 50)
    
    try:
        print("正在連接 MongoDB...")
        await connect_to_mongo()
        print("✅ MongoDB 連接成功！")
        
        is_connected = await check_connection()
        if is_connected:
            print("✅ 連接狀態正常")
        else:
            print("❌ 連接狀態異常")
            return False
        
        from app.database import get_database
        db = await get_database()
        collections = await db.list_collection_names()
        print(f"✅ 現有集合: {collections if collections else '無'}")
        
        result = await db.command("ping")
        print(f"✅ Ping 測試成功")
        
        print("\n" + "=" * 50)
        print("✅ 所有測試通過！")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ 連接失敗: {e}")
        print("\n請檢查：")
        print("1. 虛擬環境是否已啟動")
        print("2. .env 檔案中的 MONGODB_URL 是否正確")
        print("3. 網路連接是否正常")
        print("4. IP 地址是否已加入白名單")
        return False
    finally:
        await close_mongo_connection()
        print("\n連接已關閉")


if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)

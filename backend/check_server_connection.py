"""檢查服務器進程中的連接狀態"""
import asyncio
import sys
import os

# 模擬服務器進程的導入
sys.path.insert(0, os.path.abspath('.'))

from app.database import check_connection, client, database, connect_to_mongo
from app.config import settings

async def check():
    print("=" * 60)
    print("檢查服務器進程中的連接狀態")
    print("=" * 60)
    
    print(f"\n1. 環境變數:")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   MONGODB_URL: {settings.MONGODB_URL[:50]}...")
    print(f"   MONGODB_DB_NAME: {settings.MONGODB_DB_NAME}")
    
    print(f"\n2. 全局變數初始狀態:")
    print(f"   client: {client}")
    print(f"   database: {database}")
    
    print(f"\n3. 檢查連接狀態:")
    is_connected, reason = await check_connection()
    print(f"   結果: {is_connected}, {reason}")
    
    print(f"\n4. 全局變數狀態（檢查後）:")
    print(f"   client: {client}")
    print(f"   database: {database}")
    
    if is_connected:
        print(f"\n5. 測試資料庫操作:")
        try:
            result = await database.list_collection_names()
            print(f"   集合列表: {result}")
        except Exception as e:
            print(f"   錯誤: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(check())


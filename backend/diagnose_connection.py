"""診斷資料庫連接狀態"""
import asyncio
import sys
from app.database import client, database, check_connection, connect_to_mongo

async def diagnose():
    print("=" * 60)
    print("MongoDB 連接診斷")
    print("=" * 60)
    
    print(f"\n1. 全局變數狀態:")
    print(f"   client: {client}")
    print(f"   database: {database}")
    
    print(f"\n2. 檢查連接狀態:")
    is_connected, reason = await check_connection()
    print(f"   連接狀態: {is_connected}")
    print(f"   原因: {reason}")
    
    print(f"\n3. 檢查全局變數狀態（檢查後）:")
    print(f"   client: {client}")
    print(f"   database: {database}")
    
    if not is_connected:
        print(f"\n4. 嘗試手動連接:")
        try:
            result = await connect_to_mongo(max_retries=1, delay=1)
            print(f"   連接結果: {result}")
            is_connected2, reason2 = await check_connection()
            print(f"   重新檢查: {is_connected2}, {reason2}")
        except Exception as e:
            print(f"   連接失敗: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(diagnose())


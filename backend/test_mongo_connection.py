"""測試 MongoDB 連接"""
import asyncio
import sys
from app.database import connect_to_mongo, check_connection

async def test_connection():
    """測試連接"""
    print("Testing MongoDB connection...")
    print("=" * 60)
    
    try:
        # 嘗試連接
        await connect_to_mongo()
        print("✅ connect_to_mongo() completed")
        
        # 檢查連接狀態
        is_connected, reason = await check_connection()
        print(f"Connection status: {is_connected}")
        print(f"Reason: {reason}")
        
        if is_connected:
            print("\n✅ MongoDB connection successful!")
        else:
            print(f"\n❌ MongoDB connection failed: {reason}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())


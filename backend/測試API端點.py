"""
測試 API 端點
"""
import asyncio
import httpx
from app.database import connect_to_mongo, close_mongo_connection
from app.services.repositories.topic_repository import TopicRepository
from app.models.topic import Category, Status
from datetime import datetime


async def test_api():
    """測試 API 端點"""
    base_url = "http://localhost:8000"
    
    print("=" * 50)
    print("API 端點測試")
    print("=" * 50)
    
    # 連接資料庫
    await connect_to_mongo()
    
    try:
        # 建立測試主題
        topic_repo = TopicRepository()
        
        test_topic = {
            "id": "test_topic_001",
            "title": "測試主題 - 2024 春夏時尚趨勢",
            "category": Category.FASHION.value,
            "status": Status.PENDING.value,
            "source": "Test",
            "sources": [],
            "generated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await topic_repo.create_topic(test_topic)
        print("✅ 測試主題已建立")
        
        # 測試 API
        async with httpx.AsyncClient() as client:
            # 1. 測試取得主題列表
            print("\n1. 測試取得主題列表...")
            response = await client.get(f"{base_url}/api/v1/topics?page=1&limit=10")
            print(f"   狀態碼: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功，取得 {len(data.get('data', []))} 個主題")
            else:
                print(f"   ❌ 失敗: {response.text}")
            
            # 2. 測試取得主題詳情
            print("\n2. 測試取得主題詳情...")
            response = await client.get(f"{base_url}/api/v1/topics/test_topic_001")
            print(f"   狀態碼: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ 成功")
            else:
                print(f"   ❌ 失敗: {response.text}")
            
            # 3. 測試健康檢查
            print("\n3. 測試健康檢查...")
            response = await client.get(f"{base_url}/health")
            print(f"   狀態碼: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ 成功: {data}")
            else:
                print(f"   ❌ 失敗: {response.text}")
        
        print("\n" + "=" * 50)
        print("✅ API 測試完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(test_api())

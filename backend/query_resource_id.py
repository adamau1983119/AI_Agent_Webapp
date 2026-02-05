"""
查詢資源 ID 工具
用於查詢指定 ID 對應的主題、內容或圖片
"""
import asyncio
import sys
from app.database import connect_to_mongo, close_mongo_connection
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository
from bson import ObjectId
import json

# 確保輸出使用 UTF-8 編碼
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

async def query_resource(resource_id: str):
    """查詢資源"""
    print(f"🔍 查詢資源 ID: {resource_id}")
    print("=" * 60)
    
    try:
        # 連接資料庫
        await connect_to_mongo()
        print("✅ 資料庫連接成功\n")
        
        topic_repo = TopicRepository()
        content_repo = ContentRepository()
        image_repo = ImageRepository()
        
        found = False
        
        # 1. 嘗試作為主題 ID 查詢
        print("1. 查詢主題...")
        topic = await topic_repo.get_topic_by_id(resource_id)
        if topic:
            found = True
            print(f"   ✅ 找到主題:")
            print(f"   - ID: {topic.get('id', 'N/A')}")
            print(f"   - 標題: {topic.get('title', 'N/A')}")
            print(f"   - 分類: {topic.get('category', 'N/A')}")
            print(f"   - 狀態: {topic.get('status', 'N/A')}")
            print(f"   - 生成時間: {topic.get('generated_at', 'N/A')}")
            if topic.get('_id'):
                print(f"   - MongoDB _id: {topic.get('_id')}")
        else:
            print("   ❌ 未找到主題")
        
        # 2. 嘗試作為內容 ID 查詢
        print("\n2. 查詢內容...")
        content = await content_repo.get_content_by_id(resource_id)
        if content:
            found = True
            print(f"   ✅ 找到內容:")
            print(f"   - ID: {content.get('id', 'N/A')}")
            print(f"   - Topic ID: {content.get('topic_id', 'N/A')}")
            print(f"   - 版本: {content.get('version', 'N/A')}")
            print(f"   - 字數: {content.get('word_count', 0)}")
            if content.get('_id'):
                print(f"   - MongoDB _id: {content.get('_id')}")
        else:
            # 嘗試通過 topic_id 查詢
            content_by_topic = await content_repo.get_content_by_topic_id(resource_id)
            if content_by_topic:
                found = True
                print(f"   ✅ 找到內容（通過 topic_id）:")
                print(f"   - ID: {content_by_topic.get('id', 'N/A')}")
                print(f"   - Topic ID: {content_by_topic.get('topic_id', 'N/A')}")
                print(f"   - 版本: {content_by_topic.get('version', 'N/A')}")
                print(f"   - 字數: {content_by_topic.get('word_count', 0)}")
                if content_by_topic.get('_id'):
                    print(f"   - MongoDB _id: {content_by_topic.get('_id')}")
            else:
                print("   ❌ 未找到內容")
        
        # 3. 嘗試作為 MongoDB ObjectId 查詢（直接查詢 _id）
        print("\n3. 嘗試作為 MongoDB ObjectId 查詢...")
        try:
            # 檢查是否是有效的 ObjectId
            if len(resource_id) == 24:
                object_id = ObjectId(resource_id)
                
                # 查詢 topics 集合
                from app.database import get_database
                db = await get_database()
                topic_by_object_id = await db.topics.find_one({"_id": object_id})
                if topic_by_object_id:
                    found = True
                    print(f"   ✅ 在 topics 集合中找到（通過 _id）:")
                    print(f"   - MongoDB _id: {topic_by_object_id.get('_id')}")
                    print(f"   - ID: {topic_by_object_id.get('id', 'N/A')}")
                    print(f"   - 標題: {topic_by_object_id.get('title', 'N/A')}")
                
                # 查詢 contents 集合
                content_by_object_id = await db.contents.find_one({"_id": object_id})
                if content_by_object_id:
                    found = True
                    print(f"   ✅ 在 contents 集合中找到（通過 _id）:")
                    print(f"   - MongoDB _id: {content_by_object_id.get('_id')}")
                    print(f"   - ID: {content_by_object_id.get('id', 'N/A')}")
                    print(f"   - Topic ID: {content_by_object_id.get('topic_id', 'N/A')}")
                
                # 查詢 images 集合
                image_by_object_id = await db.images.find_one({"_id": object_id})
                if image_by_object_id:
                    found = True
                    print(f"   ✅ 在 images 集合中找到（通過 _id）:")
                    print(f"   - MongoDB _id: {image_by_object_id.get('_id')}")
                    print(f"   - ID: {image_by_object_id.get('id', 'N/A')}")
                    print(f"   - Topic ID: {image_by_object_id.get('topic_id', 'N/A')}")
                    print(f"   - URL: {image_by_object_id.get('url', 'N/A')[:60]}...")
                
                if not (topic_by_object_id or content_by_object_id or image_by_object_id):
                    print("   ❌ 未在任何集合中找到（通過 _id）")
        except Exception as e:
            print(f"   ⚠️ ObjectId 查詢失敗: {e}")
        
        # 4. 查詢圖片（通過 topic_id）
        print("\n4. 查詢圖片...")
        images = await image_repo.get_images_by_topic_id(resource_id)
        if images:
            found = True
            print(f"   ✅ 找到 {len(images)} 張圖片（通過 topic_id）:")
            for idx, img in enumerate(images[:5], 1):
                print(f"   - 圖片 {idx}: {img.get('url', 'N/A')[:60]}...")
        
        print("\n" + "=" * 60)
        if found:
            print("✅ 查詢完成：找到相關資源")
        else:
            print("❌ 查詢完成：未找到任何資源")
            print("\n💡 提示：")
            print("   - 確認 ID 是否正確")
            print("   - 確認資料庫是否已連接")
            print("   - 確認資源是否存在")
        
        await close_mongo_connection()
        
    except Exception as e:
        print(f"\n❌ 查詢失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        resource_id = sys.argv[1]
    else:
        # 使用預設 ID（從用戶輸入）
        resource_id = "6948c5c9fcd51e1e52696159"
    
    asyncio.run(query_resource(resource_id))


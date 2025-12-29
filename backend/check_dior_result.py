"""
檢查 Dior Sample 執行結果
"""
import asyncio
import json
import sys
from pathlib import Path
from app.database import connect_to_mongo
from app.services.repositories.topic_repository import TopicRepository
from app.services.repositories.content_repository import ContentRepository
from app.services.repositories.image_repository import ImageRepository

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def check_result():
    """檢查執行結果"""
    print("=" * 60)
    print("檢查 Dior Sample 執行結果")
    print("=" * 60)
    
    # 1. 檢查結果檔案
    print("\n1. 檢查結果檔案...")
    result_file = Path("dior_sample_result.json")
    if result_file.exists():
        print("   [OK] 結果檔案存在: dior_sample_result.json")
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                result = json.load(f)
            print(f"   [OK] 檔案內容有效")
            print(f"   - 主題 ID: {result.get('topic', {}).get('id', 'N/A')}")
            print(f"   - 內容字數: {result.get('content', {}).get('word_count', 0)}")
            print(f"   - 圖片數量: {len(result.get('images', []))}")
        except Exception as e:
            print(f"   [ERROR] 讀取檔案失敗: {e}")
    else:
        print("   [NOT FOUND] 結果檔案不存在")
    
    # 2. 檢查資料庫
    print("\n2. 檢查資料庫記錄...")
    try:
        await connect_to_mongo()
        print("   [OK] 資料庫連接成功")
        
        topic_repo = TopicRepository()
        content_repo = ContentRepository()
        image_repo = ImageRepository()
        
        topic_id = "dior_2026_spring_summer"
        
        # 檢查主題
        topic = await topic_repo.get_topic_by_id(topic_id)
        if topic:
            print(f"   [OK] 主題存在: {topic.get('title', 'N/A')}")
        else:
            print(f"   [NOT FOUND] 主題不存在: {topic_id}")
        
        # 檢查內容
        content = await content_repo.get_content_by_topic_id(topic_id)
        if content:
            print(f"   [OK] 內容存在")
            print(f"   - 短文長度: {len(content.get('article', ''))} 字")
            print(f"   - 腳本長度: {len(content.get('script', ''))} 字")
        else:
            print(f"   [NOT FOUND] 內容不存在")
        
        # 檢查圖片
        images = await image_repo.get_images_by_topic_id(topic_id)
        if images:
            print(f"   [OK] 圖片存在: {len(images)} 張")
            for idx, img in enumerate(images[:3], 1):
                print(f"   - 圖片 {idx}: {img.get('url', 'N/A')[:60]}...")
        else:
            print(f"   [NOT FOUND] 圖片不存在")
        
        from app.database import close_mongo_connection
        await close_mongo_connection()
        
    except Exception as e:
        print(f"   [ERROR] 資料庫檢查失敗: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("檢查完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_result())


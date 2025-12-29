"""
測試主題 API 端點
"""
import asyncio
import sys
import os
import httpx

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_topic_api():
    """測試主題 API"""
    base_url = "http://localhost:8000/api/v1"
    topic_id = "dior_2026_spring_summer"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 測試取得主題詳情
            print(f"測試取得主題詳情: {topic_id}")
            response = await client.get(f"{base_url}/topics/{topic_id}")
            
            print(f"狀態碼: {response.status_code}")
            print(f"回應標頭: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功取得主題詳情")
                print(f"主題標題: {data.get('title', 'N/A')}")
                print(f"內容: {'有' if data.get('content') else '無'}")
                print(f"圖片數量: {len(data.get('images', []))}")
            else:
                print(f"❌ 錯誤: {response.status_code}")
                print(f"錯誤訊息: {response.text}")
                
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_topic_api())


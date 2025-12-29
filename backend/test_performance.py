"""
效能測試腳本
測試冷啟動和 API 回應時間
"""
import asyncio
import httpx
import time
from statistics import mean, median
from datetime import datetime
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 從環境變數讀取配置
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")
API_KEY = os.getenv("API_KEY", "")

async def test_endpoint(client: httpx.AsyncClient, endpoint: str, iterations: int = 10):
    """測試端點效能"""
    times = []
    errors = []
    
    print(f"\n{'='*50}")
    print(f"測試端點: {endpoint}")
    print(f"迭代次數: {iterations}")
    print(f"{'='*50}\n")
    
    for i in range(iterations):
        start = time.time()
        try:
            response = await client.get(f"{API_URL}{endpoint}")
            elapsed = time.time() - start
            times.append(elapsed)
            status_emoji = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status_emoji} Request {i+1:2d}: {elapsed:.3f}s - Status: {response.status_code}")
        except Exception as e:
            elapsed = time.time() - start
            errors.append(str(e))
            print(f"❌ Request {i+1:2d}: {elapsed:.3f}s - Error: {str(e)[:50]}")
    
    if times:
        print(f"\n📊 統計結果:")
        print(f"  成功請求: {len(times)}/{iterations}")
        print(f"  平均時間: {mean(times):.3f}s")
        print(f"  中位數: {median(times):.3f}s")
        print(f"  最快: {min(times):.3f}s")
        print(f"  最慢: {max(times):.3f}s")
        
        if errors:
            print(f"\n⚠️ 錯誤數量: {len(errors)}")
    else:
        print(f"\n❌ 所有請求都失敗")

async def test_cold_start(client: httpx.AsyncClient):
    """測試冷啟動時間"""
    print(f"\n{'='*50}")
    print("冷啟動測試")
    print(f"{'='*50}\n")
    
    # 等待 5 分鐘（確保服務進入休眠狀態）
    print("⏳ 等待 5 分鐘以確保服務進入休眠狀態...")
    print("   （如果是本地測試，可以跳過此步驟）")
    
    # 第一次請求（冷啟動）
    start = time.time()
    try:
        response = await client.get(f"{API_URL}/health")
        cold_start = time.time() - start
        status_emoji = "✅" if response.status_code == 200 else "⚠️"
        print(f"{status_emoji} 冷啟動時間: {cold_start:.3f}s - Status: {response.status_code}")
        
        if cold_start < 5:
            print("✅ 冷啟動時間可接受（< 5 秒）")
        elif cold_start < 10:
            print("⚠️ 冷啟動時間較長（5-10 秒），建議優化")
        else:
            print("❌ 冷啟動時間過長（> 10 秒），需要解決")
            
        return cold_start
    except Exception as e:
        print(f"❌ 冷啟動測試失敗: {e}")
        return None

async def main():
    """主測試函數"""
    print(f"\n{'='*60}")
    print("效能測試腳本")
    print(f"{'='*60}")
    print(f"API URL: {API_URL}")
    print(f"API Key: {'已設定' if API_KEY else '未設定'}")
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 設定 HTTP 客戶端
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    async with httpx.AsyncClient(
        timeout=30.0,
        headers=headers,
        follow_redirects=True
    ) as client:
        # 1. 冷啟動測試
        await test_cold_start(client)
        
        # 等待 2 秒
        await asyncio.sleep(2)
        
        # 2. 健康檢查端點測試
        await test_endpoint(client, "/health", 10)
        
        # 等待 1 秒
        await asyncio.sleep(1)
        
        # 3. Topics API 測試
        await test_endpoint(client, "/topics?page=1&limit=10", 10)
        
        # 等待 1 秒
        await asyncio.sleep(1)
        
        # 4. 健康檢查端點（詳細測試）
        await test_endpoint(client, "/health", 20)
    
    print(f"\n{'='*60}")
    print("✅ 測試完成")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    asyncio.run(main())


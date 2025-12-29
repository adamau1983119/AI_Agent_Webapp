"""
簡單的 Ollama API 測試腳本
用於檢測 API 對接問題
"""
import httpx
import asyncio
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

async def test_ollama_api():
    """測試 Ollama API"""
    print("=" * 60)
    print("Ollama API 測試")
    print("=" * 60)
    
    # 顯示配置
    print("\n當前配置:")
    print(f"  OLLAMA_API_KEY: {'已設定' if settings.OLLAMA_API_KEY else '未設定'}")
    if settings.OLLAMA_API_KEY:
        masked_key = settings.OLLAMA_API_KEY[:20] + "..." if len(settings.OLLAMA_API_KEY) > 20 else "***"
        print(f"  API Key (前20字元): {masked_key}")
    print(f"  OLLAMA_CLOUD_BASE_URL: {settings.OLLAMA_CLOUD_BASE_URL}")
    print(f"  OLLAMA_MODEL: {settings.OLLAMA_MODEL}")
    print(f"  AI_SERVICE: {settings.AI_SERVICE}")
    
    # 測試不同的 API 端點
    test_urls = [
        f"{settings.OLLAMA_CLOUD_BASE_URL}/generate",
        "https://api.ollama.com/generate",
        "https://ollama.com/api/generate",
    ]
    
    headers = {
        "Authorization": f"Bearer {settings.OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": "Hello, world! This is a test.",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 100
        }
    }
    
    print("\n" + "=" * 60)
    print("測試請求詳情")
    print("=" * 60)
    print(f"請求方法: POST")
    print(f"Headers:")
    for key, value in headers.items():
        if key == "Authorization":
            masked_value = value[:30] + "..." if len(value) > 30 else value
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    print(f"Payload:")
    import json
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("測試不同的 API 端點")
    print("=" * 60)
    
    for url in test_urls:
        print(f"\n測試 URL: {url}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                print(f"  狀態碼: {response.status_code}")
                print(f"  回應標頭: {dict(response.headers)}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ 成功！")
                    print(f"  回應內容: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
                    break
                else:
                    print(f"  ❌ 失敗")
                    print(f"  錯誤訊息: {response.text[:500]}")
        except httpx.HTTPStatusError as e:
            print(f"  ❌ HTTP 錯誤: {e.response.status_code}")
            print(f"  錯誤訊息: {e.response.text[:500]}")
        except httpx.TimeoutException:
            print(f"  ❌ 超時錯誤")
        except Exception as e:
            print(f"  ❌ 其他錯誤: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ollama_api())


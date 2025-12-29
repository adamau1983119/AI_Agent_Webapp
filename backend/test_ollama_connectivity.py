"""
Ollama API 連線測試腳本
根據第三方建議建立，用於檢測 API 對接問題
"""
import httpx
import json
import sys
import os
import asyncio

# 添加專案路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_ollama_api():
    """測試 Ollama API 連線"""
    print("=" * 60)
    print("Ollama API 連線測試")
    print("=" * 60)
    
    # 顯示配置
    print("\n當前配置:")
    print(f"  API Key: {'已設定' if settings.OLLAMA_API_KEY else '未設定'}")
    if settings.OLLAMA_API_KEY:
        masked_key = settings.OLLAMA_API_KEY[:20] + "..." if len(settings.OLLAMA_API_KEY) > 20 else "***"
        print(f"  API Key (前20字元): {masked_key}")
    print(f"  Base URL: {settings.OLLAMA_CLOUD_BASE_URL}")
    print(f"  模型名稱: {settings.OLLAMA_MODEL}")
    
    # 測試參數
    api_key = settings.OLLAMA_API_KEY
    base_url = settings.OLLAMA_CLOUD_BASE_URL or "https://api.ollama.com"
    model_name = settings.OLLAMA_MODEL or "llama2"
    prompt = "Hello, world! This is a test."
    
    # 測試 URL
    url = f"{base_url}/generate"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 使用最簡請求格式
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    
    print("\n" + "=" * 60)
    print("測試請求詳情")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"方法: POST")
    print(f"Headers:")
    for key, value in headers.items():
        if key == "Authorization":
            masked_value = value[:30] + "..." if len(value) > 30 else value
            print(f"  {key}: {masked_value}")
        else:
            print(f"  {key}: {value}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("執行測試...")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"\n發送請求到: {url}")
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"\n狀態碼: {response.status_code}")
            print(f"回應標頭:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            if response.status_code == 200:
                print("\n✅ API 調用成功！")
                result = response.json()
                print("\n回應內容:")
                print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
                
                # 提取生成的內容
                if "response" in result:
                    generated_text = result["response"]
                    print(f"\n✅ 生成的內容: {generated_text[:200]}...")
                elif "text" in result:
                    generated_text = result["text"]
                    print(f"\n✅ 生成的內容: {generated_text[:200]}...")
                else:
                    print(f"\n⚠️ 未找到預期的回應欄位")
                    print(f"完整回應: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                return True
            else:
                print(f"\n❌ API 調用失敗")
                print(f"錯誤訊息: {response.text}")
                return False
                
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP 錯誤: {e.response.status_code}")
        print(f"錯誤訊息: {e.response.text}")
        return False
    except httpx.TimeoutException:
        print(f"\n❌ 請求超時")
        return False
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_ollama_api())
    print("\n" + "=" * 60)
    if result:
        print("✅ 測試通過")
    else:
        print("❌ 測試失敗")
    print("=" * 60)


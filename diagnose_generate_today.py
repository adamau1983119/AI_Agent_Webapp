"""
診斷腳本：測試 generate-today API
用於快速診斷 API 錯誤（400、500 或其他問題）
"""
import requests
import traceback

API_URL = "http://localhost:8000/api/v1/schedules/generate-today"


def diagnose_generate_today():
    """診斷 generate-today API"""
    print(f"[測試] API: {API_URL}")
    print("-" * 60)
    
    try:
        # 發送 POST 請求
        response = requests.post(
            API_URL,
            json={"force": False},  # 發送 JSON 數據
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"📡 狀態碼: {response.status_code}")
        print("-" * 60)
        
        if response.status_code == 200:
            print("[成功] 返回結果")
            try:
                data = response.json()
                print("內容:")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"解析 JSON 失敗: {e}")
                print("原始內容:", response.text)
                
        elif response.status_code == 400:
            print("[警告] 客戶端錯誤 (400)")
            print("通常表示：資料庫未連接或請求參數錯誤")
            try:
                data = response.json()
                print("錯誤內容:")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # 顯示友好提示
                if "message" in data:
                    print(f"\n[訊息] {data['message']}")
                if "suggestion" in data:
                    print(f"[建議] {data['suggestion']}")
            except Exception as e:
                print(f"解析 JSON 失敗: {e}")
                print("原始內容:", response.text)
                
        elif response.status_code == 500:
            print("[錯誤] 伺服器內部錯誤 (500)")
            print("請查看後端日誌獲取詳細錯誤資訊")
            try:
                data = response.json()
                print("錯誤內容:")
                import json
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if "detail" in data:
                    print(f"\n[詳細資訊] {data['detail']}")
            except Exception as e:
                print(f"解析 JSON 失敗: {e}")
                print("原始內容:", response.text)
                
        else:
            print(f"[警告] 其他狀態碼: {response.status_code}")
            print("內容:", response.text)

    except requests.exceptions.ConnectionError:
        print("[錯誤] 連接失敗")
        print("可能原因：")
        print("  1. 後端服務未啟動（請檢查 http://localhost:8000）")
        print("  2. 端口被佔用或防火牆阻擋")
        print("  3. 後端服務運行在不同的端口")
        print("\n[建議]")
        print("  1. 確認後端服務正在運行：")
        print("     cd backend")
        print("     .\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("  2. 檢查後端健康狀態：")
        print("     curl http://localhost:8000/health")
        
    except requests.exceptions.Timeout:
        print("[錯誤] 請求超時")
        print("可能原因：")
        print("  1. 後端處理時間過長")
        print("  2. 網路連接問題")
        print("\n[建議] 檢查後端日誌，確認是否有長時間運行的任務")
        
    except Exception as e:
        print("[錯誤] 請求失敗")
        print(f"錯誤類型: {type(e).__name__}")
        print(f"錯誤訊息: {str(e)}")
        print("\n完整堆疊追蹤:")
        print(traceback.format_exc())


if __name__ == "__main__":
    import sys
    import io
    # 設置 UTF-8 編碼以支持中文和特殊字符
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("generate-today API 診斷工具")
    print("=" * 60)
    print()
    diagnose_generate_today()
    print()
    print("=" * 60)
    print("診斷完成")
    print("=" * 60)


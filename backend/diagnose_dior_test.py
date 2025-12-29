"""
診斷 Dior Sample 測試失敗原因
"""
import sys
import os
from pathlib import Path

# 設定輸出編碼
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_config():
    """檢查配置"""
    print("=" * 60)
    print("診斷 Dior Sample 測試失敗原因")
    print("=" * 60)
    
    # 1. 檢查 .env 檔案
    print("\n1. 檢查 .env 檔案...")
    env_file = Path(".env")
    if env_file.exists():
        print("   [OK] .env 檔案存在")
        
        # 讀取 .env 檔案
        env_vars = {}
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
            
            # 檢查關鍵變數
            print("\n   檢查關鍵配置變數:")
            
            # QWEN_API_KEY
            qwen_key = env_vars.get("QWEN_API_KEY", "")
            if qwen_key:
                masked_key = qwen_key[:8] + "..." if len(qwen_key) > 8 else "***"
                print(f"   [OK] QWEN_API_KEY: {masked_key}")
            else:
                print(f"   [ERROR] QWEN_API_KEY: 未設定")
            
            # MONGODB_URL
            mongodb_url = env_vars.get("MONGODB_URL", "")
            if mongodb_url:
                # 隱藏密碼
                if "@" in mongodb_url:
                    parts = mongodb_url.split("@")
                    if len(parts) == 2:
                        user_pass = parts[0].split("//")[-1]
                        if ":" in user_pass:
                            user, _ = user_pass.split(":", 1)
                            masked_url = mongodb_url.replace(user_pass, f"{user}:***")
                        else:
                            masked_url = mongodb_url
                    else:
                        masked_url = mongodb_url
                else:
                    masked_url = mongodb_url
                print(f"   [OK] MONGODB_URL: {masked_url[:60]}...")
            else:
                print(f"   [ERROR] MONGODB_URL: 未設定")
            
            # 圖片服務 API Keys
            unsplash_key = env_vars.get("UNSPLASH_ACCESS_KEY", "")
            pexels_key = env_vars.get("PEXELS_API_KEY", "")
            pixabay_key = env_vars.get("PIXABAY_API_KEY", "")
            
            print(f"\n   圖片服務 API Keys:")
            if unsplash_key:
                print(f"   [OK] UNSPLASH_ACCESS_KEY: 已設定")
            else:
                print(f"   [WARN] UNSPLASH_ACCESS_KEY: 未設定（可選）")
            
            if pexels_key:
                print(f"   [OK] PEXELS_API_KEY: 已設定")
            else:
                print(f"   [WARN] PEXELS_API_KEY: 未設定（可選）")
            
            if pixabay_key:
                print(f"   [OK] PIXABAY_API_KEY: 已設定")
            else:
                print(f"   [WARN] PIXABAY_API_KEY: 未設定（可選）")
                
        except Exception as e:
            print(f"   [ERROR] 讀取 .env 檔案失敗: {e}")
    else:
        print("   [ERROR] .env 檔案不存在")
        print("   請建立 .env 檔案並設定必要的配置")
    
    # 2. 檢查 Python 環境
    print("\n2. 檢查 Python 環境...")
    print(f"   Python 版本: {sys.version}")
    print(f"   Python 路徑: {sys.executable}")
    
    # 3. 檢查依賴套件
    print("\n3. 檢查關鍵依賴套件...")
    required_packages = [
        "motor",
        "httpx",
        "pydantic",
        "pydantic_settings"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   [OK] {package}: 已安裝")
        except ImportError:
            print(f"   [ERROR] {package}: 未安裝")
    
    # 4. 檢查測試腳本
    print("\n4. 檢查測試腳本...")
    test_script = Path("test_dior_sample.py")
    if test_script.exists():
        print(f"   [OK] test_dior_sample.py: 存在")
    else:
        print(f"   [ERROR] test_dior_sample.py: 不存在")
    
    # 5. 總結問題
    print("\n" + "=" * 60)
    print("診斷總結")
    print("=" * 60)
    
    issues = []
    if not env_file.exists():
        issues.append("❌ .env 檔案不存在")
    elif not env_vars.get("QWEN_API_KEY"):
        issues.append("❌ QWEN_API_KEY 未設定（這是主要問題）")
    
    if not env_vars.get("MONGODB_URL"):
        issues.append("❌ MONGODB_URL 未設定")
    
    if issues:
        print("\n發現的問題:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n解決方法:")
        if "QWEN_API_KEY" in str(issues):
            print("  1. 設定 QWEN_API_KEY:")
            print("     - 申請通義千問 API Key")
            print("     - 在 .env 檔案中添加: QWEN_API_KEY=your_api_key_here")
            print("     - 參考文件: backend/通義千問API Key申請指南.md")
        
        if "MONGODB_URL" in str(issues):
            print("  2. 設定 MONGODB_URL:")
            print("     - 本地 MongoDB: mongodb://localhost:27017")
            print("     - MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/")
    else:
        print("\n✅ 所有配置檢查通過！")
        print("   如果仍然失敗，請檢查:")
        print("   1. API Key 是否有效")
        print("   2. 網路連接是否正常")
        print("   3. MongoDB 服務是否運行")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_config()


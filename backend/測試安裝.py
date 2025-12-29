"""
測試依賴安裝是否成功
"""
import sys

def test_imports():
    """測試關鍵套件是否可以正常導入"""
    errors = []
    
    # 測試 FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        errors.append(f"❌ FastAPI: {e}")
    
    # 測試 Pydantic
    try:
        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")
    except ImportError as e:
        errors.append(f"❌ Pydantic: {e}")
    
    # 測試 Motor (MongoDB)
    try:
        import motor
        # Motor 版本檢查
        try:
            from motor import _version
            version = _version.version
        except:
            try:
                import pkg_resources
                version = pkg_resources.get_distribution('motor').version
            except:
                version = '已安裝'
        print(f"✅ Motor {version}")
    except ImportError as e:
        errors.append(f"❌ Motor: {e}")
    
    # 測試 Uvicorn
    try:
        import uvicorn
        print(f"✅ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        errors.append(f"❌ Uvicorn: {e}")
    
    # 測試 Pydantic Settings
    try:
        import pydantic_settings
        version = getattr(pydantic_settings, '__version__', '已安裝')
        print(f"✅ Pydantic Settings {version}")
    except ImportError as e:
        errors.append(f"❌ Pydantic Settings: {e}")
    
    # 測試 Python-dotenv
    try:
        import dotenv
        version = getattr(dotenv, '__version__', '已安裝')
        print(f"✅ Python-dotenv {version}")
    except ImportError as e:
        errors.append(f"❌ Python-dotenv: {e}")
    
    # 測試 HTTP 客戶端
    try:
        import httpx
        print(f"✅ HTTPX {httpx.__version__}")
    except ImportError as e:
        errors.append(f"❌ HTTPX: {e}")
    
    try:
        import aiohttp
        print(f"✅ AioHTTP {aiohttp.__version__}")
    except ImportError as e:
        errors.append(f"❌ AioHTTP: {e}")
    
    # 測試 Loguru
    try:
        import loguru
        version = getattr(loguru, '__version__', '已安裝')
        print(f"✅ Loguru {version}")
    except ImportError as e:
        errors.append(f"❌ Loguru: {e}")
    
    # 測試應用程式是否可以啟動
    try:
        from app.main import app
        from app.config import settings
        print(f"✅ 應用程式模組載入成功")
        print(f"   應用名稱: {settings.APP_NAME}")
        print(f"   版本: {settings.APP_VERSION}")
    except Exception as e:
        errors.append(f"❌ 應用程式模組: {e}")
    
    # 總結
    print("\n" + "="*50)
    if errors:
        print("❌ 發現以下錯誤：")
        for error in errors:
            print(f"   {error}")
        sys.exit(1)
    else:
        print("✅ 所有依賴安裝成功！")
        print("\n下一步：")
        print("1. 複製 .env.example 為 .env")
        print("2. 執行: python -m uvicorn app.main:app --reload")
        sys.exit(0)

if __name__ == "__main__":
    test_imports()


"""
生成安全的 API Key
"""
from app.utils.security import generate_api_key
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """生成 API Key"""
    print("=" * 60)
    print("生成 API Key")
    print("=" * 60)
    
    api_key = generate_api_key()
    
    print(f"\n生成的 API Key:")
    print(f"{api_key}")
    print(f"\n請將此 API Key 添加到 .env 檔案中:")
    print(f"API_KEY={api_key}")
    print("\n注意：")
    print("1. 請妥善保管此 API Key，不要洩露")
    print("2. 如果 API Key 洩露，請立即生成新的並更新 .env")
    print("3. 在生產環境中，建議使用環境變數而非 .env 檔案")

if __name__ == "__main__":
    main()


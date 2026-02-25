"""
檢查 Meta OAuth 配置的診斷腳本
"""
import sys
import os

# 添加項目路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config_module import settings
from app.services.distribution_service import DistributionService

print("=" * 60)
print("Meta OAuth 配置診斷")
print("=" * 60)
print()

# 1. 檢查環境變數
print("1. 環境變數檢查：")
print(f"   META_APP_ID: {settings.META_APP_ID}")
print(f"   META_APP_ID 長度: {len(settings.META_APP_ID)} 位")
print(f"   META_APP_SECRET: {'已設置' if settings.META_APP_SECRET else '未設置'}")
print(f"   META_APP_SECRET 長度: {len(settings.META_APP_SECRET)} 位")
print(f"   BACKEND_URL: {settings.BACKEND_URL}")
print()

# 2. 驗證 App ID
expected_app_id = "25641504682209776"
if settings.META_APP_ID != expected_app_id:
    print(f"   [ERROR] App ID 不匹配！")
    print(f"      預期: {expected_app_id} (18 位)")
    print(f"      實際: {settings.META_APP_ID} ({len(settings.META_APP_ID)} 位)")
    if len(settings.META_APP_ID) == 17:
        print(f"      [WARNING] 缺少最後一位數字 '6'")
    elif len(settings.META_APP_ID) == 16:
        print(f"      [WARNING] 缺少最後兩位數字 '76'")
else:
    print(f"   [OK] App ID 正確: {settings.META_APP_ID}")
print()

# 3. 檢查 OAuth URL 生成
print("2. OAuth URL 生成測試：")
distribution_service = DistributionService()
test_state = "test_user_id:test_token"
oauth_url = distribution_service.get_meta_oauth_url(test_state)
print(f"   生成的 OAuth URL:")
print(f"   {oauth_url}")
print()

# 4. 檢查 URL 中的 client_id
if "client_id=" in oauth_url:
    url_parts = oauth_url.split("client_id=")
    if len(url_parts) > 1:
        client_id_part = url_parts[1].split("&")[0]
        print(f"   URL 中的 client_id: {client_id_part}")
        if client_id_part == expected_app_id:
            print(f"   [OK] URL 中的 client_id 正確")
        else:
            print(f"   [ERROR] URL 中的 client_id 不正確")
            print(f"      預期: {expected_app_id}")
            print(f"      實際: {client_id_part}")
else:
    print(f"   [ERROR] OAuth URL 中沒有 client_id 參數")
print()

# 5. 檢查 redirect_uri
if "redirect_uri=" in oauth_url:
    url_parts = oauth_url.split("redirect_uri=")
    if len(url_parts) > 1:
        redirect_uri_part = url_parts[1].split("&")[0]
        # URL 解碼
        import urllib.parse
        redirect_uri = urllib.parse.unquote(redirect_uri_part)
        print(f"   URL 中的 redirect_uri: {redirect_uri}")
        expected_redirect = f"{settings.BACKEND_URL}/api/v1/social/meta/callback"
        if redirect_uri == expected_redirect:
            print(f"   [OK] redirect_uri 正確")
        else:
            print(f"   [ERROR] redirect_uri 不匹配")
            print(f"      預期: {expected_redirect}")
            print(f"      實際: {redirect_uri}")
else:
    print(f"   [ERROR] OAuth URL 中沒有 redirect_uri 參數")
print()

# 6. 總結
print("=" * 60)
print("診斷總結：")
print("=" * 60)

issues = []
if settings.META_APP_ID != expected_app_id:
    issues.append(f"[ERROR] META_APP_ID 不正確（應該是 {expected_app_id}）")
if not settings.META_APP_SECRET:
    issues.append("[ERROR] META_APP_SECRET 未設置")
if not settings.BACKEND_URL:
    issues.append("[ERROR] BACKEND_URL 未設置")

if issues:
    print("發現以下問題：")
    for issue in issues:
        print(f"  {issue}")
    print()
    print("解決方案：")
    print("  1. 檢查 backend/.env 文件")
    print("  2. 確認以下配置：")
    print(f"     META_APP_ID={expected_app_id}")
    print(f"     META_APP_SECRET=你的_App_Secret")
    print(f"     BACKEND_URL=http://localhost:8000")
    print("  3. 重啟後端服務")
else:
    print("[OK] 所有配置看起來正確！")
    print()
    print("如果仍然無法連接，請檢查：")
    print("  1. Facebook App 設定中的 OAuth 重定向 URI")
    print("  2. Facebook App 是否處於開發模式")
    print("  3. 瀏覽器控制台的錯誤訊息")

print("=" * 60)


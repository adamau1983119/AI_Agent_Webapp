"""
測試 MongoDB 連接字串
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# 測試連接字串（使用編碼後的密碼）
uri = "mongodb+srv://aadam1983119_db_user:JQPsChzLm6%23L5VP@adamau1983119.yyykp09.mongodb.net/?retryWrites=true&w=majority&appName=adamau1983119"

print("測試 MongoDB 連接...")
print(f"連接字串: {uri.replace('JQPsChzLm6%23L5VP', '***')}")

try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("✅ 連接成功！")
    
    # 列出資料庫
    db_list = client.list_database_names()
    print(f"可用資料庫: {db_list}")
    
except Exception as e:
    print(f"❌ 連接失敗: {e}")
    print("\n可能的問題：")
    print("1. 密碼錯誤")
    print("2. 用戶名錯誤")
    print("3. IP 白名單未設定")
    print("4. 連接字串格式錯誤")


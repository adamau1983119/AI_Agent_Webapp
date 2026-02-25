"""
修正 .env 文件中的 META_APP_ID
"""
import os
import re

env_file = os.path.join(os.path.dirname(__file__), '.env')

if not os.path.exists(env_file):
    print(f"[ERROR] .env 文件不存在: {env_file}")
    exit(1)

# 讀取 .env 文件
with open(env_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 檢查當前的 META_APP_ID
current_match = re.search(r'^META_APP_ID=(.+)$', content, re.MULTILINE)
if current_match:
    current_value = current_match.group(1).strip()
    print(f"當前 META_APP_ID: {current_value} (長度: {len(current_value)} 位)")
else:
    print("[WARNING] 未找到 META_APP_ID 配置")
    current_value = None

# 正確的值
correct_value = "25641504682209776"

if current_value == correct_value:
    print(f"[OK] META_APP_ID 已經是正確的值: {correct_value}")
    exit(0)

# 修正 META_APP_ID
if current_match:
    # 替換現有的值
    new_content = re.sub(
        r'^META_APP_ID=.*$',
        f'META_APP_ID={correct_value}',
        content,
        flags=re.MULTILINE
    )
    print(f"[INFO] 將 META_APP_ID 從 {current_value} 修改為 {correct_value}")
else:
    # 如果不存在，添加到文件末尾
    if not content.endswith('\n'):
        content += '\n'
    new_content = content + f'\n# Meta Developer 配置（Instagram + Facebook）\nMETA_APP_ID={correct_value}\n'
    print(f"[INFO] 添加 META_APP_ID={correct_value}")

# 寫回文件
with open(env_file, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"[OK] .env 文件已更新")
print()
print("下一步：")
print("  1. 停止後端服務（按 Ctrl+C）")
print("  2. 重新啟動後端服務：")
print("     cd backend")
print("     .\\venv\\Scripts\\activate")
print("     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")


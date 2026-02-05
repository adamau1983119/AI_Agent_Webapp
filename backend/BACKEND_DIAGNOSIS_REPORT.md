# 🔍 後端服務診斷報告

## 📋 問題描述

**問題：** 在增加 RSS Feed 連結之後，後端服務（端口 8000）未能正常運作。

**發生時間：** 2026-01-21

**影響範圍：** 後端 API 服務（FastAPI on port 8000）

---

## 🔬 診斷結果

### ✅ 1. 服務狀態檢查

**端口監聽狀態：**
- ✅ 端口 8000 正在監聽（PID: 16568, 8212）
- ⚠️ 發現多個進程佔用同一端口（可能導致衝突）

**建議：**
```powershell
# 檢查並終止舊進程
netstat -ano | findstr ":8000"
taskkill /PID <PID> /F
```

### ✅ 2. 模組導入測試

**測試結果：**
- ✅ `TopicCollector` - 導入成功
- ✅ `ArticleExtractor` - 導入成功  
- ✅ `SchedulerService` - 導入成功
- ✅ RSS Feeds 配置：FASHION (23), FOOD (19), TREND (30)

**結論：** 所有核心模組都能正常導入，沒有語法錯誤。

### ⚠️ 3. 可能的問題原因

#### 問題 A：多進程衝突
**症狀：** 多個 Python 進程同時監聽 8000 端口

**解決方法：**
```powershell
# 1. 查找所有 Python 進程
tasklist | findstr python

# 2. 終止所有 uvicorn 進程
taskkill /F /IM python.exe

# 3. 重新啟動後端服務
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 問題 B：RSS Feed 請求超時
**症狀：** 在初始化 `TopicCollector` 時，如果嘗試連接 RSS Feed，可能導致啟動延遲或超時

**影響：** 
- 啟動時間延長
- 如果 RSS Feed 無法訪問，可能導致錯誤

**解決方法：**
1. **延遲初始化 RSS Feed**（推薦）
   - 只在需要時才連接 RSS Feed
   - 使用異步連接，避免阻塞啟動

2. **添加超時處理**
   ```python
   # 在 topic_collector.py 中已實現
   async with httpx.AsyncClient(timeout=10.0) as client:
       # RSS Feed 請求
   ```

3. **使用緩存**
   - 緩存 RSS Feed 響應
   - 避免重複請求

#### 問題 C：資料庫連接問題
**症狀：** MongoDB 連接失敗導致服務無法啟動

**檢查方法：**
```python
# 測試資料庫連接
from app.database import check_connection
is_connected, reason = await check_connection()
print(f"Connected: {is_connected}, Reason: {reason}")
```

**解決方法：**
1. 檢查 MongoDB 服務是否運行
2. 檢查 `.env` 文件中的 `MONGODB_URL`
3. 確認網路連接正常

#### 問題 D：依賴套件缺失
**症狀：** 缺少必要的 Python 套件

**檢查方法：**
```bash
pip list | findstr "feedparser\|httpx\|beautifulsoup4"
```

**解決方法：**
```bash
pip install feedparser httpx beautifulsoup4
```

---

## 🛠️ 解決步驟（按優先順序）

### 步驟 1：清理並重啟服務

```powershell
# 1. 停止所有後端進程
taskkill /F /IM python.exe

# 2. 等待 3 秒
timeout /t 3

# 3. 重新啟動後端
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 步驟 2：檢查啟動日誌

查看控制台輸出，尋找以下錯誤：
- `ConnectionFailure` - 資料庫連接失敗
- `ImportError` - 模組導入失敗
- `TimeoutError` - RSS Feed 請求超時
- `SyntaxError` - 語法錯誤

### 步驟 3：測試 API 端點

```powershell
# 測試健康檢查端點
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET

# 測試排程端點
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/schedules" -Method GET
```

### 步驟 4：檢查環境變數

確認 `.env` 文件包含：
```env
MONGODB_URL=mongodb://localhost:27017/your_database
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## 📊 詳細診斷命令

### 檢查服務狀態
```powershell
# 檢查端口佔用
netstat -ano | findstr ":8000"

# 檢查 Python 進程
tasklist | findstr python

# 檢查後端日誌（如果有）
Get-Content backend\logs\*.log -Tail 50
```

### 測試模組導入
```python
# 測試所有關鍵模組
python -c "from app.services.automation.topic_collector import TopicCollector; print('OK')"
python -c "from app.utils.article_extractor import ArticleExtractor; print('OK')"
python -c "from app.services.automation.scheduler import SchedulerService; print('OK')"
python -c "from app.main import app; print('OK')"
```

### 測試 RSS Feed 連接
```python
import asyncio
import httpx

async def test_rss():
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("https://www.vogue.com/feed/rss")
            print(f"Status: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_rss())
```

---

## 🎯 預期結果

### 正常啟動時應該看到：

```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API 測試應該返回：

**健康檢查：**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-21T18:00:00Z"
}
```

**排程端點：**
```json
[
  {
    "date": "2026-01-21",
    "timeSlot": "07:00",
    "status": "pending",
    "topicsCount": 0
  },
  ...
]
```

---

## 📝 給第三方開發者的建議

### 1. 啟動順序優化

**問題：** RSS Feed 初始化可能阻塞啟動

**建議：**
- 將 RSS Feed 連接改為懶加載（lazy loading）
- 只在實際需要收集主題時才連接 RSS Feed
- 使用異步連接，避免阻塞主線程

### 2. 錯誤處理增強

**建議：**
- 添加更詳細的錯誤日誌
- 實現重試機制（exponential backoff）
- 添加健康檢查端點，監控 RSS Feed 狀態

### 3. 性能優化

**建議：**
- 實現 RSS Feed 響應緩存（TTL: 5-10 分鐘）
- 並行處理多個 RSS Feed（使用 `asyncio.gather`）
- 限制每個 RSS Feed 的請求超時時間（建議 10 秒）

### 4. 監控和日誌

**建議：**
- 記錄每個 RSS Feed 的連接狀態
- 記錄請求失敗的原因（超時、403、404 等）
- 實現 RSS Feed 健康度評分系統

---

## 🔧 快速修復腳本

創建 `restart_backend.ps1`：

```powershell
# 停止所有 Python 進程
Write-Host "Stopping all Python processes..."
taskkill /F /IM python.exe 2>$null
Start-Sleep -Seconds 3

# 啟動後端服務
Write-Host "Starting backend service..."
cd backend
.\venv\Scripts\activate
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
Write-Host "Backend service started on http://localhost:8000"
```

---

## 📞 聯繫信息

如果問題持續存在，請提供以下信息：

1. **完整的錯誤日誌**（從啟動到錯誤發生）
2. **環境信息**：
   - Python 版本：`python --version`
   - 作業系統：Windows 版本
   - MongoDB 版本和狀態
3. **重現步驟**：
   - 如何啟動服務
   - 觸發錯誤的操作
4. **網路環境**：
   - 是否能訪問外部 RSS Feed
   - 防火牆設置

---

## ✅ 驗證清單

- [ ] 所有 Python 進程已停止
- [ ] 端口 8000 未被佔用
- [ ] 虛擬環境已激活
- [ ] 所有依賴套件已安裝
- [ ] `.env` 文件配置正確
- [ ] MongoDB 服務運行正常
- [ ] 後端服務成功啟動
- [ ] `/health` 端點返回正常
- [ ] `/api/v1/schedules` 端點返回正常

---

**報告生成時間：** 2026-01-21 18:15:00  
**診斷工具版本：** v1.0  
**後端版本：** 根據最新代碼


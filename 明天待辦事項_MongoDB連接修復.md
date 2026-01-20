# 明天待辦事項 - MongoDB 連接修復

**日期**：2026-01-17  
**優先級**：高  
**狀態**：待執行

---

## 🎯 核心目標

徹底解決「資料庫客戶端未初始化」問題，確保所有 API 端點能正確使用 MongoDB 連接。

---

## ✅ 待辦事項清單

### 1. 立即修正：確保所有 API 使用 `request.app.state.db` ⚠️ 優先

**文件**：`backend/app/api/v1/schedules.py`

**任務**：
- [ ] 檢查 `generate_today_all_topics` 函數
- [ ] 確認直接使用 `db = request.app.state.db`
- [ ] 移除所有對 `global database` 或 `from app.database import database` 的依賴
- [ ] 添加實例 ID 日誌：`logger.info(f"DB instance id: {id(db)}")`

**預期代碼**：
```python
@router.post("/generate-today")
async def generate_today_all_topics(request: Request):
    # 直接從 app.state 獲取
    db = request.app.state.db
    if db is None:
        return JSONResponse(
            status_code=400,
            content={
                "status": "failed",
                "message": "資料庫未連接，無法生成主題",
                "detail": "資料庫客戶端未初始化"
            }
        )
    
    logger.info(f"DB instance id: {id(db)}")
    # 使用 db 進行操作
```

---

### 2. 檢查 main.py 的啟動事件 ✅ 已部分完成

**文件**：`backend/app/main.py`

**任務**：
- [x] 確認已在 `lifespan` 中設置 `app.state.mongo_client` 和 `app.state.db`
- [ ] 驗證連接建立邏輯是否正確
- [ ] 確認 shutdown 時正確關閉連接
- [ ] 添加連接實例 ID 日誌

**檢查點**：
```python
# 應該有類似這樣的代碼
app.state.mongo_client = mongo_client
app.state.mongo_db = mongo_db
app.state.db = mongo_db  # 簡短別名
logger.info(f"資料庫實例 ID: {id(app.state.db)}")
```

---

### 3. 短期測試：不使用 --reload 模式 🔍 測試

**任務**：
- [ ] 停止當前服務器（如果正在運行）
- [ ] 使用不帶 `--reload` 的方式啟動：
  ```powershell
  cd backend
  .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
- [ ] 測試 `/api/v1/test/db` 端點
- [ ] 測試 `/api/v1/schedules/generate-today` 端點
- [ ] 記錄測試結果

**目的**：確認問題是否由 `--reload` 模式導致

---

### 4. 驗證所有 API 端點使用 app.state.db 📋 檢查清單

**需要檢查的文件**：
- [ ] `backend/app/api/v1/schedules.py` - 所有端點
- [ ] `backend/app/api/v1/topics.py` - 所有端點
- [ ] `backend/app/api/v1/contents.py` - 所有端點
- [ ] `backend/app/api/v1/images.py` - 所有端點
- [ ] 其他使用資料庫的 API 端點

**檢查標準**：
- ✅ 使用 `request.app.state.db` 而不是全局變數
- ✅ 添加 `request: Request` 參數（放在最前面）
- ✅ 添加實例 ID 日誌用於驗證

---

### 5. 添加詳細日誌確認實例一致性 🔍 調試

**任務**：
- [ ] 在 `main.py` startup 時記錄：`logger.info(f"Startup DB ID: {id(app.state.db)}")`
- [ ] 在每個 API 端點記錄：`logger.info(f"API DB ID: {id(request.app.state.db)}")`
- [ ] 在健康檢查端點記錄：`logger.info(f"Health DB ID: {id(request.app.state.db)}")`
- [ ] 驗證所有 ID 是否相同

**預期結果**：所有端點應該顯示相同的資料庫實例 ID

---

### 6. 驗證環境變數配置 ✅ 已配置

**文件**：`backend/.env`

**任務**：
- [x] 確認 `MONGODB_URL` 已正確配置
- [x] 確認 `MONGODB_DB_NAME` 已正確配置
- [ ] 驗證服務器啟動時能正確讀取環境變數
- [ ] 檢查日誌確認連接字串格式正確

**當前配置**：
```
MONGODB_URL=mongodb+srv://aadam1983119_db_user:Adam91511928@adamau1983119.yyykp09.mongodb.net/?appName=adamau1983119&retryWrites=true&w=majority
MONGODB_DB_NAME=ai_agent_webapp
```

---

### 7. 實施改良版 generate-today API 📝 重構

**文件**：`backend/app/api/v1/schedules.py`

**任務**：
- [ ] 參考提供的改良版範例重構 `generate_today_all_topics`
- [ ] 確保直接使用 `request.app.state.db`
- [ ] 添加清晰的錯誤處理
- [ ] 添加詳細的日誌記錄
- [ ] 測試所有功能正常

**關鍵改進**：
1. 統一使用 `request.app.state.db`
2. 清楚的錯誤處理（400/500/200）
3. 日誌透明化
4. 可擴展性

---

### 8. 測試驗證 🧪 測試

**測試步驟**：

1. **測試資料庫連接端點**：
   ```powershell
   curl http://localhost:8000/api/v1/test/db
   ```
   **預期**：`"status": "ok"` 和資料庫實例 ID

2. **測試健康檢查**：
   ```powershell
   curl http://localhost:8000/api/v1/health
   ```
   **預期**：`"database": "connected"`

3. **測試生成主題 API**：
   ```powershell
   $body = '{"force":false}'
   Invoke-RestMethod -Uri "http://localhost:8000/api/v1/schedules/generate-today" -Method POST -ContentType "application/json" -Body $body
   ```
   **預期**：`"status": "accepted"` 或 `"status": "ok"`

4. **驗證實例 ID**：
   - 查看服務器日誌
   - 確認所有端點顯示相同的資料庫實例 ID

---

### 9. 長期最佳實踐實施 🏗️ 優化

**任務**：
- [ ] 集中管理連接在 `lifespan` startup 事件
- [ ] 移除所有全局變數依賴
- [ ] 考慮使用 FastAPI 依賴注入：`get_database_dependency`
- [ ] 更新所有 Repository 類使用傳入的 db 參數
- [ ] 添加單元測試驗證連接管理

---

## 📊 優先級排序

### 🔴 高優先級（立即執行）
1. **任務 1**：確保所有 API 使用 `request.app.state.db`
2. **任務 7**：實施改良版 generate-today API
3. **任務 8**：測試驗證

### 🟡 中優先級（今天完成）
4. **任務 4**：驗證所有 API 端點
5. **任務 5**：添加詳細日誌

### 🟢 低優先級（可選）
6. **任務 3**：測試不使用 --reload 模式
7. **任務 9**：長期最佳實踐實施

---

## 🔍 診斷步驟

如果問題仍然存在，按以下順序檢查：

1. **檢查服務器日誌**：
   - 查看 startup 時的資料庫實例 ID
   - 查看 API 調用時的資料庫實例 ID
   - 確認是否相同

2. **檢查代碼**：
   - 確認所有 API 使用 `request.app.state.db`
   - 確認沒有使用全局變數
   - 確認參數順序正確（`request: Request` 在最前面）

3. **檢查環境**：
   - 確認 `.env` 文件存在且正確
   - 確認服務器能讀取環境變數
   - 確認 MongoDB Atlas 連接正常

---

## 📝 注意事項

1. **不要使用全局變數**：完全移除對 `global database` 的依賴
2. **統一訪問方式**：所有端點都使用 `request.app.state.db`
3. **添加日誌**：使用實例 ID 驗證一致性
4. **測試優先**：先測試簡單端點，再測試複雜功能
5. **逐步驗證**：每完成一個任務就測試一次

---

## 🎯 成功標準

修復完成後應該達到：
- ✅ 所有 API 端點能正常訪問資料庫
- ✅ 不再出現「資料庫客戶端未初始化」錯誤
- ✅ 健康檢查和 API 端點顯示相同的資料庫實例 ID
- ✅ 在 `--reload` 模式下也能正常工作
- ✅ 所有端點使用同一個資料庫實例

---

**創建日期**：2026-01-16  
**預計完成日期**：2026-01-17  
**當前狀態**：待執行


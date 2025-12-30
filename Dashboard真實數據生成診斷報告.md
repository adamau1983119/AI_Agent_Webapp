# Dashboard 真實數據生成診斷報告

## 🔍 問題診斷

### 用戶懷疑
- Dashboard 只顯示測試的 sample 數據
- 完全未能自動生成任何真正的內容
- 未能提供相關的照片

---

## 📊 檢查結果

### 1. 前端 Mock 數據檢查

**發現問題**：
- ✅ 所有 API 檔案都有 `USE_MOCK` 檢查
- ⚠️ 如果 `VITE_USE_MOCK=true`，會使用 mock 數據
- ⚠️ 如果 API 請求失敗，會 fallback 到 mock 數據

**檢查點**：
```typescript
// frontend/src/api/client.ts
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
```

**影響**：
- 如果 `VITE_USE_MOCK=true`，所有 API 都返回 mock 數據
- 如果 API 請求失敗，會自動 fallback 到 mock 數據

---

### 2. 後端排程服務檢查

**發現問題**：
- ✅ 排程服務已實作
- ⚠️ 只在 `ENVIRONMENT=production` 或 `AUTO_START_SCHEDULER=true` 時自動啟動
- ⚠️ 如果排程服務未啟動，不會自動生成內容

**檢查點**：
```python
# backend/app/main.py
should_start_scheduler = (
    settings.ENVIRONMENT == "production" or
    getattr(settings, 'AUTO_START_SCHEDULER', 'false').lower() == 'true'
)
```

**影響**：
- 如果排程服務未啟動，不會自動生成主題
- 需要手動觸發或設定環境變數

---

### 3. 內容生成流程檢查

**發現問題**：
- ✅ 自動化工作流已實作
- ✅ 排程服務會調用 `workflow.process_topic()`
- ⚠️ 但需要確認是否真的生成內容和照片

**檢查點**：
```python
# backend/app/services/automation/scheduler.py
await self.workflow.process_topic(
    topic_id=topic_id,
    auto_generate_content=True,
    auto_search_images=True,
    image_count=3  # ⚠️ 只生成 3 張照片，不是 8 張
)
```

**影響**：
- 內容生成應該正常
- 但照片數量可能不足（只有 3 張，不是 8 張）

---

## 🚨 發現的問題

### 問題 1: 前端可能使用 Mock 數據

**原因**：
- `VITE_USE_MOCK` 環境變數可能設為 `true`
- API 請求失敗時會 fallback 到 mock 數據

**解決方案**：
1. 確認 Vercel 環境變數 `VITE_USE_MOCK=false`
2. 確認 `VITE_API_URL` 指向正確的後端網域

---

### 問題 2: 排程服務可能未啟動

**原因**：
- 排程服務只在生產環境自動啟動
- 如果環境變數未設定，不會自動啟動

**解決方案**：
1. 確認 Railway 環境變數 `ENVIRONMENT=production`
2. 或設定 `AUTO_START_SCHEDULER=true`
3. 或手動調用 `POST /api/v1/schedules/start`

---

### 問題 3: 照片數量不足

**原因**：
- 排程服務設定 `image_count=3`，不是 8 張

**解決方案**：
- 修改排程服務，將 `image_count` 改為 8

---

### 問題 4: 內容生成可能失敗但未顯示錯誤

**原因**：
- 如果內容生成失敗，可能靜默失敗
- 前端可能顯示空內容或 mock 數據

**解決方案**：
- 檢查後端日誌
- 確認內容生成是否成功

---

## 🔧 修復方案

### 步驟 1: 確認前端環境變數

**在 Vercel Dashboard**：
1. 訪問：https://vercel.com/dashboard
2. 選擇專案：`ai-agent-webapp`
3. 點擊 "Settings" → "Environment Variables"
4. **確認以下設定**：
   ```
   VITE_USE_MOCK=false
   VITE_API_URL=https://your-backend-domain.railway.app/api/v1
   ```
5. 保存後，Vercel 會自動重新部署

---

### 步驟 2: 確認後端環境變數

**在 Railway Dashboard**：
1. 訪問：https://railway.app/dashboard
2. 選擇專案：`AI_Agent_Webapp`
3. 點擊服務：`backend`
4. 點擊 "Variables" 標籤
5. **確認以下設定**：
   ```
   ENVIRONMENT=production
   AUTO_START_SCHEDULER=true  # 可選，但建議設定
   ```
6. 保存後，Railway 會自動重新部署

---

### 步驟 3: 修復照片數量問題

**需要修改**：
- `backend/app/services/automation/scheduler.py`
- 將 `image_count=3` 改為 `image_count=8`

---

### 步驟 4: 手動觸發生成測試

**使用 API**：
```bash
# 手動觸發生成今日所有主題
curl -X POST https://your-backend-domain.railway.app/api/v1/schedules/generate-today \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

**或使用前端**：
- 在 Dashboard 點擊「立即生成」按鈕

---

### 步驟 5: 檢查後端日誌

**在 Railway Dashboard**：
1. 點擊服務：`backend`
2. 點擊 "Deployments" 標籤
3. 點擊最新的部署
4. 查看日誌，確認：
   - 排程服務是否啟動
   - 主題是否生成
   - 內容是否生成
   - 照片是否搜尋

---

## 📋 驗證清單

### 前端驗證
- [ ] `VITE_USE_MOCK=false` 已設定
- [ ] `VITE_API_URL` 指向正確的後端網域
- [ ] 前端可以成功連接到後端 API
- [ ] Dashboard 顯示的數據來自後端（不是 mock）

### 後端驗證
- [ ] `ENVIRONMENT=production` 已設定
- [ ] `AUTO_START_SCHEDULER=true` 已設定（或手動啟動）
- [ ] 排程服務已啟動（檢查日誌）
- [ ] 主題已生成（檢查資料庫）
- [ ] 內容已生成（檢查資料庫）
- [ ] 照片已搜尋（檢查資料庫）

### 功能驗證
- [ ] 今日主題已生成（9 個主題）
- [ ] 每個主題都有內容（500 字文章）
- [ ] 每個主題都有照片（至少 8 張）
- [ ] 照片與文字內容相關

---

## 🎯 立即行動

### 優先級 1（立即執行）
1. **檢查 Vercel 環境變數**
   - 確認 `VITE_USE_MOCK=false`
   - 確認 `VITE_API_URL` 正確

2. **檢查 Railway 環境變數**
   - 確認 `ENVIRONMENT=production`
   - 確認排程服務已啟動

3. **手動觸發生成**
   - 使用 Dashboard 的「立即生成」按鈕
   - 或使用 API 手動觸發

### 優先級 2（短期修復）
4. **修復照片數量**
   - 將 `image_count` 從 3 改為 8

5. **檢查後端日誌**
   - 確認生成流程是否正常
   - 確認是否有錯誤

### 優先級 3（長期優化）
6. **添加錯誤提示**
   - 如果生成失敗，在前端顯示錯誤
   - 不要靜默 fallback 到 mock 數據

---

**報告生成時間**: 2025-12-30  
**狀態**: ⚠️ **需要立即檢查和修復**


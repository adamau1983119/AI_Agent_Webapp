# Network 請求檢查指南

## 🔍 問題診斷

如果 Chrome DevTools Network 標籤是空的，可能的原因：

1. **頁面尚未加載完成**
2. **API 請求被攔截或失敗**
3. **前端未正確初始化**
4. **後端服務未運行**

---

## ✅ 檢查步驟

### 步驟 1: 確認 Network 標籤設定

1. **確認記錄已開啟**
   - 檢查 Network 標籤左上角的紅色圓圈圖標
   - 如果顯示灰色，點擊它開啟記錄

2. **清除並重新載入**
   - 點擊清除按鈕（圓圈帶斜線）
   - 按 `Ctrl + Shift + R` 硬重新載入頁面
   - 觀察 Network 標籤是否有請求出現

3. **檢查過濾器**
   - 確認 "All" 按鈕已選中
   - 檢查 "Filter" 輸入框是否為空
   - 確認 "Invert" 未勾選

---

### 步驟 2: 檢查 Console 標籤

1. **切換到 Console 標籤**
   - 查看是否有錯誤訊息
   - 查看是否有 API 請求的日誌

2. **檢查錯誤類型**
   - `Failed to fetch` = 後端連接問題
   - `CORS error` = CORS 設定問題
   - `404 Not Found` = API 端點不存在
   - `NetworkError` = 網路連接問題

---

### 步驟 3: 檢查 API 請求

**應該看到的請求**：

1. **主題列表請求**
   ```
   GET /api/v1/topics?page=1&limit=12
   ```

2. **排程列表請求**
   ```
   GET /api/v1/schedules
   ```

3. **推薦列表請求**（如果啟用）
   ```
   GET /api/v1/recommendations/user_default
   ```

---

### 步驟 4: 檢查後端服務

1. **訪問後端健康檢查**
   ```
   https://your-backend-domain.railway.app/health
   ```
   - 應該返回 `{"status": "healthy"}`

2. **檢查後端 API 文檔**
   ```
   https://your-backend-domain.railway.app/docs
   ```
   - 應該可以訪問 Swagger UI

---

### 步驟 5: 檢查環境變數

**在 Vercel Dashboard**：
1. 訪問：https://vercel.com/dashboard
2. 選擇專案：`ai-agent-webapp`
3. 點擊 "Settings" → "Environment Variables"
4. 確認：
   ```
   VITE_API_URL=https://your-backend-domain.railway.app/api/v1
   ```

---

## 🔧 常見問題解決

### 問題 1: Network 標籤完全空白

**可能原因**：
- Network 記錄未開啟
- 頁面未完全載入
- JavaScript 錯誤阻止請求

**解決**：
1. 確認 Network 記錄已開啟（紅色圓圈）
2. 清除 Network 日誌
3. 硬重新載入頁面（Ctrl + Shift + R）
4. 檢查 Console 是否有錯誤

---

### 問題 2: 看到請求但都是失敗的

**可能原因**：
- 後端服務未運行
- CORS 設定錯誤
- API URL 設定錯誤

**解決**：
1. 檢查後端健康檢查端點
2. 檢查 CORS 設定
3. 檢查 `VITE_API_URL` 環境變數

---

### 問題 3: 沒有看到 API 請求

**可能原因**：
- React Query 緩存了結果
- 組件未正確初始化
- API 請求被條件阻止

**解決**：
1. 檢查 React Query DevTools（如果安裝）
2. 檢查組件的 `enabled` 條件
3. 檢查 `useQuery` 的設定

---

## 📋 快速檢查清單

- [ ] Network 記錄已開啟（紅色圓圈）
- [ ] 已清除 Network 日誌
- [ ] 已硬重新載入頁面
- [ ] Console 沒有錯誤
- [ ] 後端健康檢查正常
- [ ] `VITE_API_URL` 環境變數正確
- [ ] CORS 設定正確

---

## 🎯 預期結果

**正常情況下，Network 標籤應該顯示**：

1. **頁面資源請求**
   - HTML、CSS、JS 文件
   - 圖片、字體等資源

2. **API 請求**
   - `GET /api/v1/topics?...` - 狀態 200
   - `GET /api/v1/schedules?...` - 狀態 200
   - `GET /api/v1/recommendations/...` - 狀態 200 或 404

3. **請求詳情**
   - 每個請求應該顯示：
     - 狀態碼（200 = 成功）
     - 類型（fetch/xhr）
     - 大小
     - 時間

---

**最後更新**: 2025-12-30


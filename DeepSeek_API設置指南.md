# DeepSeek API 設置指南

## 📋 步驟 1：獲取 DeepSeek API Key

### 1.1 訪問 DeepSeek 平台

1. **訪問 DeepSeek 開發者平台**：
   - https://platform.deepseek.com/api_keys
   - 或：https://platform.deepseek.com → 登入 → API keys

2. **登入帳號**：
   - 如果還沒有帳號，請先註冊

---

### 1.2 創建新的 API Key

1. **點擊「創建 API key」按鈕**：
   - 在 API keys 頁面底部找到黑色按鈕

2. **設置 API Key 名稱**：
   - 例如：`ai-agent-webapp-production`
   - 或：`wts-fortune-app-v30`（如果已有）

3. **創建並複製 API Key**：
   - ⚠️ **重要**：API Key 只在創建時顯示一次
   - 立即複製並保存到安全的地方
   - 格式：`sk-26442...2d5e`（以 `sk-` 開頭）

4. **保存 API Key**：
   - 建議保存到密碼管理器或安全文檔中
   - 不要分享給他人或暴露在代碼中

---

## 📋 步驟 2：在 Railway 設置環境變數

### 2.1 訪問 Railway Environment Variables

1. **訪問 Railway Dashboard**：
   - https://railway.app/dashboard

2. **選擇專案**：
   - 選擇 `gentle-enchantment` 專案

3. **進入 Settings → Variables**：
   - 點擊「Settings」標籤
   - 點擊「Variables」子標籤

---

### 2.2 添加 DeepSeek 環境變數

添加以下環境變數：

#### 必須設置：

1. **`AI_SERVICE`**：
   - **值**：`deepseek`
   - **說明**：指定使用 DeepSeek AI 服務

2. **`DEEPSEEK_API_KEY`**：
   - **值**：`sk-你的API Key`（從步驟 1.2 獲取）
   - **說明**：DeepSeek API 認證密鑰

#### 可選設置（使用預設值）：

3. **`DEEPSEEK_MODEL`**（可選）：
   - **值**：`deepseek-chat`（預設）
   - 或：`deepseek-chat-v3`（最新版本，如果可用）
   - **說明**：使用的 DeepSeek 模型

4. **`DEEPSEEK_BASE_URL`**（可選）：
   - **值**：`https://api.deepseek.com/v1/chat/completions`（預設）
   - **說明**：DeepSeek API 端點（通常不需要修改）

---

### 2.3 設置步驟詳解

1. **點擊「Add New」或「+ New Variable」**

2. **添加 `AI_SERVICE`**：
   - **Key**：`AI_SERVICE`
   - **Value**：`deepseek`
   - **Environment**：至少選擇 `Production`（建議選擇 All Environments）
   - 點擊「Save」

3. **添加 `DEEPSEEK_API_KEY`**：
   - **Key**：`DEEPSEEK_API_KEY`
   - **Value**：`sk-你的完整API Key`（例如：`sk-26442...2d5e`）
   - **Environment**：至少選擇 `Production`（建議選擇 All Environments）
   - **Sensitive**：建議啟用（隱藏值）
   - 點擊「Save」

4. **（可選）添加 `DEEPSEEK_MODEL`**：
   - **Key**：`DEEPSEEK_MODEL`
   - **Value**：`deepseek-chat` 或 `deepseek-chat-v3`
   - **Environment**：All Environments
   - 點擊「Save」

---

## 📋 步驟 3：驗證設置

### 3.1 等待重新部署

1. **自動重新部署**：
   - Railway 會在環境變數更改後自動觸發重新部署
   - 等待約 2-5 分鐘

2. **或手動觸發**：
   - 訪問 Railway → Deployments
   - 點擊最新部署右側的「...」選單
   - 選擇「Redeploy」

---

### 3.2 檢查後端日誌

1. **訪問 Railway Logs**：
   - Railway → 選擇專案 → Logs

2. **查找成功訊息**：
   - 應該看到：`✅ 環境變數驗證通過`
   - 應該看到：`AI 服務: deepseek`
   - 不應該看到：`DeepSeek API Key 未設定` 或連接錯誤

3. **如果看到錯誤**：
   - 檢查 `DEEPSEEK_API_KEY` 是否正確設置
   - 檢查 `AI_SERVICE` 是否設置為 `deepseek`
   - 確認 API Key 格式正確（以 `sk-` 開頭）

---

### 3.3 測試 API 端點

1. **測試健康檢查**：
   - 訪問：https://gentle-enchantment-production-1865.up.railway.app/health
   - 應該返回正常狀態

2. **測試主題生成**：
   - 訪問前端：https://ai-agent-webapp-ten.vercel.app
   - 點擊「立即生成今日主題」按鈕
   - 確認不再出現 500 錯誤
   - 確認主題能正常生成

---

## 🔧 故障排除

### 問題 1：API Key 無效

**症狀**：
- 日誌顯示：`DeepSeek API 調用失敗: 401` 或 `Unauthorized`

**解決方案**：
1. 確認 API Key 完整且正確（以 `sk-` 開頭）
2. 確認 API Key 沒有過期或被禁用
3. 在 DeepSeek 平台檢查 API Key 狀態
4. 如果無效，創建新的 API Key 並更新環境變數

---

### 問題 2：API 調用失敗

**症狀**：
- 日誌顯示：`DeepSeek API 調用失敗: 500` 或 `Connection timeout`

**解決方案**：
1. 檢查網路連接
2. 確認 DeepSeek API 服務正常（訪問 https://api.deepseek.com）
3. 檢查 API Key 額度是否充足
4. 確認模型名稱正確（`deepseek-chat` 或 `deepseek-chat-v3`）

---

### 問題 3：環境變數未生效

**症狀**：
- 日誌仍顯示使用其他 AI 服務（如 `ollama`）

**解決方案**：
1. 確認 `AI_SERVICE` 設置為 `deepseek`（不是 `DeepSeek` 或 `DEEPSEEK`）
2. 確認環境變數已保存
3. 觸發重新部署
4. 檢查 Railway Logs 確認環境變數已讀取

---

## 📊 檢查清單

### 設置前檢查
- [ ] 已訪問 DeepSeek 平台並登入
- [ ] 已創建 API Key 並複製保存

### 設置時檢查
- [ ] `AI_SERVICE` = `deepseek`（小寫）
- [ ] `DEEPSEEK_API_KEY` = `sk-你的完整API Key`
- [ ] API Key 格式正確（以 `sk-` 開頭）
- [ ] 環境變數已保存

### 設置後檢查
- [ ] Railway 已重新部署
- [ ] 日誌中沒有錯誤訊息
- [ ] AI 服務顯示為 `deepseek`
- [ ] 前端功能正常（主題生成、內容生成）

---

## 🎯 快速設置命令（參考）

如果使用 Railway CLI：

```bash
# 設置 AI 服務
railway variables set AI_SERVICE=deepseek

# 設置 API Key（替換為你的實際 API Key）
railway variables set DEEPSEEK_API_KEY=sk-你的API Key

# （可選）設置模型
railway variables set DEEPSEEK_MODEL=deepseek-chat
```

---

## 📝 相關資源

- **DeepSeek 平台**：https://platform.deepseek.com
- **API 文檔**：https://platform.deepseek.com/docs
- **API Keys 管理**：https://platform.deepseek.com/api_keys
- **Railway Dashboard**：https://railway.app/dashboard

---

## ✅ 完成後

設置完成後，你的後端將使用 DeepSeek AI 服務來：
- 生成主題標題
- 生成文章內容
- 生成腳本內容
- 其他 AI 相關功能

所有功能都會通過 DeepSeek API 完成，不再依賴本地 Ollama 服務。

---

**最後更新**：2025-12-30


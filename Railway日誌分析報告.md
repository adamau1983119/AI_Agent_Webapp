# Railway 日誌分析報告

> **日期**：2026-01-06  
> **部署時間**：Jan 6, 2026, 4:00 PM  
> **Commit**：40fbc3f0

---

## ✅ 已確認的配置

### 1. AI 服務配置
- ✅ `AI_SERVICE: deepseek` - **已正確配置**

### 2. 環境變數驗證
- ✅ 環境變數驗證通過
- ✅ MongoDB 連接成功
- ✅ 排程服務已啟動

---

## ❌ 發現的問題

### 問題 1：DEEPSEEK_API_KEY 狀態不明

**現象**：
- 日誌顯示 `AI_SERVICE: deepseek`
- 但沒有顯示 `DEEPSEEK_API_KEY` 的驗證結果
- 環境變數驗證通過（沒有錯誤）

**分析**：
根據 `env_validator.py` 第 69-71 行：
```python
elif ai_service == "deepseek":
    if not settings.DEEPSEEK_API_KEY:
        errors.append("AI_SERVICE=deepseek 但 DEEPSEEK_API_KEY 未設定")
```

如果 `DEEPSEEK_API_KEY` 未設定，應該會拋出錯誤並阻止啟動。但日誌顯示驗證通過，這意味著：
- **可能**：`DEEPSEEK_API_KEY` 已設置（但值可能無效）
- **或者**：驗證邏輯有問題

**需要檢查**：
- Railway 環境變數中 `DEEPSEEK_API_KEY` 是否已設置
- API Key 值是否有效

---

### 問題 2：圖片服務完全未配置 ⚠️

**現象**：
```
⚠️  所有圖片服務的 API Key 都未設定（UNSPLASH_ACCESS_KEY、PEXELS_API_KEY、PIXABAY_API_KEY），圖片搜尋功能將無法使用。
圖片服務: 0 個已配置
```

**影響**：
- 圖片搜尋功能完全無法使用
- 即使有 DuckDuckGo 備援，也可能因為其他錯誤而失敗

**解決方案**：
需要在 Railway 環境變數中設置至少一個圖片服務的 API Key：
- `GOOGLE_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`（推薦）
- 或 `UNSPLASH_ACCESS_KEY`
- 或 `PEXELS_API_KEY`
- 或 `PIXABAY_API_KEY`

---

### 問題 3：詳細環境變數日誌未顯示

**現象**：
- 我在 `main.py` 第 116-152 行添加的詳細環境變數驗證日誌沒有出現在 Railway 日誌中
- 應該顯示的日誌包括：
  - `=== 啟動環境變數驗證 ===`
  - `✅ DEEPSEEK_API_KEY 存在` 或 `⚠️ DEEPSEEK_API_KEY 不存在`
  - `✅ GOOGLE_API_KEY 存在` 等

**可能原因**：
1. 代碼修改還沒有部署到 Railway（Commit 40fbc3f0 可能不包含這些修改）
2. 日誌被截斷（但不太可能，因為看到了後續的 MongoDB 連接日誌）

**需要確認**：
- 檢查 Commit 40fbc3f0 是否包含 `main.py` 的修改
- 如果沒有，需要重新提交並部署

---

## 🔍 實際錯誤原因推測

### 500 Internal Server Error 的可能原因：

1. **DeepSeek API Key 無效或過期**
   - `DEEPSEEK_API_KEY` 可能已設置但值無效
   - 導致 API 調用失敗，返回 500 錯誤

2. **圖片搜尋失敗**
   - 所有圖片服務 API Key 都未設置
   - 即使有 DuckDuckGo 備援，也可能因為網路問題或其他錯誤而失敗

3. **代碼未更新**
   - 最新的代碼修改（動態獲取 AI 服務、詳細日誌等）可能還沒有部署
   - 舊代碼可能還有問題

---

## 🚀 立即行動計劃

### 步驟 1：檢查 Railway 環境變數

在 Railway Dashboard → Variables 中確認：

**必須設置**：
- [ ] `AI_SERVICE` = `deepseek` ✅（已確認）
- [ ] `DEEPSEEK_API_KEY` = `<有效的 API Key>` ⚠️（需要確認）

**圖片服務（至少設置一個）**：
- [ ] `GOOGLE_API_KEY` = `<API Key>`
- [ ] `GOOGLE_SEARCH_ENGINE_ID` = `<Engine ID>`
- 或 `UNSPLASH_ACCESS_KEY` = `<Key>`
- 或 `PEXELS_API_KEY` = `<Key>`
- 或 `PIXABAY_API_KEY` = `<Key>`

### 步驟 2：提交並部署最新代碼

1. 確認所有修改已提交到 Git
2. 觸發 Railway 重新部署
3. 檢查新的部署日誌，確認詳細環境變數驗證日誌出現

### 步驟 3：測試診斷端點

部署後，訪問：
- `https://gentle-enchantment-production-1865.up.railway.app/api/v1/validate/images`
- 確認返回的配置狀態

### 步驟 4：檢查實際錯誤

查看 Railway HTTP Logs，找出：
- 實際的 500 錯誤堆疊追蹤
- AI 服務調用時的錯誤訊息
- 圖片搜尋時的錯誤訊息

---

## 📋 檢查清單

- [ ] 確認 Railway 環境變數 `DEEPSEEK_API_KEY` 已設置且有效
- [ ] 設置至少一個圖片服務的 API Key（推薦 Google Custom Search）
- [ ] 確認最新代碼已提交到 Git
- [ ] 觸發 Railway 重新部署
- [ ] 檢查新的部署日誌，確認詳細環境變數驗證日誌
- [ ] 測試診斷端點 `/api/v1/validate/images`
- [ ] 查看 HTTP Logs 找出實際錯誤原因

---

**報告生成時間**：2026-01-06  
**狀態**：待檢查 Railway 環境變數和重新部署


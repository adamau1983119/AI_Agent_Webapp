# Git 提交規則 - 重要提醒 ⚠️

**建立日期：** 2026-01-08  
**重要性：** 🔴 **極高** - 必須嚴格遵守

---

## ⚠️ 重要規則

### **每次修改後必須立即更新 Git！**

**原因：**
- Vercel（前端）和 Railway（後端）都是從 GitHub 倉庫自動部署
- 如果代碼沒有推送到 Git，部署平台就無法獲取最新的更改
- **修改的內容不會立即顯示在 Dashboard 上**

---

## 📋 標準工作流程

### 1. 修改代碼或文件後

```bash
# 1. 檢查狀態
git status

# 2. 添加所有更改
git add .

# 3. 提交更改（使用清晰的提交訊息）
git commit -m "描述性的提交訊息"

# 4. 推送到 GitHub
git push origin main
```

### 2. 提交訊息格式

**推薦格式：**
```
類型: 簡短描述

詳細說明（可選）
```

**類型範例：**
- `fix:` - 修復問題
- `feat:` - 新功能
- `docs:` - 文檔更新
- `refactor:` - 重構代碼
- `test:` - 測試相關

**範例：**
```bash
git commit -m "fix: Fix image search response handling"
git commit -m "docs: Add 2026-01-08 work plan and task execution report"
git commit -m "feat: Add Google CSE comprehensive test script"
```

---

## ✅ 檢查清單

每次修改後，確認：

- [ ] 已執行 `git add .` 添加所有更改
- [ ] 已執行 `git commit -m "..."` 提交更改
- [ ] 已執行 `git push origin main` 推送到 GitHub
- [ ] 已確認推送成功（檢查 `git log`）
- [ ] 已檢查 Vercel/Railway 是否觸發自動部署

---

## 🔍 驗證部署

### 檢查 Git 狀態

```bash
# 檢查是否有未提交的更改
git status

# 應該顯示：
# "nothing to commit, working tree clean"
```

### 檢查最近的提交

```bash
# 查看最近的提交記錄
git log --oneline -5
```

### 檢查 Vercel 部署

1. 訪問：https://vercel.com/dashboard
2. 選擇專案：`ai-agent-webapp`
3. 檢查 "Deployments" 標籤
4. 確認最新的部署是從最新的 commit 觸發

### 檢查 Railway 部署

1. 訪問：https://railway.app/dashboard
2. 選擇專案
3. 檢查 "Deployments" 標籤
4. 確認最新的部署是從最新的 commit 觸發

---

## 📝 今日提交記錄（2026-01-08）

### 提交 1：`5dd5bc0`
**時間：** 2026-01-08  
**訊息：** docs: Add 2026-01-08 work plan, task execution report, Google CSE test script and dashboard links

**包含文件：**
- `backend/test_google_cse_comprehensive.py`
- `backend/google_cse_test_report_20260112_131228.txt`

### 提交 2：`990eed4`
**時間：** 2026-01-08  
**訊息：** docs: Add 2026-01-08 documentation files

**包含文件：**
- `2026-01-08_今日工作計劃.md`
- `2026-01-08_任務執行報告.md`
- `2026-01-08_Dashboard連結與Git記錄.md`
- 更新 Git 相關文檔文件

---

## 🚨 常見錯誤

### ❌ 錯誤 1：只修改了本地文件，沒有推送到 Git

**後果：**
- Dashboard 不會顯示最新更改
- 其他開發人員無法看到更改
- 部署平台無法獲取最新代碼

**解決方法：**
```bash
git add .
git commit -m "描述更改"
git push origin main
```

### ❌ 錯誤 2：忘記提交某些文件

**檢查方法：**
```bash
git status
```

**解決方法：**
```bash
git add <文件名>
git commit -m "添加遺漏的文件"
git push origin main
```

### ❌ 錯誤 3：提交訊息不清楚

**後果：**
- 無法追蹤更改歷史
- 難以回滾到特定版本

**解決方法：**
使用清晰的提交訊息格式：
```bash
git commit -m "類型: 簡短描述"
```

---

## 📊 自動部署流程

```
本地修改
    ↓
git add .
    ↓
git commit -m "..."
    ↓
git push origin main
    ↓
GitHub 倉庫更新
    ↓
Vercel/Railway 檢測到更改
    ↓
自動觸發部署
    ↓
Dashboard 顯示最新內容
```

**重要：** 如果跳過任何步驟，Dashboard 不會更新！

---

## 🎯 最佳實踐

1. **頻繁提交**
   - 完成一個功能或修復後立即提交
   - 不要累積太多更改

2. **清晰的提交訊息**
   - 使用描述性的訊息
   - 說明更改的原因和內容

3. **驗證推送**
   - 推送後檢查 `git log` 確認
   - 檢查部署平台的部署狀態

4. **定期同步**
   - 開始工作前執行 `git pull`
   - 確保本地代碼是最新的

---

## 📞 相關連結

- **GitHub 倉庫：** https://github.com/adamau1983119/AI_Agent_Webapp
- **Vercel Dashboard：** https://vercel.com/dashboard
- **Railway Dashboard：** https://railway.app/dashboard

---

**最後更新：** 2026-01-08  
**狀態：** ✅ 已建立並執行


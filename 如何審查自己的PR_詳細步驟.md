# 如何審查自己的 PR - 詳細步驟

**當前情況：** 您需要審查自己的 PR 才能合併

---

## 🎯 方法 1：在 PR 頁面直接審查（最簡單）

### 步驟 1：找到審查按鈕

在 PR 頁面，**不要**在右側的 "Reviewers" 區域操作，而是：

1. **滾動到 PR 頁面底部**（在對話區域）
2. 找到 **"Review changes"** 或 **"Approve"** 按鈕
3. 這個按鈕通常在：
   - PR 描述下方
   - 或者在 "Files changed" 標籤頁中

### 步驟 2：提交審查

1. 點擊 **"Review changes"** 按鈕
2. 選擇 **"Approve"**（批准）
3. 可選：添加評論
4. 點擊 **"Submit review"**

---

## 🎯 方法 2：通過 "Files changed" 標籤審查

### 步驟 1：查看更改

1. 在 PR 頁面，點擊 **"Files changed"** 標籤
2. 查看所有更改的文件

### 步驟 2：提交審查

1. 在 "Files changed" 頁面右上角
2. 找到 **"Review changes"** 下拉按鈕
3. 點擊並選擇 **"Approve"**
4. 點擊 **"Submit review"**

---

## 🎯 方法 3：如果無法自己審查（調整規則）

如果上述方法都不可用，可能需要調整分支保護規則：

### 步驟 1：訪問規則設置

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/settings/rules
2. 點擊 `main` 規則集

### 步驟 2：修改審查要求

找到 "Require a pull request before merging" 部分：

**選項 A：允許自己審查**
- 確保沒有勾選 "Require review from Code Owners"
- 或者添加自己到 bypass list（不建議）

**選項 B：暫時降低審查要求**
- 將 "Require approvals" 改為 0（暫時）
- 保存規則
- 合併 PR
- 然後恢復為 1

**選項 C：允許管理員繞過**
- 在 "Bypass list" 中添加自己
- 這樣您就可以直接合併，無需審查

---

## 🎯 方法 4：使用 GitHub CLI（如果已安裝）

```bash
# 審查並批准 PR
gh pr review 1 --approve

# 合併 PR
gh pr merge 1 --merge
```

---

## 🔍 找不到審查按鈕？

### 檢查位置：

1. **在 PR 對話頁面：**
   - 滾動到頁面底部
   - 在 "Merge pull request" 按鈕附近
   - 應該有 "Review changes" 按鈕

2. **在 "Files changed" 標籤：**
   - 右上角應該有 "Review changes" 下拉菜單

3. **如果仍然找不到：**
   - 可能是分支保護規則設置過於嚴格
   - 需要調整規則設置

---

## ✅ 快速檢查清單

- [ ] 已嘗試在 PR 對話頁面底部找到 "Review changes" 按鈕
- [ ] 已嘗試在 "Files changed" 標籤頁找到審查選項
- [ ] 如果找不到，已檢查分支保護規則設置
- [ ] 已考慮暫時調整規則以允許合併

---

## 🚨 緊急情況：直接合併（不推薦）

如果急需修復構建錯誤，可以：

1. **暫時禁用分支保護：**
   - Settings → Rulesets → main
   - 將 Enforcement status 改為 `Disabled`
   - 合併 PR
   - 立即恢復規則

2. **使用命令行（如果規則允許管理員繞過）：**
   ```bash
   git checkout main
   git merge fix/build-error-imagegallery
   git push origin main
   ```

---

## 📸 按鈕位置示意圖

```
PR 頁面結構：
├── 標題和描述
├── 標籤：Conversation | Commits | Checks | Files changed
├── 對話區域
│   ├── 您的評論
│   ├── 提交歷史
│   └── [Review changes 按鈕] ← 在這裡！
├── 右側邊欄
│   ├── Reviewers ← 這裡是添加其他審查者
│   └── Assignees
└── 底部
    └── [Merge pull request 按鈕] ← 審查後才能使用
```

---

## 💡 提示

1. **"Reviewers" 區域**是用來**添加其他審查者**的，不是用來自己審查的
2. **"Review changes" 按鈕**通常在 PR 內容區域，不是在右側邊欄
3. 如果確實無法自己審查，調整分支保護規則是合理的解決方案

---

**需要幫助？** 請告訴我：
- 您是否看到了 "Review changes" 按鈕？
- 如果看到了，點擊後發生了什麼？
- 如果沒看到，您看到了哪些按鈕？


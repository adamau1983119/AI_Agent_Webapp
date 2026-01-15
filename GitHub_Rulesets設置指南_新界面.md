# GitHub Rulesets 設置指南（新界面）

**適用於：** GitHub 的新 Rulesets 界面  
**目標：** 保護 `main` 分支，防止直接修改

---

## 📋 當前頁面狀態

根據您看到的界面，您已經在 "New branch ruleset" 頁面。以下是需要配置的選項：

---

## 🎯 步驟 1：基本設置

### Ruleset Name（規則集名稱）
- ✅ 已填寫：`main`
- 保持不變

### Enforcement status（執行狀態）
- 當前顯示：`Disabled`
- **需要更改為：** `Active`（啟用）
- 點擊下拉菜單，選擇 `Active`

---

## 🎯 步驟 2：Target branches（目標分支）

### 配置分支匹配規則

1. 在 "Branch targeting criteria" 區域，點擊 **"Add target"** 按鈕

2. 選擇匹配方式：
   - **選項 1：** 選擇 "Branch name pattern"
   - **輸入：** `main`
   - 或者
   - **選項 2：** 選擇 "All branches"（如果只想保護 main，不建議）

3. 點擊 **"Add"** 確認

**結果：** 應該顯示 "Branch name pattern: main"

---

## 🎯 步驟 3：Rules（規則）- 重要配置

### ✅ 必須勾選的規則：

#### 1. **Restrict deletions**（限制刪除）
- ✅ **已勾選** - 保持勾選
- 說明：只有有 bypass 權限的用戶才能刪除匹配的分支

#### 2. **Block force pushes**（阻止強制推送）
- ✅ **已勾選** - 保持勾選
- 說明：防止用戶強制推送到匹配的分支

#### 3. **Require a pull request before merging**（合併前需要 PR）⭐ **重要**
- ☐ **需要勾選**
- 說明：要求所有提交必須通過 Pull Request 才能合併
- **點擊展開後，配置：**
  - ✅ Require approvals: **1**（至少需要 1 個審查）
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners（如果有 CODEOWNERS 文件）

#### 4. **Restrict updates**（限制更新）⭐ **重要**
- ☐ **建議勾選**
- 說明：只有有 bypass 權限的用戶才能直接更新匹配的分支
- **這會阻止直接 push 到 main**

### ⚠️ 可選但建議的規則：

#### 5. **Require linear history**（要求線性歷史）
- ☐ 可選勾選
- 說明：防止合併提交被推送到匹配的分支

#### 6. **Require status checks to pass**（要求狀態檢查通過）
- ☐ 可選勾選（如果以後設置了 CI/CD）
- 說明：選擇哪些狀態檢查必須通過才能更新分支

---

## 🎯 步驟 4：Bypass list（繞過列表）

### 當前狀態
- 顯示："Bypass list is empty"

### 建議配置
- **保持為空**（除非您有特定需求）
- 這意味著沒有人可以繞過這些規則

### 如果需要添加繞過（不建議）
- 點擊 "+ Add bypass"
- 可以添加特定的用戶、團隊或應用
- **注意：** 只有非常信任的用戶才應該在繞過列表中

---

## 🎯 步驟 5：創建規則集

1. 檢查所有配置：
   - ✅ Ruleset Name: `main`
   - ✅ Enforcement status: `Active`
   - ✅ Target branches: `main` (Branch name pattern)
   - ✅ Restrict deletions: 已勾選
   - ✅ Block force pushes: 已勾選
   - ✅ Require a pull request before merging: **需要勾選**
   - ✅ Restrict updates: **建議勾選**

2. 滾動到頁面底部

3. 點擊綠色的 **"Create"** 按鈕

---

## ✅ 配置檢查清單

在點擊 "Create" 之前，確認：

- [ ] Ruleset Name: `main`
- [ ] Enforcement status: `Active`（不是 Disabled）
- [ ] Target branches: 已配置 `main` 分支
- [ ] ✅ Restrict deletions: 已勾選
- [ ] ✅ Block force pushes: 已勾選
- [ ] ✅ **Require a pull request before merging: 已勾選**
  - [ ] Require approvals: 1
- [ ] ✅ **Restrict updates: 已勾選**（重要！）
- [ ] Bypass list: 保持為空（或僅包含必要人員）

---

## 🧪 驗證設置

### 測試 1：嘗試直接 push 到 main（應該失敗）

```bash
# 創建測試提交
echo "test" > test.txt
git add test.txt
git commit -m "test: Direct push test"

# 嘗試直接 push（應該被拒絕）
git push origin main
```

**預期結果：**
```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: error: At least 1 approving review is required by reviewers with write access.
```

### 測試 2：通過 PR 合併（應該成功）

1. 創建新分支：
   ```bash
   git checkout -b test-branch
   ```

2. 進行更改並提交：
   ```bash
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: PR test"
   git push origin test-branch
   ```

3. 在 GitHub 上創建 Pull Request
4. 審查並合併 PR（應該成功）

---

## 📸 配置摘要

### 關鍵規則配置：

```
Ruleset: main
├── Enforcement: Active
├── Target: Branch name pattern "main"
├── Rules:
│   ├── ✅ Restrict deletions
│   ├── ✅ Block force pushes
│   ├── ✅ Require a pull request before merging
│   │   └── Require approvals: 1
│   └── ✅ Restrict updates
└── Bypass list: Empty
```

---

## ⚠️ 常見問題

### Q: 如果設置錯誤怎麼辦？
A: 可以在 Rulesets 頁面編輯或刪除規則集，然後重新創建。

### Q: 如何暫時禁用規則？
A: 將 Enforcement status 改為 `Disabled`，但這不建議。

### Q: 緊急情況下如何繞過？
A: 如果您是倉庫管理員，可以在 GitHub 網站上使用 "Merge without waiting for requirements" 選項。

---

## 🎉 完成後

設置完成後，您的 `main` 分支現在受到保護：
- ✅ 無法直接 push
- ✅ 無法強制推送
- ✅ 無法刪除
- ✅ 必須通過 PR 和審查才能合併

**下一步：** 繼續實施階段二的其他保護機制。


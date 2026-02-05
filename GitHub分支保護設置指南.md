# GitHub 分支保護設置指南

**步驟 3：設置 GitHub 分支保護**

---

## 🎯 目標

防止直接修改 `main` 分支，所有更改必須通過 Pull Request 和 Code Review。

---

## 📋 詳細步驟

### 步驟 1：訪問分支保護設置

1. 打開瀏覽器，訪問您的 GitHub 倉庫：
   ```
   https://github.com/adamau1983119/AI_Agent_Webapp
   ```

2. 點擊右上角的 **Settings**（設置）標籤

3. 在左側菜單中，點擊 **Branches**（分支）

### 步驟 2：添加分支保護規則

1. 在 "Branch protection rules" 區域，點擊 **Add rule**（添加規則）按鈕

2. 在 "Branch name pattern" 輸入框中，輸入：
   ```
   main
   ```

### 步驟 3：配置保護選項

勾選以下選項：

#### ✅ 基本保護
- [x] **Require a pull request before merging**
  - [x] Require approvals: **1**（至少需要 1 個審查通過）
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners（如果有 CODEOWNERS 文件）

#### ✅ 狀態檢查
- [x] **Require status checks to pass before merging**
  - [x] Require branches to be up to date before merging
  - （如果以後設置了 CI，可以在這裡添加狀態檢查）

#### ✅ 其他保護
- [x] **Do not allow bypassing the above settings**
- [x] **Restrict who can push to matching branches**
  - 選擇：**No one**（沒有人可以直接 push）

### 步驟 4：保存規則

1. 滾動到頁面底部
2. 點擊 **Create**（創建）按鈕

---

## ✅ 驗證設置

### 測試 1：嘗試直接 push 到 main（應該失敗）

```bash
# 創建一個測試文件
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

1. 創建一個新分支：
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

## 📸 視覺指南

### 分支保護規則頁面位置：
```
GitHub 倉庫
  └── Settings（設置）
      └── Branches（分支）
          └── Branch protection rules
              └── Add rule（添加規則）
```

### 關鍵設置選項位置：
```
Branch protection rule
├── Branch name pattern: main
├── ✅ Require a pull request before merging
│   ├── ✅ Require approvals: 1
│   └── ✅ Require review from Code Owners
├── ✅ Require status checks to pass before merging
│   └── ✅ Require branches to be up to date before merging
└── ✅ Do not allow bypassing the above settings
```

---

## 🔧 進階配置（可選）

### 添加 CODEOWNERS 文件

創建 `.github/CODEOWNERS` 文件：

```
# 核心後端文件
/backend/app/main.py @your-username
/backend/app/config.py @your-username
/backend/app/database.py @your-username
/backend/app/api/v1/ @your-username

# 核心前端文件
/frontend/src/api/ @your-username
/frontend/src/router/ @your-username
```

這樣可以要求特定文件必須由指定人員審查。

---

## ⚠️ 注意事項

1. **首次設置後**：您仍然可以通過 GitHub 網站直接修改，但無法通過命令行直接 push

2. **緊急情況**：如果需要緊急修復，可以：
   - 暫時禁用分支保護（不建議）
   - 使用 GitHub 網站的 "Merge without waiting for requirements"（需要管理員權限）

3. **CI/CD 集成**：如果以後設置了 GitHub Actions，可以在這裡添加狀態檢查要求

---

## 📝 完成檢查清單

- [ ] 已訪問 GitHub 倉庫設置頁面
- [ ] 已創建 `main` 分支保護規則
- [ ] 已啟用 "Require a pull request before merging"
- [ ] 已設置至少 1 個審查要求
- [ ] 已啟用 "Do not allow bypassing"
- [ ] 已測試：直接 push 被拒絕
- [ ] 已測試：通過 PR 可以合併

---

## 🎉 完成！

設置完成後，您的 `main` 分支現在受到保護，所有更改都必須通過 Pull Request 和 Code Review。

**下一步：** 繼續實施階段二的其他保護機制。


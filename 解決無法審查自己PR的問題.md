# 解決無法審查自己 PR 的問題

**問題：** GitHub 顯示 "Pull request authors can't approve their own pull request."

這是 GitHub 的默認行為，PR 作者無法審查自己的 PR。

---

## 🎯 解決方案

### 方法 1：調整分支保護規則（推薦）

允許 PR 作者審查自己的 PR，或暫時降低審查要求。

#### 步驟 1：訪問規則設置

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/settings/rules
2. 點擊 `main` 規則集進行編輯

#### 步驟 2：修改審查要求

找到 "Require a pull request before merging" 部分：

**選項 A：暫時降低審查要求（快速修復）**
- 將 "Require approvals" 從 `1` 改為 `0`
- 保存規則
- 返回 PR 頁面，現在應該可以直接合併
- **合併後立即恢復為 1**

**選項 B：允許自己審查（如果規則支持）**
- 檢查是否有 "Allow specified actors to bypass required pull requests" 選項
- 將自己添加到 bypass list（不建議，但可以解決問題）

#### 步驟 3：合併 PR

1. 返回 PR 頁面：https://github.com/adamau1983119/AI_Agent_Webapp/pull/1
2. 現在應該可以直接點擊 "Merge pull request"
3. 確認合併

#### 步驟 4：恢復規則

合併完成後：
1. 立即返回規則設置
2. 將 "Require approvals" 恢復為 `1`
3. 保存規則

---

### 方法 2：添加協作者審查（長期解決方案）

如果您有另一個 GitHub 帳號或團隊成員：

1. 在 PR 頁面的 "Reviewers" 區域
2. 添加另一個審查者
3. 等待他們審查並批准
4. 然後合併

---

### 方法 3：使用 GitHub CLI（如果已安裝）

```bash
# 審查並批准（如果規則允許）
gh pr review 1 --approve

# 合併 PR
gh pr merge 1 --merge
```

**注意：** 這可能仍然會被規則阻止。

---

### 方法 4：暫時禁用分支保護（緊急情況）

如果急需修復構建錯誤：

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/settings/rules
2. 點擊 `main` 規則集
3. 將 "Enforcement status" 改為 `Disabled`
4. 保存
5. 返回 PR 合併
6. **立即恢復規則**

---

## ✅ 推薦操作流程（緊急修復）

由於這是緊急修復構建錯誤，建議：

### 快速修復步驟：

1. **調整規則（2 分鐘）：**
   - 訪問規則設置
   - 將 "Require approvals" 改為 `0`
   - 保存

2. **合併 PR（1 分鐘）：**
   - 返回 PR 頁面
   - 點擊 "Merge pull request"
   - 確認合併

3. **恢復規則（1 分鐘）：**
   - 返回規則設置
   - 將 "Require approvals" 恢復為 `1`
   - 保存

**總時間：約 4 分鐘**

---

## 🔍 為什麼會這樣？

GitHub 的默認行為：
- PR 作者不能審查自己的 PR（防止自我批准）
- 這是為了確保代碼質量
- 但對於個人專案，這可能過於嚴格

---

## 📝 長期解決方案

### 選項 1：調整規則以適應個人專案

在分支保護規則中：
- 設置 "Require approvals" 為 `0`（個人專案可以這樣做）
- 保留其他保護（如阻止直接 push、要求 PR）

### 選項 2：使用 GitHub Actions 自動審查

設置自動化檢查，如果檢查通過就視為"審查通過"：
- 結構驗證通過
- 構建成功
- 測試通過

這樣就不需要人工審查。

---

## 🎯 立即行動

**最簡單的方法：**

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/settings/rules
2. 點擊 `main` 規則集
3. 找到 "Require approvals"
4. 暫時改為 `0`
5. 保存
6. 返回 PR 合併
7. 合併後立即恢復

---

## ⚠️ 重要提醒

1. **這是緊急修復：** 構建錯誤需要立即修復
2. **所有檢查已通過：** Vercel 部署成功，代碼正確
3. **臨時調整是合理的：** 修復後立即恢復規則

---

**下一步：** 請按照上述步驟調整規則並合併 PR。


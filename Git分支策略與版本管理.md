# Git 分支策略與版本管理

## 📋 概述

本專案採用 **Phase 專屬分支 + 主幹分支策略**，確保多階段開發的穩定性與可追溯性。

---

## 🌳 分支結構

```
main (穩定版，受保護)
  │
  └── develop (整合分支，受保護)
        │
        ├── phase-1-login-register    ← 登入/註冊功能
        ├── phase-2-membership        ← 會員系統
        ├── phase-3-content           ← 內容功能
        ├── phase-4-ai                ← AI 個人化
        └── phase-5-distribution      ← 分發與整合
```

---

## 📌 分支說明

| 分支 | 用途 | 保護狀態 |
|------|------|---------|
| `main` | 正式發布版本，只接受來自 `develop` 的合併 | 🔒 受保護 |
| `develop` | 整合分支，所有 Phase 完成後合併到此 | 🔒 受保護 |
| `phase-X-*` | 各階段功能開發分支 | 開放 |
| `hotfix-*` | 緊急修復分支（從 main 建立） | 開放 |

---

## 🔄 工作流程

### 1. 開始新 Phase

```bash
# 從 develop 建立新分支
git checkout develop
git pull origin develop
git checkout -b phase-1-login-register
```

### 2. 開發與提交

```bash
# 在 Phase 分支上開發
git add .
git commit -m "feat(phase-1): 完成語言選擇頁 UI"

# 定期推送到遠端
git push origin phase-1-login-register
```

### 3. 測試完成後建立 Tag

```bash
# 測試通過後，建立測試完成標記
git tag -a phase-1-tested-ok -m "Phase 1 登入/註冊功能測試通過"
git push origin phase-1-tested-ok
```

### 4. 合併到 develop

```bash
# 切換到 develop
git checkout develop
git pull origin develop

# 合併 Phase 分支
git merge phase-1-login-register --no-ff -m "Merge phase-1-login-register into develop"

# 推送
git push origin develop
```

### 5. 發布到 main

```bash
# 所有 Phase 完成後，從 develop 合併到 main
git checkout main
git pull origin main
git merge develop --no-ff -m "Release v4.0.0"
git tag -a v4.0.0 -m "v4.0.0 正式發布"
git push origin main --tags
```

---

## 🏷️ Tag 命名規範

| Tag 格式 | 說明 | 範例 |
|---------|------|------|
| `phase-X-tested-ok` | Phase 測試通過 | `phase-1-tested-ok` |
| `phase-X-dev` | Phase 開發中快照 | `phase-1-dev-20260203` |
| `vX.Y.Z-feature` | 功能里程碑（穩定基線） | `v4.2.0-i18n-complete` |
| `vX.Y.Z-beta` | Beta 版本 | `v4.0.0-beta` |
| `vX.Y.Z` | 正式版本 | `v4.0.0` |

### 🔒 受保護標籤

以下標籤代表重要里程碑，**不應被刪除或覆蓋**：

| 標籤 | 說明 |
|------|------|
| `v4.2.0-i18n-complete` | i18n 全面完成，所有 UI 文字已國際化 |
| `v4.0.0-i18n-stable` | i18n 系統基礎穩定版 |

---

## 📋 Phase 1 開發清單

### 範圍
- 語言選擇頁 (`LanguageSelection.tsx`)
- 登入頁 (`Login.tsx`)
- 註冊頁 (`Register.tsx`)
- 忘記密碼頁 (`ForgotPassword.tsx`)
- OAuth 回調頁 (`OAuthCallback.tsx`)
- 路由整合 (`App.tsx`)
- 多語言支援 (`i18n/index.ts`)

### 測試項目
- [ ] 語言選擇功能
- [ ] Email 登入功能
- [ ] Google OAuth 登入功能
- [ ] 註冊功能
- [ ] 忘記密碼功能
- [ ] 響應式設計（手機/桌面）
- [ ] 多語言切換

### 完成標準
- 所有測試項目通過
- 無 Linter 錯誤
- 前後端連接正常
- 建立 `phase-1-tested-ok` Tag

---

## 🚨 緊急修復流程

如果 `main` 分支發現嚴重 Bug：

```bash
# 1. 從 main 建立 hotfix 分支
git checkout main
git checkout -b hotfix-login-bug

# 2. 修復問題
git commit -m "fix: 修復登入頁面崩潰問題"

# 3. 合併回 main 和 develop
git checkout main
git merge hotfix-login-bug --no-ff
git tag -a v4.0.1 -m "Hotfix: 登入頁面崩潰"

git checkout develop
git merge hotfix-login-bug --no-ff

# 4. 刪除 hotfix 分支
git branch -d hotfix-login-bug
```

---

## 📊 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| `v4.2.0-i18n-complete` | 2026-02-05 | **🎉 i18n 全面完成** - 修復 220+ 硬編碼文字，穩定基線 |
| `v4.1.0` | 2026-02-04 | Dashboard UI 重構完成 |
| `v4.0.0-i18n-stable` | 2026-02-03 | i18n 系統穩定版 |
| `ce14a45` | 2026-02-03 | v4.0.0 基礎版本（Phase 1 開始前） |

---

## ⚠️ 注意事項

### 禁止操作
- ❌ 直接在 `main` 分支上修改
- ❌ 直接在 `develop` 分支上修改
- ❌ 未測試就合併到 `develop`
- ❌ 跳過 Tag 直接發布

### 建議操作
- ✅ 每個 Phase 在獨立分支開發
- ✅ 測試通過後建立 Tag
- ✅ 使用 `--no-ff` 保留合併歷史
- ✅ 定期推送到遠端備份

---

## 🔧 常用指令

```bash
# 查看所有分支
git branch -a

# 查看所有 Tag
git tag -l

# 查看提交歷史（圖形化）
git log --oneline --graph --all

# 回退到特定 Tag
git checkout phase-1-tested-ok

# 刪除本地分支
git branch -d phase-1-login-register

# 刪除遠端分支
git push origin --delete phase-1-login-register
```

---

## 📅 Phase 時間表

| Phase | 名稱 | 預計時間 | 狀態 |
|-------|------|---------|------|
| 1 | 登入/註冊 | Day 1-2 | 🔄 進行中 |
| 2 | 首頁 Dashboard | Day 3 | ⬜ 待開始 |
| 3 | 主題列表頁 | Day 4-5 | ⬜ 待開始 |
| 4 | 內容生成頁 | Day 6-7 | ⬜ 待開始 |
| 5 | 會員頻道管理 | 穿插進行 | ⬜ 待開始 |

---

## 📝 更新日誌

- **2026-02-05**：🎉 **重大里程碑** - i18n 全面完成
  - 修復 220+ 硬編碼文字（11 批次提交）
  - 建立穩定標籤 `v4.2.0-i18n-complete`
  - 此版本為未來開發的基礎版本
- **2026-02-04**：Dashboard UI 重構完成
- **2026-02-03**：建立分支策略文件，開始 Phase 1 開發


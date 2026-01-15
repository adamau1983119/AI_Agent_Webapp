# Git 備份記錄

## 📋 備份概述

本文檔記錄所有 Git 備份的詳細信息，包括備份時間、原因、標籤和相關提交。

---

## 🔖 備份列表

### 備份 #1: backup_20260113_143852

**備份時間：** 2026-01-13 14:38:52  
**備份原因：** 搜尋邏輯修改前的備份  
**分支：** `feature/ui-improvements`  
**提交 Hash：** `119c0f5`  
**標籤：** `backup_20260113_143852`

#### 備份時狀態

- **當前分支：** `feature/ui-improvements`
- **最新提交：** `docs: Add search logic template and documentation files`
- **提交 Hash：** `119c0f5`

#### 最近 5 個提交

1. `119c0f5` - docs: Add search logic template and documentation files
2. `8ef9cef` - feat: Move Today Topics card to first position on the left
3. `e003ee2` - feat: Arrange six dashboard cards in a single row
4. `fa9959f` - feat: Move generate button to bottom-right corner of today topics card
5. `5f1f790` - feat: Change generate button to purple and reduce size by 50%

#### 分支狀態

- **本地分支：**
  - `feature/ui-improvements` (當前)
  - `main`
- **遠程分支：**
  - `origin/feature/ui-improvements`
  - `origin/main`
  - `origin/fix/build-error-imagegallery`

#### 備份內容

- ✅ 所有已提交的代碼更改
- ✅ 搜尋邏輯範本文檔 (`搜尋邏輯範本_第三方開發指南.md`)
- ✅ 主題生成 Token 使用量分析 (`主題生成Token使用量分析.md`)
- ✅ 後台今日主題搜尋邏輯說明 (`後台今日主題搜尋邏輯說明.md`)
- ✅ 即將來到事件與最近活動功能說明 (`即將來到事件與最近活動功能說明.md`)
- ✅ Dashboard UI 改動（六個卡片並列顯示）

#### 還原方法

```bash
# 還原到備份點
git checkout backup_20260113_143852

# 或創建新分支從備份點開始
git checkout -b restore_from_backup backup_20260113_143852

# 查看備份詳情
git show backup_20260113_143852
```

#### 備份位置

- **本地標籤：** `backup_20260113_143852`
- **遠程標籤：** `origin/backup_20260113_143852`

---

## 📝 備份記錄格式

每次備份應記錄以下信息：

- **備份時間：** YYYY-MM-DD HH:MM:SS
- **備份原因：** 簡要說明備份原因
- **分支：** 備份時所在分支
- **提交 Hash：** 備份點的提交 Hash
- **標籤：** 備份標籤名稱
- **最近提交：** 列出最近幾個提交
- **備份內容：** 說明備份包含的主要內容
- **還原方法：** 提供還原命令

---

## 🔄 備份策略

### 何時創建備份

1. **重大功能修改前**
   - 修改核心搜尋邏輯
   - 修改資料庫結構
   - 修改 API 接口

2. **重要里程碑**
   - 完成主要功能模組
   - 發布版本前
   - 合併到主分支前

3. **風險操作前**
   - 大量重構代碼
   - 刪除或移動重要文件
   - 修改核心配置

### 備份命名規則

格式：`backup_YYYYMMDD_HHMMSS`

範例：
- `backup_20260113_143852` - 2026年1月13日 14:38:52 的備份

### 備份標籤管理

```bash
# 創建備份標籤
git tag -a backup_YYYYMMDD_HHMMSS -m "備份原因說明"

# 推送標籤到遠程
git push origin backup_YYYYMMDD_HHMMSS

# 列出所有備份標籤
git tag --list backup_*

# 刪除本地標籤（謹慎使用）
git tag -d backup_YYYYMMDD_HHMMSS

# 刪除遠程標籤（謹慎使用）
git push origin --delete backup_YYYYMMDD_HHMMSS
```

---

## 📊 備份統計

- **總備份數：** 1
- **最新備份：** 2026-01-13 14:38:52
- **備份頻率：** 根據需要（重大修改前）

---

## ⚠️ 注意事項

1. **備份標籤不應刪除**：備份標籤是重要的還原點，除非確認不再需要，否則不應刪除。

2. **定期清理**：如果備份過多，可以考慮：
   - 保留重要里程碑的備份
   - 刪除過時的備份（需謹慎）
   - 使用 Git 分支代替頻繁的標籤備份

3. **遠程備份**：確保所有備份標籤都已推送到遠程倉庫，以便在任何地方都能還原。

4. **文檔同步**：每次創建備份後，應更新此記錄文件。

---

## 🔗 相關資源

- **Git 標籤文檔：** https://git-scm.com/book/en/v2/Git-Basics-Tagging
- **Git 還原文檔：** https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified
- **專案保護文檔：** `DISASTER_RECOVERY.md`
- **自動備份腳本：** `scripts/auto_backup.ps1`


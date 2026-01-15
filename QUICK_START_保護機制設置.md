# 快速開始：保護機制設置指南

**預計時間：** 30-60 分鐘  
**難度：** ⭐⭐ 簡單

---

## 🚀 立即開始（5 分鐘）

### 步驟 1：測試結構驗證腳本

```powershell
# 在專案根目錄執行
python scripts/validate_structure.py
```

**預期結果：** ✅ 專案結構驗證通過

---

### 步驟 2：設置 Pre-commit Hook

```powershell
# 運行設置腳本
powershell -ExecutionPolicy Bypass -File scripts/setup_pre_commit_hook.ps1
```

**驗證：**
```bash
# 嘗試刪除一個核心目錄（測試用）
# 然後嘗試提交，應該被阻止
```

---

### 步驟 3：設置 GitHub 分支保護

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/settings/branches
2. 點擊 "Add rule"
3. 設置：
   - Branch name pattern: `main`
   - ✅ Require a pull request before merging
   - ✅ Require approvals: 1
   - ✅ Require status checks to pass before merging
4. 點擊 "Create"

**驗證：**
```bash
# 嘗試直接 push 到 main（應該失敗）
git push origin main
```

---

## 📋 完整檢查清單

### ✅ 階段一完成檢查

- [ ] `.cursorrules` 文件已創建
- [ ] `scripts/validate_structure.py` 可以運行
- [ ] Pre-commit hook 已設置
- [ ] GitHub 分支保護已設置
- [ ] `PROTECTED_FILES.md` 已創建
- [ ] `DISASTER_RECOVERY.md` 已創建

### 🧪 測試驗證

- [ ] 結構驗證腳本可以檢測缺失的目錄
- [ ] Pre-commit hook 可以阻止無效提交
- [ ] 無法直接 push 到 main 分支
- [ ] 自動備份腳本可以運行

---

## 🎯 下一步

完成階段一後，可以繼續：

1. **階段二：** 增強驗證和自動備份（1-3 天）
2. **階段三：** Staging 環境和 E2E 測試（1-2 週）

詳細計劃請參考：`專案保護與備份實施行動計劃.md`

---

## ❓ 常見問題

### Q: Pre-commit hook 不工作？
A: 確保：
- Python 在 PATH 中
- Hook 文件有執行權限
- 使用 Git Bash 或配置 Git 使用 PowerShell

### Q: 結構驗證失敗但文件存在？
A: 檢查：
- 路徑是否正確（相對路徑）
- 文件權限是否正確
- Python 版本是否兼容

### Q: 如何跳過 pre-commit hook？
A: 使用 `--no-verify` 標誌（不建議）：
```bash
git commit --no-verify -m "緊急修復"
```

---

**需要幫助？** 查看詳細文檔：
- `專案保護與備份實施行動計劃.md` - 完整計劃
- `DISASTER_RECOVERY.md` - 災難恢復指南
- `PROTECTED_FILES.md` - 受保護文件清單


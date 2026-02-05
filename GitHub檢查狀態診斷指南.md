# GitHub 檢查狀態診斷指南

**當前狀態：** main 分支顯示 "X 1/2"（2 個檢查中有 1 個失敗）

---

## 🔍 如何查看詳細檢查信息

### 方法 1：在 Branches 頁面查看

1. 在 Branches 頁面，點擊 main 分支右側的 **"X 1/2"** 狀態
2. 或點擊右側的 **三點菜單** → 查看詳細信息

### 方法 2：在 Actions 頁面查看

1. 訪問：https://github.com/adamau1983119/AI_Agent_Webapp/actions
2. 查看最近的 workflow runs
3. 點擊失敗的檢查查看詳細錯誤

### 方法 3：在提交頁面查看

1. 點擊 main 分支的 "43 minutes ago" 鏈接
2. 查看該提交的檢查狀態
3. 點擊失敗的檢查查看詳細信息

---

## 📋 常見檢查類型

### 1. 分支保護規則檢查
- **名稱：** 通常是 "Branch protection" 或 "Ruleset"
- **目的：** 驗證分支保護規則是否正確配置
- **失敗原因：** 可能是規則配置不完整

### 2. 部署檢查（Vercel/Railway）
- **名稱：** 可能包含 "Vercel" 或 "Railway"
- **目的：** 驗證部署是否成功
- **失敗原因：** 部署失敗、構建錯誤、環境變數問題

### 3. GitHub Actions 工作流
- **名稱：** 自定義的工作流名稱
- **目的：** 運行自動化測試或驗證
- **失敗原因：** 測試失敗、腳本錯誤

---

## 🔧 診斷步驟

### 步驟 1：識別失敗的檢查

1. 點擊 "X 1/2" 查看詳細信息
2. 記錄失敗的檢查名稱
3. 查看錯誤訊息

### 步驟 2：根據檢查類型處理

#### 如果是分支保護規則檢查失敗：

**可能原因：**
- 規則集配置不完整
- 缺少必要的規則（如 "Require a pull request before merging"）

**解決方案：**
1. 訪問 Settings → Rulesets
2. 點擊 `main` 規則集
3. 檢查所有必要規則是否已啟用
4. 確保 "Require a pull request before merging" 已勾選

#### 如果是部署檢查失敗：

**可能原因：**
- Vercel 或 Railway 部署失敗
- 構建錯誤
- 環境變數缺失

**解決方案：**
1. 檢查 Vercel Dashboard：https://vercel.com/dashboard
2. 檢查 Railway Dashboard：https://railway.app/dashboard
3. 查看部署日誌找出錯誤原因

#### 如果是 GitHub Actions 工作流失敗：

**可能原因：**
- 工作流配置錯誤
- 測試失敗
- 腳本執行錯誤

**解決方案：**
1. 訪問 Actions 頁面查看詳細日誌
2. 修復工作流配置或測試問題

---

## 🎯 建議：設置結構驗證檢查

為了確保專案結構不被破壞，建議設置 GitHub Actions 自動驗證：

### 創建 GitHub Actions 工作流

**文件位置：** `.github/workflows/validate-structure.yml`

**內容：**
```yaml
name: Validate Project Structure

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Validate project structure
      run: |
        python scripts/validate_structure.py
```

---

## ✅ 快速檢查清單

- [ ] 已點擊 "X 1/2" 查看詳細信息
- [ ] 已識別失敗的檢查名稱
- [ ] 已查看錯誤訊息
- [ ] 已確定失敗原因
- [ ] 已採取修復措施
- [ ] 已重新檢查狀態

---

## 📞 需要幫助？

如果無法確定失敗原因，請提供：
1. 失敗檢查的名稱
2. 錯誤訊息的截圖或文本
3. 檢查的詳細日誌

這樣我可以提供更具體的解決方案。


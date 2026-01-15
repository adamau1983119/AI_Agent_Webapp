# UI 改動分支使用指南

**分支名稱：** `feature/ui-improvements`  
**創建時間：** 2026-01-13  
**狀態：** ✅ 已創建並推送到遠程

---

## ✅ 當前狀態

- ✅ 分支已創建：`feature/ui-improvements`
- ✅ 已推送到遠程：`origin/feature/ui-improvements`
- ✅ 當前分支：`feature/ui-improvements`
- ✅ 基於最新的 `main` 分支

---

## 🎨 可以安全改動的文件

### 完全安全的區域：

#### 1. UI 組件
```
frontend/src/components/ui/
├── Button.tsx          ✅ 可以改動
├── Card.tsx            ✅ 可以改動
├── LoadingSpinner.tsx  ✅ 可以改動
└── ...                 ✅ 所有 UI 組件
```

#### 2. 功能組件（僅 UI 部分）
```
frontend/src/components/features/
├── ImageGallery.tsx    ✅ 可以改動 UI 部分
├── ImageSearch.tsx     ✅ 可以改動 UI 部分
├── TopicEditor.tsx     ✅ 可以改動 UI 部分
└── ...                 ✅ 可以改動 UI 部分
```

#### 3. 頁面組件（僅 UI 部分）
```
frontend/src/pages/
├── Dashboard.tsx       ✅ 可以改動布局和樣式
├── Topics.tsx          ✅ 可以改動布局和樣式
└── TopicDetail.tsx     ✅ 可以改動布局和樣式
```

#### 4. 樣式文件
```
frontend/src/
├── styles/             ✅ 可以任意改動
├── assets/             ✅ 可以任意改動
└── tailwind.config.js  ✅ 可以任意改動
```

---

## 🚀 開始改動

### 步驟 1：確認當前分支

```bash
# 確認當前分支
git branch

# 應該顯示：* feature/ui-improvements
```

### 步驟 2：啟動開發服務器

```bash
# 進入前端目錄
cd frontend

# 啟動開發服務器
npm run dev

# 瀏覽器會自動打開 http://localhost:5173
```

### 步驟 3：進行 UI 改動

在編輯器中改動以下文件：
- `frontend/src/components/ui/*.tsx` - UI 組件
- `frontend/src/pages/*.tsx` - 頁面布局
- `frontend/src/styles/*.css` - 樣式文件

### 步驟 4：測試改動

```bash
# 在瀏覽器中查看改動效果
# 檢查控制台是否有錯誤

# 構建測試（確保沒有錯誤）
npm run build
```

---

## 📝 提交改動

### 標準提交流程：

```bash
# 1. 查看改動
git status

# 2. 添加改動的文件
git add frontend/src/components/ui/
git add frontend/src/pages/
# 或添加所有改動
git add .

# 3. 提交（Pre-commit hook 會自動驗證結構）
git commit -m "feat: Improve UI layout and styling"

# 4. 推送到遠程
git push origin feature/ui-improvements
```

### 提交訊息格式建議：

```
feat: 描述改動內容

範例：
- feat: Improve dashboard layout and spacing
- feat: Add hover effects to image gallery
- feat: Enhance button styling and animations
- feat: Optimize responsive design for mobile
```

---

## 🔄 同步 main 分支的更新

如果在改動期間 main 分支有更新：

```bash
# 1. 切換到 main 分支
git checkout main

# 2. 拉取最新更改
git pull origin main

# 3. 切換回功能分支
git checkout feature/ui-improvements

# 4. 合併 main 的更新
git merge main

# 5. 解決衝突（如果有）
# 6. 繼續改動
```

---

## 🎯 完成改動後

### 步驟 1：最終測試

```bash
# 確保所有改動都測試過
cd frontend
npm run build  # 確保構建成功
npm run dev    # 確保開發服務器正常
```

### 步驟 2：提交所有更改

```bash
git add .
git commit -m "feat: Complete UI improvements"
git push origin feature/ui-improvements
```

### 步驟 3：創建 Pull Request

1. **訪問 GitHub：**
   - https://github.com/adamau1983119/AI_Agent_Webapp/pull/new/feature/ui-improvements
   - 或點擊 GitHub 提示的鏈接

2. **填寫 PR 信息：**
   - Title: `feat: UI improvements - [描述改動]`
   - Description: 描述改動的內容和目的

3. **等待檢查通過：**
   - 結構驗證
   - 構建檢查

4. **合併 PR：**
   - 審查通過後合併到 main
   - Vercel 會自動部署

---

## ⚠️ 注意事項

### 不要改動：

- ❌ `frontend/src/api/*.ts` - API 客戶端
- ❌ `frontend/src/router/*.tsx` - 路由配置（除非必要）
- ❌ `backend/app/*` - 所有後端文件

### 改動前確認：

- [ ] 當前在 `feature/ui-improvements` 分支
- [ ] 改動的文件在安全區域內
- [ ] 沒有修改 API 調用邏輯
- [ ] 本地測試通過

---

## 📋 快速命令參考

```bash
# 查看當前分支
git branch

# 查看改動狀態
git status

# 查看改動內容
git diff

# 添加所有改動
git add .

# 提交改動
git commit -m "feat: UI improvements"

# 推送到遠程
git push origin feature/ui-improvements

# 啟動開發服務器
cd frontend && npm run dev

# 構建測試
cd frontend && npm run build
```

---

## 🎨 改動建議

### 可以改動的內容：

1. **視覺設計**
   - 顏色方案
   - 字體大小和樣式
   - 間距和對齊
   - 圖標和圖片

2. **布局優化**
   - 響應式設計
   - 組件排列
   - 頁面結構
   - 導航布局

3. **用戶體驗**
   - 交互反饋
   - 加載動畫
   - 過渡效果
   - 錯誤提示樣式

4. **組件改進**
   - 按鈕樣式
   - 卡片設計
   - 表單樣式
   - 列表布局

---

## ✅ 當前分支信息

- **分支名稱：** `feature/ui-improvements`
- **遠程分支：** `origin/feature/ui-improvements`
- **基於：** `main` 分支（最新版本）
- **狀態：** ✅ 已創建並推送到遠程

---

**現在可以開始進行 UI 改動了！** 🎨

所有改動都在安全的分支中，不會影響 main 分支和後端結構。


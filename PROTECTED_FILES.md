# 受保護的核心文件清單

本文檔列出了專案中受保護的核心文件，這些文件不應該被隨意修改或刪除。

## 🔴 後端核心文件（最高優先級）

### 應用入口和配置
- `backend/app/main.py` - FastAPI 應用入口
- `backend/app/config.py` - 配置管理
- `backend/app/database.py` - 資料庫連接

### API 端點
- `backend/app/api/v1/*.py` - 所有 API 端點文件
  - `topics.py` - 主題 API
  - `contents.py` - 內容 API
  - `images.py` - 圖片 API（包含代理端點）
  - `user.py` - 用戶 API
  - `health.py` - 健康檢查 API
  - `schedules.py` - 排程 API
  - `interactions.py` - 互動 API
  - `recommendations.py` - 推薦 API
  - `discover.py` - 發掘 API
  - `validate.py` - 驗證 API

### 業務邏輯服務
- `backend/app/services/**/*.py` - 所有服務文件
  - `images/` - 圖片服務
  - `automation/` - 自動化服務
  - `ai/` - AI 服務

### 數據模型
- `backend/app/models/*.py` - 所有數據模型

---

## 🔴 前端核心文件（最高優先級）

### API 客戶端
- `frontend/src/api/*.ts` - 所有 API 客戶端文件
  - `client.ts` - API 客戶端基礎
  - `topics.ts` - 主題 API
  - `contents.ts` - 內容 API
  - `images.ts` - 圖片 API
  - `interactions.ts` - 互動 API

### 路由配置
- `frontend/src/router/*.tsx` - 路由配置
- `frontend/src/App.tsx` - 應用主組件

### 核心頁面
- `frontend/src/pages/*.tsx` - 所有頁面組件
  - `Dashboard.tsx` - 控制面板
  - `Topics.tsx` - 主題列表
  - `TopicDetail.tsx` - 主題詳情

### 類型定義
- `frontend/src/types/*.ts` - TypeScript 類型定義

---

## 🟡 重要配置文件（高優先級）

### 後端配置
- `backend/requirements.txt` - Python 依賴
- `backend/pyproject.toml` - Python 專案配置
- `backend/.env.example` - 環境變數範例

### 前端配置
- `frontend/package.json` - Node.js 依賴
- `frontend/tsconfig.json` - TypeScript 配置
- `frontend/vite.config.ts` - Vite 配置
- `frontend/.env.example` - 環境變數範例

### 專案配置
- `.gitignore` - Git 忽略文件
- `.cursorrules` - Cursor AI 規則
- `README.md` - 專案說明

---

## 🟢 受保護的目錄結構

### 後端目錄
```
backend/
├── app/
│   ├── api/v1/        # API 端點（禁止刪除）
│   ├── services/       # 業務邏輯（禁止刪除）
│   ├── models/         # 數據模型（禁止刪除）
│   └── utils/          # 工具函數（禁止刪除）
```

### 前端目錄
```
frontend/
├── src/
│   ├── api/            # API 客戶端（禁止刪除）
│   ├── components/     # React 組件（禁止刪除）
│   ├── pages/          # 頁面組件（禁止刪除）
│   ├── router/         # 路由配置（禁止刪除）
│   └── types/          # 類型定義（禁止刪除）
```

---

## ⚠️ 修改規則

### 修改前必須：
1. ✅ 創建 feature 分支
2. ✅ 創建備份（使用 `scripts/auto_backup.ps1`）
3. ✅ 通過結構驗證（`scripts/validate_structure.py`）
4. ✅ 創建 Pull Request
5. ✅ 通過 Code Review
6. ✅ 通過 CI/CD 測試

### 禁止操作：
- ❌ 直接修改 main 分支
- ❌ 刪除核心目錄
- ❌ 清空關鍵文件內容
- ❌ 修改資料庫連接邏輯
- ❌ 修改 API 路由結構
- ❌ 跳過測試直接部署

---

## 📝 更新記錄

- **2026-01-13**: 初始版本，列出所有受保護的核心文件

---

**注意：** 本文檔應該與 `.cursorrules` 和結構驗證腳本同步更新。


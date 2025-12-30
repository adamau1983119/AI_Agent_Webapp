# AI Agent Webapp for Social Media Content Generation

## ⚠️ 重要設計要求

**所有版面設定必須確保在手機和平板上使用 Webapp 也能清楚顯示。**

詳細設計要求請參考：[專案設計要求.md](./專案設計要求.md)

> **專案名稱**：AI Agent Webapp for Social Media Content Generation  
> **版本**：1.0.0  
> **狀態**：開發中  
> **建立日期**：2025-12-19

---

## 📖 專案簡介

AI Agent Webapp 是一個用於社交媒體內容生成的全端 Web 應用程式。透過 AI 技術自動生成文章和腳本，並整合多個圖片搜尋服務，幫助使用者快速建立高品質的社交媒體內容。

### 主要功能

- 🤖 **AI 內容生成**：使用 Ollama、Google Gemini、OpenAI 等 AI 服務生成文章和腳本
- 🖼️ **圖片搜尋**：整合 Unsplash、Pexels、Pixabay、Google Custom Search、DuckDuckGo
- 📝 **主題管理**：建立、編輯、刪除主題，支援分類和狀態管理
- 🎨 **現代化 UI**：使用 React + TypeScript + Tailwind CSS 建構
- 🔒 **安全認證**：API Key 認證、Rate Limiting、CORS 保護
- 📊 **分頁與搜尋**：支援分頁顯示和關鍵字搜尋

---

## 🚀 快速開始

### 前置需求

- **Node.js** 18+ 和 npm
- **Python** 3.13+
- **MongoDB**（本地或 MongoDB Atlas）
- **Git**

### 安裝步驟

#### 1. 複製專案

```bash
git clone <repository-url>
cd AI_Agent_Wbbapp_for_Social_Media_Content_Generation
```

#### 2. 後端設定

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定必要的環境變數
# 至少需要設定：
# - MONGODB_URL（MongoDB 連接字串）
# - AI_SERVICE（選擇使用的 AI 服務）
```

#### 3. 前端設定

```bash
# 進入前端目錄
cd frontend

# 安裝依賴
npm install

# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定 API URL
# VITE_API_URL=http://localhost:8000/api/v1
```

#### 4. 啟動服務

**啟動後端**（在 `backend` 目錄）：

```bash
# 使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用提供的腳本
# Windows:
.\啟動後端服務_簡單版.bat
```

**啟動前端**（在 `frontend` 目錄）：

```bash
# 使用 npm
npm run dev

# 或使用提供的腳本
# Windows:
.\啟動前端Dashboard.bat
```

#### 5. 訪問應用

- **前端**：http://localhost:3000 或 http://localhost:5173
- **後端 API**：http://localhost:8000
- **API 文檔**：http://localhost:8000/docs

---

## 🛠️ 技術棧

### 前端
- **React** 18.2.0 - UI 框架
- **TypeScript** 5.2.2 - 類型安全
- **Vite** 5.0.8 - 建置工具
- **Tailwind CSS** 3.3.6 - 樣式框架
- **React Router** 6.20.0 - 路由管理
- **React Query** 5.12.0 - 伺服器狀態管理
- **Zustand** 4.4.7 - 狀態管理
- **React Hot Toast** 2.6.0 - 通知系統

### 後端
- **FastAPI** 0.115.0 - Web 框架
- **Python** 3.13 - 程式語言
- **Uvicorn** 0.32.0 - ASGI 伺服器
- **Motor** 3.6.0 - MongoDB 異步驅動
- **Pydantic** 2.10.0 - 資料驗證
- **httpx** 0.27.0 - HTTP 客戶端

### 資料庫
- **MongoDB Atlas** - 雲端資料庫（或本地 MongoDB）

### AI 服務（可選）
- **Ollama** - 本地/雲端 AI 服務
- **Google Gemini** - Google AI 服務
- **OpenAI** - OpenAI API
- **通義千問** - 阿里雲 AI 服務

### 圖片搜尋服務（可選）
- **Unsplash** - 免費圖片
- **Pexels** - 免費圖片
- **Pixabay** - 免費圖片
- **Google Custom Search** - Google 圖片搜尋
- **DuckDuckGo** - 備援圖片搜尋（不需要 API Key）

---

## 📁 專案結構

```
AI_Agent_Wbbapp_for_Social_Media_Content_Generation/
├── backend/                 # 後端應用
│   ├── app/                 # 應用程式碼
│   │   ├── api/            # API 端點
│   │   ├── models/         # 資料模型
│   │   ├── schemas/        # Pydantic 驗證模型
│   │   ├── services/       # 業務邏輯服務
│   │   ├── middleware/     # 中間件（認證、限流）
│   │   └── utils/          # 工具函數
│   ├── requirements.txt    # Python 依賴
│   └── .env.example        # 環境變數範例
│
├── frontend/               # 前端應用
│   ├── src/
│   │   ├── app/           # App 層（路由、Provider）
│   │   ├── pages/         # 頁面元件
│   │   ├── components/    # 元件
│   │   ├── api/          # API 客戶端
│   │   ├── stores/       # Zustand stores
│   │   └── utils/        # 工具函數
│   ├── package.json       # Node.js 依賴
│   └── .env.example       # 環境變數範例
│
├── README.md              # 本文件
├── DEPLOYMENT.md          # 部署指南
├── 網域設定指南.md        # 網域設定說明
└── .gitignore            # Git 忽略檔案
```

---

## 🔧 環境變數設定

### 後端環境變數

詳見 `backend/.env.example`

**必須設定**：
- `MONGODB_URL` - MongoDB 連接字串
- `AI_SERVICE` - 選擇使用的 AI 服務（ollama, gemini, openai, qwen）

**可選設定**：
- `API_KEY` - API 認證金鑰（生產環境建議設定）
- 各種 AI 服務的 API Key
- 圖片搜尋服務的 API Key

### 前端環境變數

詳見 `frontend/.env.example`

**必須設定**：
- `VITE_API_URL` - 後端 API URL（預設：http://localhost:8000/api/v1）

**可選設定**：
- `VITE_USE_MOCK` - 是否使用 Mock 資料（開發用）

---

## 📚 相關文件

### 開發文件
- [進度記錄.md](./進度記錄.md) - 開發進度記錄
- [技術規格書.md](./技術規格書.md) - 技術規格說明
- [API設計草圖.md](./API設計草圖.md) - API 設計文件

### 部署文件
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南
- [網域設定指南.md](./網域設定指南.md) - 網域設定說明

### 設定指南
- [後端服務啟動步驟.md](./後端服務啟動步驟.md) - 後端啟動指南
- [Google_Custom_Search_API設定指南.md](./Google_Custom_Search_API設定指南.md) - Google API 設定

---

## 🧪 測試

### 後端 API 測試

```bash
cd backend
python test_backend_api_comprehensive.py
```

### 前端測試

前端目前使用手動測試，未來可添加自動化測試。

---

## 🚢 部署

詳見 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 推薦部署平台

- **前端**：Vercel、Netlify
- **後端**：Railway、Render、Fly.io
- **資料庫**：MongoDB Atlas（已使用）

---

## 🔒 安全性

### 已實作的安全功能

- ✅ API Key 認證
- ✅ Rate Limiting（請求限流）
- ✅ CORS 保護
- ✅ 環境變數管理
- ✅ 錯誤處理

### 生產環境建議

- 必須設定 `API_KEY`
- 必須使用 HTTPS
- 限制 CORS 來源
- 定期輪換 API Key
- 啟用日誌記錄

詳見 [認證與安全設定完成報告.md](./認證與安全設定完成報告.md)

---

## 📝 開發規範

### 代碼風格

- **後端**：遵循 PEP 8 Python 風格指南
- **前端**：使用 ESLint 和 Prettier

### Git 工作流程

- 使用功能分支開發
- 提交前執行測試
- 提交訊息使用中文

---

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

---

## 📄 授權

本專案為私有專案。

---

## 📞 聯絡方式

如有問題，請提交 Issue 或聯絡專案維護者。

---

## 🎯 下一步

- [ ] 完成 Git 備份機制
- [ ] 完善單元測試
- [ ] 優化效能
- [ ] 添加更多 AI 服務支援
- [ ] 實作排程功能

---

**最後更新**：2025-12-24  
**維護者**：開發團隊


# Influencers AI Agents（網紅 AI 助手）

> **版本**：v4.1.1  
> **更新日期**：2026-02-05  
> **當前分支**：`phase-1-login-register`

---

## ⚠️ 重要提醒（開發者必讀）

| # | 規則 | 說明 |
|:-:|------|------|
| 1 | **查看真實日期** | 每次查看 README 必須確認「更新日期」，判斷文檔是否過時。如果超過 7 天未更新，請先查看 `工作記錄.md` 了解最新狀態。 |
| 2 | **遵循架構文件** | 修改前先閱讀下方「專案架構」區段的所有文件 |
| 3 | **按鈕必須標記** | 所有新增按鈕必須添加 `data-testid` 屬性，參考 `按鈕測試ID架構表.md` |
| 4 | **🔴 禁止模擬測試** | 測試必須使用**真正的後台和 API**，禁止使用 Mock 數據、模板輸入輸出。所有測試結果必須來自真實服務回應。 |

---

## 🤖 AI 助手必讀（每次對話開始）

### 🎯 觸發關鍵字

當用戶輸入以下關鍵字時，AI 必須**自動讀取所有必讀文件**後再回應：

| 關鍵字 | 動作 |
|--------|------|
| `開展今天的工作` | 讀取必讀文件 → 報告今日任務 → 開始工作 |
| `work today` | 同上（英文版） |
| `開始工作` | 同上 |
| `今日任務` | 讀取工作記錄 → 報告待辦事項 |

### 💡 產品核心價值

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   👻 訪客（未登入）= Google News                                │
│      → 瀏覽 30 個熱門主題，吸引用戶註冊                         │
│                                                                 │
│   👤 會員（登入）= 網紅 AI 助手                                 │
│      → AI 生成專屬內容 + 風格學習 + 一鍵發布                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 📚 必讀文件（按順序）

| 順序 | 文件 | 目的 |
|:----:|------|------|
| 1 | **README.md** | 核心價值、規則、禁止操作 |
| 2 | [專案完整架構表.md](./專案完整架構表.md) | 路由、組件結構、技術架構 |
| 3 | [Git分支策略與版本管理.md](./Git分支策略與版本管理.md) | 分支規則、合併流程 |
| 4 | [工作記錄.md](./工作記錄.md) | 當前狀態、今日任務、進度 |
| 5 | [品牌設計規範.md](./品牌設計規範.md) | Lane Crawford 風格 |
| 6 | [按鈕測試ID架構表.md](./按鈕測試ID架構表.md) | data-testid 命名 |

### 🔒 Git 分支規則（摘要）

| 規則 | 說明 |
|------|------|
| 📍 **當前分支** | 查看 `工作記錄.md` 頂部或本文件頂部 |
| ❌ **禁止** | 永遠不要直接修改 `main` 或 `develop` |
| ✅ **開發** | 只在 `phase-X-*` 分支上進行 |
| 🏷️ **測試** | 測試通過後建立 Tag |

詳細流程請參考：[Git分支策略與版本管理.md](./Git分支策略與版本管理.md)

### ⛔ 啟動檢查

```
⚠️ 未完成上述讀取，禁止進行任何代碼修改！

檢查清單：
□ 確認當前分支（不是 main/develop）
□ 確認文檔更新日期
□ 了解今日任務（工作記錄.md）
□ 了解專案架構（專案完整架構表.md）
```

---

## 📐 專案架構（必讀）

**⚠️ 開發前請務必閱讀：**

| 文件 | 說明 |
|------|------|
| 📋 [專案完整架構表.md](./專案完整架構表.md) | **完整架構圖、路由定義、組件結構** |
| 🔘 [按鈕架構表.md](./按鈕架構表.md) | **按鈕清單、狀態定義、測試檢查** |
| 🧪 [按鈕測試ID架構表.md](./按鈕測試ID架構表.md) | **自動化測試 ID 規範** |
| 🎨 [品牌設計規範.md](./品牌設計規範.md) | **字體、標語、色彩、佈局規範** |
| 📝 [v4.0.0_Checklist_TestList.md](./v4.0.0_Checklist_TestList.md) | 開發檢查清單與測試案例 |
| 📖 [v4.0.0_完整需求規格書.md](./v4.0.0_完整需求規格書.md) | 完整功能需求規格 |

### 🛣️ 路由快速參考

```
認證頁面（無 Layout）：
  /language        → 語言選擇
  /login           → 登入
  /register        → 註冊
  /oauth-callback  → OAuth 回調

主要頁面（有 Layout）：
  /dashboard       → 控制面板 ⭐
  /topics          → 主題列表
  /topics/:id      → 主題詳情
  /channels        → 我的頻道
  /inspiration     → 靈感策劃
  /style-profile   → 風格檔案
  /publish         → 一鍵發布
  /social-connect  → 平台連接
  /settings        → 設定

⚠️ "/" 是重定向，不是頁面！Dashboard 在 /dashboard
```

---

## 🔴 核心設計原則（CRITICAL）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ⛔ 禁止使用靜態模板 - NO STATIC TEMPLATES                                  │
│                                                                             │
│   本專案的核心原則：                                                         │
│                                                                             │
│   ❌ 後台不存在任何靜態內容模板                                              │
│   ❌ 不使用預設文章範本                                                      │
│   ❌ 不使用固定文案模板                                                      │
│                                                                             │
│   ✅ 所有內容必須通過 AI API 即時生成                                        │
│   ✅ 每次生成都是獨一無二的內容                                              │
│   ✅ 根據用戶風格檔案動態調整輸出                                            │
│                                                                             │
│   原因：避免輸出重複的模板內容，確保每位用戶獲得專屬的個人化內容             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 即時生成架構

```
用戶請求 → AI API 即時呼叫 → 個人化參數注入 → 獨特內容輸出
    │              │                │               │
    │              │                │               └── 每次都不同
    │              │                └── 風格檔案/語言/格式偏好
    │              └── DeepSeek/OpenAI/Gemini
    └── 主題/靈感/頻道內容
```

### 禁止的做法

| ❌ 禁止 | ✅ 正確做法 |
|--------|------------|
| 儲存文章模板在資料庫 | API 即時生成文章 |
| 預設 Caption 範本 | AI 根據內容動態生成 Caption |
| 固定 Hashtag 列表 | AI 分析內容後即時推薦 Hashtag |
| 靜態風格範本 | 從用戶評分學習動態風格檔案 |

---

## 🤖 AI Agent 核心職責（CRITICAL）

### 產品核心理念

> **Influencers AI 是一個智能 AI Agent 系統。**  
> **Agent 會自動運行，用戶不需要操心任何事情。**  
> **打開 App，內容已經準備好，只需審核、編輯、發布。**

### 三大內容類別（公開內容）

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   📰 時尚趨勢 (Fashion)     - 每日 10 個主題                    │
│   🍜 美食推薦 (Food)        - 每日 10 個主題                    │
│   📊 社會趨勢 (Trend)       - 每日 10 個主題                    │
│                                                                 │
│   ══════════════════════════════════════════════════════════    │
│                                                                 │
│   👤 會員 (Member)  → 可看所有主題 + 生成文章 + 完整功能        │
│   👻 訪客 (Guest)   → 可看所有主題（瀏覽模式）                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**重要：主題是公開的熱門話題，不是用戶專屬內容。所有人都能看到相同的趨勢主題。**

### Agent 自動化流程

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   🤖 Agent 每 6 小時自動運行（無需用戶觸發）                      │
│                         ↓                                        │
│   📡 收集全球熱門話題 / RSS / 社群趨勢                           │
│                         ↓                                        │
│   🎯 AI 分析並生成 30 個主題（3 類別 × 10）                      │
│                         ↓                                        │
│   💾 儲存到資料庫                                                │
│                         ↓                                        │
│   ┌────────────────────────────────────────────────────────┐    │
│   │  📱 所有用戶/訪客 打開 App 即可看到今日熱門主題        │    │
│   │     - Dashboard 顯示今日主題概覽                       │    │
│   │     - Topics 頁面顯示完整主題列表                      │    │
│   └────────────────────────────────────────────────────────┘    │
│                         ↓                                        │
│   👤 用戶選擇感興趣的主題                                        │
│                         ↓                                        │
│   🤖 Agent 根據用戶「風格檔案」生成專屬文章/腳本                 │
│                         ↓                                        │
│   🖼️ Agent 自動搜尋並匹配相關圖片                               │
│                         ↓                                        │
│   ✅ 用戶審核 → 編輯 → 一鍵發布到社群平台                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Agent 的五大核心功能

| 功能 | 說明 | 觸發方式 |
|------|------|----------|
| 🔍 **主題發掘** | 自動收集熱門趨勢、RSS、社群話題 | 每 6 小時自動執行 |
| ✍️ **內容生成** | 根據用戶風格檔案生成文章/腳本 | 用戶點擊「生成」 |
| 🖼️ **圖片匹配** | 自動搜尋並匹配相關圖片 | 用戶點擊「匹配圖片」 |
| 📅 **排程發布** | 根據最佳時間安排發布 | 用戶設定排程 |
| 📊 **學習優化** | 從用戶評分中學習，越來越精準 | 用戶評分後自動學習 |

### 關鍵設計原則

| 原則 | 說明 |
|------|------|
| **自動化優先** | Agent 自動運行，用戶無需手動觸發主題收集 |
| **內容永遠存在** | Dashboard/Topics 頁面永遠有內容可看 |
| **訪客友好** | 未登入也能瀏覽所有主題，吸引用戶註冊 |
| **個人化生成** | 文章/腳本根據用戶風格檔案動態生成 |

---

## ⚠️ 其他重要設計要求

**所有版面設定必須確保在手機和平板上使用 Webapp 也能清楚顯示。**

詳細設計要求請參考：[專案設計要求.md](./專案設計要求.md)


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

### 前端自動化測試

本專案使用 `data-testid` 屬性標記所有按鈕、連結和輸入框，支援以下測試框架：

- **React Testing Library**
- **Cypress**
- **Playwright**

#### 測試 ID 命名規範

```
data-testid="{類型}-{位置}-{功能}"
```

| 前綴 | 類型 | 範例 |
|------|------|------|
| `btn-` | 按鈕 | `btn-login-submit` |
| `link-` | 連結 | `link-sidebar-dashboard` |
| `input-` | 輸入框 | `input-login-email` |
| `form-` | 表單 | `form-register` |
| `modal-` | 彈窗 | `modal-delete-confirm` |
| `menu-` | 選單 | `menu-header-lang` |

#### 已標記的組件

| 組件 | Test ID 數量 |
|------|:------------:|
| Sidebar.tsx | 11 |
| Header.tsx | 15 |
| Login.tsx | 10 |
| Register.tsx | 11 |
| Dashboard.tsx | 6 |

#### 測試範例

**Cypress:**
```javascript
// 測試登入流程
cy.get('[data-testid="input-login-email"]').type('test@example.com');
cy.get('[data-testid="input-login-password"]').type('password123');
cy.get('[data-testid="btn-login-submit"]').click();
cy.url().should('include', '/topics');
```

**React Testing Library:**
```javascript
import { render, screen, fireEvent } from '@testing-library/react';

test('should submit login form', () => {
  render(<Login />);
  
  fireEvent.change(screen.getByTestId('input-login-email'), {
    target: { value: 'test@example.com' }
  });
  fireEvent.click(screen.getByTestId('btn-login-submit'));
});
```

**Playwright:**
```javascript
test('login flow', async ({ page }) => {
  await page.goto('/login');
  await page.getByTestId('input-login-email').fill('test@example.com');
  await page.getByTestId('input-login-password').fill('password123');
  await page.getByTestId('btn-login-submit').click();
  await expect(page).toHaveURL('/topics');
});
```

📖 完整測試 ID 清單請參考：[按鈕測試ID架構表.md](./按鈕測試ID架構表.md)

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

### ⚠️ 工作記錄管理規範

**重要：本專案只維護一個統一的工作記錄文件 `工作記錄.md`**

| 規則 | 說明 |
|------|------|
| 📄 **唯一文件** | 所有工作記錄統一寫在 `工作記錄.md`，**禁止建立其他記錄文件** |
| 📝 **新增方式** | 新的工作內容添加到「工作記錄（按時間倒序）」區段的**最前面** |
| 🔄 **狀態更新** | 完成重大功能後，更新「當前狀態總覽」區段 |
| ✅ **待辦事項** | 待辦事項寫在工作記錄的「待處理」區段，不要建立獨立文件 |
| 🚫 **禁止行為** | 不要建立 `YYYY-MM-DD_工作記錄.md`、`明天待辦事項.md` 等文件 |

**工作記錄文件結構**：
```
工作記錄.md
├── 當前狀態總覽          # 已完成/進行中/待處理
│   └── 待處理/明日待辦   # 待辦事項放這裡，不要獨立文件
├── 工作記錄（按時間倒序）  # 每日工作詳情
├── 技術架構              # 專案結構說明
├── 規劃階段              # Phase 實施計劃
└── 重要提醒              # Cursor AI 規則等
```

**⛔ 禁止建立的文件類型**：
- `YYYY-MM-DD_工作記錄.md`
- `明天待辦事項.md` / `待辦事項_YYYY-MM-DD.md`
- `今日工作.md` / `每日記錄.md`

### ⚠️ Cursor AI 行為規則

1. **永遠不要直接修改 main 分支** - 所有更改必須在 feature 分支進行
2. **修改核心 API 前必須先創建備份分支**
3. **修改後端結構前必須先諮詢用戶**

**受保護的核心文件**（修改前必須先備份）：
- `backend/app/main.py`、`config.py`、`database.py`
- `backend/app/api/v1/*.py`
- `frontend/src/api/*.ts`
- `frontend/src/router/*.tsx`

**禁止操作**：
- 禁止刪除核心目錄結構
- 禁止清空關鍵文件內容
- 禁止修改資料庫連接邏輯
- 禁止修改 API 路由結構

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

**最後更新**：2026-02-05  
**維護者**：開發團隊


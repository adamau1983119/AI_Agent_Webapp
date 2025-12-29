# Backend - AI Agent Webapp

> **建立日期**：2025-12-19  
> **狀態**：開發中

---

## 📋 專案結構

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用入口
│   ├── database.py          # MongoDB 連接
│   ├── config.py            # 配置管理
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── topics.py    # 主題相關 API
│   │       ├── contents.py  # 內容相關 API
│   │       ├── images.py    # 圖片相關 API
│   │       └── health.py    # 健康檢查
│   ├── models/              # MongoDB 資料模型
│   │   ├── __init__.py
│   │   ├── topic.py
│   │   ├── content.py
│   │   └── image.py
│   ├── schemas/             # Pydantic 驗證模型
│   │   ├── __init__.py
│   │   ├── topic.py
│   │   ├── content.py
│   │   └── image.py
│   ├── services/            # 業務邏輯服務
│   │   ├── __init__.py
│   │   ├── ai/              # AI 服務
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # AI 服務抽象層
│   │   │   └── qwen.py      # 通義千問服務
│   │   └── images/          # 圖片服務
│   │       ├── __init__.py
│   │       ├── base.py      # 圖片服務抽象層
│   │       ├── unsplash.py  # Unsplash 服務
│   │       ├── pexels.py    # Pexels 服務
│   │       └── pixabay.py   # Pixabay 服務
│   ├── prompts/             # Prompt 模板
│   │   ├── article.txt      # 短文生成 Prompt
│   │   └── script.txt       # 腳本生成 Prompt
│   └── utils/               # 工具函數
│       ├── __init__.py
│       └── logger.py        # 日誌工具
├── requirements.txt          # Python 依賴
├── .env.example             # 環境變數範本
└── README.md                # 本文件
```

---

## 🚀 快速開始

### 1. 安裝 Python

**Windows**：
- 下載 Python 3.11+：https://www.python.org/downloads/
- 安裝時勾選「Add Python to PATH」

**驗證安裝**：
```bash
python --version
```

### 2. 建立虛擬環境

```bash
cd backend
python -m venv venv
```

**啟動虛擬環境**：

**方法 1：使用提供的腳本（推薦）**
- Windows CMD: 雙擊 `啟動虛擬環境.bat`
- Windows PowerShell: 執行 `.\啟動虛擬環境.ps1`

**方法 2：手動啟動**
- Windows CMD: `venv\Scripts\activate.bat`
- Windows PowerShell: `venv\Scripts\Activate.ps1`
- Linux/Mac: `source venv/bin/activate`

**注意**：如果 PowerShell 出現執行策略錯誤，請執行：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

### 4. 設定環境變數

複製 `.env.example` 為 `.env` 並填入實際值：

```bash
cp .env.example .env
```

### 5. 啟動服務

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📝 開發進度

### Phase 1: 後端基礎架構

- [x] 建立專案目錄結構
- [ ] 設定 Python 虛擬環境
- [ ] 安裝核心依賴
- [ ] 建立 FastAPI 應用
- [ ] 設定 MongoDB 連接
- [ ] 建立資料模型
- [ ] 建立基礎 API 路由

### Phase 2: API 整合

- [ ] AI 服務整合（通義千問）
- [ ] 圖片服務整合（Unsplash、Pexels、Pixabay）
- [ ] 資料收集服務

---

## 🔧 技術棧

- **框架**：FastAPI
- **資料庫**：MongoDB (Motor)
- **驗證**：Pydantic
- **AI 服務**：通義千問（Qwen）
- **圖片服務**：Unsplash、Pexels、Pixabay

---

**最後更新**：2025-12-19


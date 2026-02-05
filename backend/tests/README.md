# 測試執行指南

## 安裝測試依賴

```bash
# 進入 backend 目錄
cd backend

# 激活虛擬環境
.\venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac

# 安裝測試依賴
pip install -r tests/requirements-test.txt
```

## 執行測試

### 執行所有測試
```bash
pytest tests/ -v
```

### 執行特定測試文件
```bash
# Phase 1.2 + 1.3: 文章評分 + 多樣性
pytest tests/test_scoring_service.py -v

# Phase 5B: 智能圖片匹配
pytest tests/test_image_matcher.py -v

# Phase 2: 健康監控
pytest tests/test_feed_health.py -v

# Phase 1.1: RSS 角色分配
pytest tests/test_feed_roles.py -v

# Phase 3: Health API
pytest tests/test_feeds_api.py -v
```

### 執行並顯示覆蓋率
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

### 執行並顯示詳細輸出
```bash
pytest tests/ -v -s
```

## 測試文件結構

```
tests/
├── __init__.py                 # 測試包初始化
├── conftest.py                 # 共用 fixtures
├── requirements-test.txt       # 測試依賴
├── test_scoring_service.py     # Phase 1.2 + 1.3 (14 個測試)
├── test_image_matcher.py       # Phase 5B (16 個測試)
├── test_feed_health.py         # Phase 2 (12 個測試)
├── test_feed_roles.py          # Phase 1.1 (14 個測試)
└── test_feeds_api.py           # Phase 3 (10 個測試)
```

## 測試統計

| 測試文件 | 測試數量 | 涵蓋 Phase |
|---------|---------|-----------|
| test_scoring_service.py | 14 | Phase 1.2, 1.3 |
| test_image_matcher.py | 16 | Phase 5B |
| test_feed_health.py | 12 | Phase 2 |
| test_feed_roles.py | 14 | Phase 1.1 |
| test_feeds_api.py | 10 | Phase 3 |
| **總計** | **66** | **所有 Phase** |

## 預期測試結果

所有測試應該通過，因為：
- ✅ 所有功能已實施
- ✅ 測試使用 mock 避免外部依賴
- ✅ 測試覆蓋核心邏輯

## 故障排除

### 如果測試失敗

1. **ImportError**: 確保在 backend 目錄執行，且虛擬環境已激活
2. **ModuleNotFoundError**: 執行 `pip install -r requirements.txt` 安裝主依賴
3. **AsyncIO 錯誤**: 確保安裝 `pytest-asyncio`

### 跳過需要 MongoDB 的測試

某些測試需要 MongoDB 連接。如果沒有 MongoDB，可以使用 mock：

```bash
pytest tests/ -v --ignore=tests/test_feed_health.py
```

## 持續集成

在 CI/CD 環境中執行：

```bash
pytest tests/ --cov=app --cov-report=xml --junitxml=test-results.xml
```


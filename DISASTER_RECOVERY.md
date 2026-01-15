# 災難恢復指南

**最後更新：** 2026-01-13  
**適用於：** AI Agent Webapp for Social Media Content Generation

---

## 🚨 緊急情況處理流程

### 情況 1：專案結構被破壞

#### 步驟 1：立即停止所有更改
```bash
# 暫存當前更改
git stash

# 或取消所有未提交的更改
git reset --hard HEAD
```

#### 步驟 2：檢查 Git 歷史
```bash
# 查看最近的提交
git log --oneline -20

# 查看文件變更歷史
git log --all --full-history -- <file-path>
```

#### 步驟 3：還原到穩定版本

**方法 A：還原到特定提交**
```bash
# 找到最後一個穩定提交的 hash
git log --oneline

# 還原到該提交
git checkout <stable-commit-hash>

# 創建還原分支
git checkout -b recovery-$(date +%Y%m%d)
```

**方法 B：還原到標籤**
```bash
# 查看所有標籤
git tag -l

# 還原到穩定標籤
git checkout <stable-tag-name>
```

**方法 C：從備份目錄還原**
```bash
# 查看備份目錄
ls -la backups/daily/

# 還原特定備份
cp -r backups/daily/20260113_120000/* ./
```

#### 步驟 4：驗證還原
```bash
# 運行結構驗證
python scripts/validate_structure.py

# 檢查關鍵文件
ls -la backend/app/main.py
ls -la frontend/src/api/client.ts
```

#### 步驟 5：創建緊急備份
```bash
# 創建緊急備份標籤
git tag emergency-backup-$(date +%Y%m%d-%H%M%S)

# 推送到遠程
git push origin --tags
```

---

### 情況 2：資料庫損壞或數據丟失

#### 步驟 1：檢查 MongoDB Atlas 快照
1. 登入 MongoDB Atlas
2. 進入 Clusters → Snapshots
3. 查看可用的快照列表
4. 選擇最近的穩定快照

#### 步驟 2：還原資料庫
1. 在 MongoDB Atlas 中選擇快照
2. 點擊 "Restore" 按鈕
3. 選擇還原目標（可以創建新集群或還原到現有集群）
4. 等待還原完成

#### 步驟 3：更新連接字符串
```bash
# 更新環境變數
# Railway: Settings → Variables → MONGODB_URL
```

#### 步驟 4：驗證資料庫連接
```bash
# 測試後端健康檢查
curl https://gentle-enchantment-production-1865.up.railway.app/health
```

---

### 情況 3：部署環境崩潰

#### Railway 後端還原

**方法 A：Rollback 到上一個版本**
1. 登入 Railway Dashboard
2. 進入 Deployments 頁面
3. 找到上一個成功的部署
4. 點擊 "Redeploy" 或 "Rollback"

**方法 B：從 Git 重新部署**
```bash
# 還原到穩定版本
git checkout <stable-commit>

# 推送到觸發重新部署
git push origin main
```

#### Vercel 前端還原

**方法 A：Rollback 部署**
1. 登入 Vercel Dashboard
2. 進入 Deployments 頁面
3. 找到上一個成功的部署
4. 點擊 "..." → "Promote to Production"

**方法 B：從 Git 重新部署**
```bash
# 還原到穩定版本
git checkout <stable-commit>

# 推送到觸發重新部署
git push origin main
```

---

## 📋 還原檢查清單

### Git 還原後檢查：
- [ ] 結構驗證通過 (`python scripts/validate_structure.py`)
- [ ] 關鍵文件存在且非空
- [ ] 可以正常啟動後端 (`python -m uvicorn app.main:app`)
- [ ] 可以正常啟動前端 (`npm run dev`)
- [ ] API 端點可以訪問 (`/health`)

### 資料庫還原後檢查：
- [ ] MongoDB 連接成功
- [ ] 可以查詢主題數據
- [ ] 可以查詢內容數據
- [ ] 可以查詢圖片數據

### 部署還原後檢查：
- [ ] 後端健康檢查通過
- [ ] 前端可以正常訪問
- [ ] API 請求可以正常響應
- [ ] 圖片可以正常顯示

---

## 🔄 定期備份策略

### 每日備份
- **時間：** 每天凌晨 2:00
- **內容：** 關鍵文件和配置
- **位置：** `backups/daily/`
- **保留：** 7 天

### 每週備份
- **時間：** 每週日 凌晨 2:00
- **內容：** 完整專案快照
- **位置：** `backups/weekly/`
- **保留：** 4 週

### 里程碑備份
- **觸發：** 每次重要功能發布
- **內容：** 完整專案 + Git 標籤
- **位置：** `backups/milestones/`
- **保留：** 永久

---

## 📞 緊急聯繫方式

### 技術支持
- **GitHub Issues:** https://github.com/adamau1983119/AI_Agent_Webapp/issues
- **Railway Support:** https://railway.app/help
- **Vercel Support:** https://vercel.com/support

### 服務狀態
- **Railway Status:** https://status.railway.app/
- **Vercel Status:** https://www.vercel-status.com/
- **MongoDB Atlas Status:** https://status.mongodb.com/

---

## 📝 還原記錄

記錄每次還原操作的詳細信息：

| 日期 | 問題描述 | 還原方法 | 還原時間 | 負責人 | 備註 |
|------|----------|----------|----------|--------|------|
| 2026-01-13 | 初始文檔 | - | - | - | 建立還原流程 |

---

## ⚠️ 預防措施

### 日常維護
1. ✅ 定期檢查備份是否正常
2. ✅ 定期測試還原流程
3. ✅ 監控系統健康狀態
4. ✅ 及時修復已知問題

### 部署前檢查
1. ✅ 運行結構驗證
2. ✅ 運行單元測試
3. ✅ 運行 E2E 測試
4. ✅ 檢查環境變數
5. ✅ 創建備份標籤

---

**重要提醒：** 在進行任何還原操作前，請確保已經創建了當前狀態的備份！


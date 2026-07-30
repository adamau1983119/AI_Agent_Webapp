# 版本管理政策（v6／v7 凍結 · v8 上架演進）

> **建立日期**：2026-06-04  
> **修訂**：2026-07-29（**v7 code-freeze**；上架改走 **v8**）  
> **狀態**：生效中  
> **目的**：v6／v7 珍貴快照不可被上架熱修覆蓋；**測試與正式上架只在 v8**。

---

## 1. 原則（必讀）

| # | 規則 |
|---|------|
| 1 | **v6 文件＝唯讀凍結**：僅勘誤（`v6-doc-fix-only`）；**禁止**改功能描述。 |
| 2 | **v7 ＝ code-freeze 唯讀保全**：tag **`v7.0.0-code-freeze`**（`9556ea7`）＋ [`docs/archives/v7.0.0_*_凍結.md`](./archives/v7.0.0_CODE_FREEZE_MANIFEST.md)；**禁止**改正文。 |
| 3 | **v8 ＝上架／測試／熱修唯一演進 SoT**：分支 **`feature/v8-launch`**；架構寫 [`專案完整架構表_v8.md`](../專案完整架構表_v8.md)。 |
| 4 | **Git**：還原 v7 用 tag／`backup/v7-pre-launch`；**勿**在 freeze tag 上直接 commit 上架變更。 |

---

## 2. v6 凍結清單

| 路徑 | 處理 |
|------|------|
| [`專案完整架構表.md`](../專案完整架構表.md) | 不得改正文 |
| [`docs/archives/v6.0.0_專案完整架構表_凍結.md`](./archives/v6.0.0_專案完整架構表_凍結.md) | **永遠不得修改** |

---

## 3. v7 凍結清單（2026-07-29）

| 路徑／Ref | 處理 |
|-----------|------|
| Git tag **`v7.0.0-code-freeze`** | 程式＋文件可還原錨點 |
| 分支 **`backup/v7-pre-launch`** | 長期備份分支 |
| [`docs/archives/v7.0.0_專案完整架構表_凍結.md`](./archives/v7.0.0_專案完整架構表_凍結.md) | **永遠不得修改** |
| [`docs/archives/v7.0.0_需求文件_凍結.md`](./archives/v7.0.0_需求文件_凍結.md) | **永遠不得修改** |
| [`docs/archives/v7.0.0_CODE_FREEZE_MANIFEST.md`](./archives/v7.0.0_CODE_FREEZE_MANIFEST.md) | 保全索引 |
| [`專案完整架構表_v7.md`](../專案完整架構表_v7.md) | 頂部凍結橫幅；**不再**作上架演進 SoT |

勘誤例外：PR 必須標 **`v7-doc-fix-only`**，且**不得**改 archives 凍結副本（應改活檔或只修連結）。

---

## 4. v8 演進清單（上架）

| 路徑 | 角色 |
|------|------|
| [`專案完整架構表_v8.md`](../專案完整架構表_v8.md) | **v8 架構 SoT** |
| [`docs/alter_ego_launch_dns_checklist.md`](./alter_ego_launch_dns_checklist.md) | 正式域 DNS／OAuth |
| 分支 **`feature/v8-launch`** | 上架與線上熱修 |
| 未來 | `docs/v8_*` checklist／需求增量 |

---

## 5. Git 操作指引

### 5.1 還原 v7 整樹

```powershell
git fetch --tags origin
git checkout v7.0.0-code-freeze
```

### 5.2 檢查 v7 隔離

```powershell
python scripts/check_git_v7_refs.py
```

### 5.3 檢查 v6 ref

```powershell
python scripts/check_git_v6_refs.py
```

### 5.4 上架開發

```text
feature/v8-launch
```

---

## 6. 助手／開發者檢查清單

- [ ] 本次是否上架／DNS／生產設定？→ **只動 v8**（`feature/v8-launch`）
- [ ] 是否誤改 `docs/archives/v7.0.0_*_凍結.md`？→ **拒絕**
- [ ] 是否誤改 `docs/archives/v6.0.0_*`？→ **拒絕**
- [ ] 新路由／API 是否寫入 **架構表 v8**？
- [ ] `工作記錄.md` 頂部是否標 **v8 上架項**（v7 歷史段保留）

---

## 7. 版本歷史

| 日期 | 變更 |
|------|------|
| 2026-06-04 | 初版：v6 凍結、v7 演進 |
| 2026-07-29 | **v7 code-freeze**；archives 獨立檔；**v8** 為上架 SoT |

**文件維護者**：開發團隊

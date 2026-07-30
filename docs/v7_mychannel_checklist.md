# v7.1 MyChannel SKU（我的頻道）— 工作明細與完成檢查清單

> **SoT 對照**：[`docs/V7.1-SPEC.md`](./V7.1-SPEC.md)、[`專案完整架構表_v7.md`](../專案完整架構表_v7.md) **MyChannel SKU**、[`v7.0.0_需求文件.md`](./v7.0.0_需求文件.md) 頻道區塊 13  
> **與 Discover 分界**：**禁止**混用 `public_feed:feed:*`、**禁止** Mock 假卡（MC-6；對齊 README）  
> **建議分支**：延續 `feature/v7-cost-pipeline` 或 `feature/v7-mychannel`（勿在 `main` 直接改）  
> **填寫規則**：勾選前須**可重現** + **截圖**；禁止模糊签收（UI + Network）  
> **截圖政策**：[`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)（前綴 `…_v7_MC-…`、`E0-MC_*`）  
> **測試矩陣**：[`architecture_test_matrix.md`](./architecture_test_matrix.md) **矩陣 L**  
> **日期 SoT**：**2026-07-21** — 見 [`工作記錄.md`](../工作記錄.md) 頂部  
> **備份（2026-06-25）**：[`docs/backups/2026-06-25_f05-mychannel-program_snapshot/`](../backups/2026-06-25_f05-mychannel-program_snapshot/SNAPSHOT_README.md)  
> **備份（2026-07-21）**：[`docs/backups/2026-07-21_launch-sprint-trigger_snapshot/`](../backups/2026-07-21_launch-sprint-trigger_snapshot/SNAPSHOT_README.md)  
> **測試 SoT**：[`launch_test_sprint_2026-07-22.md`](./v7_program_line/launch_test_sprint_2026-07-22.md)（**Day2＝MC + Post Kit**）  
> **上線 DNS**：[`alter_ego_launch_dns_checklist.md`](./alter_ego_launch_dns_checklist.md)（品牌 **Alter Ego** · 網域 **`ai-alterego.com`**）

---

## Phase DNS-0 — 上線前（品牌／網域 · 文件）

> **觸發**：MVP 程式 + 上架衝刺結案後；**開發期不勾** Spaceship 變更。

- [x] **PD-DNS0-01** [`alter_ego_launch_dns_checklist.md`](./alter_ego_launch_dns_checklist.md) 建立（一頁 checklist + 附錄 A Spaceship／`.env`）  
- [x] **PD-DNS0-02** [`專案完整架構表_v7.md`](../專案完整架構表_v7.md) **品牌與網域** 章、本檔互鏈  
- [ ] **CD-DNS0-1** 上線日依 checklist **D1～F3** 逐項勾選（瀏覽器 + `check_meta_config.py`）— **2026-07-30**：D1～D5／H1～H4／P4／E1～E7／S1／S3 ✅；O2～O3／S2／E8／F2 ⏳
- [ ] **CD-DNS0-2** 正式域 E2E **S1～S5**（禁止 Mock）+ 證據目錄 — S1／S3 ✅；S2／S4／S5 ⏳

---

## 工程鐵律 MC-1～MC-7

> 詳述見 [`V7.1-SPEC.md`](./V7.1-SPEC.md) 頻道區塊 2。開發前必讀；**違反任一條不得勾 CD-*。**

- [ ] **MC-RULE-1** 團隊已讀 V7.1-SPEC 頻道區塊 2 + README 禁止模糊驗收  
  - 證據：工作記錄一句 —

---

## 開發順序（v7.1 · 原子 Phase）

> **策略**：MyChannel **獨立於** Discover PF-*；程式已結 → **上架衝刺 Day2** 跑 E0-MC／CD-MC*。

| 序 | Phase | 目標 | 狀態 |
|:--:|-------|------|------|
| 0 | **MC-0** | 規格／鐵律對齊（本檔 + V7.1-SPEC） | ✅ 文件 |
| 1 | **MC-1** | Redis 帳本 + 初始 5 點 + AddPoints | ✅ 程式（2026-06-25） |
| 2 | **MC-2** | `GET …/my-channel/feed`（免費層；無 URL） | ✅ 程式 |
| 3 | **MC-3** | `POST …/unlock`（1 點；URL + digest_300） | ✅ 程式 |
| 4 | **MC-4** | 前端 MyChannel 首屏 + 登入 redirect | ✅ 程式 |
| 5 | **MC-5** | Step 10–12 防禦（schema／降級／防連點） | ✅ 程式 |
| 6 | **MC-6** | 熱門頻道模板（無頻道用戶） | ✅ **PD-MC4-03**（2026-07-21 · 靜態 JSON） |
| 7 | **上架衝刺測試** | E0-MC + CD-MC*（Day2） | ✅ **Day2 主路結**（2026-07-28 補測：E0-MC／CD-MC2-1／CD-MC3-1／2／PK1～4）；餘 CD-MC3-3 可選、CD-MC1-2／3 改日 |

---

## 文件收口（2026-07-21）

- [x] **DOC-BAK-4** 快照 `2026-07-21_launch-sprint-trigger_snapshot`  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-07-21_launch-sprint-trigger_snapshot/SNAPSHOT_README.md)

---

## Phase MC-0 — 規格（文件）

- [x] **PD-MC0-01** [`V7.1-SPEC.md`](./V7.1-SPEC.md) 建立  
- [x] **PD-MC0-02** 需求 頻道區塊 13、架構表 MyChannel 章、本檔、工作記錄交叉引用  
- [x] **PD-MC0-03** 矩陣 L 草案入 [`architecture_test_matrix.md`](./architecture_test_matrix.md)

---

## Phase MC-1 — 點數帳本（Redis + ledger）

**結案判定**：**CD-MC1-1～CD-MC1-3** 必須 `[x]`。

### 工作明細

- [x] **PD-MC1-01** `credit_ledger` 服務：`balance` + `DECRBY` + idempotency key  
  - 證據：`credit_ledger_service.py`；`check_mychannel_bf_static.py` —
- [x] **PD-MC1-02** 新用戶註冊／首次進站 → **5 點**  
  - 證據：`ensure_initial_balance` + `INITIAL_CREDITS=5` —
- [x] **PD-MC1-03** `POST /api/v1/admin/users/{id}/credits` — AddPoints  
  - 證據：`my_channel.admin_router`；admin role gate —
- [x] **PD-MC1-04** 扣點失敗 → **402**；**禁止**後續 DeepSeek 外連  
  - 證據：`HTTP_402_PAYMENT_REQUIRED`；unlock 無 LLM 呼叫 —

### 完成檢查

- [ ] **CD-MC1-1** 新用戶 balance=5（Redis 或 Mongo 可查）  
  - **N/A（2026-07-28）**：本測帳已非新戶；unlock 前 balance=4、後=3（見 CD-MC3-1）—
- [ ] **CD-MC1-2** AddPoints +10 → balance=15
- [ ] **CD-MC1-3** 餘額 0 時 unlock → 402；Network **無** `api.deepseek.com`

---

## Phase MC-2 — Feed 組裝（免費層）

**結案判定**：**CD-MC2-1～CD-MC2-4** 必須 `[x]`。

### 工作明細

- [x] **PD-MC2-01** `my_channel_cache.py` — key `my_channel:feed:{user_id}:{lang}`  
  - 證據：`my_channel_cache.py`；grep **0** `public_feed:feed:` —
- [x] **PD-MC2-02** 組裝 **僅**讀 DB 候選（heading + ≤30 字）；**禁止**登入 collect  
  - 證據：`my_channel_service._assemble_cards` + `list_by_channel_id` —
- [x] **PD-MC2-03** 出卡前驗證 **MC-1**（無 URL 不入 feed）  
  - 證據：`_has_valid_source_url` —
- [x] **PD-MC2-04** 24h 組裝 **≤3 次**（MC-7）  
  - 證據：`can_assemble` + `_MAX_ASSEMBLES_24H = 3` —

### 完成檢查

- [x] **CD-MC2-1** `GET …/my-channel/feed?lang=zh-TW` → **200**；每卡有 heading + intro；**無** `source_url`  
  - 證據（2026-07-28）：[`2026-07-28_v7_CD-MC2-1_feed_200.png`](./evidence/v7/2026-07-28/2026-07-28_v7_CD-MC2-1_feed_200.png)；後端卡 keys=`heading,intro,id,…` 無 source_url —
- [x] **CD-MC2-2** grep：MC 模組 **0** `public_feed:feed:`  
  - 證據（2026-07-28）：`check_mychannel_bf_static.py` PASS；`my_channel/*.py` hits=0 —
- [ ] **CD-MC2-3** 登入組裝前後 Network **無** collect／DeepL／DeepSeek（除預期 unlock）
- [ ] **CD-MC2-4** DB 中無 URL 的 topic **不出現**於 feed JSON

---

## Phase MC-3 — 解鎖（1 點）

**結案判定**：**CD-MC3-1～CD-MC3-3** 必須 `[x]`。

### 工作明細

- [x] **PD-MC3-01** `POST …/my-channel/topics/{id}/unlock` — 先 DECRBY 再回 body  
  - 證據：topic 驗證後 `decr_credits`；`check_mychannel_bf_static.py` —
- [x] **PD-MC3-02** 回傳 `source_url`（http(s)）+ `digest_300`（≤300 字）  
  - 證據：`schemas/my_channel.py` `Field(max_length=300)` —
- [x] **PD-MC3-03** 重複 unlock 同 topic（同 idempotency key）→ 不二次扣點  
  - 證據：`get_unlock_result` / `set_unlock_result` Redis —

### 完成檢查

- [x] **CD-MC3-1** unlock 成功 → balance **-1**；response 含可點 URL  
  - 證據（2026-07-28）：`POST …/topics/topic_food_20260602214627_3d67f550/unlock` **200**；balance **4→3**；[`…_CD-MC3-1_unlock_200.png`](./evidence/v7/2026-07-28/2026-07-28_v7_CD-MC3-1_unlock_200.png)；Response JSON 見 `…_CD-MC3-1_unlock_response.json` —  
- [x] **CD-MC3-2** 手動點 URL → 海外原文可開（截圖）  
  - 證據（2026-07-28）：`source_url`=SCMP Brazilian beef；[`…_CD-MC3-2_unlock_response_ui.png`](./evidence/v7/2026-07-28/2026-07-28_v7_CD-MC3-2_unlock_response_ui.png)；助手 HEAD/GET 可連 —  
- [ ] **CD-MC3-3** 快速雙擊 unlock → 只扣 **1** 點

---

## Phase MC-4 — 前端 MyChannel 首屏

**結案判定**：**CD-MC4-1～CD-MC4-3** 必須 `[x]`。

### 工作明細

- [x] **PD-MC4-01** 登入後預設進 MyChannel（非 Discover 首屏）  
  - 證據：`AlterEgoGateRedirect` → `/my-channel` —
- [x] **PD-MC4-02** 卡列表 + 解鎖 CTA；i18n 三語；`data-testid` 對照架構表  
  - 證據：`MyChannel.tsx`；`myChannel.*` 三語；`btn-my-channel-unlock-*` —
- [x] **PD-MC4-03** 無頻道 → 熱門模板 UI（MC-6；靜態 JSON）  
  - 證據：`channel_templates.json` + `GET /my-channel/channel-templates` + `MyChannel.tsx` 模板區；CreateChannel query 預填 —  
  - 現況：空狀態 → 建立頻道／Discover 連結（非 curated 模板）—

### 完成檢查

- [x] **CD-MC4-1** 登入 → MyChannel 路由（截圖 + URL）  
  - 證據（2026-07-28）：同上 E0-MC-A；URL `/my-channel` —
- [x] **CD-MC4-2** 免費卡可見 heading+intro；解鎖前 **無** 外連按鈕  
  - 證據（2026-07-28）：E0-MC-A／feed 截圖僅「解鎖全文 (1點)」CTA，無外連 —
- [ ] **CD-MC4-3** RSS 空 →「暫無更新」；**無**假卡

---

## Phase MC-5 — 防禦 Step 10–12

### 工作明細（程式段）

- [x] **PD-MC5-01** unlock response schema 字數上限（`digest_300` ≤300、`intro` ≤30）  
  - 證據：`schemas/my_channel.py` Pydantic `Field(max_length=…)` —
- [x] **PD-MC5-02** Redis 不可用 → 帳本降級 Mongo `credit_ledger` collection  
  - 證據：`credit_ledger_service.get_balance` Mongo fallback —
- [x] **PD-MC5-03** 解鎖 idempotency + 前端按鈕 disabled（防連點）  
  - 證據：`unlockingId` state；`get_unlock_result` —

### 完成檢查（測試週）

- [ ] **CD-MC5-1** unlock response JSON schema 字數上限 enforced  
- [ ] **CD-MC5-2** Redis 不可用 → 仍 200 讀 Mongo 降級  
- [ ] **CD-MC5-3** 解鎖中按鈕 disabled + 後端 idempotency（併 CD-MC3-3）

---

## 每日 E0-MC（上架衝刺 · Day2）

- [x] **E0-MC-A** `/health` + 登入 MyChannel 首屏  
  - 證據（2026-07-28）：[`2026-07-28_v7_E0-MC-A_my_channel_home.png`](./evidence/v7/2026-07-28/2026-07-28_v7_E0-MC-A_my_channel_home.png) — `/my-channel` + adam au + 多卡 +「編寫全文 (1點)」—
- [x] **E0-MC-B** feed GET 200 + unlock 一卡 + URL 可點  
  - 證據（2026-07-28）：feed／unlock **200**；`source_url` SCMP **200** 可開（CD-MC2-1／CD-MC3-1／2）—

---

## 對照架構表

| 架構 MC | 本檔 |
|---------|------|
| MC-1 帳本 | CD-MC1-* |
| MC-2 feed | CD-MC2-* |
| MC-3 unlock | CD-MC3-* |
| MC-4 前端 | CD-MC4-* |
| MC-5 防禦 | CD-MC5-* |

---

## 變更紀錄

| 日期 | 說明 |
|------|------|
| 2026-06-25 | **PD-MC1～MC5**、**PD-AE1-F05～F07** 程式段；備份 `2026-06-25_f05-mychannel-program_snapshot` |
| 2026-06-16 | 初版：MC-0～6、E0-MC、對齊 V7.1-SPEC 與 PM 點數／解鎖規則 |

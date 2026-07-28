# 上架衝刺測試排程 — 2026-07-22～24（每日 1.5h）

> **目標**：三日內完成 **MVP 上架必測**；非阻塞項標 **N/A／上線後**。  
> **環境**：`:8000` + `:3000`；每項須 **截圖或 Network 一句** 才可勾。  
> **SoT**：本檔 + [`index.md`](./index.md) Active + [`工作記錄.md`](../../工作記錄.md) 頂部。  
> **觸發**：`專案開始，先讀 docs/v7_program_line/_GATE.md 與 launch_test_sprint_2026-07-22.md 當日 Day，再開測 @AGENTS.md`  
> （等價：`專案開始 v7 測試週`）

---

## 原則（4.5h 總量）

| 優先 | 做法 |
|------|------|
| **P0 上架門檻** | 登入動線、AE 主路、MyChannel 扣點、Post Kit copy、Discover 有卡 |
| **P1 同日若有餘裕** | rollback 手測、Discover 語系、Token 煙霧 |
| **延後／N/A** | DNS 正式域、KPI 基線、staging 30 批（無 DT-5 則 N/A）、全量 C*／X* 細項 |

**證據目錄建議**：`docs/evidence/v7/2026-07-22/`～`2026-07-24/`（截圖檔名含當日代號）。

---

## Day 1｜2026-07-22（三）· 90′ — 環境 + Alter Ego 主路

| 分鐘 | 代號 | 動作 | PASS |
|------|------|------|------|
| 0–10 | **E0-B／E0-F／E0-N** | `/health`（含 cost_controls）；`:3000` 可開；Network Preserve log | 截圖 1 張可勾三項 |
| 10–35 | **E0-AE-1** | 新／pending 帳：onboarding → 貼范文 extract → active | UI + Network extract 200 |
| 35–50 | **E0-AE-2** | Skip → 進 `/my-channel`（不再強制 onboarding） | 截圖 URL |
| 50–70 | **E0-AE-3 + CD-AE-C3** | 詳情頁 generate：Pro + response `generation_meta.dna_version_id` | Network + 對照 snapshot（Mongo 或 status） |
| 70–85 | **CD-AE-C1** | extract → preview／Post Kit 區可見仿文 + copy | 截圖 Post Kit |
| 85–90 | 收尾 | 勾 checklist；失敗項寫 FAIL＋重現 | 工作記錄一句 |

### Day1 實測進度（2026-07-22）

| 代號 | 結果 | 證據一句 |
|------|------|----------|
| **E0-B／F** | ✅ | `:8000/health` healthy／DB connected；`:3000` 可開 |
| **E0-AE-1** | ✅ **PASS** | extract **200** → active → Continue → `/my-channel`；見 `docs/evidence/v7/2026-07-22/` |
| **E0-AE-2** | ✅ **PASS**（2026-07-28） | Skip **200** → `/my-channel`；見 `docs/evidence/v7/2026-07-28/` |
| **E0-AE-3／CD-AE-C3** | ✅ **PASS**（2026-07-28） | `regenerate` **200**；`deepseek-v4-pro` + `generation_meta.dna_version_id`；見 `docs/evidence/v7/2026-07-28/` |
| **CD-AE-C1** | ✅ **PASS**（2026-07-28） | Post Kit 仿文／copy 區 + `adopt-copy` **200**；見 `…_CD-AE-C1_postkit_copy_adopt_200.png` |
| **CD-AE-C2**（可選同日） | ✅ **PASS**（2026-07-28） | Mongo `adopted_without_edit`（audit + feedback） |

**同日若提前完成（可選）**：**CD-AE-A2**（抽 1 份范文人工看 tone）或 **CD-AE-C2**（adopt-copy → audit／feedback 可查）。

---

## Day 2｜2026-07-23（四）· 90′ — MyChannel + Post Kit

| 分鐘 | 代號 | 動作 | PASS |
|------|------|------|------|
| 0–10 | **E0-MC-A** | `/health` + 登入 MyChannel 首屏 | 截圖 |
| 10–25 | **CD-MC4-1／CD-MC1-1** | 登入落點 MyChannel；新戶或查 balance=5 | URL + 餘額 |
| 25–45 | **CD-MC2-1 + E0-MC-B** | feed GET 200；卡有 heading+intro；**無** `source_url` | Network body |
| 45–65 | **CD-MC3-1／2 + CD-MC5-3** | unlock → balance−1；原文可開；解鎖中 disabled | 截圖 + Network |
| 65–75 | **CD-MC3-3**（或併上） | 快速雙擊 unlock → 只扣 1 | Network 兩次／餘額 |
| 75–90 | **PK1～PK4** | 固定 topic：四區可見；copy 標題／內文／hashtag | 剪貼簿核對 |

**同日若有餘裕**：**PK5～PK6**（圖連結 + 375 RWD）；**CD-MC4-2**（解鎖前無外連）；無頻道帳測 **MC-6 模板** 可點進 CreateChannel。

**餘額 0 → 402（CD-MC1-3）**：若無空戶，用 admin 扣光或記 **BLOCK／改日**。

### Day2 實測進度（2026-07-28 補測）

| 代號 | 結果 | 證據一句 |
|------|------|----------|
| **E0-MC-A／CD-MC4-1** | ✅ | `/my-channel` 首屏；`…_E0-MC-A_my_channel_home.png` |
| **CD-MC2-1／E0-MC-B** | ✅ | feed **200** 無 `source_url`；unlock **200** + SCMP 可開 |
| **CD-MC3-1／2／CD-MC4-2** | ✅ | balance 4→3；`…_unlock_response.json` |
| **CD-MC1-1** | N/A | 非新戶 |
| **CD-MC3-3** | ⏳ | 雙擊只扣 1（可選） |
| **PK1** | ✅ | 四區可見；`…_PK1-4_postkit_four_zones.png` |
| **PK2～4** | ✅ | User copy OK（標題1／內文／Hashtag）+ toast；`…_PK2-4_copy_ok_toast.png` |
| **PK5／6** | N/A／上線後 | Day2 允許 |

---

## Day 3｜2026-07-24（五）· 90′ — Discover + 煙霧 + 收口

| 分鐘 | 代號 | 動作 | PASS |
|------|------|------|------|
| 0–15 | **E0-PF + CD-4-1** | `/discover` ≥1 張卡（真 RSS／既有庫；禁空殼） | 截圖 |
| 15–30 | **CD-4-2／CD-B-3** | Network **僅** feed GET；無 generate／DeepL／DeepSeek | Network |
| 30–40 | **CD-4-3／CD-B-2** | zh-TW↔ja（＋en）標題／摘要變化、非裸 key | 兩語截圖／Network `lang=` |
| 40–55 | **PD-AE2-03** | 故意改壞 DNA／tone → rollback → preview 恢復 | Network rollback 200 |
| 55–70 | **Token 煙霧** | 任選：**C1-5** generate=pro；**C3-3** 無 summary_flash → 400；或 **C4-2** 切語系 0 翻譯 API | 各一句證據 |
| 70–85 | **Landing 煙霧** | `/welcome` 可開、主 CTA 可點（靜態已過；補 1 張 375 可選） | 截圖 |
| 85–90 | **三日收口** | 總表：PASS／FAIL／N/A；未測 ≤3 且寫理由；工作記錄「上架測試結案」 | 見下表 |

**同日若有餘裕**：**CD-H-4**（重啟後 `/health` 含 `safe_batch_size`）；**CD-MC2-2**（grep 靜態可助手代跑）。

---

## 三日後允許 N/A／上線後（不阻塞「可上架」宣告）

| 項 | 理由 |
|----|------|
| **CD-DNS0-*** | 正式域／Spaceship；上線日另跑 |
| **CD-AE-KPI-*** | 需流量基線；上線後 7～14 日 |
| **DT-5 + staging 30 批** | 營運後台告警未設則 **N/A**；設好再補 |
| **CD-MC5-2** Redis 全掛 | 邊緣；可上線後 |
| **CD-2-*** 全批細項、**CD-X-***、全量 **C2／C3／C4／X-*** | 壓縮為 Day3 煙霧；餘項標「上線後監測週」 |
| **Post Kit P1／P2 API** | 非 L0 必測 |

---

## 上架門檻（三日結束須全部有結果）

- [x] E0-B／F + E0-AE-1／2／3（**✅ 2026-07-22／28**）  
- [x] CD-AE-C1（或 C3）至少一條主路 PASS（**C1＋C3 ✅**）  
- [x] E0-MC-A／B + CD-MC2-1 + CD-MC3-1（**✅ 2026-07-28**）  
- [x] PK1～PK4 PASS（**✅ 2026-07-28**；PK5／6 N/A／上線後）  
- [x] CD-4-1 + CD-4-2（Discover 真有卡、讀取 0 LLM）（**✅ 2026-07-28**）  
- [x] CD-4-3／CD-B-2／E0-Discover-i18n（zh-TW↔ja＋en 摘要；**✅ 2026-07-28**）  
- [x] 工作記錄寫明：**條件上架** + 阻塞 ≤3（**✅ 2026-07-28**；見工作記錄頂部「上架判決」）  

---

## 每日收尾模板（貼工作記錄）

```text
日期：2026-07-2x｜目標：Day N
實際完成：（代號 PASS/FAIL）
證據：（截圖檔名／status）
明日第一步：（一句）
```

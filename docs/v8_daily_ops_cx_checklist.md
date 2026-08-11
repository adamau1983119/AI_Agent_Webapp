# v8 正式域 — 日常運作與客戶體驗（CX／OPS）

> **狀態（2026-08-11）**：產品**已正式上架**；監察 Agent＋每日日報（Resend）**已開通**。預設工作＝真實客戶體感＋日常運作煙霧。  
> **觸發**：`專案開始，正式域日常運作，客戶體驗優先 @AGENTS.md`  
> **證據**：`docs/evidence/v8/YYYY-MM-DD/`（截圖或 Network／信箱一句才可勾）  
> **改碼**：僅 **CX／OPS FAIL 阻塞客戶** 才開 `feature/v8-*`＋PR。  
> **OBS／日報 SoT**：[`v8_observability_alerting.md`](./v8_observability_alerting.md) · 備份 [`2026-08-11_topic_dashboard_hkt_pr24_snapshot`](./backups/2026-08-11_topic_dashboard_hkt_pr24_snapshot/SNAPSHOT_README.md) · [`2026-08-11_ops_digest_resend_pass_snapshot`](./backups/2026-08-11_ops_digest_resend_pass_snapshot/SNAPSHOT_README.md)

---

## 代號總表（現行）

| 族 | 代號 | 客戶／營運問題 | 最短驗法 |
|----|------|----------------|----------|
| **CX** | **CX-LOGIN** | 能登入正式域、語系可切 | 登入 → **`/dashboard`**（AE pending 仍進 onboarding） |
| **CX** | **CX-AE** | Alter Ego 主路可用 | extract／skip／regenerate 其一＋截圖 |
| **CX** | **CX-TOPIC** | 主題卡隨介面語系（尤其 **en／ja**） | Dashboard 切 en／ja → 標題摘要對語系 |
| **CX** | **CX-MC** | My Channel 真實 feed | `/my-channel` 有卡或可解鎖 |
| **CX** | **CX-PK** | Post Kit 可仿文／複製 | 詳情 Post Kit copy＋toast |
| **OPS** | **OPS-HEALTH** | API／DB 活著 | `api…/health` → 200、`database: connected` |
| **OPS** | **OPS-CARD** | 當日有自動產卡 | Dashboard **今日主題 N/15**、底部 TopicCard 網格；或 Mongo `generated_at` HKT 當日 |
| **OPS** | **OPS-I18N** | 新卡含三語預寫 | 新 topic 有 `titles_i18n.en`＋`.ja`（需 `ENABLE_TOPIC_TRIPLE_PRELOAD=true`） |
| **OPS** | **OPS-DIGEST** | 正式域每日營運報告進信箱 | Deploy log `Email 發送成功 (resend)` 或信箱自動收到 |
| **OPS** | **OPS-COST** | 成本未失控 | DeepSeek／DeepL 用量或告警一句 |
| **FIX** | **FIX-*** | 上列 FAIL 且阻塞客戶 | 最小 PR；結案對回 CX／OPS |

---

## PR #24 主題卡修復（2026-08-11 · 已 merge `main`）

| 項 | 狀態 | 一句 |
|----|------|------|
| **FIX-TOPIC-HKT** | ✅ **已部署** | Dashboard HKT 今日 filter；`N/15`；Vercel Ready |
| **FIX-TOPIC-UX** | ✅ | 空狀態「準備中」；schedules 失敗不清空卡 |
| **CX-LOGIN** | ✅ **對齊程式** | AE 完成 → `/dashboard`（pending → onboarding） |
| **OPS-I18N 預載** | ⏳ **env** | 需 Railway `ENABLE_TOPIC_TRIPLE_PRELOAD=true` + DeepL key |
| **回歸腳本** | ✅ | `python scripts/check_topic_core_regression.py` |
| **備份** | ✅ | `backup/2026-08-11-topic-dashboard-hkt-pr24` · snapshot README |

--- 

### 本日異常（PR #27 部署檔案路徑）

| 項 | 狀態 | 一句 |
|----|------|------|
| **FIX-TOPIC-I18N-CONFIG** | ❌ 已觀察 | 正式域 `/api/v1/topics` 回 `total>0` 但 `data=[]`；根因 `/shared/topic_languages.json` 不存在（Railway Root = `backend/`）。 |
| 熱修復 | ⏳ 待合併 | 已在 `fix/topic-languages-railway-config` 移到 `backend/config/topic_languages.json` + embedded fallback；待合併 redeploy。 |

**明日 OPS 第一步**：正式域登入 → Dashboard 確認 **OPS-CARD N/15**（不再是空列表）；若 I18N 待開 → 設 triple preload env 後等下一批產卡。

---

| 項 | 狀態 | 一句 |
|----|------|------|
| Watchdog／digest loop | ✅ | `WATCHDOG_START digest=True` |
| 寄信 | ✅ | **Resend HTTPS**（PR #19）；網域 Verified |
| **正式域自動進信箱** | ✅ **PASS** | 08-11 信箱已收；`Email 發送成功 (resend)` |
| From | ✅ | `noreply@ai-alterego.com` |
| checklist | **PD-OBS-TL-07b／09 `[x]`** | 見 observability 檔 |

---

## 每日建議順序（約 45′～90′）

1. **OPS-HEALTH**（正式域）  
2. **OPS-CARD**＋**OPS-I18N**（今日新卡）  
3. 任選 **1～2 個 CX-***（真實帳號）  
4. **OPS-DIGEST**／**OPS-COST**（DIGEST 已 PASS；例行看信箱即可）  
5. 有 FAIL → 記 **FIX-***；無則不改碼  

**OPS-CARD 證據句範例**：`Dashboard 今日 12/15；GET /topics 200；HKT 2026-08-11 generated_at 12 筆`  
**OPS-I18N 證據句範例**：`抽樣 topic_xxx titles_i18n.en+ja 皆有；Dashboard 切 ja 標題為日文`  
**回滾首登 landing**：Vercel 設 `VITE_POST_LOGIN_PATH=/my-channel`（預設不設＝Dashboard）

---

## 當日勾選（複製到工作記錄）

```text
日期：2026-08-11
OPS-HEALTH：PASS（healthy／connected）
OPS-CARD：❌ 目前 Dashboard TopicCard 空列表；已定位為 PR #27 部署路徑問題（`/shared` 不存在）
OPS-I18N：⏳ triple preload env 未開則僅驗 zh-TW；開 env 後驗 en/ja（修復合併後再驗）
CX-LOGIN：⏳ AE 完成 → /dashboard（截圖）
OPS-DIGEST／COST：DIGEST PASS（Resend）；COST：
FAIL／FIX：FIX-TOPIC-HKT 已 merge PR #24；⏳ 密鑰輪換（PD-OBS-TL-08）
明日第一步：Dashboard OPS-CARD 手測（需恢復 TopicCard） + 視需要開 ENABLE_TOPIC_TRIPLE_PRELOAD
```

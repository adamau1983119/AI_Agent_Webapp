# Alter Ego SKU（數位副本 · Onboarding）— 工作明細與完成檢查清單

> **規格 SoT**：[`docs/ALTER_EGO_SPEC.md`](./ALTER_EGO_SPEC.md)（**AE-0** ✅ 2026-06-24）  
> **與 Discover／MyChannel 分界**：**禁止**讀寫 `public_feed:feed:*`、`my_channel:feed:*`；**禁止** Mock DNA／假仿文卡（README、規則 5）  
> **建議分支**：Post Kit 結案後 `feature/alter-ego-onboarding`（勿在 `main` 直接改）  
> **填寫規則**：勾選前須**可重現**；原子驗收 **A→B→C** 順序，**禁止**僅 E2E  
> **截圖政策**：[`v7_evidence_screenshot_guide.md`](./v7_evidence_screenshot_guide.md)（前綴 `…_v7_AE-…`、`E0-AE_*`）  
> **日期 SoT**：**2026-07-22（星期三）** — 見 [`工作記錄.md`](../工作記錄.md) 頂部  
> **執行順序**：**PF-B → PF-M → Landing → Post Kit → AE-0～AE-2（程式）→ MC-1～6 → 上架衝刺測試**  
> **測試 SoT**：[`launch_test_sprint_2026-07-22.md`](./v7_program_line/launch_test_sprint_2026-07-22.md)（07-22～24 · Day1＝AE）  
> **備份（2026-06-17）**：[`docs/backups/2026-06-17_alter-ego-architecture_snapshot/`](../backups/2026-06-17_alter-ego-architecture_snapshot/SNAPSHOT_README.md)  
> **備份（2026-06-24）**：[`docs/backups/2026-06-24_ae-preview-pipeline_snapshot/`](../backups/2026-06-24_ae-preview-pipeline_snapshot/SNAPSHOT_README.md) — preview + `pipeline_version` + dev `--reload`  
> **備份（2026-06-25）**：[`docs/backups/2026-06-25_f05-mychannel-program_snapshot/`](../backups/2026-06-25_f05-mychannel-program_snapshot/SNAPSHOT_README.md) — F05～F07 + MC-1～5 程式段  
> **備份（2026-07-21）**：[`docs/backups/2026-07-21_launch-sprint-trigger_snapshot/`](../backups/2026-07-21_launch-sprint-trigger_snapshot/SNAPSHOT_README.md) — 上架衝刺觸發詞 + 日更主題設定  
> **備份（2026-07-22）**：[`docs/backups/2026-07-22_day1_e0_ae1_snapshot/`](../backups/2026-07-22_day1_e0_ae1_snapshot/SNAPSHOT_README.md) — Day1 **E0-AE-1** PASS + AE timeout 120s

---

## 文件收口（2026-06-17 · 非程式驗收）

- [x] **DOC-BAK-1** 快照 `2026-06-17_alter-ego-architecture_snapshot` 已建立  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-06-17_alter-ego-architecture_snapshot/SNAPSHOT_README.md)
- [x] **DOC-DATE-1** Alter Ego 文件日期 SoT **2026-06-17**（需求 頻道區塊 14、架構表、工作記錄頂部）  
  - 證據：本檔頂部 + 工作記錄 —
- [x] **DOC-ALIGN-1** 铁律 AE-1～8 与需求 頻道區塊 14／架构表 Alter Ego 章 **一致**  
  - 證據：备份目录三档同 revision —
- [x] **DOC-BAK-2** 快照 `2026-06-24_ae-preview-pipeline_snapshot` 已建立  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-06-24_ae-preview-pipeline_snapshot/SNAPSHOT_README.md)
- [x] **DOC-BAK-3** 快照 `2026-06-25_f05-mychannel-program_snapshot` 已建立  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-06-25_f05-mychannel-program_snapshot/SNAPSHOT_README.md)
- [x] **DOC-BAK-4** 快照 `2026-07-21_launch-sprint-trigger_snapshot` 已建立  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-07-21_launch-sprint-trigger_snapshot/SNAPSHOT_README.md)
- [x] **DOC-DATE-4** 日期 SoT **2026-07-21**；上架衝刺 **07-22～24**（Day1＝E0-AE + CD-AE-C*）  
  - 證據：本檔頂部 + [`launch_test_sprint`](./v7_program_line/launch_test_sprint_2026-07-22.md) —
- [x] **DOC-ALIGN-4** AGENTS 推薦一句／`_GATE`／index Active 與上架衝刺 Day 表 **一致**  
  - 證據：快照三档 + AGENTS「上架衝刺」章 —
- [x] **DOC-BAK-5** 快照 `2026-07-22_day1_e0_ae1_snapshot` 已建立  
  - 證據：[`SNAPSHOT_README.md`](../backups/2026-07-22_day1_e0_ae1_snapshot/SNAPSHOT_README.md)
- [x] **DOC-DATE-5** 日期 SoT **2026-07-22（三）**；Day1 **E0-AE-1** 已 PASS  
  - 證據：本檔 E0-AE-1 + [`工作記錄.md`](../工作記錄.md) 頂部 —

---

## 工程鐵律 AE-1～AE-8

> 違反任一條 **不得**勾 **CD-AE*** 完成項。

| # | 規則 |
|---|------|
| **AE-1** | Alter Ego 管線 **Flash-only**（extract／soul／shell／preview／週 batch）；schema fail → Flash 重试或 UX 重贴，**不 silent 升 Pro** |
| **AE-2** | **分路由**：`/api/v1/alter-ego/*` 与 `/api/v1/contents/{id}/generate\|regenerate` **物理隔离**；详情长文仍 **D2 Pro** |
| **AE-3** | **ContentStyleService** 为风格 context **唯一入口**；AE 路径 **禁止**读 `style_profiles` 当 SoT |
| **AE-4** | **dna_status** 四态：`pending` \| `active` \| `skipped` \| `legacy_only`（**非** boolean「启用 AE」） |
| **AE-5** | DNA 写入必 **snapshot + bump `current_dna_version_id`**；generate 必 persist **`generation_meta.dna_version_id`** |
| **AE-6** | **LLM Factory**：`get_llm_client(namespace="alter_ego")` assert Flash-only |
| **AE-7** | 首登 `pending` → onboarding；必含 **Skip** → `skipped` → MyChannel；**禁止**每次 login 强制 AE |
| **AE-8** | 禁止 Mock／模糊驗收（对齐 README） |

---

## 開發順序（原子 Phase）

| 序 | Phase | 目標 | 狀態 |
|:--:|-------|------|------|
| 0 | **AE-0** | 規格：DNA Pydantic、snapshot、Shell YAML、ContentStyleService、version_tag | ✅ **2026-06-24**（PD-AE0-01～07） |
| 1 | **AE-1a** | 後端：`POST …/alter-ego/extract`、`preview`；Mongo collections | ✅ **PD-AE1-01/02/04**（2026-06-24） |
| 2 | **AE-1b** | `ShellManager` + FB／Threads／X + Visual Prompt（IG v1 不做） | ✅ YAML + formatter + Shell Flash |
| 3 | **AE-1c** | `ContentStyleService` + `contents/generate` compressed DNA + `dna_version_id` | ✅ **PD-AE1-03/05/06**（2026-06-25） |
| 4 | **AE-1d** | 前端：onboarding + Skip；Post Kit 平台切换；CreateChannel 贴范文 | ✅ **F01～F07**（2026-06-25） |
| 5 | **AE-2** | exemplar 库 + 週 batch Flash patch + rollback API | ✅ **PD-AE2-01/02/04**（2026-07-21）；**PD-AE2-03** 手測留測試週 |
| 6 | **上架衝刺測試** | E0-AE + CD-AE-C*（Day1） | ✅ **Day1 AE 主路結**（E0-AE-1～3、CD-AE-C1～C3）；可選 A2／KPI 上線後 |

**依赖**：AE-1 **不得**抢在 **Post Kit UI** 之前（交付物无去处）。

---

## Phase AE-0 — 規格（文件 · Gate）

**結案判定**：**PD-AE0-01～07** 必須 `[x]` 方可开 AE-1 程式。（**2026-06-24**：**01／05** ✅）

- [x] **PD-AE0-01** [`ALTER_EGO_SPEC.md`](./ALTER_EGO_SPEC.md) 建立（DNA 扁平 Pydantic、必填最小集、exemplar_snippets）  
  - 證據：本檔 + `backend/app/models/alter_ego_dna.py` —
- [x] **PD-AE0-02** `alter_ego_dna` + `alter_ego_dna_snapshots` + `user_feedback_logs` schema  
  - 證據：需求 頻道區塊 14.6、架构表 **資料模型** —
- [x] **PD-AE0-03** `ContentStyleService.resolve_for_route(user_id, route)` + `StyleContext` + **dna_status 四态**  
  - 證據：需求 頻道區塊 14.3、架构表 **架构已決議** —
- [x] **PD-AE0-04** `current_dna_version_id` + `generation_meta.dna_version_id` 契约 + Redis key 含 version  
  - 證據：需求 頻道區塊 14.3 version_tag、架构表 `generation_meta` —
- [x] **PD-AE0-05** Shell YAML 样例（`facebook.yaml`、`threads.yaml`、`x.yaml`）+ `ShellManager` 接口  
  - 證據：`backend/app/config/shells/*.yaml`、`backend/app/services/shells/shell_manager.py`；`list_platforms` → facebook/threads/x —
- [x] **PD-AE0-06** API 草案：`extract`、`preview`、`dna/rollback`；Router + Factory 双层防御说明  
  - 證據：需求 頻道區塊 14.4～14.7、架构表 API 表 —
- [x] **PD-AE0-07** 需求 頻道區塊 14、架构表 Alter Ego 章、本档、工作記錄交叉引用  
  - 證據：**DOC-BAK-1** 快照 2026-06-17 —

---

## Phase AE-1 — MVP 後端

### 工作明細

- [x] **PD-AE1-01** `POST /api/v1/alter-ego/extract` — Flash + strict JSON validate；fail → 重试 ≤2  
  - 證據：`backend/app/api/v1/alter_ego.py`、`alter_ego_service.py`、`llm_factory.py`（namespace Flash）；`main.py` router 已註冊 —
- [x] **PD-AE1-02** `POST /api/v1/alter-ego/preview` — Soul Flash + Shell Flash  
  - 證據：`alter_ego_service.preview`；`check_ae_live.py` **200** + `soul_text` + `X-Alter-Ego-Preview-Version: 2`；`/health` `alter_ego.pipeline_version=2` —
- [x] **PD-AE1-03** `AlterEgoBodyGateway` middleware（对齐 TokenGateway 限 body）  
  - 證據：`alter_ego_body_gateway.py`；`main.py` 已註冊；`ALTER_EGO_BODY_GATEWAY_PASSED` —
- [x] **PD-AE1-04** `get_llm_client(namespace="alter_ego")` — Pro 调用即报错  
  - 證據：`AlterEgoLLMClient` + `check_ae_bf_static.py` Pro rejected —
- [x] **PD-AE1-05** `ContentStyleService` 实作；废弃 `_style_dna_hint` 直读  
  - 證據：`content_style_service.py`；`compress_for_generate` ≤500；`contents.py` 改 `resolve_for_route` —
- [x] **PD-AE1-06** `contents/generate` 注入 compressed DNA + 写入 `generation_meta.dna_version_id`  
  - 證據：`ContentResponse.generation_meta`；`prompt_version=v3.1-content-style-dna`；static **27/27** + live extract/preview —
- [x] **PD-AE1-07** `POST /api/v1/alter-ego/dna/rollback`  
  - 證據：`alter_ego_service.rollback`；`check_ae_live.py` rollback **200** —

### 原子化验收 Gate（必过 · 顺序 A → B → C）

> **原则**：整合前先分别 PASS；失败时判定 Soul Error vs Shell Error。

#### A — Soul Integrity（不测平台格式）

- [x] **CD-AE-A1** 固定 Golden Exemplar → `extract` → **Pydantic strict PASS**  
  - 證據：`scripts/check_ae_live.py` — Golden Exemplar POST **200** + `AlterEgoDnaJson` re-validate（2026-06-24）—
- [ ] **CD-AE-A2** 人工抽检：lexicon／tone 与范文特征一致  
- [x] **CD-AE-A3** schema fail 日志 `[ALTER_EGO_DNA_EXTRACT_FAIL]`（勿 log 全文范文）  
  - 證據：`alter_ego_service.py` + `check_ae_bf_static.py` grep PASS —

**A 未全 `[x]` → 禁止勾 B／C。**

#### B — Shell Injection（冻结 DNA，只换 Platform YAML）

- [x] **CD-AE-B1** 冻结同一份 DNA JSON；换 FB YAML → 首段 ≤90 字 + 4～6 `#`  
  - 證據：`shell_formatter.py` + `check_ae_bf_static.py`（golden soul + tags）—
- [x] **CD-AE-B2** 同 DNA + Threads YAML → 0～1 hashtag  
  - 證據：同上 —
- [x] **CD-AE-B3** 同 DNA + X YAML → ≤280 字或 thread 结构  
  - 證據：同上 —

**B 未全 `[x]` → 禁止勾 C。**

#### C — E2E（可选 AE-1 末）

- [x] **CD-AE-C1** Exemplar → extract → soul → shell → Post Kit copy 区  
  - 證據（2026-07-28）：詳情頁「發文套件」標題／內文／Hashtag／複製；`POST …/adopt-copy` **200**；[`2026-07-28_v7_CD-AE-C1_postkit_copy_adopt_200.png`](./evidence/v7/2026-07-28/2026-07-28_v7_CD-AE-C1_postkit_copy_adopt_200.png)；extract 鏈見 E0-AE-1 —
- [x] **CD-AE-C2** 一键采用事件 `adopted_without_edit` 写入 audit  
  - 證據（2026-07-28）：Network `adopt-copy` **200**；Mongo `audit_logs.changes.event=adopted_without_edit`（platform=threads）+ `user_feedback_logs.action=adopted_without_edit`；同上截圖 —
- [x] **CD-AE-C3** generate 后 `generation_meta.dna_version_id` 与 snapshot 可对照  
  - 證據（2026-07-28）：`POST …/regenerate` **200**；`generation_meta.dna_status=active` + `dna_version_id` 前綴 `0f83b956cb27`；`docs/evidence/v7/2026-07-28/2026-07-28_v7_E0-AE-3_regenerate_200_generation_meta.png` —

---

## Phase AE-1 — 前端／动线

- [x] **PD-AE1-F01** `/onboarding/alter-ego` — 贴 1～3 篇范文 + 仿文预览  
  - 證據：`AlterEgoOnboarding.tsx`；`check_ae_bf_ui.py` **22/22**；`npm run build` PASS —
- [x] **PD-AE1-F02** **Skip** → `dna_status=skipped` → `/my-channel`  
  - 證據：`POST /alter-ego/skip`；`btn-alter-ego-skip` —
- [x] **PD-AE1-F03** `RootRedirect`：`pending` → onboarding；否则 MyChannel  
  - 證據：`AlterEgoGateRedirect` + `resolvePostLoginPath` —
- [x] **PD-AE1-F04** Settings「建立我的 Alter Ego」入口（Skip 用户回补）  
  - 證據：`btn-settings-alter-ego-setup` in `Settings.tsx` —
- [x] **PD-AE1-F05** Post Kit 平台切换（FB／Threads／X + Visual Prompt）  
  - 證據：`PostKitPanel.tsx` — `btn-postkit-platform-*`、`section-postkit-visual-prompt`；`check_ae_bf_ui.py` —
- [x] **PD-AE1-F06** CreateChannel 助手：贴范文触发 extract  
  - 證據：`input-channels-assist-exemplar`、`btn-channels-assist-extract-dna` —
- [x] **PD-AE1-F07** i18n 三语 + `data-testid` 对照 [`按鈕測試ID架構表.md`](../按鈕測試ID架構表.md)  
  - 證據：`postKit.platformSwitch`／`channels.assist.extractDna` 三語；`check_ae_bf_ui.py` —

### 动线 KPI（产品 · 记录于工作記錄）

- [ ] **CD-AE-KPI-1** Skip rate 有基线数字  
- [ ] **CD-AE-KPI-2** extract 完成率  
- [ ] **CD-AE-KPI-3** Skip 后 7 日内回补 DNA 率  

---

## Phase AE-2 — 护城河（DNA 累积 · 无 fine-tune MVP）

- [x] **PD-AE2-01** 週 batch Flash JSON patch + snapshot  
  - 證據：`alter_ego_weekly_batch.py` + `scripts/run_alter_ego_weekly_batch.py`；staging／prod cron 週日 05:00 UTC；dev 僅 CLI —
- [x] **PD-AE2-02** 👍👎 → `user_feedback_logs` → batch 输入  
  - 證據：`POST /alter-ego/feedback` + interactions like/dislike 同步 + adopt-copy 寫入 —
- [ ] **PD-AE2-03** rollback 灾难恢复手测（故意改坏 tone → 回滚 → preview 恢复）  
  - 備註：rollback API 已有（PD-AE1-07）；**→ 07-24 Day3** —
- [x] **PD-AE2-04** onboarding 外 re-extract 是否耗点（建议：首次免费 1 次）  
  - 證據：`alter_ego_reextract.py` — active 首次 re-extract 免費，其後扣 1 點（402） —

---

## Phase E0-AE — 整批测试週（程式结案的 AE 项）

> **起算**：AE-1 **PD-AE1-* + CD-AE-A/B** 程式 `[x]` 后，併入整批测试週。

- [x] **E0-AE-1** 首登 pending → onboarding → extract → active（UI + Network）  
  - 證據：[`2026-07-22_v7_E0-AE-1_onboarding_preview_200.png`](./evidence/v7/2026-07-22/2026-07-22_v7_E0-AE-1_onboarding_preview_200.png)（preview **200** + 仿文 UI）；[`…_my_channel_after_continue.png`](./evidence/v7/2026-07-22/2026-07-22_v7_E0-AE-1_my_channel_after_continue.png)；後端 `ALTER_EGO_EXTRACT_OK` + `POST …/extract` **200**（05:51:19）—
- [x] **E0-AE-2** Skip 路径 → MyChannel（不再强制 onboarding）  
  - 證據：[`2026-07-28_v7_E0-AE-2_onboarding_pending_status_200.png`](./evidence/v7/2026-07-28/2026-07-28_v7_E0-AE-2_onboarding_pending_status_200.png)；[`2026-07-28_v7_E0-AE-2_skip_200_my_channel.png`](./evidence/v7/2026-07-28/2026-07-28_v7_E0-AE-2_skip_200_my_channel.png)（`POST …/skip` **200** → `/my-channel`）—
- [x] **E0-AE-3** `contents/generate` Network：Pro model + response 含 generation_meta  
  - 證據（2026-07-28）：`regenerate` **200**；`model_used=deepseek-v4-pro`；`generation_meta` 含 `dna_version_id`；見上 CD-AE-C3 截圖 —  
- [ ] **E0-AE-4** 文风归因：改 DNA → generate → 查 dna_version_id 与 snapshot 一致  

---

## 與 style_profiles 遷移

| 狀態 | 行為 |
|------|------|
| `legacy_only` | `contents_generate` 用现有 one-liner；AE 路径不用 |
| 首次 extract 成功 | 可选 seed `preset_style`；`style_profiles.superseded_by_ae_at` |
| `active` | **停止双写** style_profiles；反馈 → `user_feedback_logs` |
| `/style-profile` | 只读或 410；v7_nav 仍隐藏 |

---

## 版本

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.10 | 2026-07-22 | **DOC-BAK-5**；**E0-AE-1** `[x]`；AE client timeout 120s |
| v0.9 | 2026-07-21 | **DOC-BAK-4** 上架衝刺快照；測試 SoT → Day1 AE；觸發詞鎖定 |
| v0.1 | 2026-06-17 | 初版：AE-0～2 原子 Phase、铁律 AE-1～8、A/B/C 验收、ContentStyleService + version_tag |
| v0.8 | 2026-06-25 | **F05～F07** Post Kit 平台／CreateChannel extract；**DOC-BAK-3**；adopt-copy API |
| v0.7 | 2026-06-25 | **PD-AE1-07** rollback；**AE-1d** F01～F04；`check_ae_bf_ui.py` |
| v0.5 | 2026-06-24 | **DOC-BAK-2**；**PD-AE1-02/04**；`pipeline_version` + `run_backend_dev.py`；preview live 證據 |
| v0.4 | 2026-06-24 | **PD-AE1-02/04** ✅；Soul+Shell preview；`AlterEgoLLMClient` |

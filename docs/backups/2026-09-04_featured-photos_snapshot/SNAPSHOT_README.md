# Snapshot — 2026-09-04 精選照片最多 4 張 2×2（PR #62）

## 1. 摘要

本快照封存 **PR #62 已合 `main`**（merge `1aaf098`，程式 `d3b5b1e`）之精選照片：

1. **上限 4**：畫廊 2×2 只顯示前 4 張；搜尋／新增滿 4 不塞第 5 張。
2. **匹配事實錨**：不再要求 `content.article`；優先 `summary_flash` → 原文 → 標題（`match_facts.py`）。
3. **產卡不變**：`preview_images: 1`、`generate_content=false`、每日 15 張公眾卡。
4. **i18n**：只加 `images.featured`／`featuredFull`，不刪鍵；合入後三語 **1139**。
5. **未改**：翻譯核心（`title_matches_display_language`／`usable_cached_title`／`_pack_ok`）。

金流 **PR #59** 已在 `main`，與本快照無關。

## 2. Git／PR

| 項 | 值 |
|:---|:---|
| 程式基線 | `main` `1aaf098`（PR #62） |
| 改碼前備份 | `backup/2026-09-04-pre-featured-photos` |
| WIP 凍結（勿當 PR 來源） | `backup/2026-09-04-featured-photos-wip`＝`d3b5b1e` |
| 合入後備份 | `backup/2026-09-04-featured-photos-merged` |
| PR | [#62](https://github.com/adamau1983119/AI_Agent_Webapp/pull/62) |
| 誤開 | PR #60 從備份分支開 — **關閉、勿合** |

## 3. 正式域

Vercel／Railway 於合入後部署。畫廊 2×2、空庫匹配、滿 4 張 **待使用者手測**；本快照不代勾 PASS。

## 4. 備份檔案清單

| 檔案 | 說明 |
|:---|:---|
| `match_facts.py` | 事實錨（summary_flash → 原文 → 標題） |
| `images.py` | `POST .../match?min_count=4` |
| `test_match_facts.py` | 匹配單元測試 |
| `featuredPhotos.ts` | 前端上限 4 |
| `ImageGallery.tsx` | 2×2 畫廊 |
| `ImageSearch.tsx` | 搜尋滿 4 不塞第 5 張 |

## 5. 回滾

- 精選照片：revert PR #62（`1aaf098`）或切回 `backup/2026-09-04-pre-featured-photos`。
- 金流不受影響（PR #59 仍在 `main`）。

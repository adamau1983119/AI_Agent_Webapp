# 按鈕測試 ID 架構表 (Button Test ID Architecture)

> **版本**: v1.0.0  
> **更新日期**: 2026-02-05  
> **專案**: Influencers AI Agents  
> **用途**: 自動化測試（React Testing Library / Cypress / Playwright）

---

## 📋 目錄

1. [命名規範](#命名規範)
2. [導航類 (Navigation)](#1-導航類-navigation)
3. [認證類 (Authentication)](#2-認證類-authentication)
4. [表單類 (Forms)](#3-表單類-forms)
5. [操作類 (Actions)](#4-操作類-actions)
6. [輔助類 (Utility)](#5-輔助類-utility)
7. [測試範例](#測試範例)

---

## 命名規範

### 格式

```
data-testid="{類型}-{位置}-{功能}"
```

### 類型前綴

| 前綴 | 類型 | 說明 |
|------|------|------|
| `btn-` | 按鈕 | 可點擊的按鈕元素 |
| `link-` | 連結 | 導航連結 (Link/a) |
| `input-` | 輸入框 | 文字輸入、密碼框等 |
| `form-` | 表單 | 表單容器 |
| `modal-` | 彈窗 | 模態框 |
| `card-` | 卡片 | 卡片元素 |
| `menu-` | 選單 | 下拉選單 |
| `icon-` | 圖示按鈕 | 僅圖示的按鈕 |

### 位置代碼

| 代碼 | 位置 |
|------|------|
| `sidebar` | 側邊欄 |
| `header` | 頁首 |
| `login` | 登入頁 |
| `register` | 註冊頁 |
| `forgot` | 忘記密碼頁 |
| `lang` | 語言選擇頁 |
| `dashboard` | 控制面板 |
| `topics` | 主題列表 |
| `discover` | 探索（公共主題牆） |
| `topic` | 主題詳情 |
| `channels` | 頻道管理 |
| `inspiration` | 靈感策劃 |
| `settings` | 設定頁 |

---

## 1. 導航類 (Navigation)

### 1.1 Sidebar 導航

| Test ID | 元素 | 功能 | 目標路由 |
|---------|------|------|----------|
| `link-sidebar-logo` | Logo | 返回首頁 | `/dashboard` |
| `link-sidebar-dashboard` | 選單項 | 控制面板 | `/dashboard` |
| `link-sidebar-topics` | 選單項 | 主題列表 | `/topics` |
| `link-sidebar-discover` | 選單項 | 探索（公共主題牆） | `/discover` |
| `link-sidebar-channels` | 選單項 | 我的頻道 | `/channels` |
| `link-sidebar-inspiration` | 選單項 | 靈感策劃 | `/inspiration` |
| `link-sidebar-style` | 選單項 | 風格檔案 | `/style-profile` |
| `link-sidebar-publish` | 選單項 | 一鍵發布 | `/publish` |
| `link-sidebar-social` | 選單項 | 社群連結 | `/social-connect` |
| `link-sidebar-preferences` | 選單項 | 偏好設定 | `/preferences` |
| `link-sidebar-schedule` | 選單項 | 排程管理 | `/schedule` |
| `btn-sidebar-logout` | 按鈕 | 登出 | `/login` |

### 1.2 Header 導航

| Test ID | 元素 | 功能 | 目標路由/動作 |
|---------|------|------|---------------|
| `btn-header-menu` | 按鈕 | 漢堡選單 | 開啟 Sidebar |
| `btn-header-notification` | 按鈕 | 通知 | 開啟通知 |
| `btn-header-lang` | 按鈕 | 語言選擇 | 開啟語言選單 |
| `menu-header-lang` | 選單 | 語言下拉 | - |
| `btn-header-lang-zh` | 選項 | 繁體中文 | 切換語言 |
| `btn-header-lang-en` | 選項 | English | 切換語言 |
| `btn-header-lang-ja` | 選項 | 日本語 | 切換語言 |
| `btn-header-user` | 按鈕 | 用戶選單 | 開啟用戶選單 |
| `menu-header-user` | 選單 | 用戶下拉 | - |
| `link-header-settings` | 連結 | 設定 | `/settings` |
| `btn-header-logout` | 按鈕 | 登出 | `/login` |
| `link-header-login` | 連結 | 登入 | `/login` |
| `link-header-register` | 連結 | 註冊 | `/register` |

### 1.3 Dashboard 快速操作

| Test ID | 元素 | 功能 | 目標路由 |
|---------|------|------|----------|
| `link-dashboard-topics` | 連結 | 瀏覽主題 | `/topics` |
| `link-dashboard-channels` | 連結 | 我的頻道 | `/channels` |
| `link-dashboard-inspiration` | 連結 | 靈感策劃 | `/inspiration` |
| `link-dashboard-style` | 連結 | 風格檔案 | `/style-profile` |

### 1.4 Discover 公共主題牆（v7 PF-4）

| Test ID | 元素 | 功能 |
|---------|------|------|
| `page-discover` | 頁面容器 | `/discover` 根節點 |
| `discover-page-title` | 標題 | 頁面主標 |
| `discover-page-subtitle` | 副標 | 說明文字 |
| `discover-feed-skeleton` | 骨架 | 載入中占位 |
| `discover-feed-grid` | 網格 | 卡片列表容器 |
| `card-discover-feed-{n}` | 卡片 | 第 n 張公共主題卡（0-based） |
| `card-discover-feed-{n}-title` | 文字 | 卡片標題 |
| `card-discover-feed-{n}-description` | 文字 | 卡片摘要 |
| `card-discover-feed-{n}-category` | 標籤 | 分類徽章 |
| `card-discover-feed-{n}-source` | 文字 | 來源名稱 |

---

## 2. 認證類 (Authentication)

### 2.1 語言選擇頁

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-lang-zh` | 按鈕 | 選擇繁體中文 |
| `btn-lang-en` | 按鈕 | 選擇 English |
| `btn-lang-ja` | 按鈕 | 選擇日本語 |
| `btn-lang-reset` | 按鈕 | 重置語言 |

### 2.2 登入頁

| Test ID | 元素 | 功能 |
|---------|------|------|
| `form-login` | 表單 | 登入表單 |
| `input-login-email` | 輸入框 | Email 輸入 |
| `input-login-password` | 輸入框 | 密碼輸入 |
| `btn-login-toggle-password` | 按鈕 | 顯示/隱藏密碼 |
| `btn-login-submit` | 按鈕 | 登入提交 |
| `btn-login-google` | 按鈕 | Google 登入 |
| `btn-login-guest` | 按鈕 | 訪客瀏覽 |
| `link-login-forgot` | 連結 | 忘記密碼 |
| `link-login-register` | 連結 | 前往註冊 |
| `btn-login-back` | 按鈕 | 返回 |
| `btn-login-lang` | 按鈕 | 切換語言 |

### 2.3 註冊頁

| Test ID | 元素 | 功能 |
|---------|------|------|
| `form-register` | 表單 | 註冊表單 |
| `input-register-name` | 輸入框 | 姓名輸入 |
| `input-register-email` | 輸入框 | Email 輸入 |
| `input-register-password` | 輸入框 | 密碼輸入 |
| `input-register-confirm` | 輸入框 | 確認密碼 |
| `select-register-lang` | 選擇器 | 語言偏好 |
| `checkbox-register-terms` | 核取方塊 | 同意條款 |
| `btn-register-submit` | 按鈕 | 註冊提交 |
| `btn-register-google` | 按鈕 | Google 註冊 |
| `link-register-login` | 連結 | 前往登入 |
| `btn-register-back` | 按鈕 | 返回 |
| `btn-register-lang` | 按鈕 | 切換語言 |

### 2.4 忘記密碼頁

| Test ID | 元素 | 功能 |
|---------|------|------|
| `form-forgot` | 表單 | 忘記密碼表單 |
| `input-forgot-email` | 輸入框 | Email 輸入 |
| `btn-forgot-submit` | 按鈕 | 提交 |
| `btn-forgot-back` | 按鈕 | 返回登入 |
| `link-forgot-login` | 連結 | 返回登入連結 |
| `btn-forgot-lang` | 按鈕 | 切換語言 |

---

## 3. 表單類 (Forms)

### 3.1 搜尋表單

| Test ID | 元素 | 功能 |
|---------|------|------|
| `form-header-search` | 表單 | Header 搜尋 |
| `input-header-search` | 輸入框 | 搜尋輸入 |
| `btn-header-search-clear` | 按鈕 | 清除搜尋 |

### 3.2 主題編輯

| Test ID | 元素 | 功能 |
|---------|------|------|
| `form-topic-edit` | 表單 | 主題編輯表單 |
| `input-topic-title` | 輸入框 | 標題輸入 |
| `input-topic-summary` | 輸入框 | 摘要輸入 |
| `btn-topic-save` | 按鈕 | 儲存 |
| `btn-topic-cancel` | 按鈕 | 取消 |

---

## 4. 操作類 (Actions)

### 4.1 Dashboard 操作

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-dashboard-generate` | 按鈕 | 生成今日主題 |
| `btn-dashboard-delete` | 按鈕 | 刪除今日主題 |
| `btn-dashboard-retry` | 按鈕 | 重試載入 |

### 4.2 主題操作

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-topic-edit` | 按鈕 | 編輯主題 |
| `btn-topic-confirm` | 按鈕 | 確認主題 |
| `btn-topic-delete` | 按鈕 | 刪除主題 |
| `btn-topic-generate` | 按鈕 | 生成內容 |
| `btn-topic-regenerate` | 按鈕 | 重新生成 |
| `btn-topic-back` | 按鈕 | 返回列表 |

### 4.3 圖片操作

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-image-add` | 按鈕 | 新增圖片 |
| `btn-image-match` | 按鈕 | 智能匹配 |
| `btn-image-search` | 按鈕 | 搜尋圖片 |
| `btn-image-delete` | 按鈕 | 刪除圖片 |
| `btn-image-reorder` | 按鈕 | 排序圖片 |

### 4.4 互動按鈕

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-interact-like` | 按鈕 | 喜歡 |
| `btn-interact-dislike` | 按鈕 | 不喜歡 |
| `btn-interact-share` | 按鈕 | 分享 |
| `btn-interact-copy` | 按鈕 | 複製 |

### 4.5 頻道 AI 助手與建立精靈表單 (`CreateChannel.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-channels-create-back` | 按鈕 | 返回頻道列表 |
| `link-channels-phasec-skip-to-form` | 連結 | 鍵盤／無障礙：跳至主表單區 `#channel-create-form` |
| `panel-channels-create-form` | 區塊 | 三步驟表單白卡（`id="channel-create-form"` 為外層錨點，可含收合提示） |
| `panel-channels-form-collapsed-hint` | 區塊 | 大螢幕＋助手開啟：表單收合時之虛線提示區 |
| `btn-channels-expand-wizard-form` | 按鈕 | 展開完整三步表單 |
| `btn-channels-collapse-wizard-form` | 按鈕 | 收合完整三步表單（僅大螢幕顯示） |
| `btn-channels-step1-category-{category}` | 按鈕 | Step1 選類別（`fashion`／`food` 等） |
| `btn-channels-step1-next` | 按鈕 | Step1 → Step2 |
| `btn-channels-step2-region-{region}` | 按鈕 | Step2 選地區（與 `ChannelRegion` 值一致） |
| `input-channels-step2-keyword` | 輸入 | 類別為 `other` 時自訂關鍵字 |
| `btn-channels-step2-keyword-add` | 按鈕 | 新增關鍵字 |
| `btn-channels-step2-keyword-remove-{index}` | 按鈕 | 移除第 index 個關鍵字 |
| `btn-channels-step2-prev` | 按鈕 | Step2 → Step1 |
| `btn-channels-step2-next` | 按鈕 | Step2 → Step3 |
| `input-channels-step3-name` | 輸入 | Step3 頻道名稱 |
| `input-channels-step3-description` | 輸入 | Step3 頻道描述 |
| `panel-channels-step3-preview` | 區塊 | Step3 預覽卡 |
| `btn-channels-step3-prev` | 按鈕 | Step3 → Step2 |
| `btn-channels-step3-submit` | 按鈕 | 建立頻道（主 CTA） |
| `btn-channels-assist` | 按鈕 | 助手收合時：展開 AI 助手（`/channels/create` 進頁預設開啟時較少出現） |
| `btn-channels-assist-minimize` | 按鈕 | 助手展開時：收起助手（不清空狀態；與關閉 ✕ 不同） |
| `btn-channels-assist-close` | 按鈕 | 關閉助手對話框 |
| `panel-channels-create-summary` | 區塊 | 建立前摘要（名稱／描述／類別／地區／RSS 數；Phase B，助手開啟時顯示） |
| `panel-channels-assist-request-error` | 區塊 | Phase C：`/channels/assist` 失敗時助手內提示 |
| `btn-channels-assist-error-dismiss` | 按鈕 | 關閉助手內分析錯誤橫幅 |
| `panel-channels-guided-load-error` | 區塊 | 精靈選項載入失敗 |
| `btn-channels-guided-retry` | 按鈕 | 重新載入精靈選項 |
| `text-channels-phasec-step-hint` | 文字 | Phase C：步驟圓圈與精靈敘事對齊說明（助手開啟時） |
| `panel-channels-assist-feed-action-error` | 區塊 | Phase C：表單區 RSS 池／白名單／validate／建立失敗時，助手內同步橫幅（助手開啟時） |
| `btn-channels-assist-feed-error-dismiss` | 按鈕 | 關閉上述表單區錯誤橫幅 |
| `link-channels-assist-go-to-form` | 連結 | 從助手錯誤橫幅捲動並聚焦至主表單區 `#channel-create-form` |
| `btn-channels-mobile-summary-drawer` | 按鈕 | 小螢幕：開啟「步驟與摘要」底抽屜 |
| `btn-channels-mobile-drawer-backdrop` | 按鈕 | 抽屜遮罩（關閉） |
| `btn-channels-mobile-drawer-close` | 按鈕 | 抽屜標題列關閉 |
| `text-channels-mobile-drawer-step-hint` | 文字 | 抽屜內步驟說明（與 `text-channels-phasec-step-hint` 同文案） |
| `btn-channels-mobile-drawer-go-form` | 按鈕 | 抽屜內「前往表單」 |
| `input-channels-assist` | 輸入框 | AI 助手輸入 |
| `btn-channels-assist-submit` | 按鈕 | 提交助手輸入 |
| `btn-channels-assist-confirm` | 按鈕 | 確認應用結果 |
| `btn-channels-assist-modify` | 按鈕 | 修改輸入 |
| `btn-channels-assist-preset-{key}` | 按鈕 | 預設組合按鈕（japanFashion/hkFood/globalTrend等） |
| `btn-channels-assist-quick-category-{category}` | 按鈕 | 快捷選擇類別（finance/sports/tech/entertainment/other） |
| `btn-channels-assist-quick-region-{region}` | 按鈕 | 快捷選擇地區（全部 8 個地區） |
| `btn-channels-step2-pool-add-{index}` | 按鈕 | Step 2 候選池「加入」已選（index 為候選列表序號） |
| `btn-channels-step2-selected-remove-{index}` | 按鈕 | Step 2 已選來源「移除」（index 為已選列表序號） |
| `source-preview-{index}` | 卡片 | 來源預覽卡片（含 favicon/網域/類型標籤） |
| `source-link-{index}` | 連結 | 訪問來源按鈕 |

### 4.6 頻道詳情頁 (`ChannelDetail.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-channel-detail-back` | 按鈕 | 返回頻道列表 |
| `btn-channel-detail-collect` | 按鈕 | 手動觸發收集 |
| `btn-channel-detail-edit` | 連結 | 跳轉到頻道設定頁 |

### 4.7 頻道設定頁 (`ChannelEdit.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-channel-edit-back` | 按鈕 | 返回頻道詳情 |
| `input-channel-edit-name` | 輸入框 | 頻道名稱 |
| `input-channel-edit-description` | 輸入框 | 頻道描述 |
| `input-channel-edit-keyword` | 輸入框 | 關鍵字輸入 |
| `btn-channel-edit-add-keyword` | 按鈕 | 添加關鍵字 |
| `btn-channel-edit-remove-keyword-{index}` | 按鈕 | 移除關鍵字 |
| `radio-channel-edit-status-active` | 單選 | 狀態：啟用 |
| `radio-channel-edit-status-paused` | 單選 | 狀態：暫停 |
| `btn-channel-edit-submit` | 按鈕 | 儲存變更 |
| `btn-channel-edit-delete` | 按鈕 | 刪除頻道 |
| `btn-channel-edit-delete-cancel` | 按鈕 | 取消刪除 |
| `btn-channel-edit-delete-confirm` | 按鈕 | 確認刪除 |

### 4.8 主題列表頁 (`Topics.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-topics-view-infinite` | 按鈕 | 切換到無限滾動模式 |
| `btn-topics-view-pagination` | 按鈕 | 切換到分頁模式 |
| `topic-card-{topicId}` | 卡片 | 主題卡片（可點擊） |

### 4.9 主題詳情頁 (`TopicDetail.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-topic-detail-back` | 按鈕 | 返回主題列表 |
| `btn-topic-detail-edit` | 按鈕 | 編輯主題 |
| `btn-topic-detail-confirm` | 按鈕 | 確認主題 |
| `btn-topic-detail-delete` | 按鈕 | 刪除主題 |
| `btn-topic-detail-generate` | 按鈕 | 生成內容 |
| `btn-topic-detail-regenerate` | 按鈕 | 重新生成內容 |
| `btn-topic-detail-add-image` | 按鈕 | 新增圖片 |
| `btn-topic-detail-match-photos` | 按鈕 | 智能匹配照片 |
| `btn-topic-detail-search-images` | 按鈕 | 搜尋圖片 |
| `btn-topic-card-translate` | 按鈕 | 主題卡：譯為目前語言（v7 Phase 4 改為語系切換自動 standard；保留 testid 供手動重試元件） |
| `btn-topic-card-kol-style` | 按鈕 | 主題卡：網紅風格（kol_style Flash 按需） |
| `btn-topic-card-show-collected` | 按鈕 | 主題卡：顯示收集時標題 |
| `btn-topic-detail-translate-display` | 按鈕 | 詳情：譯為目前語言（標題／摘要） |
| `btn-topic-detail-kol-style` | 按鈕 | 詳情：網紅風格（kol_style Flash 按需） |
| `btn-topic-detail-show-collected` | 按鈕 | 詳情：顯示收集時標題 |

### 4.10 內容生成面板 (`ContentGenerationPanel.tsx`)

| Test ID | 元素 | 功能 |
|---------|------|------|
| `content-generation-panel` | 容器 | 內容生成設定面板 |
| `btn-content-gen-toggle` | 按鈕 | 展開/收合設定面板 |
| `btn-content-style-{style}` | 按鈕 | 風格選擇（professional/casual/humorous/storytelling/educational） |
| `btn-content-format-{format}` | 按鈕 | 輸出格式選擇（article/script/both） |
| `btn-content-article-length-{length}` | 按鈕 | 文章長度選擇（300/500/800/1200） |
| `btn-content-script-duration-{duration}` | 按鈕 | 腳本時長選擇（15/30/60/90） |
| `btn-content-gen-start` | 按鈕 | 開始生成/重新生成 |

---

## 5. 輔助類 (Utility)

### 5.1 彈窗

| Test ID | 元素 | 功能 |
|---------|------|------|
| `modal-delete-confirm` | 彈窗 | 刪除確認 |
| `btn-modal-confirm` | 按鈕 | 確認 |
| `btn-modal-cancel` | 按鈕 | 取消 |
| `modal-login-prompt` | 彈窗 | 登入提示 |
| `btn-prompt-login` | 按鈕 | 前往登入 |
| `btn-prompt-register` | 按鈕 | 前往註冊 |
| `btn-prompt-cancel` | 按鈕 | 取消 |

### 5.2 分頁

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-page-prev` | 按鈕 | 上一頁 |
| `btn-page-next` | 按鈕 | 下一頁 |
| `btn-page-number` | 按鈕 | 頁碼 |

### 5.3 篩選

| Test ID | 元素 | 功能 |
|---------|------|------|
| `btn-filter-reset` | 按鈕 | 重置篩選 |
| `select-filter-category` | 選擇器 | 分類篩選 |
| `select-filter-status` | 選擇器 | 狀態篩選 |

---

## 測試範例

### React Testing Library

```typescript
import { render, screen, fireEvent } from '@testing-library/react';

// 測試登入表單
test('should submit login form', async () => {
  render(<Login />);
  
  const emailInput = screen.getByTestId('input-login-email');
  const passwordInput = screen.getByTestId('input-login-password');
  const submitButton = screen.getByTestId('btn-login-submit');
  
  fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
  fireEvent.change(passwordInput, { target: { value: 'password123' } });
  fireEvent.click(submitButton);
  
  // 驗證結果...
});
```

### Cypress

```typescript
// 測試導航
describe('Navigation', () => {
  it('should navigate to topics page', () => {
    cy.visit('/dashboard');
    cy.get('[data-testid="link-sidebar-topics"]').click();
    cy.url().should('include', '/topics');
  });
  
  it('should open language menu', () => {
    cy.get('[data-testid="btn-header-lang"]').click();
    cy.get('[data-testid="menu-header-lang"]').should('be.visible');
    cy.get('[data-testid="btn-header-lang-en"]').click();
  });
});
```

### Playwright

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('/login');
  
  await page.getByTestId('input-login-email').fill('test@example.com');
  await page.getByTestId('input-login-password').fill('password123');
  await page.getByTestId('btn-login-submit').click();
  
  await expect(page).toHaveURL('/topics');
});
```

---

## 維護指南

### 新增按鈕時

1. 確定類型前綴（btn-/link-/input-等）
2. 確定位置代碼
3. 添加功能描述
4. 在此文件新增記錄
5. 在代碼中添加 `data-testid`

### 命名原則

- 使用小寫英文
- 使用連字符分隔
- 保持簡潔明確
- 避免重複 ID

---

## 版本歷史

| 版本 | 日期 | 變更說明 |
|------|------|----------|
| v1.0.0 | 2026-02-05 | 初始版本 - 完整按鈕測試 ID 定義 |
| v1.1.0 | 2026-02-07 | 新增: AI助手預設組合按鈕、來源卡片增強、內容生成面板(風格/格式/長度/時長) |

---

> **注意**: 此文件應與程式碼保持同步。每次新增或修改按鈕時，請同步更新此架構表。


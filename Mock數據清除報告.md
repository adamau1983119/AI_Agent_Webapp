# Mock 數據清除報告

## 問題發現

用戶報告 Dashboard 顯示了 mock 數據，即使已經清除了所有 mock 數據。經過檢查，發現以下問題：

### 1. 硬編碼的 Mock 數據

#### Dashboard.tsx
- **「內容評分」卡片**：硬編碼為 `85/100`（第 128-133 行）
- **已修復**：改為從實際 topics 數據計算平均字數

#### UpcomingEvents.tsx
- **硬編碼的事件列表**：包含兩個假事件
- **已修復**：移除 mock 數據，顯示空狀態

#### RecentActivities.tsx
- **硬編碼的活動列表**：包含三個假活動
- **已修復**：移除 mock 數據，顯示空狀態

### 2. React Query 緩存問題

當 API 返回 502 Bad Gateway 錯誤時，React Query 仍在使用舊的緩存數據，導致：
- 前端顯示舊數據（85% 內容完成度、100% 圖片完成度）
- 用戶誤以為是 mock 數據

**已修復**：
- 添加 `staleTime: 0` 和 `gcTime: 0`，確保不使用過期緩存
- 當有錯誤時，強制使用空數組，不顯示緩存數據

## 修復內容

### 1. Dashboard.tsx

```typescript
// 修復前：硬編碼
<ProgressCard
  title="內容評分"
  value="85/100"
  percentage={85}
/>

// 修復後：從實際數據計算
<ProgressCard
  title="內容評分"
  value={topics.length > 0 ? `${Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)}/100` : "0/100"}
  percentage={topics.length > 0 ? Math.min(100, Math.round(topics.reduce((sum, t) => sum + (t.wordCount || 0), 0) / topics.length)) : 0}
/>
```

```typescript
// 修復前：可能使用緩存數據
const topics = topicsResponse?.data || []

// 修復後：有錯誤時不使用緩存
const topics = (topicsError || schedulesError) ? [] : (topicsResponse?.data || [])
```

```typescript
// 添加緩存控制
useQuery({
  queryKey: ['topics'],
  queryFn: () => topicsAPI.getTopics(),
  staleTime: 0, // 不使用過期緩存
  gcTime: 0, // 立即清除緩存
})
```

### 2. UpcomingEvents.tsx

```typescript
// 修復前：硬編碼事件
const events = [
  { title: 'Webinar: AI 內容生成', date: '08.06.2024', time: '18:00-20:00' },
  { title: 'Conference: 社群媒體趨勢', date: '17.06.2024', time: '10:00-16:00' },
]

// 修復後：空數組，等待真實 API
const events: Array<{ title: string; date: string; time: string }> = []
```

### 3. RecentActivities.tsx

```typescript
// 修復前：硬編碼活動
const activities = [
  { icon: 'document', title: '新主題已生成', time: '2 小時前', color: 'purple' },
  // ...
]

// 修復後：空數組，等待真實 API
const activities: Array<{ icon: string; title: string; time: string; color: string }> = []
```

## 根本原因分析

### 為什麼會顯示「mock 數據」？

1. **硬編碼數據**：Dashboard 中有硬編碼的「內容評分」85/100
2. **React Query 緩存**：當 API 失敗（502）時，React Query 使用舊的緩存數據
3. **舊數據殘留**：如果之前成功獲取過數據，緩存中可能還有舊的主題數據

### 502 Bad Gateway 錯誤

從 Network 標籤可以看到：
- `topics?page=1&limit...` → 502 Bad Gateway
- `schedules` → 502 Bad Gateway

這表示：
1. **後端服務未運行**：Railway 上的後端服務可能已停止
2. **環境變數未設定**：後端啟動時環境變數驗證失敗，服務未啟動
3. **網路問題**：前端無法連接到後端

## 解決方案

### 立即修復（已完成）

1. ✅ 移除所有硬編碼的 mock 數據
2. ✅ 添加 React Query 緩存控制
3. ✅ 當 API 失敗時，不顯示緩存數據

### 後續步驟

1. **檢查後端服務狀態**
   ```bash
   # 檢查 Railway 上的後端服務是否運行
   railway status
   ```

2. **檢查環境變數**
   ```bash
   # 確認所有必需的環境變數已設定
   railway variables
   ```

3. **檢查日誌**
   ```bash
   # 查看後端日誌，確認啟動時環境驗證是否通過
   railway logs
   ```

4. **測試健康檢查端點**
   ```bash
   curl https://gentle-enchantment-production-1865.up.railway.app/api/v1/health/detailed
   ```

## 驗證步驟

1. **清除瀏覽器緩存**
   - 打開開發者工具
   - Application → Clear storage → Clear site data

2. **檢查 Network 標籤**
   - 確認 API 請求是否成功
   - 如果仍有 502 錯誤，檢查後端服務

3. **檢查 Console**
   - 確認沒有錯誤訊息
   - 確認數據來源正確

## 總結

**問題根源**：
- 硬編碼的 mock 數據（已清除）
- React Query 緩存機制（已修復）
- 後端服務 502 錯誤（需要檢查 Railway）

**修復狀態**：
- ✅ 所有硬編碼 mock 數據已清除
- ✅ React Query 緩存控制已添加
- ⚠️ 後端服務 502 錯誤需要檢查 Railway 配置


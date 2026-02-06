# i18n 合規性檢查摘要報告

> **檢查日期**: 2026-02-06  
> **檢查工具**: `check_i18n_compliance.py`

---

## 📊 總體統計

- **檢查文件數**: 216
- **發現問題數**: 2650
- **有問題的文件數**: 131

---

## ⚠️ 重要說明

檢查腳本發現的 2650 個問題中，**大部分是開發者可見的文字**，不需要 i18n：

### ✅ 不需要 i18n 的文字（約 80%）

1. **API 文檔描述** (`description=`)
   - 用於 Swagger/OpenAPI 文檔
   - 僅開發者可見
   - 範例：`description="分類篩選"`

2. **日誌訊息** (`logger.info/error/warning`)
   - 用於系統日誌
   - 僅開發者可見
   - 範例：`logger.info("用戶註冊成功")`

3. **模型字段描述** (`Field(description=)`)
   - 用於 API 文檔
   - 僅開發者可見
   - 範例：`Field(..., description="頻道名稱")`

4. **文檔字符串** (`"""..."""`)
   - 用於代碼文檔
   - 僅開發者可見

### 🔴 需要 i18n 的文字（約 20%）

1. **API 錯誤訊息** (`HTTPException(detail=)`)
   - 返回給用戶的錯誤訊息
   - **必須使用 i18n**
   - 範例：`detail="Email 或密碼錯誤"`

2. **前端硬編碼文字**
   - 所有用戶可見的 UI 文字
   - **必須使用 i18n**
   - 範例：`'時尚'`, `'美食'`, `'趨勢'`

3. **API 響應訊息** (`message=`)
   - 返回給用戶的成功/錯誤訊息
   - **必須使用 i18n**
   - 範例：`message="Email 驗證成功"`

---

## 🔍 需要修復的關鍵問題

### 1. 後端 API 錯誤訊息（高優先級）

**位置**: `backend/app/api/v1/*.py`

**問題**: 直接返回硬編碼的中文錯誤訊息

**範例**:
```python
# ❌ 錯誤
raise HTTPException(
    status_code=400,
    detail="Email 或密碼錯誤"
)

# ✅ 正確
raise HTTPException(
    status_code=400,
    detail=self._get_error_message("auth.invalid_credentials", language)
)
```

**需要修復的文件**:
- `backend/app/api/v1/auth.py` - 13 個問題
- `backend/app/api/v1/channels.py` - 需要檢查
- `backend/app/api/v1/generate.py` - 需要檢查
- 其他 API 文件

### 2. 前端硬編碼文字（高優先級）

**位置**: `frontend/src/**/*.ts`, `frontend/src/**/*.tsx`

**問題**: 直接使用硬編碼的中文/日文文字

**範例**:
```typescript
// ❌ 錯誤
const categories = {
  fashion: '時尚',
  food: '美食',
  trend: '趨勢'
}

// ✅ 正確
const categories = {
  fashion: t('channels.category.fashion'),
  food: t('channels.category.food'),
  trend: t('channels.category.trend')
}
```

**需要修復的文件**:
- `frontend/src/api/channels.ts` - 16 個問題
- `frontend/src/api/errors.ts` - 11 個問題
- `frontend/src/api/ratings.ts` - 14 個問題
- `frontend/src/api/styleProfile.ts` - 11 個問題
- 其他前端文件

### 3. 後端服務錯誤訊息（中優先級）

**位置**: `backend/app/services/**/*.py`

**問題**: 返回給用戶的錯誤訊息使用硬編碼

**範例**:
```python
# ❌ 錯誤
return None, "更新風格失敗"

# ✅ 正確
return None, self._get_error_message("style.update_failed", language)
```

**已正確處理的文件**:
- ✅ `backend/app/services/channel_assist_service.py` - 已使用 `_get_error_message()`

---

## 📋 修復建議

### 後端修復步驟

1. **建立錯誤訊息字典**
   - 在每個服務中建立 `error_messages` 字典
   - 支援三種語言（zh-TW, en, ja）
   - 使用 `_get_error_message()` 方法

2. **修改 API 端點**
   - 所有 `HTTPException(detail=)` 使用 i18n
   - 所有 `message=` 使用 i18n
   - 從用戶請求中獲取語言偏好

3. **參考範例**
   - 參考 `channel_assist_service.py` 的實作方式

### 前端修復步驟

1. **檢查所有硬編碼文字**
   - 使用 `t('translation.key')` 替代
   - 確保所有翻譯鍵在 `i18n/index.ts` 中定義

2. **API 響應處理**
   - 確保錯誤訊息從後端返回時已使用 i18n
   - 前端僅處理顯示邏輯

---

## 🎯 優先級分類

### P0（必須修復 - 用戶可見）

1. **API 錯誤訊息** - 所有 `HTTPException(detail=)` 和 `message=`
2. **前端 UI 文字** - 所有用戶可見的文字

### P1（建議修復 - 部分用戶可見）

1. **API 響應訊息** - 成功/失敗提示
2. **表單驗證訊息** - 錯誤提示

### P2（可選 - 開發者可見）

1. **API 文檔描述** - 可保持中文（僅開發者可見）
2. **日誌訊息** - 可保持中文（僅開發者可見）

---

## 📝 下一步行動

1. ✅ **已完成**: 建立檢查工具
2. ⬜ **待完成**: 修復後端 API 錯誤訊息（P0）
3. ⬜ **待完成**: 修復前端硬編碼文字（P0）
4. ⬜ **待完成**: 建立後端 i18n 系統（參考 `channel_assist_service.py`）
5. ⬜ **待完成**: 更新 `i18n/index.ts` 添加缺失的翻譯鍵

---

**報告生成時間**: 2026-02-06  
**下次檢查**: 修復完成後重新執行 `python check_i18n_compliance.py`


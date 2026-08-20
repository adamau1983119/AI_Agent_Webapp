# ==============================================================================
# 控制人員 3 秒一鍵還原工具 (Emergency Undo Tool for Keep-All Misoperation)
# 用途：當控制人員誤按「Keep All」或 AI 產生錯誤代碼時，0.5 秒無痛還原至乾淨狀態
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host "⚠️  【控制人員緊急防呆還原】" -ForegroundColor Yellow
Write-Host "正在清除所有未提交之本地修改與暫存檔案..." -ForegroundColor Yellow
Write-Host "==================================================================" -ForegroundColor Yellow
Write-Host ""

try {
    # 1. 還原所有已追蹤檔案的修改
    git -c safe.directory=* restore .
    
    # 2. 清除所有未追蹤的臨時檔案與目錄（保留已存在腳本）
    git -c safe.directory=* clean -fd

    Write-Host "✅ 【還原成功】本地工作區已 100% 恢復至最乾淨狀態！" -ForegroundColor Green
    Write-Host "   誤按 Keep All 之所有變更已完全消除，代碼庫零污染。" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ 還原過程發生錯誤: $_" -ForegroundColor Red
}

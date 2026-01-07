# Git 倉庫復修腳本 (PowerShell 版本)
# 用於修復損壞的 Git 倉庫，保護未提交文件並恢復遠程追蹤
# 適用於 Windows PowerShell 環境

$ErrorActionPreference = "Stop"

Write-Host "=== Git 倉庫復修腳本 ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: 建立全量備份
Write-Host "=== Step 1: 建立全量備份 ===" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "..\project_backup_$timestamp"
$untrackedDir = "$backupDir\untracked_files"

if (Test-Path $backupDir) {
    Write-Host "⚠️  備份目錄已存在: $backupDir" -ForegroundColor Yellow
    $response = Read-Host "是否覆蓋? (y/n)"
    if ($response -ne "y") {
        Write-Host "❌ 操作已取消" -ForegroundColor Red
        exit 1
    }
    Remove-Item -Recurse -Force $backupDir
}

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
New-Item -ItemType Directory -Path $untrackedDir -Force | Out-Null

# 備份整個專案目錄
Write-Host "正在備份專案目錄..." -ForegroundColor Gray
Copy-Item -Path "." -Destination $backupDir -Recurse -Exclude @(".git", "node_modules", "__pycache__", "*.pyc")
Write-Host "✅ 已建立備份於: $backupDir" -ForegroundColor Green

# Step 2: 保護未追蹤文件
Write-Host ""
Write-Host "=== Step 2: 保護未追蹤文件 ===" -ForegroundColor Yellow
try {
    $untrackedFiles = git ls-files --others --exclude-standard
    if ($untrackedFiles) {
        Write-Host "發現未追蹤文件:" -ForegroundColor Gray
        foreach ($file in $untrackedFiles) {
            Write-Host "  - $file" -ForegroundColor Gray
            $destPath = Join-Path $untrackedDir $file
            $destParent = Split-Path $destPath -Parent
            if (-not (Test-Path $destParent)) {
                New-Item -ItemType Directory -Path $destParent -Force | Out-Null
            }
            Copy-Item -Path $file -Destination $destPath -Force
        }
        Write-Host "✅ 未追蹤文件已保存到: $untrackedDir" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  沒有未追蹤文件" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  無法獲取未追蹤文件列表: $_" -ForegroundColor Yellow
}

# Step 3: 備份損壞的 .git 目錄
Write-Host ""
Write-Host "=== Step 3: 備份損壞的 .git 目錄 ===" -ForegroundColor Yellow
if (Test-Path ".git") {
    $corruptedBackup = ".git_corrupted_backup_$timestamp"
    Write-Host "正在備份損壞的 .git 目錄到: $corruptedBackup" -ForegroundColor Gray
    Copy-Item -Path ".git" -Destination $corruptedBackup -Recurse -Force
    Write-Host "✅ 已備份損壞的 .git 目錄" -ForegroundColor Green
} else {
    Write-Host "ℹ️  沒有找到 .git 目錄" -ForegroundColor Gray
}

# Step 4: 獲取遠程倉庫 URL
Write-Host ""
Write-Host "=== Step 4: 獲取遠程倉庫配置 ===" -ForegroundColor Yellow
$remoteUrl = git config --get remote.origin.url
if (-not $remoteUrl) {
    Write-Host "⚠️  無法獲取遠程倉庫 URL，請手動輸入:" -ForegroundColor Yellow
    $remoteUrl = Read-Host "遠程倉庫 URL"
    if (-not $remoteUrl) {
        Write-Host "❌ 未提供遠程倉庫 URL，操作已取消" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ 遠程倉庫 URL: $remoteUrl" -ForegroundColor Green
}

# Step 5: 嘗試從遠程恢復（如果可能）
Write-Host ""
Write-Host "=== Step 5: 嘗試從遠程恢復歷史記錄 ===" -ForegroundColor Yellow
$tempDir = "temp_git_recovery_$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    Write-Host "正在從遠程倉庫克隆..." -ForegroundColor Gray
    Push-Location $tempDir
    git clone $remoteUrl temp_repo 2>&1 | Out-Null
    
    if (Test-Path "temp_repo\.git") {
        Write-Host "✅ 成功從遠程恢復 Git 歷史" -ForegroundColor Green
        Pop-Location
        
        # 移除損壞的 .git
        if (Test-Path ".git") {
            Remove-Item -Recurse -Force ".git"
        }
        
        # 複製新的 .git
        Copy-Item -Path "$tempDir\temp_repo\.git" -Destination ".git" -Recurse -Force
        
        # 清理臨時目錄
        Remove-Item -Recurse -Force $tempDir
        
        Write-Host "✅ 已恢復 Git 歷史記錄" -ForegroundColor Green
    } else {
        throw "克隆失敗"
    }
} catch {
    Write-Host "⚠️  無法從遠程恢復，將重新初始化倉庫" -ForegroundColor Yellow
    Pop-Location
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    
    # 移除損壞的 .git
    if (Test-Path ".git") {
        Remove-Item -Recurse -Force ".git"
    }
    
    # 重新初始化
    git init
    Write-Host "✅ 新的 Git 倉庫已初始化" -ForegroundColor Green
    
    # 重新建立遠程追蹤
    git remote add origin $remoteUrl
    Write-Host "✅ 已新增遠程 origin: $remoteUrl" -ForegroundColor Green
}

# Step 6: 檢查並設定分支
Write-Host ""
Write-Host "=== Step 6: 檢查並設定分支 ===" -ForegroundColor Yellow
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    # 嘗試從遠程獲取分支信息
    try {
        git fetch origin 2>&1 | Out-Null
        $remoteBranches = git branch -r
        if ($remoteBranches -match "origin/main") {
            git checkout -b main origin/main 2>&1 | Out-Null
            Write-Host "✅ 已切換到 main 分支（從遠程）" -ForegroundColor Green
        } elseif ($remoteBranches -match "origin/master") {
            git checkout -b master origin/master 2>&1 | Out-Null
            Write-Host "✅ 已切換到 master 分支（從遠程）" -ForegroundColor Green
        } else {
            git checkout -b main
            Write-Host "✅ 已創建 main 分支" -ForegroundColor Green
        }
    } catch {
        git checkout -b main
        Write-Host "✅ 已創建 main 分支" -ForegroundColor Green
    }
} else {
    Write-Host "✅ 當前分支: $currentBranch" -ForegroundColor Green
}

# Step 7: 檢查 .gitignore
Write-Host ""
Write-Host "=== Step 7: 檢查 .gitignore ===" -ForegroundColor Yellow
if (Test-Path ".gitignore") {
    Write-Host "✅ 找到 .gitignore 文件" -ForegroundColor Green
} else {
    Write-Host "⚠️  沒有找到 .gitignore 文件" -ForegroundColor Yellow
}

# Step 8: 添加並提交未追蹤文件
Write-Host ""
Write-Host "=== Step 8: 添加並提交未追蹤文件 ===" -ForegroundColor Yellow
Write-Host "正在檢查工作區狀態..." -ForegroundColor Gray

try {
    $status = git status --porcelain 2>&1
    if ($status -and ($status -ne "")) {
        Write-Host "發現變更:" -ForegroundColor Gray
        git status --short
    
        $response = Read-Host "`n是否提交這些變更? (y/n)"
        if ($response -eq "y") {
            git add .
            $commitMessage = Read-Host "請輸入 commit 訊息 (或按 Enter 使用預設訊息)"
            if (-not $commitMessage) {
                $commitMessage = "修復損壞倉庫並重新提交未追蹤文件 - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
            }
            git commit -m $commitMessage
            Write-Host "✅ 已提交變更" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  跳過提交" -ForegroundColor Gray
        }
    } else {
        Write-Host "ℹ️  工作區乾淨，無需提交" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  無法檢查工作區狀態: $_" -ForegroundColor Yellow
    Write-Host "ℹ️  跳過提交步驟" -ForegroundColor Gray
}

# Step 9: 設定遠程追蹤
Write-Host ""
Write-Host "=== Step 9: 設定遠程追蹤 ===" -ForegroundColor Yellow
try {
    $currentBranch = git branch --show-current
    git branch --set-upstream-to=origin/$currentBranch $currentBranch 2>&1 | Out-Null
    Write-Host "✅ 已設定 $currentBranch 追蹤 origin/$currentBranch" -ForegroundColor Green
} catch {
    Write-Host "⚠️  無法設定 upstream，可能需要先推送分支" -ForegroundColor Yellow
}

# Step 10: 修正編碼設定
Write-Host ""
Write-Host "=== Step 10: 修正編碼設定 ===" -ForegroundColor Yellow
git config --global i18n.commitEncoding utf-8
git config --global i18n.logOutputEncoding utf-8
Write-Host "✅ 已設定 Git 使用 UTF-8 編碼" -ForegroundColor Green

# Step 11: 驗證修復結果
Write-Host ""
Write-Host "=== Step 11: 驗證修復結果 ===" -ForegroundColor Yellow
Write-Host "當前分支: $(git branch --show-current)" -ForegroundColor Gray
Write-Host "最新 commit: $(git log --oneline -1)" -ForegroundColor Gray
Write-Host "遠程倉庫: $(git config --get remote.origin.url)" -ForegroundColor Gray

Write-Host ""
Write-Host "=== 修復完成 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 請檢查以下項目:" -ForegroundColor Yellow
Write-Host "1. 遠程倉庫是否完整: git fetch origin" -ForegroundColor Gray
Write-Host "2. Commit hash 是否正確: git log --oneline -5" -ForegroundColor Gray
Write-Host "3. 未追蹤文件是否已提交: git status" -ForegroundColor Gray
Write-Host "4. 備份位置: $backupDir" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  如果一切正常，可以刪除備份目錄: $backupDir" -ForegroundColor Yellow


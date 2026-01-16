#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
專案結構驗證腳本
用於檢查核心目錄和文件是否存在
"""
import os
import sys
from pathlib import Path

# 設置輸出編碼為 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 定義專案核心目錄結構
REQUIRED_DIRS = [
    "backend/app/api/v1",
    "backend/app/services",
    "backend/app/models",
    "frontend/src/api",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/types",
]

# 關鍵文件（必須存在且非空）
REQUIRED_FILES = [
    "backend/app/main.py",
    "backend/app/config_module.py",  # 已重命名為 config_module.py
    "backend/app/config/__init__.py",  # config 現在是包
    "backend/app/database.py",
    "frontend/src/api/client.ts",
]

def main():
    """驗證專案結構"""
    errors = []
    warnings = []
    
    # 檢查核心目錄
    for dir_path in REQUIRED_DIRS:
        if not os.path.exists(dir_path):
            errors.append(f"❌ 缺少核心目錄: {dir_path}")
        elif not os.path.isdir(dir_path):
            errors.append(f"❌ 路徑不是目錄: {dir_path}")
    
    # 檢查關鍵文件
    for file_path in REQUIRED_FILES:
        if not os.path.exists(file_path):
            errors.append(f"❌ 缺少關鍵文件: {file_path}")
        elif os.path.getsize(file_path) == 0:
            warnings.append(f"⚠️ 關鍵文件為空: {file_path}")
    
    # 輸出結果
    if errors:
        print("❌ 專案結構驗證失敗！")
        for error in errors:
            print(f"  {error}")
        print("\n請確保所有核心目錄和文件都存在。")
        sys.exit(1)
    
    if warnings:
        print("⚠️ 專案結構驗證通過，但有警告：")
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("✅ 專案結構驗證通過，所有核心目錄和文件存在。")
    
    sys.exit(0)

if __name__ == "__main__":
    main()


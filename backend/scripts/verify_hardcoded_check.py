"""
硬編碼檢查驗證腳本
提供詳細的驗證報告，讓用戶可以手動驗證檢查結果
"""
import re
import os
import sys
from pathlib import Path

# 設定輸出編碼（Windows 相容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

FILES_TO_CHECK = [
    "backend/tests/inspiration/test_source_verification.py",
    "backend/app/services/inspiration_preference_service.py",
    "backend/app/services/inspiration_preference_cleanup_service.py",
]


def show_file_content(file_path: str, line_num: int, context_lines: int = 3):
    """顯示檔案內容（帶行號）"""
    if not os.path.exists(file_path):
        print(f"  [ERROR] File not found: {file_path}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        print(f"\n  File: {file_path}")
        print(f"  Lines {start+1}-{end}:")
        print("  " + "-" * 76)
        for i in range(start, end):
            marker = ">>>" if i == line_num - 1 else "   "
            print(f"  {marker} {i+1:4d} | {lines[i].rstrip()}")
        print("  " + "-" * 76)
    except Exception as e:
        print(f"  [ERROR] Failed to read file: {e}")


def main():
    """主函數 - 提供詳細驗證報告"""
    print("=" * 80)
    print("Hardcoded Text Verification Report")
    print("=" * 80)
    print()
    print("This script provides detailed verification of hardcoded text check results.")
    print("You can manually verify each finding by examining the actual code.")
    print()
    print("=" * 80)
    print()
    
    # 檢查每個檔案
    for file_path in FILES_TO_CHECK:
        print(f"[VERIFYING] {file_path}")
        print("-" * 80)
        
        if not os.path.exists(file_path):
            print(f"  [ERROR] File not found")
            print()
            continue
        
        # 讀取檔案並檢查
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            chinese_found = []
            japanese_found = []
            
            for line_num, line in enumerate(lines, 1):
                # 檢查中文
                if re.search(r'[\u4e00-\u9fff]', line):
                    # 檢查是否為允許的情況
                    prev_line = lines[line_num - 2] if line_num > 1 else ""
                    is_comment = line.strip().startswith('#')
                    is_docstring = line.strip().startswith('"""') or line.strip().startswith("'''")
                    is_logger = 'logger.' in line or 'logger.' in prev_line
                    is_test_file = 'test' in file_path.lower()
                    
                    if not (is_comment or is_docstring or is_logger or is_test_file):
                        chinese_found.append({
                            "line": line_num,
                            "content": line.rstrip(),
                            "context": {
                                "is_comment": is_comment,
                                "is_docstring": is_docstring,
                                "is_logger": is_logger,
                                "is_test_file": is_test_file,
                                "prev_line": prev_line.rstrip() if prev_line else None
                            }
                        })
                
                # 檢查日文（只檢查假名，不包括漢字）
                if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', line):
                    prev_line = lines[line_num - 2] if line_num > 1 else ""
                    is_comment = line.strip().startswith('#')
                    is_docstring = line.strip().startswith('"""') or line.strip().startswith("'''")
                    is_logger = 'logger.' in line or 'logger.' in prev_line
                    is_test_file = 'test' in file_path.lower()
                    
                    if not (is_comment or is_docstring or is_logger or is_test_file):
                        japanese_found.append({
                            "line": line_num,
                            "content": line.rstrip(),
                            "context": {
                                "is_comment": is_comment,
                                "is_docstring": is_docstring,
                                "is_logger": is_logger,
                                "is_test_file": is_test_file,
                                "prev_line": prev_line.rstrip() if prev_line else None
                            }
                        })
            
            # 顯示結果
            if chinese_found or japanese_found:
                print(f"  [FOUND] Potential hardcoded text:")
                print()
                
                for item in chinese_found:
                    print(f"  Line {item['line']}: Chinese text found")
                    show_file_content(file_path, item['line'])
                    print(f"  Context analysis:")
                    print(f"    - Is comment: {item['context']['is_comment']}")
                    print(f"    - Is docstring: {item['context']['is_docstring']}")
                    print(f"    - Is logger: {item['context']['is_logger']}")
                    print(f"    - Is test file: {item['context']['is_test_file']}")
                    if item['context']['prev_line']:
                        print(f"    - Previous line: {item['context']['prev_line']}")
                    print()
                
                for item in japanese_found:
                    print(f"  Line {item['line']}: Japanese text found")
                    show_file_content(file_path, item['line'])
                    print(f"  Context analysis:")
                    print(f"    - Is comment: {item['context']['is_comment']}")
                    print(f"    - Is docstring: {item['context']['is_docstring']}")
                    print(f"    - Is logger: {item['context']['is_logger']}")
                    print(f"    - Is test file: {item['context']['is_test_file']}")
                    if item['context']['prev_line']:
                        print(f"    - Previous line: {item['context']['prev_line']}")
                    print()
            else:
                print(f"  [OK] No hardcoded text found (all Chinese/Japanese text is in allowed contexts)")
                print()
        
        except Exception as e:
            print(f"  [ERROR] Failed to check file: {e}")
            print()
    
    print("=" * 80)
    print("Verification Complete")
    print("=" * 80)
    print()
    print("Summary:")
    print("  - All findings shown above with full context")
    print("  - You can manually verify each finding by checking the actual code")
    print("  - Logger messages and test data are allowed (not user-visible)")
    print()


if __name__ == "__main__":
    main()


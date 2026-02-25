"""
檢查硬編碼文字腳本
用於檢查新生成的程式是否有硬編碼問題
"""
import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# 設定輸出編碼（Windows 相容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 需要檢查的檔案列表（包含所有新修改的檔案）
FILES_TO_CHECK = [
    # P0 問題修復
    "frontend/src/components/ui/InfiniteScroll.tsx",
    "backend/app/services/search_service.py",
    "frontend/src/pages/Topics.tsx",
    "frontend/src/pages/ResetPassword.tsx",
    "frontend/src/types/index.ts",
    "frontend/src/api/topics.ts",
    "frontend/src/pages/TopicDetail.tsx",
    "frontend/src/api/contents.ts",
    "backend/app/schemas/content.py",
    "backend/app/api/v1/contents.py",
    "frontend/src/components/features/ImageGallery.tsx",
    "backend/app/api/v1/images.py",
    "backend/app/services/images/enhanced_photo_matcher.py",
    "frontend/src/components/features/InteractionButtons.tsx",
    "frontend/src/api/interactions.ts",
    "backend/app/schemas/interaction.py",
    "backend/app/services/repositories/interaction_repository.py",
    "backend/app/api/v1/interactions.py",
    # P1 問題修復
    "backend/app/api/v1/auth.py",
    "frontend/src/pages/Dashboard.tsx",
    "frontend/src/components/ui/TopicCard.tsx",
    "frontend/src/components/features/ImageSearch.tsx",
    "backend/app/api/v1/inspiration.py",
]

# 允許的中文字符（註釋、日誌等非用戶可見）
ALLOWED_CHINESE_PATTERNS = [
    r'#.*[\u4e00-\u9fff]',  # 註釋中的中文
    r'""".*[\u4e00-\u9fff].*"""',  # 文檔字串中的中文
    r"'''.*[\u4e00-\u9fff].*'''",  # 文檔字串中的中文
    r'logger\.(info|warning|error|debug)\(.*[\u4e00-\u9fff]',  # 日誌訊息
    r'print\(.*[\u4e00-\u9fff]',  # print 語句（測試用）
]

# 禁止的中文字符模式（用戶可見）
FORBIDDEN_PATTERNS = [
    r'"[^"]*[\u4e00-\u9fff][^"]*"',  # 字串中的中文（非註釋）
    r"'[^']*[\u4e00-\u9fff][^']*'",  # 字串中的中文（非註釋）
    r'f"[^"]*[\u4e00-\u9fff][^"]*"',  # f-string 中的中文
    r"f'[^']*[\u4e00-\u9fff][^']*'",  # f-string 中的中文
]

# 例外情況（允許的中文）
EXCEPTIONS = [
    r'logger\.(info|warning|error|debug)',  # 日誌訊息
    r'#.*',  # 註釋
    r'""".*"""',  # 文檔字串
    r"'''.*'''",  # 文檔字串
    r'print\(',  # print 語句（測試用）
    r'測試',  # 測試相關
    r'問題',  # 問題描述
    r'說明',  # 說明文字
]


def contains_chinese(text: str) -> bool:
    """檢查文字是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def contains_japanese(text: str) -> bool:
    """檢查文字是否包含日文字符"""
    # 日文字符範圍：ひらがな、カタカナ、漢字、記号
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))


def is_allowed_chinese(line: str, file_path: str = "", lines: list = None, line_num: int = 0) -> bool:
    """檢查是否為允許的中文（註釋、日誌、測試數據、docstring 等）"""
    line_stripped = line.strip()
    
    # 檢查是否為註釋
    if line_stripped.startswith('#'):
        return True
    
    # 檢查是否為文檔字串（docstring）
    # 檢查是否在 docstring 區塊內（前後有 """ 或 '''）
    if lines and line_num > 0:
        # 檢查是否在 docstring 內（簡化版：檢查前後是否有 """ 或 '''）
        # 檢查前幾行是否有開始的 """
        for i in range(max(0, line_num - 10), line_num):
            if i < len(lines):
                prev_line = lines[i].strip()
                if prev_line.startswith('"""') or prev_line.startswith("'''"):
                    # 檢查是否已結束（在當前行之前）
                    for j in range(i + 1, line_num):
                        if j < len(lines):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                break
                    else:
                        # 仍在 docstring 內
                        return True
    
    # 檢查是否為日誌訊息（後端日誌可以使用中文，因為不是用戶可見的）
    if re.search(r'logger\.(info|warning|error|debug)\(', line):
        return True
    
    # 檢查是否為 print 語句（測試用）
    if re.search(r'print\(', line):
        return True
    
    # 檢查是否為測試檔案中的測試數據（測試案例數據可以使用中文/日文）
    if 'test' in file_path.lower() or 'tests' in file_path.lower():
        # 測試檔案中的測試數據允許使用中文/日文（所有測試數據）
        return True
    
    return False


def is_allowed_japanese(line: str, file_path: str = "") -> bool:
    """檢查是否為允許的日文（註釋、日誌、測試數據等）"""
    # 日文和中文使用相同的允許規則
    return is_allowed_chinese(line, file_path)


def check_file(file_path: str) -> List[Dict[str, any]]:
    """檢查單個檔案"""
    issues = []
    
    # 獲取專案根目錄（腳本在 backend/scripts/，所以需要向上兩級）
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    full_path = project_root / file_path
    
    if not full_path.exists():
        return [{"type": "error", "message": f"檔案不存在: {file_path} (嘗試路徑: {full_path})"}]
    
    file_path = str(full_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # 檢查前一行是否有 logger（處理跨行的 logger 訊息）
            prev_line = lines[line_num - 2] if line_num > 1 else ""
            is_logger_context = 'logger.' in prev_line or 'logger.' in line
            
            # 跳過允許的中文/日文（註釋、日誌、測試數據、docstring 等）
            if is_allowed_chinese(line, file_path, lines, line_num) or is_allowed_japanese(line, file_path) or is_logger_context:
                continue
            
            # 檢查是否包含中文
            if contains_chinese(line):
                # 檢查是否在字串中
                # 尋找字串（單引號或雙引號）
                string_pattern = r'["\']([^"\']*[\u4e00-\u9fff][^"\']*)["\']'
                matches = re.finditer(string_pattern, line)
                
                for match in matches:
                    # 檢查是否在註釋中
                    comment_pos = line.find('#')
                    if comment_pos != -1 and match.start() > comment_pos:
                        continue
                    
                    # 檢查是否在文檔字串中
                    if '"""' in line or "'''" in line:
                        continue
                    
                    # 檢查是否為日誌訊息（檢查當前行和前一行）
                    if 'logger.' in line or 'logger.' in prev_line:
                        continue
                    
                    # 檢查是否為 print 語句
                    if 'print(' in line:
                        continue
                    
                    # 發現硬編碼中文
                    issues.append({
                        "file": file_path,
                        "line": line_num,
                        "content": line.strip(),
                        "match": match.group(0),
                        "type": "hardcoded_chinese",
                        "full_line": line
                    })
            
            # 檢查是否包含日文（只檢查純日文字符，不包括漢字，因為漢字已在中文檢查中處理）
            # 日文假名範圍：ひらがな \u3040-\u309F, カタカナ \u30A0-\u30FF
            if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', line):
                # 檢查是否在字串中
                # 尋找字串（單引號或雙引號）
                string_pattern = r'["\']([^"\']*[\u3040-\u309F\u30A0-\u30FF][^"\']*)["\']'
                matches = re.finditer(string_pattern, line)
                
                for match in matches:
                    # 檢查是否在註釋中
                    comment_pos = line.find('#')
                    if comment_pos != -1 and match.start() > comment_pos:
                        continue
                    
                    # 檢查是否在文檔字串中
                    if '"""' in line or "'''" in line:
                        continue
                    
                    # 檢查是否為日誌訊息（檢查當前行和前一行）
                    if 'logger.' in line or 'logger.' in prev_line:
                        continue
                    
                    # 檢查是否為 print 語句
                    if 'print(' in line:
                        continue
                    
                    # 發現硬編碼日文
                    issues.append({
                        "file": file_path,
                        "line": line_num,
                        "content": line.strip(),
                        "match": match.group(0),
                        "type": "hardcoded_japanese",
                        "full_line": line
                    })
        
        return issues
    
    except Exception as e:
        return [{"type": "error", "message": f"讀取檔案失敗: {file_path}, 錯誤: {e}"}]


def main():
    """主函數"""
    print("=" * 80)
    print("Hardcoded Text Checker - Detailed Report")
    print("=" * 80)
    print()
    print("Checking files:")
    for file_path in FILES_TO_CHECK:
        print(f"  - {file_path}")
    print()
    print("=" * 80)
    print()
    
    all_issues = []
    all_allowed = []
    
    # 獲取專案根目錄
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    for file_path_rel in FILES_TO_CHECK:
        # 轉換為絕對路徑
        file_path = str(project_root / file_path_rel)
        print(f"[CHECKING] {file_path_rel}")
        print("-" * 80)
        
        if not os.path.exists(file_path):
            print(f"  [ERROR] File not found: {file_path_rel} (嘗試路徑: {file_path})")
            all_issues.append({"type": "error", "file": file_path_rel, "message": "File not found"})
            print()
            continue
        
        issues = check_file(file_path_rel)
        
        if issues:
            all_issues.extend(issues)
            for issue in issues:
                if issue.get("type") == "hardcoded_chinese":
                    print(f"  [WARNING] Line {issue['line']}: Found hardcoded Chinese text")
                    print(f"     Full line: {issue['content']}")
                    print(f"     Matched text: {issue['match']}")
                    print(f"     Context: Checking if this is user-visible text...")
                    # 檢查是否為允許的情況
                    line_content = issue.get('content', '')
                    if 'logger.' in line_content:
                        print(f"     [ALLOWED] This is a logger message (backend log, not user-visible)")
                        all_allowed.append(issue)
                    elif 'test' in file_path.lower():
                        print(f"     [ALLOWED] This is test data (not user-visible)")
                        all_allowed.append(issue)
                    else:
                        print(f"     [ISSUE] This appears to be user-visible text!")
                    print()
                elif issue.get("type") == "hardcoded_japanese":
                    print(f"  [WARNING] Line {issue['line']}: Found hardcoded Japanese text")
                    print(f"     Full line: {issue['content']}")
                    print(f"     Matched text: {issue['match']}")
                    print(f"     Context: Checking if this is user-visible text...")
                    # 檢查是否為允許的情況
                    line_content = issue.get('content', '')
                    if 'logger.' in line_content:
                        print(f"     [ALLOWED] This is a logger message (backend log, not user-visible)")
                        all_allowed.append(issue)
                    elif 'test' in file_path.lower():
                        print(f"     [ALLOWED] This is test data (not user-visible)")
                        all_allowed.append(issue)
                    else:
                        print(f"     [ISSUE] This appears to be user-visible text!")
                    print()
                else:
                    print(f"  [ERROR] {issue.get('message', 'Unknown error')}")
                    print()
        else:
            print(f"  [OK] No hardcoded text found")
            print()
        
        print()
    
    print("=" * 80)
    print("DETAILED CHECK SUMMARY")
    print("=" * 80)
    print()
    
    # 分類問題
    real_issues = [issue for issue in all_issues if issue.get("type") in ["hardcoded_chinese", "hardcoded_japanese"] and issue not in all_allowed]
    allowed_issues = [issue for issue in all_issues if issue in all_allowed]
    error_issues = [issue for issue in all_issues if issue.get("type") == "error"]
    
    hardcoded_chinese_count = sum(1 for issue in real_issues if issue.get("type") == "hardcoded_chinese")
    hardcoded_japanese_count = sum(1 for issue in real_issues if issue.get("type") == "hardcoded_japanese")
    allowed_chinese_count = sum(1 for issue in allowed_issues if issue.get("type") == "hardcoded_chinese")
    allowed_japanese_count = sum(1 for issue in allowed_issues if issue.get("type") == "hardcoded_japanese")
    
    print("STATISTICS:")
    print(f"  Total issues found: {len(all_issues)}")
    print(f"  - Real issues (user-visible): {len(real_issues)}")
    print(f"    * Hardcoded Chinese: {hardcoded_chinese_count}")
    print(f"    * Hardcoded Japanese: {hardcoded_japanese_count}")
    print(f"  - Allowed (not user-visible): {len(allowed_issues)}")
    print(f"    * Logger messages (Chinese): {allowed_chinese_count}")
    print(f"    * Logger messages (Japanese): {allowed_japanese_count}")
    print(f"  - Errors: {len(error_issues)}")
    print()
    
    if real_issues:
        print("=" * 80)
        print("REAL ISSUES (Need to fix - user-visible text):")
        print("=" * 80)
        for issue in real_issues:
            lang_type = "Chinese" if issue.get("type") == "hardcoded_chinese" else "Japanese"
            print(f"\n  File: {issue['file']}:{issue['line']}")
            print(f"  Type: Hardcoded {lang_type}")
            print(f"  Content: {issue['content']}")
            print(f"  Matched: {issue['match']}")
        print()
        return 1
    else:
        print("=" * 80)
        print("RESULT: [PASSED]")
        print("=" * 80)
        print()
        print("All hardcoded text found are in allowed contexts:")
        print("  - Logger messages (backend logs, not user-visible)")
        print("  - Test data (test cases, not user-visible)")
        print()
        print("No user-visible hardcoded text found. Code complies with Rule #6.")
        print()
        return 0


if __name__ == "__main__":
    exit(main())


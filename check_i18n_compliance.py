#!/usr/bin/env python3
"""
i18n 合規性檢查工具
檢查專案中所有硬編碼文字，確保使用 i18n 系統
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict

# 專案根目錄
PROJECT_ROOT = Path(__file__).parent

# 需要檢查的目錄
FRONTEND_DIR = PROJECT_ROOT / "frontend" / "src"
BACKEND_DIR = PROJECT_ROOT / "backend" / "app"

# 排除的目錄和文件
EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    "__pycache__",
    ".next",
    "venv",
    ".venv",
    "temp",
    "tmp",
    "i18n",  # i18n 配置文件本身
}

EXCLUDE_FILES = {
    "i18n/index.ts",  # i18n 配置文件
    "i18n/index.js",
}

# 允許的硬編碼文字（技術性文字、變數名等）
ALLOWED_HARDCODED = {
    # 技術性文字
    "data-testid",
    "className",
    "id",
    "type",
    "method",
    "GET",
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
    "status",
    "error",
    "success",
    "loading",
    "true",
    "false",
    "null",
    "undefined",
    # 品牌名稱（根據 README，這是唯一例外）
    "INFLUENCERS",
    "Influencers AI",
    # 常見的技術標識符
    "zh-TW",
    "en",
    "ja",
    "zh",
    "TW",
    # API 相關
    "api",
    "v1",
    "Bearer",
    "Authorization",
    "Content-Type",
    "application/json",
    # 常見的 HTML/CSS 屬性
    "href",
    "src",
    "alt",
    "title",
    "aria-label",
    # 常見的變數名
    "email",
    "password",
    "name",
    "username",
    "token",
    "key",
    "value",
    # 常見的函數名
    "t(",
    "useTranslation",
    "i18n",
    # 常見的註釋標記
    "TODO",
    "FIXME",
    "NOTE",
    "WARNING",
    # 常見的日誌級別
    "INFO",
    "DEBUG",
    "WARNING",
    "ERROR",
    "CRITICAL",
}

# 中文字符正則（包括繁體和簡體）
CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fff]+')
# 日文字符正則（平假名、片假名、漢字）
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4e00-\u9fff]+')
# 用戶可見的文字模式（只檢查這些）
USER_VISIBLE_PATTERNS = [
    # HTTPException detail（返回給用戶的錯誤訊息）
    re.compile(r'HTTPException\s*\([^)]*detail\s*=\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
    # API 響應 message（返回給用戶的訊息）
    re.compile(r'message\s*=\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
    # 錯誤建議 suggestion（返回給用戶的）
    re.compile(r'suggestion["\']?\s*[:=]\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
    # return 錯誤訊息（返回給用戶的）
    re.compile(r'return\s+(?:None|False|True)?\s*,\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
    # raise Exception with 中文訊息（可能返回給用戶）
    re.compile(r'raise\s+\w+Exception\s*\(["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
    # 前端硬編碼文字（在 .ts/.tsx 文件中）
    re.compile(r'["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']'),
]

# 需要排除的模式（開發者可見，不需要 i18n）
EXCLUDE_PATTERNS = [
    # API 文檔描述
    re.compile(r'description\s*=\s*["\']([^"\']+)["\']'),
    # 日誌訊息
    re.compile(r'logger\.(info|error|warning|debug)\s*\([^)]*["\']([^"\']+)["\']'),
    # 文檔字符串（docstring）
    re.compile(r'"""[^"]*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"]*"""'),
    # 註釋
    re.compile(r'#\s*[^\n]*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+'),
    re.compile(r'//\s*[^\n]*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+'),
    # console.log/warn/error（開發者調試用）
    re.compile(r'console\.(log|warn|error|debug)\s*\([^)]*["\']([^"\']+)["\']'),
    # 變數名和函數名
    re.compile(r'(?:const|let|var|function|class)\s+\w+\s*[:=]'),
    # 配置字典（內部數據）
    re.compile(r'["\']\w+["\']\s*:\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']\s*,?\s*(?:#|//)'),
]

# 已使用 i18n 的模式
I18N_PATTERNS = [
    re.compile(r't\(["\']([^"\']+)["\']\)'),  # t('key')
    re.compile(r't\(`([^`]+)`\)'),  # t(`key`)
    re.compile(r'useTranslation\(\)'),  # useTranslation()
    re.compile(r'i18n\.t\(["\']([^"\']+)["\']\)'),  # i18n.t('key')
    re.compile(r'_get_error_message\([^)]+\)'),  # 後端的錯誤訊息函數
    re.compile(r'self\.error_messages\['),  # 後端的錯誤訊息字典
]


class I18nChecker:
    """i18n 合規性檢查器"""
    
    def __init__(self):
        self.issues: List[Dict] = []
        self.stats = {
            "files_checked": 0,
            "issues_found": 0,
            "files_with_issues": 0,
        }
        self.by_file: Dict[str, List[Dict]] = defaultdict(list)
    
    def is_excluded(self, filepath: Path) -> bool:
        """檢查文件是否應該被排除"""
        # 檢查目錄
        for part in filepath.parts:
            if part in EXCLUDE_DIRS:
                return True
        
        # 檢查文件路徑
        filepath_str = str(filepath)
        for exclude in EXCLUDE_FILES:
            if exclude in filepath_str:
                return True
        
        return False
    
    def is_allowed_hardcoded(self, text: str) -> bool:
        """檢查是否為允許的硬編碼文字"""
        text_lower = text.lower().strip()
        
        # 檢查是否在允許列表中
        if text_lower in ALLOWED_HARDCODED:
            return True
        
        # 檢查是否為純技術標識符（無中文/日文）
        if not CHINESE_PATTERN.search(text) and not JAPANESE_PATTERN.search(text):
            # 可能是技術性文字
            if re.match(r'^[a-zA-Z0-9_\-\.]+$', text):
                return True
        
        return False
    
    def has_i18n_usage(self, line: str) -> bool:
        """檢查該行是否使用了 i18n"""
        for pattern in I18N_PATTERNS:
            if pattern.search(line):
                return True
        return False
    
    def is_excluded_pattern(self, line: str, match_start: int) -> bool:
        """檢查是否匹配排除模式（開發者可見，不需要 i18n）"""
        for pattern in EXCLUDE_PATTERNS:
            if pattern.search(line):
                # 檢查匹配位置是否在我們關注的文字之前或重疊
                exclude_match = pattern.search(line)
                if exclude_match:
                    # 如果排除模式匹配的位置包含或接近我們關注的文字，則排除
                    if abs(exclude_match.start() - match_start) < 50:
                        return True
        return False
    
    def find_hardcoded_text(self, content: str, filepath: Path) -> List[Dict]:
        """在文件內容中查找硬編碼文字（只檢查用戶可見的）"""
        issues = []
        lines = content.split('\n')
        is_frontend = filepath.suffix in ['.ts', '.tsx', '.js', '.jsx']
        is_backend = filepath.suffix == '.py'
        
        for line_num, line in enumerate(lines, 1):
            # 跳過註釋行
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            # 跳過已經使用 i18n 的行
            if self.has_i18n_usage(line):
                continue
            
            # 後端：只檢查 HTTPException detail、message、suggestion 等
            if is_backend:
                # 檢查 HTTPException detail
                detail_match = re.search(r'HTTPException\s*\([^)]*detail\s*=\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']', line)
                if detail_match:
                    text = detail_match.group(1)
                    if text and not self.is_allowed_hardcoded(text):
                        issue = {
                            "file": str(filepath.relative_to(PROJECT_ROOT)),
                            "line": line_num,
                            "text": text,
                            "context": line.strip()[:100],
                            "severity": "error",
                            "type": "HTTPException detail"
                        }
                        issues.append(issue)
                        self.issues.append(issue)
                        self.by_file[str(filepath.relative_to(PROJECT_ROOT))].append(issue)
                
                # 檢查 message= (API 響應訊息)
                message_match = re.search(r'message\s*=\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']', line)
                if message_match:
                    text = message_match.group(1)
                    if text and not self.is_allowed_hardcoded(text):
                        # 排除 logger 訊息
                        if 'logger.' not in line.lower():
                            issue = {
                                "file": str(filepath.relative_to(PROJECT_ROOT)),
                                "line": line_num,
                                "text": text,
                                "context": line.strip()[:100],
                                "severity": "error",
                                "type": "API response message"
                            }
                            issues.append(issue)
                            self.issues.append(issue)
                            self.by_file[str(filepath.relative_to(PROJECT_ROOT))].append(issue)
                
                # 檢查 suggestion= (錯誤建議)
                suggestion_match = re.search(r'suggestion["\']?\s*[:=]\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']', line)
                if suggestion_match:
                    text = suggestion_match.group(1)
                    if text and not self.is_allowed_hardcoded(text):
                        issue = {
                            "file": str(filepath.relative_to(PROJECT_ROOT)),
                            "line": line_num,
                            "text": text,
                            "context": line.strip()[:100],
                            "severity": "error",
                            "type": "Error suggestion"
                        }
                        issues.append(issue)
                        self.issues.append(issue)
                        self.by_file[str(filepath.relative_to(PROJECT_ROOT))].append(issue)
                
                # 檢查 return None/False, "錯誤訊息" (服務層返回的錯誤)
                return_match = re.search(r'return\s+(?:None|False|True)?\s*,\s*["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']', line)
                if return_match:
                    text = return_match.group(1)
                    if text and not self.is_allowed_hardcoded(text):
                        # 排除 logger 和註釋
                        if 'logger.' not in line.lower() and not line.strip().startswith('#'):
                            issue = {
                                "file": str(filepath.relative_to(PROJECT_ROOT)),
                                "line": line_num,
                                "text": text,
                                "context": line.strip()[:100],
                                "severity": "error",
                                "type": "Service error message"
                            }
                            issues.append(issue)
                            self.issues.append(issue)
                            self.by_file[str(filepath.relative_to(PROJECT_ROOT))].append(issue)
            
            # 前端：檢查所有硬編碼文字（但排除註釋和 console）
            elif is_frontend:
                # 排除 console.log/warn/error
                if 'console.' in line.lower():
                    continue
                
                # 檢查硬編碼的中文/日文字符串
                string_matches = re.finditer(r'["\']([^"\']*[\u4e00-\u9fff\u3040-\u309F\u30A0-\u30FF]+[^"\']*)["\']', line)
                for match in string_matches:
                    text = match.group(1)
                    
                    if not text or self.is_allowed_hardcoded(text):
                        continue
                    
                    # 排除註釋
                    if '//' in line[:match.start()] or '/*' in line[:match.start()]:
                        continue
                    
                    # 排除已經使用 i18n 的情況
                    if 't(' in line or 'useTranslation' in line:
                        continue
                    
                    # 排除變數名和函數名
                    if re.match(r'^\w+$', text.strip()):
                        continue
                    
                    issue = {
                        "file": str(filepath.relative_to(PROJECT_ROOT)),
                        "line": line_num,
                        "text": text,
                        "context": line.strip()[:100],
                        "severity": "error" if len(text) > 3 else "warning",
                        "type": "Frontend hardcoded text"
                    }
                    issues.append(issue)
                    self.issues.append(issue)
                    self.by_file[str(filepath.relative_to(PROJECT_ROOT))].append(issue)
        
        return issues
    
    def check_file(self, filepath: Path):
        """檢查單個文件"""
        if self.is_excluded(filepath):
            return
        
        # 只檢查特定類型的文件
        if filepath.suffix not in ['.py', '.ts', '.tsx', '.js', '.jsx']:
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.stats["files_checked"] += 1
            issues = self.find_hardcoded_text(content, filepath)
            
            if issues:
                self.stats["files_with_issues"] += 1
                self.stats["issues_found"] += len(issues)
        
        except Exception as e:
            print(f"❌ 讀取文件失敗 {filepath}: {e}")
    
    def check_directory(self, directory: Path):
        """遞歸檢查目錄"""
        if not directory.exists():
            print(f"⚠️  目錄不存在: {directory}")
            return
        
        for root, dirs, files in os.walk(directory):
            # 過濾排除的目錄
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                filepath = Path(root) / file
                self.check_file(filepath)
    
    def generate_report(self) -> str:
        """生成檢查報告"""
        report = []
        report.append("=" * 80)
        report.append("i18n 合規性檢查報告")
        report.append("=" * 80)
        report.append("")
        
        # 統計信息
        report.append("📊 統計信息")
        report.append("-" * 80)
        report.append(f"檢查文件數: {self.stats['files_checked']}")
        report.append(f"發現問題數: {self.stats['issues_found']}")
        report.append(f"有問題的文件數: {self.stats['files_with_issues']}")
        report.append("")
        
        if not self.issues:
            report.append("✅ 恭喜！未發現硬編碼文字問題。")
            report.append("")
            return "\n".join(report)
        
        # 按文件分組顯示問題
        report.append("❌ 發現的問題")
        report.append("-" * 80)
        report.append("")
        
        for filepath, issues in sorted(self.by_file.items()):
            report.append(f"📄 {filepath}")
            report.append(f"   發現 {len(issues)} 個問題")
            report.append("")
            
            for issue in issues[:10]:  # 每個文件最多顯示10個問題
                severity_icon = "🔴" if issue["severity"] == "error" else "🟡"
                report.append(f"   {severity_icon} 第 {issue['line']} 行:")
                report.append(f"      文字: {issue['text'][:50]}")
                report.append(f"      上下文: {issue['context'][:70]}")
                report.append("")
            
            if len(issues) > 10:
                report.append(f"   ... 還有 {len(issues) - 10} 個問題")
                report.append("")
        
        # 建議
        report.append("")
        report.append("💡 修復建議")
        report.append("-" * 80)
        report.append("1. 前端: 使用 t('translation.key') 替代硬編碼文字")
        report.append("2. 後端: 使用錯誤訊息字典和 _get_error_message() 函數")
        report.append("3. API 響應: 確保所有用戶可見的訊息都通過 i18n 系統")
        report.append("4. 檢查 i18n/index.ts 確保所有翻譯鍵都已定義")
        report.append("")
        
        return "\n".join(report)
    
    def save_json_report(self, output_path: Path):
        """保存 JSON 格式的報告"""
        report_data = {
            "stats": self.stats,
            "issues": self.issues,
            "by_file": {
                filepath: issues
                for filepath, issues in self.by_file.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)


def main():
    """主函數"""
    import sys
    import io
    
    # 設置 UTF-8 編碼輸出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("🔍 開始 i18n 合規性檢查...")
    print("")
    
    checker = I18nChecker()
    
    # 檢查前端
    print("📱 檢查前端代碼...")
    if FRONTEND_DIR.exists():
        checker.check_directory(FRONTEND_DIR)
    else:
        print(f"⚠️  前端目錄不存在: {FRONTEND_DIR}")
    
    # 檢查後端
    print("🔧 檢查後端代碼...")
    if BACKEND_DIR.exists():
        checker.check_directory(BACKEND_DIR)
    else:
        print(f"⚠️  後端目錄不存在: {BACKEND_DIR}")
    
    # 生成報告
    print("")
    print("📝 生成報告...")
    report = checker.generate_report()
    print(report)
    
    # 保存報告
    report_file = PROJECT_ROOT / "i18n_compliance_report.txt"
    json_report_file = PROJECT_ROOT / "i18n_compliance_report.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    checker.save_json_report(json_report_file)
    
    print("")
    print(f"✅ 報告已保存:")
    print(f"   - {report_file}")
    print(f"   - {json_report_file}")
    print("")
    
    # 返回退出碼
    if checker.stats["issues_found"] > 0:
        print(f"❌ 發現 {checker.stats['issues_found']} 個問題，請修復後重新檢查")
        return 1
    else:
        print("✅ 所有檢查通過！")
        return 0


if __name__ == "__main__":
    exit(main())


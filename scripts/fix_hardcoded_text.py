#!/usr/bin/env python3
"""
硬編碼文字修復工具
==================
功能：
1. 掃描所有 .tsx 文件找出硬編碼文字
2. 生成需要添加到 i18n 的翻譯
3. 報告修復進度
4. 校對檢查遺漏

作者：AI Agent
日期：2026-02-05
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, field

# 配置
FRONTEND_PATH = Path(__file__).parent.parent / "frontend" / "src"
PAGES_PATH = FRONTEND_PATH / "pages"
COMPONENTS_PATH = FRONTEND_PATH / "components"
I18N_PATH = FRONTEND_PATH / "i18n" / "index.ts"

# 品牌名稱例外（不需要翻譯）
BRAND_EXCEPTIONS = [
    "INFLUENCERS",
    "AI-POWERED CONTENT CREATION",
]

# 常見的硬編碼模式
HARDCODED_PATTERNS = [
    # 中文字符
    r'>[^<{]*?([\u4e00-\u9fff]+[^<]*?)<',
    # 全大寫英文（可能是 UI 標籤）
    r">\s*([A-Z][A-Z\s]+[A-Z])\s*<",
    # 字符串中的中文
    r"['\"]([^'\"]*[\u4e00-\u9fff]+[^'\"]*)['\"]",
]

@dataclass
class HardcodedText:
    """硬編碼文字資訊"""
    file: str
    line: int
    text: str
    context: str
    suggested_key: str = ""
    
@dataclass
class ScanResult:
    """掃描結果"""
    total_files: int = 0
    files_with_issues: int = 0
    total_hardcoded: int = 0
    hardcoded_list: List[HardcodedText] = field(default_factory=list)
    
def is_exception(text: str) -> bool:
    """檢查是否為例外（品牌名稱等）"""
    text = text.strip()
    for exc in BRAND_EXCEPTIONS:
        if exc in text:
            return True
    # 忽略純數字、純符號
    if re.match(r'^[\d\s\.\-\+\*\/\%\$\#\@\!\?\,\;\:\(\)\[\]\{\}]+$', text):
        return True
    # 忽略 className 等屬性值
    if text.startswith('text-') or text.startswith('bg-') or text.startswith('font-'):
        return True
    return False

def suggest_i18n_key(file_path: str, text: str) -> str:
    """根據文件和文字內容建議 i18n key"""
    # 從文件名推斷模組
    filename = Path(file_path).stem.lower()
    
    # 常見映射
    module_map = {
        'login': 'auth.login',
        'register': 'auth.register',
        'dashboard': 'dashboard',
        'settings': 'settings',
        'topics': 'topics',
        'topicdetail': 'topics.detail',
        'channels': 'channels',
        'inspiration': 'inspiration',
        'styleprofile': 'style',
        'socialconnect': 'social',
        'preferences': 'preferences',
        'schedule': 'schedule',
        'oauthcallback': 'auth.oauth',
        'terms': 'legal.terms',
        'privacy': 'legal.privacy',
    }
    
    module = module_map.get(filename, filename)
    
    # 從文字內容推斷 key 名稱
    text_lower = text.lower().strip()
    
    # 常見文字映射
    text_map = {
        '載入中': 'loading',
        'loading': 'loading',
        '搜尋中': 'searching',
        '已連結': 'connected',
        '未連結': 'notConnected',
        '深色模式': 'darkMode',
        '淺色模式': 'lightMode',
        '儲存': 'save',
        '取消': 'cancel',
        '確認': 'confirm',
        '刪除': 'delete',
        '編輯': 'edit',
        '返回': 'back',
        '下一步': 'next',
        '提交': 'submit',
    }
    
    for cn, en in text_map.items():
        if cn in text_lower or en in text_lower:
            return f"{module}.{en}"
    
    # 如果沒有匹配，生成一個基於文字的 key
    # 移除非字母數字字符，轉換為 camelCase
    clean_text = re.sub(r'[^\w\s]', '', text)
    words = clean_text.split()[:3]  # 最多取 3 個詞
    if words:
        key_name = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
        return f"{module}.{key_name}"
    
    return f"{module}.text"

def scan_file(file_path: Path) -> List[HardcodedText]:
    """掃描單個文件的硬編碼文字"""
    hardcoded = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        print(f"  [WARN] Cannot read file: {file_path} - {e}")
        return hardcoded
    
    for i, line in enumerate(lines, 1):
        # 跳過註釋和 import
        if line.strip().startswith('//') or line.strip().startswith('import') or line.strip().startswith('*'):
            continue
        
        # 檢查中文字符
        chinese_matches = re.findall(r'[\u4e00-\u9fff]+[^\u4e00-\u9fff\n]*[\u4e00-\u9fff]*', line)
        for match in chinese_matches:
            if not is_exception(match) and len(match.strip()) > 1:
                # 檢查是否已經在 t() 函數中
                if f"t('" not in line and f't("' not in line:
                    hardcoded.append(HardcodedText(
                        file=str(file_path),
                        line=i,
                        text=match.strip(),
                        context=line.strip()[:80],
                        suggested_key=suggest_i18n_key(str(file_path), match)
                    ))
        
        # 檢查全大寫英文標籤（但不包括已在 t() 中的）
        if f"t('" not in line and f't("' not in line:
            upper_matches = re.findall(r">\s*([A-Z][A-Z\s]{2,}[A-Z])\s*<", line)
            for match in upper_matches:
                if not is_exception(match):
                    hardcoded.append(HardcodedText(
                        file=str(file_path),
                        line=i,
                        text=match.strip(),
                        context=line.strip()[:80],
                        suggested_key=suggest_i18n_key(str(file_path), match)
                    ))
    
    return hardcoded

def scan_directory(dir_path: Path) -> ScanResult:
    """掃描目錄中的所有 .tsx 文件"""
    result = ScanResult()
    
    if not dir_path.exists():
        print(f"[WARN] Directory not found: {dir_path}")
        return result
    
    tsx_files = list(dir_path.glob("**/*.tsx"))
    result.total_files = len(tsx_files)
    
    for file_path in tsx_files:
        hardcoded = scan_file(file_path)
        if hardcoded:
            result.files_with_issues += 1
            result.total_hardcoded += len(hardcoded)
            result.hardcoded_list.extend(hardcoded)
    
    return result

def generate_i18n_translations(hardcoded_list: List[HardcodedText]) -> Dict[str, Dict[str, str]]:
    """生成需要添加的 i18n 翻譯"""
    translations = {
        'zh-TW': {},
        'en': {},
        'ja': {},
    }
    
    for item in hardcoded_list:
        key = item.suggested_key
        text = item.text
        
        # 繁體中文（原文）
        translations['zh-TW'][key] = text
        
        # 英文（需要手動翻譯，這裡只是佔位）
        translations['en'][key] = f"[EN] {text}"
        
        # 日文（需要手動翻譯，這裡只是佔位）
        translations['ja'][key] = f"[JA] {text}"
    
    return translations

def generate_report(result: ScanResult) -> str:
    """生成掃描報告"""
    report = []
    report.append("=" * 60)
    report.append("HARDCODED TEXT SCAN REPORT")
    report.append("=" * 60)
    report.append(f"\n[STATS] Summary")
    report.append(f"   Total files scanned: {result.total_files}")
    report.append(f"   Files with issues: {result.files_with_issues}")
    report.append(f"   Total hardcoded texts: {result.total_hardcoded}")
    
    if result.hardcoded_list:
        report.append(f"\n[LIST] Detailed List")
        report.append("-" * 60)
        
        # 按文件分組
        by_file = {}
        for item in result.hardcoded_list:
            if item.file not in by_file:
                by_file[item.file] = []
            by_file[item.file].append(item)
        
        for file, items in by_file.items():
            filename = Path(file).name
            report.append(f"\n[FILE] {filename} ({len(items)} items)")
            for item in items:
                report.append(f"   Line {item.line}: \"{item.text}\"")
                report.append(f"      -> Suggested key: {item.suggested_key}")
    
    report.append("\n" + "=" * 60)
    return "\n".join(report)

def main():
    """主函數"""
    # 設置 UTF-8 編碼
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("[SCAN] Starting hardcoded text scan...")
    print()
    
    # 掃描 pages 目錄
    print("[DIR] Scanning pages directory...")
    pages_result = scan_directory(PAGES_PATH)
    
    # 掃描 components 目錄
    print("[DIR] Scanning components directory...")
    components_result = scan_directory(COMPONENTS_PATH)
    
    # 合併結果
    total_result = ScanResult(
        total_files=pages_result.total_files + components_result.total_files,
        files_with_issues=pages_result.files_with_issues + components_result.files_with_issues,
        total_hardcoded=pages_result.total_hardcoded + components_result.total_hardcoded,
        hardcoded_list=pages_result.hardcoded_list + components_result.hardcoded_list
    )
    
    # 生成報告
    report = generate_report(total_result)
    print(report)
    
    # 保存報告
    report_path = Path(__file__).parent / "hardcoded_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n[SAVE] Report saved to: {report_path}")
    
    # 生成建議的翻譯
    if total_result.hardcoded_list:
        translations = generate_i18n_translations(total_result.hardcoded_list)
        translations_path = Path(__file__).parent / "suggested_translations.json"
        with open(translations_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        print(f"[SAVE] Suggested translations saved to: {translations_path}")
    
    return total_result

if __name__ == "__main__":
    main()

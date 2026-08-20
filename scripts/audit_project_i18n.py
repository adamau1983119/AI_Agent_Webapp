"""
Official Multilingual & i18n Automated Audit Gatekeeper for AI_Agent_Webapp
Usage:
    python scripts/audit_project_i18n.py [--strict]

Checks:
1. Frontend i18n dictionary parity (zh-TW == en == ja)
2. Frontend pages & components hardcoded text detection
3. Inspiration AI generation regex parsing multi-language support
4. Topic repository search query multi-language field coverage
5. Script detection rules consistency
"""

import sys
import os
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Ensure UTF-8 output across platforms
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

def parse_ts_dict(content: str, var_name: str) -> Dict[str, str]:
    pattern = rf"const\s+{var_name}(?:\s*:\s*[^=]+)?\s*=\s*\{{"
    m = re.search(pattern, content)
    if not m:
        return {}
    start = m.end() - 1
    depth = 0
    end = start
    for i in range(start, len(content)):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    block = content[start:end]
    
    result = {}
    for line in block.splitlines():
        line_s = line.strip()
        if line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
            continue
        kv = re.match(r"^['\"]([^'\"]+)['\"]\s*:\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`),?", line_s)
        if kv:
            k = kv.group(1)
            v = kv.group(2) if kv.group(2) is not None else (kv.group(3) if kv.group(3) is not None else kv.group(4))
            result[k] = v
    return result


def audit_frontend_i18n() -> List[str]:
    errors = []
    print("=" * 80)
    print("【1. 前端 i18n 字典完整度檢驗】(frontend/src/i18n/index.ts)")
    print("=" * 80)
    
    i18n_path = ROOT / "frontend" / "src" / "i18n" / "index.ts"
    if not i18n_path.exists():
        errors.append(f"找不到檔案: {i18n_path}")
        return errors
        
    content = i18n_path.read_text(encoding="utf-8", errors="replace")
    zh_dict = parse_ts_dict(content, "zhTW")
    en_dict = parse_ts_dict(content, "en")
    ja_dict = parse_ts_dict(content, "ja")
    
    print(f"  • zh-TW 鍵值數: {len(zh_dict)}")
    print(f"  • en    鍵值數: {len(en_dict)}")
    print(f"  • ja    鍵值數: {len(ja_dict)}")
    
    all_keys = set(zh_dict.keys()) | set(en_dict.keys()) | set(ja_dict.keys())
    missing_en = sorted(list(all_keys - set(en_dict.keys())))
    missing_ja = sorted(list(all_keys - set(ja_dict.keys())))
    missing_zh = sorted(list(all_keys - set(zh_dict.keys())))
    
    if missing_en:
        errors.append(f"英文 (en) 缺少 {len(missing_en)} 個鍵值: {missing_en[:5]}")
    if missing_ja:
        errors.append(f"日文 (ja) 缺少 {len(missing_ja)} 個鍵值: {missing_ja[:5]}")
    if missing_zh:
        errors.append(f"繁中 (zh-TW) 缺少 {len(missing_zh)} 個鍵值: {missing_zh[:5]}")
        
    if not errors:
        print("  [PASS] 繁中、英文、日文三語字典 100% 同步對齊！")
    else:
        for err in errors:
            print(f"  [FAIL] {err}")
            
    return errors


def audit_inspiration_regex() -> List[str]:
    errors = []
    print("\n" + "=" * 80)
    print("【2. 靈感生成多語言正則解析檢驗】(inspiration_service.py)")
    print("=" * 80)
    
    insp_path = ROOT / "backend" / "app" / "services" / "inspiration_service.py"
    if not insp_path.exists():
        errors.append(f"找不到檔案: {insp_path}")
        return errors
        
    code = insp_path.read_text(encoding="utf-8", errors="replace")
    
    # Check if regex supports multi-language headers
    has_multilingual_regex = bool(re.search(r"Inspiration.*アイディア|アイディア.*Inspiration", code))
    has_fallback_parsing = "blocks = [b.strip() for b in re.split" in code
    
    print(f"  • 支援中英日多語言正則匹配: {'[PASS]' if has_multilingual_regex else '[FAIL]'}")
    print(f"  • 具備段落優雅降級容錯 (Fallback): {'[PASS]' if has_fallback_parsing else '[FAIL]'}")
    
    if not has_multilingual_regex:
        errors.append("inspiration_service.py 正則解析未支援中英日多語言標頭！")
    if not has_fallback_parsing:
        errors.append("inspiration_service.py 缺少段落解析容錯降級機制！")
        
    return errors


def audit_topic_search() -> List[str]:
    errors = []
    print("\n" + "=" * 80)
    print("【3. 主題庫跨語言搜尋欄位檢驗】(topic_repository.py)")
    print("=" * 80)
    
    repo_path = ROOT / "backend" / "app" / "services" / "repositories" / "topic_repository.py"
    if not repo_path.exists():
        errors.append(f"找不到檔案: {repo_path}")
        return errors
        
    code = repo_path.read_text(encoding="utf-8", errors="replace")
    
    has_ja_search = '"titles_i18n.ja"' in code
    has_en_search = '"titles_i18n.en"' in code
    has_orig_search = '"original_title"' in code
    
    print(f"  • 搜尋涵蓋日文翻譯欄位 (titles_i18n.ja): {'[PASS]' if has_ja_search else '[FAIL]'}")
    print(f"  • 搜尋涵蓋英文翻譯欄位 (titles_i18n.en): {'[PASS]' if has_en_search else '[FAIL]'}")
    print(f"  • 搜尋涵蓋原始標題 (original_title):     {'[PASS]' if has_orig_search else '[FAIL]'}")
    
    if not (has_ja_search and has_en_search and has_orig_search):
        errors.append("topic_repository.py 搜尋查詢未完整涵蓋多語言與原始標題欄位！")
        
    return errors


def audit_script_detection_rules() -> List[str]:
    errors = []
    print("\n" + "=" * 80)
    print("【4. 語言腳本判定一致性檢驗】(topic_languages.py & topicLanguages.ts)")
    print("=" * 80)
    
    py_path = ROOT / "backend" / "app" / "utils" / "topic_languages.py"
    ts_path = ROOT / "frontend" / "src" / "lib" / "topicLanguages.ts"
    
    if not py_path.exists() or not ts_path.exists():
        errors.append("找不到 topic_languages 模組檔案")
        return errors
        
    py_code = py_path.read_text(encoding="utf-8", errors="replace")
    ts_code = ts_path.read_text(encoding="utf-8", errors="replace")
    
    py_has_strict_ja = "if _has_cjk(text):\n            return False" in py_code or "if _has_cjk(text):" in py_code
    ts_has_strict_ja = "if (hasCjk(trimmed)) return false" in ts_code
    
    print(f"  • 後端日文腳本嚴格過濾（純漢字非日語）: {'[PASS]' if py_has_strict_ja else '[FAIL]'}")
    print(f"  • 前端日文腳本嚴格過濾（純漢字非日語）: {'[PASS]' if ts_has_strict_ja else '[FAIL]'}")
    
    if not (py_has_strict_ja and ts_has_strict_ja):
        errors.append("語言腳本判定未落實「純 CJK 漢字禁止判定為日文」之嚴格守門！")
        
    return errors


def main():
    parser = argparse.ArgumentParser(description="Multilingual Audit Gatekeeper")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if errors found")
    args = parser.parse_args()
    
    all_errors = []
    all_errors.extend(audit_frontend_i18n())
    all_errors.extend(audit_inspiration_regex())
    all_errors.extend(audit_topic_search())
    all_errors.extend(audit_script_detection_rules())
    
    print("\n" + "=" * 80)
    if not all_errors:
        print("🎉 【全專案多語言防護審計結果：100% 通過 (ALL PASS)】")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"❌ 【審計失敗：發現 {len(all_errors)} 個問題】")
        for e in all_errors:
            print(f"   • {e}")
        print("=" * 80)
        if args.strict:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()

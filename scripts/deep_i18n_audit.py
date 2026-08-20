"""
Deep i18n & Multilingual Audit Script for AI_Agent_Webapp
Analyzes:
1. Frontend i18n Dictionary Integrity (zh-TW, en, ja)
2. Generation Modules (API + Prompts + Services)
3. Search Modules (Multilingual search capabilities across models & DB)
4. Display & Detail Endpoints (Overlay coverage)
5. Frontend Hardcoded Strings in Pages & Components
"""

import os
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def audit_i18n_dictionary():
    print("=" * 80)
    print("【1. 前端 i18n 翻譯字典完整度審計】 (frontend/src/i18n/index.ts)")
    print("=" * 80)
    
    i18n_path = ROOT / "frontend" / "src" / "i18n" / "index.ts"
    content = i18n_path.read_text(encoding="utf-8", errors="replace")
    
    # Extract keys and values from zhTW, en, ja object blocks
    def extract_dict(var_name: str) -> dict:
        pattern = rf"const\s+{var_name}\s*=\s*\{{"
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
        # Match 'key': 'value' or 'key': "value" or 'key': `value`
        for line in block.splitlines():
            line_s = line.strip()
            kv = re.match(r"^['\"]([^'\"]+)['\"]\s*:\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`),?", line_s)
            if kv:
                key = kv.group(1)
                val = kv.group(2) if kv.group(2) is not None else (kv.group(3) if kv.group(3) is not None else kv.group(4))
                result[key] = val
        return result

    zhtw_dict = extract_dict("zhTW")
    en_dict = extract_dict("en")
    ja_dict = extract_dict("ja")
    
    print(f"zh-TW 鍵值總數: {len(zhtw_dict)}")
    print(f"en    鍵值總數: {len(en_dict)}")
    print(f"ja    鍵值總數: {len(ja_dict)}")
    
    all_keys = set(zhtw_dict.keys()) | set(en_dict.keys()) | set(ja_dict.keys())
    
    missing_in_en = set(zhtw_dict.keys()) - set(en_dict.keys())
    missing_in_ja = set(zhtw_dict.keys()) - set(ja_dict.keys())
    missing_in_zh = all_keys - set(zhtw_dict.keys())
    
    print(f"\n[缺漏鍵值統計]:")
    print(f"  - 英文 (en) 缺少鍵值: {len(missing_in_en)} 個")
    if missing_in_en:
        for k in sorted(list(missing_in_en))[:10]:
            print(f"    * 缺: {k} (zh-TW: {zhtw_dict.get(k)})")
            
    print(f"  - 日文 (ja) 缺少鍵值: {len(missing_in_ja)} 個")
    if missing_in_ja:
        for k in sorted(list(missing_in_ja))[:10]:
            print(f"    * 缺: {k} (zh-TW: {zhtw_dict.get(k)})")

    # Check for Chinese remnants in en dictionary
    def has_cjk(s: str) -> bool:
        return bool(re.search(r"[\u4e00-\u9fff]", s))
    def has_kana(s: str) -> bool:
        return bool(re.search(r"[\u3040-\u309f\u30a0-\u30ff]", s))

    en_with_chinese = {k: v for k, v in en_dict.items() if has_cjk(v)}
    print(f"\n[英文字典中未翻譯（含中文字符）的鍵值]: {len(en_with_chinese)} 個")
    for k, v in list(en_with_chinese.items())[:10]:
        print(f"  * {k} -> \"{v}\"")

    # Check for Japanese entries that are purely Chinese (no Kana)
    ja_pure_cjk = {k: v for k, v in ja_dict.items() if has_cjk(v) and not has_kana(v) and len(v) > 2}
    print(f"\n[日文字典中疑似未翻譯（全漢字且無日語假名）的鍵值]: {len(ja_pure_cjk)} 個")
    for k, v in list(ja_pure_cjk.items())[:15]:
        print(f"  * {k} -> \"{v}\" (繁中: {zhtw_dict.get(k)})")


def audit_generation_modules():
    print("\n" + "=" * 80)
    print("【2. 生成模組審計 (重點：生成 Generation)】")
    print("=" * 80)
    
    # Check all prompt files
    prompt_dir = ROOT / "backend" / "app" / "prompts"
    print("\n--- A. AI Prompt 提示詞語系支援分析 ---")
    for p in prompt_dir.glob("*.py"):
        code = p.read_text(encoding="utf-8", errors="replace")
        print(f"\n[Prompt 檔案: {p.name}]")
        
        # Check if prompt mandates a specific language or allows language parameter
        has_lang_placeholder = bool(re.search(r"\{(?:language|lang|target_lang|target_language)\}", code, re.IGNORECASE))
        has_hardcoded_zh = bool(re.search(r"(?:繁體中文|使用繁體中文|輸出為繁體中文|請使用繁體中文)", code))
        has_multilingual_rules = bool(re.search(r"(?:日文|English|Japanese|目標語言|根據語言|用戶語言)", code))
        
        print(f"  * 是否包含動態語言佔位符 ({{language}} / {{target_lang}}): {'✅ 是' if has_lang_placeholder else '❌ 否 (未動態注入語系)'}")
        print(f"  * 是否包含硬編碼繁體中文規則: {'⚠️ 是 (可能強制生成繁中)' if has_hardcoded_zh else '否'}")
        print(f"  * 是否有多語系規則說明: {'✅ 是' if has_multilingual_rules else '否'}")

        # Extract prompt constants
        prompt_vars = re.findall(r"([A-Z0-9_]+_PROMPT)\s*=\s*['\"`]{1,3}(.*?)['\"`]{1,3}", code, re.DOTALL)
        for var_name, prompt_text in prompt_vars[:3]:
            print(f"    - Prompt 變數 `{var_name}` (長度 {len(prompt_text)} 字符)")
            # Check prompt excerpt
            first_lines = "\n".join([l.strip() for l in prompt_text.splitlines() if l.strip()][:3])
            print(f"      摘要: {first_lines[:150]}...")

    # Check generation service files
    print("\n--- B. 後端生成服務 (Services) 語言參數支援分析 ---")
    gen_service_files = [
        "backend/app/api/v1/contents.py",
        "backend/app/api/v1/generate.py",
        "backend/app/services/alter_ego_service.py",
        "backend/app/services/inspiration_service.py",
        "backend/app/services/inspiration_conversation_service.py",
        "backend/app/services/channel_assist_service.py",
        "backend/app/services/content_style_service.py",
        "backend/app/services/automation/workflow.py",
        "backend/app/services/automation/topic_collector.py",
        "backend/app/services/summarization/summary_flash_service.py",
    ]
    
    for rel in gen_service_files:
        fpath = ROOT / rel
        if not fpath.exists():
            print(f"\n[服務: {rel}] -> 檔案不存在")
            continue
        code = fpath.read_text(encoding="utf-8", errors="replace")
        print(f"\n[服務: {rel}]")
        
        # Check endpoint/function definitions
        endpoints = re.findall(r"@(router\.(?:get|post|put|delete))\s*\(['\"]([^'\"]+)['\"].*?\)\s*async\s+def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", code, re.DOTALL)
        if endpoints:
            for method, route, func_name, params in endpoints:
                params_clean = " ".join(params.split())
                has_lang = any(k in params_clean.lower() for k in ["lang", "language", "locale"])
                print(f"  - API Endpoint: {route} (`{func_name}`)")
                print(f"    * 接收語言參數: {'✅ 是' if has_lang else '❌ 否 (前端無法傳入指定語系)'}")
                print(f"    * 參數簽名: {params_clean[:120]}...")
        else:
            # Check key methods
            methods = re.findall(r"async\s+def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", code, re.DOTALL)
            for mname, mparams in methods[:4]:
                params_clean = " ".join(mparams.split())
                has_lang = any(k in params_clean.lower() for k in ["lang", "language", "locale", "target"])
                print(f"  - 方法 `{mname}`:")
                print(f"    * 語言參數: {'✅ 有' if has_lang else '❌ 無'}")


def audit_search_modules():
    print("\n" + "=" * 80)
    print("【3. 搜尋模組審計 (搜尋 Search)】")
    print("=" * 80)
    
    search_files = [
        ("主題搜尋 (Topics API)", "backend/app/api/v1/topics.py"),
        ("靈感搜尋 (Inspiration API)", "backend/app/api/v1/inspiration.py"),
        ("探索搜尋 (Discover / Public Feed)", "backend/app/api/v1/discover.py"),
        ("搜尋服務層 (Search Service)", "backend/app/services/search_service.py"),
        ("ElasticSearch 服務", "backend/app/services/elasticsearch_service.py"),
        ("前端主題搜尋 (Topics.tsx)", "frontend/src/pages/Topics.tsx"),
        ("前端靈感搜尋 (Inspiration.tsx)", "frontend/src/pages/Inspiration.tsx"),
        ("前端探索搜尋 (Discover.tsx)", "frontend/src/pages/Discover.tsx"),
    ]
    
    for title, rel in search_files:
        fpath = ROOT / rel
        if not fpath.exists():
            print(f"\n[{title}] -> {rel} (不存在)")
            continue
        code = fpath.read_text(encoding="utf-8", errors="replace")
        print(f"\n[{title}] -> {rel}")
        
        # Check if search queries multi-language fields
        queries_i18n = "titles_i18n" in code or "description_i18n" in code or "title_i18n" in code
        translates_query = "translate" in code and "query" in code
        has_keyword = "keyword" in code or "query" in code or "search" in code
        
        print(f"  * 包含關鍵字搜尋邏輯: {'✅ 是' if has_keyword else '否'}")
        print(f"  * 搜尋時跨多語系欄位 (titles_i18n / description_i18n): {'✅ 是' if queries_i18n else '⚠️ 否 (僅搜尋單一 title/content 欄位，跨語系搜尋會失效)'}")
        print(f"  * 搜尋時自動翻譯搜尋詞: {'✅ 是' if translates_query else '否 (直接以原詞查詢)'}")


def audit_display_and_detail_modules():
    print("\n" + "=" * 80)
    print("【4. 顯示與詳情模組審計 (顯示 Display)】")
    print("=" * 80)
    
    display_targets = [
        ("主題卡片 (TopicCard.tsx)", "frontend/src/components/ui/TopicCard.tsx"),
        ("主題詳情頁 (TopicDetail.tsx)", "frontend/src/pages/TopicDetail.tsx"),
        ("靈感頁面 (Inspiration.tsx)", "frontend/src/pages/Inspiration.tsx"),
        ("探索公開流卡片 (PublicFeedCard.tsx)", "frontend/src/components/discover/PublicFeedCard.tsx"),
        ("我的頻道 (MyChannel.tsx)", "frontend/src/pages/MyChannel.tsx"),
        ("PostKit 貼文面板 (PostKitPanel.tsx)", "frontend/src/components/features/PostKitPanel.tsx"),
        ("風格檔案 (StyleProfile.tsx)", "frontend/src/pages/StyleProfile.tsx"),
    ]
    
    for title, rel in display_targets:
        fpath = ROOT / rel
        if not fpath.exists():
            print(f"\n[{title}] -> {rel} (不存在)")
            continue
        code = fpath.read_text(encoding="utf-8", errors="replace")
        print(f"\n[{title}] -> {rel}")
        
        uses_i18n = "useTranslation" in code or "t(" in code or "i18n" in code
        uses_topic_display = "resolveTopicDisplayCopy" in code or "hasCompleteDisplayPack" in code or "usableCachedTitle" in code
        has_translate_button = "TopicTranslateDisplayButton" in code or "translateDisplay" in code or "translate" in code
        
        print(f"  * 使用 UI i18n 多語言: {'✅ 是' if uses_i18n else '❌ 否'}")
        print(f"  * 使用主題動態多語覆蓋解析 (topicDisplay): {'✅ 是' if uses_topic_display else '❌ 否 (直接顯示原生 title/description)'}")
        print(f"  * 具備翻譯轉換/重試觸發: {'✅ 是' if has_translate_button else '❌ 否'}")


def audit_frontend_hardcoded_text():
    print("\n" + "=" * 80)
    print("【5. 前端頁面與組件硬編碼字串掃描】")
    print("=" * 80)
    
    frontend_src = ROOT / "frontend" / "src"
    ts_files = list(frontend_src.glob("**/*.tsx")) + list(frontend_src.glob("**/*.ts"))
    ts_files = [f for f in ts_files if "i18n" not in f.parts and "test" not in f.name and ".d.ts" not in f.name]
    
    results = []
    
    for f in ts_files:
        rel = f.relative_to(ROOT)
        code = f.read_text(encoding="utf-8", errors="replace")
        
        # Find raw Chinese characters in JSX or string literals
        lines = code.splitlines()
        file_findings = []
        for idx, line in enumerate(lines, 1):
            line_str = line.strip()
            # Ignore comments
            if line_str.startswith("//") or line_str.startswith("/*") or line_str.startswith("*"):
                continue
            # Look for Chinese text outside t('...')
            chinese_matches = re.findall(r"[\u4e00-\u9fff]+", line_str)
            if chinese_matches:
                # Check if it's inside t('...') or test comment
                # If the whole line is like `t('something')` or contains `data-testid`
                if "t('" in line_str or 't("' in line_str or 't(`' in line_str:
                    # Check if Chinese is only inside fallback or comment
                    continue
                file_findings.append((idx, line_str))
                
        if file_findings:
            results.append((str(rel), len(file_findings), file_findings))

    print(f"總共有 {len(results)} 個前端檔案發現硬編碼中文字串（未透過 i18n 翻譯）:")
    for rel_path, count, findings in results:
        print(f"\n  📄 {rel_path} ({count} 處硬編碼中文字串):")
        for line_num, line_code in findings[:5]:
            print(f"    Line {line_num:4d}: {line_code[:100]}")
        if count > 5:
            print(f"    ... 以及其餘 {count - 5} 處")


if __name__ == "__main__":
    audit_i18n_dictionary()
    audit_generation_modules()
    audit_search_modules()
    audit_display_and_detail_modules()
    audit_frontend_hardcoded_text()
    print("\n" + "=" * 80)
    print("【全專案多語言審計完成】")
    print("=" * 80)

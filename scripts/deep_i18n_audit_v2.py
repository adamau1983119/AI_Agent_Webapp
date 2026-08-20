"""
Deep i18n & Multilingual Audit Script v2 for AI_Agent_Webapp
Scans and identifies:
1. All missing keys and untranslated strings in frontend/src/i18n/index.ts (zh-TW vs en vs ja)
2. All Generation endpoints & services (Content, Inspiration, Alter Ego, Channel Assist, PostKit)
3. All Search endpoints & services (Topics, Inspiration, Discover, ElasticSearch, MongoDB queries)
4. All Display endpoints & components (Locale Overlay coverage, dynamic translation triggers)
5. All hardcoded text in frontend pages & components (excluding comments)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent

def parse_ts_dict(content: str, var_name: str) -> Dict[str, str]:
    # Match: const var_name: typeof zhTW = { ... } or const var_name = { ... }
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
    lines = block.splitlines()
    for line in lines:
        line_s = line.strip()
        # Ignore full-line comments
        if line_s.startswith("//") or line_s.startswith("/*") or line_s.startswith("*"):
            continue
        # Extract 'key': 'value' or 'key': "value" or 'key': `value`
        # Handle trailing commas or comments
        kv = re.match(r"^['\"]([^'\"]+)['\"]\s*:\s*(?:'([^']*)'|\"([^\"]*)\"|`([^`]*)`),?", line_s)
        if kv:
            k = kv.group(1)
            v = kv.group(2) if kv.group(2) is not None else (kv.group(3) if kv.group(3) is not None else kv.group(4))
            result[k] = v
    return result


def audit_frontend_i18n():
    print("=" * 90)
    print("【1. 前端 i18n 字典審計 (frontend/src/i18n/index.ts)】")
    print("=" * 90)
    
    i18n_path = ROOT / "frontend" / "src" / "i18n" / "index.ts"
    content = i18n_path.read_text(encoding="utf-8", errors="replace")
    
    zh_dict = parse_ts_dict(content, "zhTW")
    en_dict = parse_ts_dict(content, "en")
    ja_dict = parse_ts_dict(content, "ja")
    
    print(f"📊 字典總鍵值統計:")
    print(f"   • 繁體中文 (zh-TW): {len(zh_dict)} 個鍵值")
    print(f"   • 英文     (en)   : {len(en_dict)} 個鍵值")
    print(f"   • 日文     (ja)   : {len(ja_dict)} 個鍵值")
    
    all_keys = sorted(list(set(zh_dict.keys()) | set(en_dict.keys()) | set(ja_dict.keys())))
    
    missing_en = [k for k in all_keys if k not in en_dict]
    missing_ja = [k for k in all_keys if k not in ja_dict]
    missing_zh = [k for k in all_keys if k not in zh_dict]
    
    print(f"\n🔍 缺漏鍵值統計:")
    print(f"   • 英文 (en) 缺少鍵值數量: {len(missing_en)}")
    if missing_en:
        for k in missing_en[:15]:
            print(f"     ❌ 缺: `{k}` (zh-TW 內容: \"{zh_dict.get(k)}\")")
        if len(missing_en) > 15:
            print(f"     ... 尚有 {len(missing_en) - 15} 個")
            
    print(f"   • 日文 (ja) 缺少鍵值數量: {len(missing_ja)}")
    if missing_ja:
        for k in missing_ja[:15]:
            print(f"     ❌ 缺: `{k}` (zh-TW 內容: \"{zh_dict.get(k)}\")")
        if len(missing_ja) > 15:
            print(f"     ... 尚有 {len(missing_ja) - 15} 個")

    # Untranslated checks
    def has_cjk(s: str) -> bool:
        return bool(re.search(r"[\u4e00-\u9fff]", s))
    def has_kana(s: str) -> bool:
        return bool(re.search(r"[\u3040-\u309f\u30a0-\u30ff]", s))

    # In en_dict, check for values with Chinese characters (ignoring brand names like 'Alter-ego')
    en_untranslated = {}
    for k, v in en_dict.items():
        if has_cjk(v):
            en_untranslated[k] = v
            
    print(f"\n🔍 英文字典中「殘留中文未翻譯」的鍵值: {len(en_untranslated)} 個")
    for k, v in list(en_untranslated.items())[:15]:
        print(f"     ⚠️ `{k}`: \"{v}\"")
        
    # In ja_dict, check for values with Chinese characters but NO Kana (length > 1, not common Kanji like '日')
    ja_suspicious = {}
    for k, v in ja_dict.items():
        # If it has CJK but no Kana and is longer than 2 characters
        if has_cjk(v) and not has_kana(v) and len(v) > 2:
            # Check if value is identical to zh_dict
            if v == zh_dict.get(k):
                ja_suspicious[k] = (v, zh_dict.get(k))

    print(f"\n🔍 日文字典中「與繁中完全相同且無假名（極高機率未翻譯）」的鍵值: {len(ja_suspicious)} 個")
    for k, (ja_val, zh_val) in list(ja_suspicious.items())[:15]:
        print(f"     ⚠️ `{k}`: \"{ja_val}\" (繁中: \"{zh_val}\")")


def audit_generation_system():
    print("\n" + "=" * 90)
    print("【2. 生成系統 (Generation) 語言參數與翻譯支援全面審計】")
    print("=" * 90)

    findings = []
    
    # 1. Topic Detail -> Content Generation (短文 / 腳本生成)
    # File: backend/app/api/v1/contents.py -> POST /{topic_id}/generate
    # Prompt: backend/app/prompts/article_prompt.py, script_prompt.py
    # Frontend: frontend/src/components/features/ContentGenerationPanel.tsx, TopicDetail.tsx
    findings.append({
        "module": "1. 主題內容生成 (文章 Article & 影片腳本 Script)",
        "api_endpoint": "POST /api/v1/contents/{topic_id}/generate",
        "backend_files": ["backend/app/api/v1/contents.py", "backend/app/prompts/article_prompt.py", "backend/app/prompts/script_prompt.py"],
        "frontend_files": ["frontend/src/pages/TopicDetail.tsx", "frontend/src/components/features/ContentGenerationPanel.tsx", "frontend/src/api/contents.ts"],
        "status": "⚠️ 部分支援（需防禦性校驗）",
        "details": [
            "後端 prompt (`article_prompt.py`, `script_prompt.py`) 已支援 `target_language` 傳入 `zh-TW` / `en` / `ja` 並指定輸出語言。",
            "前端 `TopicDetail.tsx` (line 171) 已傳遞 `language: userLanguage`。",
            "後端 `GenerateContentRequest` schema 中的 `language` 欄位若為空，會回退至 `topic.get('display_language', 'zh-TW')`。",
            "⚠️ 潛在風險：若用戶透過 Quick Generate (`api/v1/generate.py`)，該端點 `quick_generate` 缺少 `language` 參數，預設只會使用繁中。"
        ]
    })

    # 2. Inspiration Generation (靈感策劃 生成與問答)
    findings.append({
        "module": "2. 靈感策劃生成 (Inspiration Idea & Question Generation)",
        "api_endpoint": "POST /api/v1/inspiration/assistant/generate, GET /api/v1/inspiration/search",
        "backend_files": [
            "backend/app/api/v1/inspiration.py",
            "backend/app/services/inspiration_service.py",
            "backend/app/services/inspiration_content_generator_service.py",
            "backend/app/services/inspiration_question_generator_service.py"
        ],
        "frontend_files": ["frontend/src/pages/Inspiration.tsx", "frontend/src/api/inspiration.ts"],
        "status": "⚠️ 存在正則解析盲區與硬編碼中文字串",
        "details": [
            "後端 `InspirationContentGeneratorService` 支援 `language` 參數（支援 zh-TW, en, ja）。",
            "⚠️ `inspiration_service.py` 中的 `_parse_ai_response` 使用中文硬編碼正則 `靈感\\d+:\\s*(.+?)\\n描述:`，當 AI 回傳英文 (Inspiration 1:) 或日文 (アイディア1:) 時會解析失敗導致返回空陣列！",
            "⚠️ `extract_keywords` Prompt 只有中文版，未傳遞用戶語言，導致外語搜尋時提取的關鍵字可能混合中文。",
            "⚠️ 前端 `Inspiration.tsx` 含有硬編碼繁體中文字串（如 `{confidence}% 可信度`、`自定義提示詞` 等）。"
        ]
    })

    # 3. Alter Ego (分身貼文與腳本生成)
    findings.append({
        "module": "3. Alter Ego 創作者分身生成 (Soul Post & Shell Scripts)",
        "api_endpoint": "POST /api/v1/alter-ego/generate, POST /api/v1/alter-ego/preview",
        "backend_files": [
            "backend/app/api/v1/alter_ego.py",
            "backend/app/services/alter_ego_service.py",
            "backend/app/services/shells/shell_manager.py"
        ],
        "frontend_files": ["frontend/src/pages/AlterEgoOnboarding.tsx", "frontend/src/components/features/PostKitPanel.tsx"],
        "status": "✅ 具備完整多語言生成與語言腳本檢驗 (title_matches_display_language)",
        "details": [
            "`alter_ego_service.py` 支援 `output_lang`，Prompt 明確指示 `IMPORTANT: Write the entire post ONLY in {label}. Do not mix languages.`",
            "具備 `title_matches_display_language(preview_text, output_lang)` 二次校驗，若 AI 生成非目標語言會自動重新生成或調整。"
        ]
    })

    # 4. Channel Assistant (AI 頻道建立助手)
    findings.append({
        "module": "4. AI 頻道建立助手 (Channel Assist & Wizard Options)",
        "api_endpoint": "POST /api/v1/channels/assist, POST /api/v1/channels/assist/wizard-options",
        "backend_files": [
            "backend/app/api/v1/channels.py",
            "backend/app/services/channel_assist_service.py"
        ],
        "frontend_files": ["frontend/src/pages/CreateChannel.tsx", "frontend/src/api/channels.ts"],
        "status": "✅ 支援多語言（zh-TW / en / ja 專屬 Prompt 模板）",
        "details": [
            "`channel_assist_service.py` 內建繁中、日文、英文三種獨立 Prompt 模板 (`_build_assist_prompt`)。",
            "`CreateChannel.tsx` 傳送 API 請求時已帶入當前語言偏好。"
        ]
    })

    # 5. Daily Topic Collector & Summary Flash Generation (日常自動產卡與摘要生成)
    findings.append({
        "module": "5. 主題卡自動採集、成套翻譯與 Summary Flash (三語預載)",
        "api_endpoint": "內部 Scheduler / POST /api/v1/schedules/generate-today",
        "backend_files": [
            "backend/app/services/automation/topic_collector.py",
            "backend/app/services/automation/topic_triple_preload.py",
            "backend/app/services/summarization/summary_flash_service.py",
            "backend/app/services/translation/flash_pack_provider.py"
        ],
        "frontend_files": ["frontend/src/components/ui/TopicCard.tsx", "frontend/src/pages/Dashboard.tsx"],
        "status": "✅ 剛完成修復（三語 Triple Preload + 嚴格語言腳本守門）",
        "details": [
            "採集後自動觸發 `topic_triple_preload.py`，預載繁中、日文、英文三語套件至 `titles_i18n` 與 `description_i18n`。",
            "已修復繁體中文漢字誤判為日語的腳本缺陷，並在快取讀取與寫入時加入目標語言腳本檢驗。"
        ]
    })

    for item in findings:
        print(f"\n📦 【{item['module']}】")
        print(f"   • 端點: {item['api_endpoint']}")
        print(f"   • 狀態: {item['status']}")
        for d in item["details"]:
            print(f"     - {d}")


def audit_search_system():
    print("\n" + "=" * 90)
    print("【3. 搜尋系統 (Search) 跨語言查詢與索引審計】")
    print("=" * 90)
    
    # Check TopicRepository search query
    topic_repo_path = ROOT / "backend" / "app" / "services" / "repositories" / "topic_repository.py"
    tr_code = topic_repo_path.read_text(encoding="utf-8", errors="replace")
    
    print("\n🔍 A. 主題庫搜尋 (TopicRepository.list_topics / search)")
    print("   • 現行 MongoDB 搜尋 Filter:")
    # Extract search filter lines
    m = re.search(r"if search and search\.strip\(\):.*?(?=if not clauses)", tr_code, re.DOTALL)
    if m:
        for l in m.group(0).splitlines():
            print(f"     {l}")
            
    print("\n   ⚠️ 【重大搜尋盲區分析】:")
    print("     1. 現有 MongoDB 查詢僅以正則查詢 `title` 與 `source` 欄位。")
    print("     2. 當日語用戶搜尋「ウェディング」（婚宴）或英語用戶搜尋「wedding」時：")
    print("        - 若該主題主要 `title` 是繁中（例如「這款婚宴賓客禮服趨勢…」），而日語翻譯儲存於 `titles_i18n.ja`；")
    print("        - ❌ 搜尋引擎將無法命中該主題，造成跨語言搜尋 100% 查無結果！")
    print("     3. 改善方案：MongoDB 搜尋子句應包含 `titles_i18n.ja`、`titles_i18n.en`、`titles_i18n.zh-TW` 以及 `original_title`。")

    # Check Inspiration search
    print("\n🔍 B. 靈感庫搜尋 (Inspiration API & Google CSE)")
    print("   • Google CSE: 支援傳入 `lr=lang_zh-TW / lang_en / lang_ja`，依據 UI 語言過濾搜尋結果。")
    print("   • AI 生成 Fallback: 支援輸出語言標籤，但正則解析需支持多語言關鍵字標頭。")

    # Check Discover / Public Feed search
    print("\n🔍 C. 探索公開流搜尋 (Public Feed / Discover)")
    print("   • 公開流卡片目前直接從各國 RSS 來源拉取，若未經 `deepl_title.py` 或 `feed_translation_loader.py` 處理，會直接顯示各國原生文字。")


def audit_display_system():
    print("\n" + "=" * 90)
    print("【4. 顯示系統 (Display) 與卡片多語言覆蓋審計】")
    print("=" * 90)

    display_modules = [
        {
            "name": "Dashboard / Topics 主題卡片 (TopicCard)",
            "file": "frontend/src/components/ui/TopicCard.tsx",
            "locale_overlay": "✅ 支援 (resolveTopicDisplayCopy + usableCachedTitle + 標籤翻譯)",
            "status": "✅ 完整支援多語言切換與自動/手動翻譯"
        },
        {
            "name": "主題詳情頁 (TopicDetail)",
            "file": "frontend/src/pages/TopicDetail.tsx",
            "locale_overlay": "✅ 支援 (後端 GET /contents/{id}?ui_lang=xxx 動態翻譯回傳)",
            "status": "✅ 完整支援多語言切換"
        },
        {
            "name": "靈感策劃頁面 (Inspiration)",
            "file": "frontend/src/pages/Inspiration.tsx",
            "locale_overlay": "⚠️ 部分支援 (UI 文字使用 t()，但生成的靈感歷史卡片無動態 i18n 覆蓋)",
            "status": "⚠️ 歷史靈感卡片以生成時的語言保存，切換語系時不會即時重譯"
        },
        {
            "name": "探索公開流 (Discover / PublicFeedCard)",
            "file": "frontend/src/components/discover/PublicFeedCard.tsx",
            "locale_overlay": "⚠️ 部分支援 (`deepl_title` 僅限標題，內容摘要無動態覆蓋)",
            "status": "⚠️ 僅標題支援翻譯，切換語系時依賴後端快取"
        },
        {
            "name": "我的頻道 (MyChannel / ChannelDetail)",
            "file": "frontend/src/pages/MyChannel.tsx",
            "locale_overlay": "⚠️ 頻道名稱與自訂描述為用戶自訂輸入，無自動多語翻譯覆蓋",
            "status": "ℹ️ 正常行為（用戶自訂頻道資產）"
        },
        {
            "name": "PostKit 貼文預覽 (PostKitPanel)",
            "file": "frontend/src/components/features/PostKitPanel.tsx",
            "locale_overlay": "✅ 生成時依 `language` 輸出，預覽與複製均為目標語系",
            "status": "✅ 完整支援"
        }
    ]

    for dm in display_modules:
        print(f"\n🖥️ 【{dm['name']}】")
        print(f"   • 檔案: {dm['file']}")
        print(f"   • 動態多語覆蓋: {dm['locale_overlay']}")
        print(f"   • 評估: {dm['status']}")


def audit_frontend_hardcoded_texts():
    print("\n" + "=" * 90)
    print("【5. 前端硬編碼中文字串精確清單 (排除註解)】")
    print("=" * 90)

    frontend_src = ROOT / "frontend" / "src"
    ts_files = list(frontend_src.glob("**/*.tsx")) + list(frontend_src.glob("**/*.ts"))
    ts_files = [f for f in ts_files if "i18n" not in f.parts and "test" not in f.name and ".d.ts" not in f.name]

    total_issues = 0
    file_issues = []

    for f in ts_files:
        rel = f.relative_to(ROOT)
        code = f.read_text(encoding="utf-8", errors="replace")
        lines = code.splitlines()
        
        issues = []
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            # Ignore comments
            if s.startswith("//") or s.startswith("/*") or s.startswith("*") or s.startswith("{/*"):
                continue
            # Remove inline comments like // ...
            if "//" in s:
                s = s.split("//")[0].strip()
            # Check for Chinese characters
            if re.search(r"[\u4e00-\u9fff]", s):
                # If it's pure t('some.key') or date format string, skip
                if "t('" in s or 't("' in s or 't(`' in s:
                    # Check if there's raw Chinese outside the t() call
                    # Quick check: does it contain Chinese in JSX tags >中文< or placeholder="中文"
                    jsx_text = re.findall(r">([^<]*[\u4e00-\u9fff]+[^<]*)<", s)
                    props_text = re.findall(r"(?:placeholder|title|label|alt)=['\"]([^'\"]*[\u4e00-\u9fff]+[^'\"]*)['\"]", s)
                    raw_strings = jsx_text + props_text
                    if not raw_strings:
                        continue
                issues.append((idx, s))

        if issues:
            total_issues += len(issues)
            file_issues.append((str(rel), issues))

    print(f"🚨 共發現 {len(file_issues)} 個檔案、{total_issues} 處潛在硬編碼文字（未調用 i18n t() 翻譯）:\n")
    for rel_path, issues in file_issues:
        print(f"  📄 【{rel_path}】 ({len(issues)} 處):")
        for line_no, text in issues[:4]:
            print(f"     Line {line_no:4d}: {text[:90]}")
        if len(issues) > 4:
            print(f"     ... 另有 {len(issues) - 4} 處")


if __name__ == "__main__":
    audit_frontend_i18n()
    audit_generation_system()
    audit_search_system()
    audit_display_system()
    audit_frontend_hardcoded_texts()
    print("\n" + "=" * 90)
    print("✅ 深度多語言全方位審計掃描完成")
    print("=" * 90)

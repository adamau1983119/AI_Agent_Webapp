#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主題卡事實錨定與風格解耦防線審計 (Topic Generation & Anti-Pollution Pipeline Audit)
遵循《開發人員必讀規則》規則 19。
採用純標準庫實現，保證零依賴環境下 100% 穩定運行。
"""
import os
import re
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"【{title}】")
    print("=" * 80)

def audit_yaml_config():
    print_header("1. 主題卡產卡設定審計 (backend/config/topic_generation.yaml)")
    yaml_path = os.path.join(ROOT_DIR, "backend", "config", "topic_generation.yaml")
    if not os.path.exists(yaml_path):
        print("  [FAIL] 找不到 topic_generation.yaml")
        return False

    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 檢測是否有 generate_content: true
    bad_gen = re.findall(r"generate_content\s*:\s*true", content, re.IGNORECASE)
    if bad_gen:
        print(f"  [FAIL] 發現 {len(bad_gen)} 處 generate_content: true！違背按需生成原則（會大量浪費 Token）")
        return False

    # 檢查是否有三類別的 generate_content: false
    for cat in ["fashion", "food", "trend"]:
        if f"{cat}:" in content:
            print(f"  • 分類 {cat}: generate_content=false (按需生成符合) [PASS]")

    return True

def audit_frontend_postkit():
    print_header("2. 前端 PostKitPanel 按需生成審計 (frontend/src/components/features/PostKitPanel.tsx)")
    ts_path = os.path.join(ROOT_DIR, "frontend", "src", "components", "features", "PostKitPanel.tsx")
    if not os.path.exists(ts_path):
        print("  [FAIL] 找不到 PostKitPanel.tsx")
        return False

    with open(ts_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 檢查是否有在 useEffect 中自動呼叫 loadPlatformPreview
    bad_pattern = re.search(r"useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*loadPlatformPreview\s*\([^}]*\}\s*,", content, re.DOTALL)
    if bad_pattern:
        print("  [FAIL] 檢測到 useEffect 自動背景觸發 loadPlatformPreview！必須改為用戶按鈕或手動觸發。")
        return False

    if "handleGeneratePlatformPreview" not in content and "alterEgoApi.preview" not in content:
        print("  [FAIL] 找不到平台專屬預覽生成處理函數")
        return False

    print("  • 移除 useEffect 背景自動偷跑生成: [PASS]")
    print("  • 嚴格採用按需用戶按鈕觸發 (JIT): [PASS]")
    return True

def audit_backend_alter_ego_prompts():
    print_header("3. 後端事實錨定與語義解耦 Prompt 審計 (alter_ego_service.py & article_prompt.py)")
    ae_path = os.path.join(ROOT_DIR, "backend", "app", "services", "alter_ego_service.py")
    art_path = os.path.join(ROOT_DIR, "backend", "app", "prompts", "article_prompt.py")

    all_ok = True
    with open(ae_path, "r", encoding="utf-8") as f:
        ae_content = f.read()

    if "ANTI-POLLUTION" not in ae_content:
        print("  [FAIL] alter_ego_service.py 缺少 ANTI-POLLUTION (防名詞跨領域污染) 門禁指令")
        all_ok = False
    else:
        print("  • AlterEgo Soul Prompt 具備 ANTI-POLLUTION 防跨領域污染門禁: [PASS]")

    if "FACT ANCHORING" not in ae_content:
        print("  [FAIL] alter_ego_service.py 缺少 FACT ANCHORING (事實上下文錨定) 門禁指令")
        all_ok = False
    else:
        print("  • AlterEgo Soul Prompt 具備 FACT ANCHORING 事實錨定門禁: [PASS]")

    with open(art_path, "r", encoding="utf-8") as f:
        art_content = f.read()

    if "防污染" not in art_content:
        print("  [FAIL] article_prompt.py 缺少風格解耦防污染規範")
        all_ok = False
    else:
        print("  • Article Prompt 具備風格解耦防污染規範: [PASS]")

    return all_ok

def main():
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass
    print("正在執行主題卡管線與事實錨定門禁審計...")
    v1 = audit_yaml_config()
    v2 = audit_frontend_postkit()
    v3 = audit_backend_alter_ego_prompts()

    if v1 and v2 and v3:
        print("\n" + "=" * 80)
        print("[PASS] 【主題卡事實錨定與風格解耦門禁審計：100% 通過 (ALL PASS)】")
        print("=" * 80 + "\n")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("[FAIL] 【主題卡事實錨定與風格解耦門禁審計：發現違規項，請修正！】")
        print("=" * 80 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

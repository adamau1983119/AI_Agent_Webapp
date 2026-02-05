#!/usr/bin/env python3
"""
自動修復硬編碼文字工具
======================
功能：
1. 掃描所有硬編碼文字
2. 生成規範的 i18n key
3. 創建翻譯條目
4. 自動替換組件代碼
5. 校對檢查

作者：AI Agent
日期：2026-02-05
"""

import os
import re
import sys
import io
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict

# 設置 UTF-8 編碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 配置
FRONTEND_PATH = Path(__file__).parent.parent / "frontend" / "src"
PAGES_PATH = FRONTEND_PATH / "pages"
COMPONENTS_PATH = FRONTEND_PATH / "components"
I18N_PATH = FRONTEND_PATH / "i18n" / "index.ts"

# 品牌名稱例外
BRAND_EXCEPTIONS = ["INFLUENCERS", "AI-POWERED CONTENT CREATION"]

# 忽略的模式（註釋、className 等）
IGNORE_PATTERNS = [
    r'^\s*//',           # 單行註釋
    r'^\s*\*',           # 多行註釋
    r'className=',       # className 屬性
    r'data-testid=',     # testid 屬性
    r'console\.',        # console 輸出
    r'import\s+',        # import 語句
    r'export\s+',        # export 語句
]

# 翻譯映射表（中文 -> 英文 -> 日文）
COMMON_TRANSLATIONS = {
    '載入中': ('Loading', '読み込み中'),
    '搜尋中': ('Searching', '検索中'),
    '儲存': ('Save', '保存'),
    '取消': ('Cancel', 'キャンセル'),
    '確認': ('Confirm', '確認'),
    '刪除': ('Delete', '削除'),
    '編輯': ('Edit', '編集'),
    '返回': ('Back', '戻る'),
    '下一步': ('Next', '次へ'),
    '上一步': ('Previous', '前へ'),
    '提交': ('Submit', '送信'),
    '關閉': ('Close', '閉じる'),
    '重試': ('Retry', '再試行'),
    '成功': ('Success', '成功'),
    '失敗': ('Failed', '失敗'),
    '錯誤': ('Error', 'エラー'),
    '我的頻道': ('My Channels', 'マイチャンネル'),
    '建立頻道': ('Create Channel', 'チャンネル作成'),
    '頻道名稱': ('Channel Name', 'チャンネル名'),
    '頻道描述': ('Channel Description', 'チャンネル説明'),
    '選擇類別': ('Select Category', 'カテゴリを選択'),
    '選擇地區': ('Select Region', '地域を選択'),
    '自定義關鍵字': ('Custom Keywords', 'カスタムキーワード'),
    '添加': ('Add', '追加'),
    '移除': ('Remove', '削除'),
    '主題': ('Topics', 'トピック'),
    '內容': ('Content', 'コンテンツ'),
    '生成': ('Generate', '生成'),
    '發布': ('Publish', '公開'),
    '排程': ('Schedule', 'スケジュール'),
    '設定': ('Settings', '設定'),
    '偏好設定': ('Preferences', '環境設定'),
    '個人資料': ('Profile', 'プロフィール'),
    '帳號': ('Account', 'アカウント'),
    '密碼': ('Password', 'パスワード'),
    '登入': ('Sign In', 'ログイン'),
    '登出': ('Sign Out', 'ログアウト'),
    '註冊': ('Register', '登録'),
    '已連結': ('Connected', '連携済み'),
    '未連結': ('Not Connected', '未連携'),
    '深色模式': ('Dark Mode', 'ダークモード'),
    '淺色模式': ('Light Mode', 'ライトモード'),
    '通知': ('Notifications', '通知'),
    '語言': ('Language', '言語'),
    '時區': ('Timezone', 'タイムゾーン'),
    '風格檔案': ('Style Profile', 'スタイルプロファイル'),
    '靈感策劃': ('Inspiration', 'インスピレーション'),
    '平台連接': ('Social Connect', 'ソーシャル連携'),
    '一鍵發布': ('One-Click Publish', 'ワンクリック公開'),
    '控制面板': ('Dashboard', 'ダッシュボード'),
    '今日': ('Today', '今日'),
    '本週': ('This Week', '今週'),
    '趨勢': ('Trend', 'トレンド'),
    '時尚': ('Fashion', 'ファッション'),
    '美食': ('Food', 'グルメ'),
    '圖片': ('Images', '画像'),
    '影片': ('Video', '動画'),
    '腳本': ('Script', 'スクリプト'),
    '短文': ('Short Post', 'ショートポスト'),
    '長文': ('Long Post', 'ロングポスト'),
    '評分': ('Rating', '評価'),
    '複製': ('Copy', 'コピー'),
    '分享': ('Share', 'シェア'),
    '全部': ('All', 'すべて'),
    '篩選': ('Filter', 'フィルター'),
    '排序': ('Sort', '並べ替え'),
    '最新': ('Latest', '最新'),
    '熱門': ('Popular', '人気'),
    '推薦': ('Recommended', 'おすすめ'),
    '更多': ('More', 'もっと見る'),
    '查看': ('View', '表示'),
    '詳情': ('Details', '詳細'),
    '狀態': ('Status', 'ステータス'),
    '來源': ('Source', 'ソース'),
    '類別': ('Category', 'カテゴリ'),
    '標籤': ('Tags', 'タグ'),
    '日期': ('Date', '日付'),
    '時間': ('Time', '時間'),
    '字數': ('Word Count', '文字数'),
    '預覽': ('Preview', 'プレビュー'),
    '匯出': ('Export', 'エクスポート'),
    '匯入': ('Import', 'インポート'),
}

@dataclass
class TranslationEntry:
    """翻譯條目"""
    key: str
    zh_tw: str
    en: str
    ja: str
    file: str
    line: int

def generate_key(module: str, text: str, existing_keys: set) -> str:
    """生成唯一的 i18n key"""
    # 從文字推斷 key 名稱
    text_clean = text.strip()
    
    # 嘗試匹配常見翻譯
    for zh, (en, ja) in COMMON_TRANSLATIONS.items():
        if zh in text_clean:
            base_key = f"{module}.{en.lower().replace(' ', '')}"
            if base_key not in existing_keys:
                return base_key
    
    # 生成基於文字的 key
    # 移除特殊字符
    clean = re.sub(r'[^\w\u4e00-\u9fff]', '', text_clean)
    
    # 如果是中文，取前 4 個字
    if re.search(r'[\u4e00-\u9fff]', clean):
        clean = clean[:4]
    else:
        # 英文取前 3 個單詞
        words = clean.split()[:3]
        clean = ''.join(words)
    
    # 轉換為 camelCase
    base_key = f"{module}.{clean}"
    
    # 確保唯一性
    if base_key in existing_keys:
        counter = 1
        while f"{base_key}{counter}" in existing_keys:
            counter += 1
        base_key = f"{base_key}{counter}"
    
    return base_key

def translate_text(zh_text: str) -> Tuple[str, str]:
    """翻譯中文文字為英文和日文"""
    # 嘗試匹配常見翻譯
    for zh, (en, ja) in COMMON_TRANSLATIONS.items():
        if zh in zh_text:
            # 替換匹配部分
            en_text = zh_text.replace(zh, en)
            ja_text = zh_text.replace(zh, ja)
            
            # 處理剩餘的中文
            if re.search(r'[\u4e00-\u9fff]', en_text):
                en_text = f"[TRANSLATE] {zh_text}"
            if re.search(r'[\u4e00-\u9fff]', ja_text):
                ja_text = f"[TRANSLATE] {zh_text}"
            
            return en_text, ja_text
    
    # 如果沒有匹配，標記需要手動翻譯
    return f"[TRANSLATE] {zh_text}", f"[TRANSLATE] {zh_text}"

def should_skip_line(line: str) -> bool:
    """檢查是否應該跳過這一行"""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, line):
            return True
    return False

def is_in_t_function(line: str, text: str) -> bool:
    """檢查文字是否已在 t() 函數中"""
    # 檢查是否在 t('...') 或 t("...") 中
    patterns = [
        rf"t\(['\"].*{re.escape(text)}.*['\"]\)",
        rf"\{{t\(['\"].*{re.escape(text)}.*['\"]\)\}}"
    ]
    for pattern in patterns:
        if re.search(pattern, line):
            return True
    return False

def extract_hardcoded_texts(file_path: Path) -> List[Tuple[int, str, str]]:
    """從文件中提取硬編碼文字"""
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"[ERROR] Cannot read {file_path}: {e}")
        return results
    
    for i, line in enumerate(lines, 1):
        # 跳過不需要處理的行
        if should_skip_line(line):
            continue
        
        # 提取中文文字
        # 匹配 JSX 文字內容 >文字<
        jsx_matches = re.findall(r'>([^<>]*[\u4e00-\u9fff]+[^<>]*)<', line)
        for match in jsx_matches:
            text = match.strip()
            if text and not is_brand_exception(text) and not is_in_t_function(line, text):
                # 清理文字
                text = clean_text(text)
                if text and len(text) > 1:
                    results.append((i, text, line))
        
        # 匹配字符串中的中文 '文字' 或 "文字"
        string_matches = re.findall(r'["\']([^"\']*[\u4e00-\u9fff]+[^"\']*)["\']', line)
        for match in string_matches:
            text = match.strip()
            if text and not is_brand_exception(text) and not is_in_t_function(line, text):
                text = clean_text(text)
                if text and len(text) > 1:
                    # 避免重複
                    if not any(t[1] == text for t in results if t[0] == i):
                        results.append((i, text, line))
    
    return results

def is_brand_exception(text: str) -> bool:
    """檢查是否為品牌例外"""
    for exc in BRAND_EXCEPTIONS:
        if exc in text:
            return True
    return False

def clean_text(text: str) -> str:
    """清理文字，移除不必要的部分"""
    # 移除 JSX 表達式
    text = re.sub(r'\{[^}]+\}', '', text)
    # 移除多餘空白
    text = ' '.join(text.split())
    # 移除開頭和結尾的標點
    text = text.strip('.,;:!?()[]{}"\' ')
    return text

def get_module_name(file_path: Path) -> str:
    """從文件路徑獲取模組名稱"""
    name = file_path.stem.lower()
    
    # 特殊映射
    mappings = {
        'topicdetail': 'topics',
        'createchannel': 'channels',
        'oauthcallback': 'auth',
        'forgotpassword': 'auth',
        'languageselection': 'language',
        'styleprofile': 'style',
        'socialconnect': 'social',
    }
    
    return mappings.get(name, name)

def process_file(file_path: Path, existing_keys: set) -> List[TranslationEntry]:
    """處理單個文件"""
    entries = []
    module = get_module_name(file_path)
    
    hardcoded = extract_hardcoded_texts(file_path)
    
    for line_num, text, context in hardcoded:
        # 生成 key
        key = generate_key(module, text, existing_keys)
        existing_keys.add(key)
        
        # 翻譯
        en_text, ja_text = translate_text(text)
        
        entries.append(TranslationEntry(
            key=key,
            zh_tw=text,
            en=en_text,
            ja=ja_text,
            file=str(file_path),
            line=line_num
        ))
    
    return entries

def generate_i18n_additions(entries: List[TranslationEntry]) -> Dict[str, str]:
    """生成需要添加到 i18n 的代碼"""
    # 按模組分組
    by_module = defaultdict(list)
    for entry in entries:
        module = entry.key.split('.')[0]
        by_module[module].append(entry)
    
    zh_tw_code = []
    en_code = []
    ja_code = []
    
    for module, items in sorted(by_module.items()):
        zh_tw_code.append(f"\n  // {module.upper()}")
        en_code.append(f"\n  // {module.upper()}")
        ja_code.append(f"\n  // {module.upper()}")
        
        for entry in items:
            zh_tw_code.append(f"  '{entry.key}': '{entry.zh_tw}',")
            en_code.append(f"  '{entry.key}': '{entry.en}',")
            ja_code.append(f"  '{entry.key}': '{entry.ja}',")
    
    return {
        'zh-TW': '\n'.join(zh_tw_code),
        'en': '\n'.join(en_code),
        'ja': '\n'.join(ja_code),
    }

def generate_replacement_map(entries: List[TranslationEntry]) -> Dict[str, List[Tuple[str, str]]]:
    """生成替換映射"""
    # 按文件分組
    by_file = defaultdict(list)
    for entry in entries:
        by_file[entry.file].append((entry.zh_tw, entry.key))
    
    return dict(by_file)

def main():
    """主函數"""
    print("=" * 60)
    print("AUTO-FIX HARDCODED TEXT TOOL")
    print("=" * 60)
    print()
    
    existing_keys = set()
    all_entries = []
    
    # 處理 pages 目錄
    print("[SCAN] Processing pages directory...")
    if PAGES_PATH.exists():
        for file_path in PAGES_PATH.glob("*.tsx"):
            entries = process_file(file_path, existing_keys)
            if entries:
                print(f"  [FILE] {file_path.name}: {len(entries)} items")
                all_entries.extend(entries)
    
    # 處理 components 目錄
    print("\n[SCAN] Processing components directory...")
    if COMPONENTS_PATH.exists():
        for file_path in COMPONENTS_PATH.glob("**/*.tsx"):
            entries = process_file(file_path, existing_keys)
            if entries:
                print(f"  [FILE] {file_path.name}: {len(entries)} items")
                all_entries.extend(entries)
    
    print(f"\n[TOTAL] Found {len(all_entries)} hardcoded texts")
    
    # 生成 i18n 代碼
    print("\n[GEN] Generating i18n translations...")
    i18n_code = generate_i18n_additions(all_entries)
    
    # 保存到文件
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 保存翻譯代碼
    for lang, code in i18n_code.items():
        output_file = output_dir / f"i18n_{lang.replace('-', '_')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"  [SAVE] {output_file}")
    
    # 保存替換映射
    replacement_map = generate_replacement_map(all_entries)
    map_file = output_dir / "replacement_map.json"
    with open(map_file, 'w', encoding='utf-8') as f:
        json.dump(replacement_map, f, ensure_ascii=False, indent=2)
    print(f"  [SAVE] {map_file}")
    
    # 保存完整報告
    report_file = output_dir / "full_report.json"
    report_data = [
        {
            'key': e.key,
            'zh_tw': e.zh_tw,
            'en': e.en,
            'ja': e.ja,
            'file': e.file,
            'line': e.line
        }
        for e in all_entries
    ]
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    print(f"  [SAVE] {report_file}")
    
    print("\n" + "=" * 60)
    print("[DONE] All files generated!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review output/i18n_*.txt files")
    print("2. Add translations to frontend/src/i18n/index.ts")
    print("3. Replace hardcoded texts in components")
    print("4. Run verification scan")
    
    return all_entries

if __name__ == "__main__":
    main()


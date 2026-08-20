"""
短文生成 Prompt 模板（v7：僅 summary_flash，禁止 original_content）
"""
from typing import List, Optional

from app.prompts.system_constants import ARTICLE_SYSTEM


def build_article_prompt(
    topic_title: str,
    topic_category: str,
    keywords: List[str],
    target_length: int = 500,
    summary_flash: Optional[str] = None,
    source_urls: Optional[List[str]] = None,
    target_language: Optional[str] = None,
    style_hint: Optional[str] = None,
) -> str:
    """
    建立短文生成 Prompt（D5：輸入以 summary_flash 為主）。
    """
    lang_labels = {
        "zh-TW": "繁體中文",
        "en": "English",
        "ja": "日本語",
    }
    target_lang_label = lang_labels.get(target_language, "繁體中文") if target_language else "繁體中文"

    category_map = {
        "fashion": "時尚",
        "food": "美食",
        "trend": "社會趨勢",
    }
    category_cn = category_map.get(topic_category, topic_category)
    keywords_str = "、".join(keywords) if keywords else ""
    source_urls_str = "\n".join([f"- {url}" for url in (source_urls or [])])
    fact_block = (summary_flash or topic_title or "").strip()[:400]
    style_block = (style_hint or "").strip()

    return f"""{ARTICLE_SYSTEM}

**summary_flash（事實源）**：
{fact_block}

**來源連結**：
{source_urls_str if source_urls_str else "無"}

**主題**：{topic_title}
**分類**：{category_cn}
**關鍵字**：{keywords_str}
**目標長度**：約 {target_length} 字
{f"**風格 DNA（精簡）**：{style_block}" + chr(10) if style_block else ""}
**要求**：
1. **僅根據 summary_flash 改寫**，不得添加未出現的資訊
2. 若有來源連結，可適度引用格式：「根據報導 (連結)…」
3. 適合小紅書/Instagram 風格；**輸出語言為 {target_lang_label}**
4. 長度約 {target_length} 字；可適度使用 emoji
5. 避免具體人名與易過時職稱
6. **風格與主題解耦防污染**：風格 DNA 僅提供語氣、句型節奏與觀點視角，嚴禁將與本主題領域無關之專有名詞或食物詞彙（如非美食主題卻提及食物比喻）生搬硬套入文章中

請直接輸出短文，不要標題或說明文字。"""

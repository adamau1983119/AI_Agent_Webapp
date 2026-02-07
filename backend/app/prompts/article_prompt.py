"""
短文生成 Prompt 模板
"""
from typing import List, Optional


def build_article_prompt(
    topic_title: str,
    topic_category: str,
    keywords: List[str],
    target_length: int = 500,
    original_content: Optional[str] = None,
    source_urls: Optional[List[str]] = None,
    original_language: Optional[str] = None,
    style_info: Optional[dict] = None,
    target_language: Optional[str] = None
) -> str:
    """
    建立短文生成 Prompt（改進版：基於原文內容改寫）
    
    Args:
        topic_title: 主題標題
        topic_category: 主題分類
        keywords: 關鍵字列表
        target_length: 目標長度（字）
        original_content: 原文內容（可選）
        source_urls: 來源 URL 列表（可選）
        original_language: 原文語言（可選）
        style_info: 原文風格資訊（可選）
        target_language: 目標輸出語言（可選，預設中文）
        
    Returns:
        Prompt 字串
    """
    # 語言標籤映射
    lang_labels = {
        "zh-TW": "繁體中文",
        "en": "English",
        "ja": "日本語",
    }
    target_lang_label = lang_labels.get(target_language, "繁體中文") if target_language else "繁體中文"
    
    category_map = {
        "fashion": "時尚",
        "food": "美食",
        "trend": "社會趨勢"
    }
    category_cn = category_map.get(topic_category, topic_category)
    keywords_str = "、".join(keywords) if keywords else ""
    
    # 如果有原文內容，使用改寫模式
    if original_content:
        source_urls_str = "\n".join([f"- {url}" for url in (source_urls or [])])
        
        # 構建風格要求
        style_requirements = ""
        if style_info:
            tone_map = {
                "enthusiastic": "熱情洋溢",
                "news_report": "新聞報導",
                "casual_sharing": "輕鬆分享",
                "neutral": "中性"
            }
            tone_cn = tone_map.get(style_info.get("tone"), "自然")
            style_requirements = f"\n**風格要求**：\n- 語調：{tone_cn}\n- 結構：保持原文的段落風格\n- 詞彙：保持原文的專業程度\n"
        
        prompt = f"""請基於以下來源內容，改寫為適合社群媒體的{target_lang_label}短文：

**來源內容**（{original_language or "原文"}）：
{original_content[:2000]}  # 限制長度避免 token 過多

**來源連結**：
{source_urls_str if source_urls_str else "無"}

**主題**：{topic_title}
**分類**：{category_cn}
**關鍵字**：{keywords_str}
**目標長度**：約 {target_length} 字
{style_requirements}
**要求**：
1. **必須基於來源內容改寫**，不要自行創作或添加未在原文中的資訊
2. **必須在文章中引用原文連結**，格式如：「根據原文報導 ({source_urls[0] if source_urls else "來源連結"})，...」
3. 內容生動有趣，適合小紅書/Instagram 風格
4. 語言自然流暢，符合{target_lang_label}表達習慣
5. **輸出語言必須為{target_lang_label}**
6. 長度控制在 {target_length} 字左右
7. 使用 emoji 增加趣味性（適度使用）
8. 結構清晰，有開頭、主體、結尾
9. **保持原文的核心資訊和事實**，不要改變或誇大

**風格**：
- 親切自然，像朋友分享
- 避免過於正式或學術化
- 可以適當優化表達方式，但不要改變事實

**重要注意事項**：
- **嚴格基於原文內容**，不要無中生有
- 如果原文提到品牌名稱，必須準確保留（如：Valentino、Dior、Ami 等）
- 避免使用具體人名（如設計師、創意總監的名字），優先使用通用描述（如「設計師」、「品牌」、「設計團隊」等）
- 避免使用可能變動的時效性資訊（如職位、人名等）
- 專注於品牌、設計、風格等不會變動的內容

請直接輸出改寫後的短文內容，不要包含標題、說明文字或其他格式標記。"""
    else:
        # 沒有原文內容時，使用原來的生成模式
        prompt = f"""請為以下主題生成一篇適合社群媒體的{target_lang_label}短文：

**主題**：{topic_title}
**分類**：{category_cn}
**關鍵字**：{keywords_str}
**目標長度**：約 {target_length} 字
**輸出語言**：{target_lang_label}

**要求**：
1. 內容生動有趣，適合小紅書/Instagram 風格
2. 語言自然流暢，符合{target_lang_label}表達習慣
3. 包含實用資訊或觀點
4. **輸出語言必須為{target_lang_label}**
5. 長度控制在 {target_length} 字左右
6. 使用 emoji 增加趣味性（適度使用）
7. 結構清晰，有開頭、主體、結尾

**風格**：
- 親切自然，像朋友分享
- 避免過於正式或學術化
- 可以加入個人觀點或經驗

**重要注意事項**：
- 避免使用具體人名（如設計師、創意總監的名字），優先使用通用描述（如「設計師」、「品牌」、「設計團隊」等）
- 避免使用可能變動的時效性資訊（如職位、人名等）
- 專注於品牌、設計、風格等不會變動的內容

請直接輸出短文內容，不要包含標題、說明文字或其他格式標記。"""
    
    return prompt

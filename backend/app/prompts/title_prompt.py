"""
中文標題生成 Prompt 模板
"""
from app.models.topic import Category


def build_title_prompt(
    category: Category,
    keyword: str = None,
    english_title: str = None
) -> str:
    """
    建立中文標題生成 Prompt（包含標題和30字摘要）
    
    Args:
        category: 主題分類
        keyword: 關鍵字（可選）
        english_title: 英文標題（可選，用於翻譯）
        
    Returns:
        Prompt 字串
    """
    category_map = {
        Category.FASHION: "時尚",
        Category.FOOD: "美食",
        Category.TREND: "社會趨勢"
    }
    category_cn = category_map.get(category, category.value)
    
    if english_title:
        # 翻譯模式
        prompt = f"""請將以下英文標題翻譯並改寫為適合社群媒體的中文標題和摘要：

**英文標題**：{english_title}
**分類**：{category_cn}

**要求**：
1. 標題：翻譯準確，符合中文表達習慣，吸引人，適合小紅書/Instagram 風格，長度控制在 15-25 字之間
2. 摘要：根據標題內容生成約30字的中文摘要，簡潔說明主題的核心內容和價值
3. 可以適當優化，使其更符合目標受眾
4. 避免使用過於正式或學術化的詞彙

**風格**：
- 親切自然，有吸引力
- 可以使用 emoji（適度使用）
- 符合 {category_cn} 分類的風格

**輸出格式**（必須嚴格按照此格式）：
標題：[中文標題]
摘要：[約30字的中文摘要]

請直接輸出，不要包含其他說明文字。"""
    else:
        # 生成模式
        keyword_part = f"**關鍵字**：{keyword}\n" if keyword else ""
        prompt = f"""請為以下主題生成一個適合社群媒體的中文標題和摘要：

**分類**：{category_cn}
{keyword_part}
**要求**：
1. 標題：吸引人，適合小紅書/Instagram 風格，長度控制在 15-25 字之間，符合 {category_cn} 分類的主題
2. 摘要：根據標題內容生成約30字的中文摘要，簡潔說明主題的核心內容、價值或亮點
3. 標題必須具體，不能只是關鍵字的簡單重複（例如：不要只寫「美食趨勢」，而要寫「2025年最值得關注的5大美食趨勢」）
4. 可以使用 emoji（適度使用）
5. 避免使用過於正式或學術化的詞彙

**風格**：
- 親切自然，有吸引力
- 能夠引起目標受眾的興趣
- 符合 {category_cn} 分類的風格

**輸出格式**（必須嚴格按照此格式）：
標題：[中文標題]
摘要：[約30字的中文摘要]

請直接輸出，不要包含其他說明文字。"""
    
    return prompt


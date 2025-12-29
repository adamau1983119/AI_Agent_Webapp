"""
短文生成 Prompt 模板
"""
from typing import List


def build_article_prompt(
    topic_title: str,
    topic_category: str,
    keywords: List[str],
    target_length: int = 500
) -> str:
    """
    建立短文生成 Prompt
    
    Args:
        topic_title: 主題標題
        topic_category: 主題分類
        keywords: 關鍵字列表
        target_length: 目標長度（字）
        
    Returns:
        Prompt 字串
    """
    category_map = {
        "fashion": "時尚",
        "food": "美食",
        "trend": "社會趨勢"
    }
    category_cn = category_map.get(topic_category, topic_category)
    keywords_str = "、".join(keywords) if keywords else ""
    
    prompt = f"""請為以下主題生成一篇適合社群媒體的短文：

**主題**：{topic_title}
**分類**：{category_cn}
**關鍵字**：{keywords_str}
**目標長度**：約 {target_length} 字

**要求**：
1. 內容生動有趣，適合小紅書/Instagram 風格
2. 語言自然流暢，符合目標受眾
3. 包含實用資訊或觀點
4. 長度控制在 {target_length} 字左右
5. 使用 emoji 增加趣味性（適度使用）
6. 結構清晰，有開頭、主體、結尾

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

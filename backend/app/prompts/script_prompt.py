"""
腳本生成 Prompt 模板
"""
from typing import List


def build_script_prompt(
    topic_title: str,
    topic_category: str,
    keywords: List[str],
    target_duration: int = 30
) -> str:
    """
    建立腳本生成 Prompt
    
    Args:
        topic_title: 主題標題
        topic_category: 主題分類
        keywords: 關鍵字列表
        target_duration: 目標時長（秒）
        
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
    
    # 估算字數（假設每 17 字 = 1 秒）
    estimated_words = target_duration * 17
    
    prompt = f"""請為以下主題生成一個適合短影片的腳本：

**主題**：{topic_title}
**分類**：{category_cn}
**關鍵字**：{keywords_str}
**目標時長**：約 {target_duration} 秒（約 {estimated_words} 字）

**要求**：
1. 腳本適合拍攝短影片（小紅書/YouTube Shorts/Instagram Reels）
2. 語言口語化，適合口述
3. 包含清晰的結構：
   - 開場（3-5 秒）：吸引注意力
   - 主體內容（20-25 秒）：核心資訊
   - 結尾（3-5 秒）：呼籲行動或總結
4. 時長控制在 {target_duration} 秒左右（約每 17 字 = 1 秒）
5. 可以包含拍攝提示（用括號標註）

**風格**：
- 輕鬆活潑，有節奏感
- 適合快速剪輯和視覺呈現
- 語言簡潔有力

**重要注意事項**：
- 避免使用具體人名（如設計師、創意總監的名字），優先使用通用描述（如「設計師」、「品牌」、「設計團隊」等）
- 避免使用可能變動的時效性資訊（如職位、人名等）
- 專注於品牌、設計、風格等不會變動的內容

請直接輸出腳本內容，使用自然的口語表達，不要包含標題或其他格式標記。"""
    
    return prompt

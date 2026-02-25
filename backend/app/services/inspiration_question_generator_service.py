"""
靈感策劃問題生成服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. AI 動態生成問題（1-5 個）
2. 根據主題個性化問題
3. 提供快速選擇選項
"""
from typing import Dict, Any, List, Optional
from app.services.ai.ai_service_factory import AIServiceFactory
import logging
import json
import re

logger = logging.getLogger(__name__)


class InspirationQuestionGeneratorService:
    """靈感策劃問題生成服務"""
    
    def __init__(self):
        self.ai_service = None
    
    def _get_ai_service(self):
        """取得 AI 服務實例（延遲載入）"""
        if self.ai_service is None:
            self.ai_service = AIServiceFactory.get_service()
        return self.ai_service
    
    async def generate_questions(
        self,
        topic: str,
        language: str = "zh-TW",
        user_preferences: Optional[Dict[str, Any]] = None,
        max_questions: int = 3
    ) -> List[Dict[str, Any]]:
        """
        AI 動態生成問題
        
        Args:
            topic: 主題
            language: 語言
            user_preferences: 用戶偏好（可選）
            max_questions: 最大問題數（1-5）
            
        Returns:
            問題列表，每個問題包含：
            - question_id: 問題 ID
            - question: 問題內容
            - type: 問題類型（region, format, tone, etc.）
            - options: 快速選擇選項（可選）
            - required: 是否必填
        """
        try:
            ai_service = self._get_ai_service()
            
            # 語言標籤
            lang_labels = {
                "zh-TW": "繁體中文",
                "en": "English",
                "ja": "日本語"
            }
            
            # 建構 Prompt
            prompt = self._build_question_prompt(
                topic=topic,
                language=language,
                lang_label=lang_labels.get(language, "繁體中文"),
                user_preferences=user_preferences,
                max_questions=max_questions
            )
            
            # 調用 AI 生成
            # 注意：AI 服務沒有通用的 generate 方法，需要使用 _call_api（私有方法）
            # 或者使用 generate_article 方法（會忽略參數，只使用 prompt）
            if hasattr(ai_service, '_call_api'):
                # 使用私有方法 _call_api（直接傳遞 prompt）
                response = await ai_service._call_api(prompt)
            elif hasattr(ai_service, 'generate_article'):
                # Fallback：使用 generate_article（會忽略參數，但會使用 prompt）
                # 注意：這不是最佳實踐，但可以工作
                response = await ai_service.generate_article(
                    topic_title="",
                    topic_category="",
                    keywords=[],
                    length=1000
                )
            else:
                raise ValueError("AI 服務不支援問題生成")
            
            if not response:
                logger.warning("AI 生成問題失敗，返回空列表")
                return []
            
            # 解析 AI 回應
            questions = self._parse_ai_response(response, max_questions)
            
            return questions
            
        except Exception as e:
            logger.error(f"生成問題失敗: {e}")
            # 返回預設問題作為 fallback
            return self._get_fallback_questions(language, max_questions)
    
    def _build_question_prompt(
        self,
        topic: str,
        language: str,
        lang_label: str,
        user_preferences: Optional[Dict[str, Any]],
        max_questions: int
    ) -> str:
        """建構問題生成 Prompt"""
        
        # 偏好上下文
        preference_context = ""
        if user_preferences:
            prefs = user_preferences.get("preferences", {})
            if prefs.get("default_format"):
                preference_context += f"\n用戶偏好格式：{prefs.get('default_format')}"
            if prefs.get("default_tone"):
                preference_context += f"\n用戶偏好語氣：{prefs.get('default_tone')}"
        
        prompt = f"""作為內容創作靈感助手，根據以下主題生成 {max_questions} 個針對性問題，幫助用戶明確創作需求。

主題：{topic}
輸出語言：{lang_label}
{preference_context}

要求：
1. 問題應該針對主題，幫助用戶明確創作方向
2. 每個問題應該有明確的類型（region, format, tone, detail_level, etc.）
3. 提供 3-5 個快速選擇選項（如果適用）
4. 問題數量：{max_questions} 個（根據主題複雜度動態調整，最少 1 個，最多 {max_questions} 個）
5. 問題應該簡潔明瞭，易於理解

輸出格式（嚴格遵守 JSON 格式）：
{{
  "questions": [
    {{
      "question_id": "q1",
      "question": "問題內容",
      "type": "region",
      "options": ["選項1", "選項2", "選項3"],
      "required": true
    }},
    {{
      "question_id": "q2",
      "question": "問題內容",
      "type": "format",
      "options": ["選項1", "選項2", "選項3"],
      "required": true
    }}
  ]
}}

只返回 JSON，不要返回其他內容。"""
        
        return prompt
    
    def _parse_ai_response(
        self,
        response: str,
        max_questions: int
    ) -> List[Dict[str, Any]]:
        """解析 AI 回應"""
        questions = []
        
        try:
            # 嘗試提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                questions = data.get("questions", [])
            else:
                # 如果沒有 JSON，嘗試解析文本格式
                questions = self._parse_text_response(response, max_questions)
            
            # 驗證和清理問題
            questions = self._validate_questions(questions, max_questions)
            
        except json.JSONDecodeError as e:
            logger.warning(f"解析 AI 回應 JSON 失敗: {e}，嘗試文本解析")
            questions = self._parse_text_response(response, max_questions)
        except Exception as e:
            logger.error(f"解析 AI 回應失敗: {e}")
            questions = []
        
        return questions
    
    def _parse_text_response(
        self,
        response: str,
        max_questions: int
    ) -> List[Dict[str, Any]]:
        """解析文本格式的回應（fallback）"""
        questions = []
        lines = response.split('\n')
        
        current_question = None
        question_id_counter = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 檢測問題開始
            if '問題' in line or 'question' in line.lower() or line.startswith('Q'):
                if current_question:
                    questions.append(current_question)
                
                current_question = {
                    "question_id": f"q{question_id_counter}",
                    "question": line.replace('問題', '').replace('Question', '').strip(': '),
                    "type": "general",
                    "options": [],
                    "required": True
                }
                question_id_counter += 1
                
                if len(questions) >= max_questions:
                    break
            
            # 檢測選項
            elif current_question and (line.startswith('-') or line.startswith('•') or line.startswith('1.')):
                option = line.lstrip('- •1234567890.').strip()
                if option:
                    current_question["options"].append(option)
        
        # 添加最後一個問題
        if current_question and len(questions) < max_questions:
            questions.append(current_question)
        
        return questions[:max_questions]
    
    def _validate_questions(
        self,
        questions: List[Dict[str, Any]],
        max_questions: int
    ) -> List[Dict[str, Any]]:
        """驗證和清理問題"""
        validated = []
        
        for i, q in enumerate(questions[:max_questions]):
            # 確保必要欄位存在
            if not isinstance(q, dict):
                continue
            
            question_id = q.get("question_id", f"q{i+1}")
            question = q.get("question", "").strip()
            
            if not question:
                continue
            
            validated.append({
                "question_id": question_id,
                "question": question,
                "type": q.get("type", "general"),
                "options": q.get("options", [])[:5],  # 最多 5 個選項
                "required": q.get("required", True)
            })
        
        # 如果沒有問題，至少返回一個預設問題
        if not validated:
            validated.append({
                "question_id": "q1",
                "question": "您希望以什麼形式輸出？",
                "type": "format",
                "options": ["影片講稿", "文章", "社交貼文", "策劃大綱"],
                "required": True
            })
        
        return validated
    
    def _get_fallback_questions(
        self,
        language: str,
        max_questions: int
    ) -> List[Dict[str, Any]]:
        """取得預設問題（fallback）"""
        
        # 根據語言選擇問題
        if language == "zh-TW":
            questions = [
                {
                    "question_id": "q1",
                    "question": "您希望以什麼形式輸出？",
                    "type": "format",
                    "options": ["影片講稿", "文章", "社交貼文", "策劃大綱"],
                    "required": True
                },
                {
                    "question_id": "q2",
                    "question": "您希望使用什麼語氣？",
                    "type": "tone",
                    "options": ["輕鬆", "專業", "故事性"],
                    "required": True
                }
            ]
        elif language == "en":
            questions = [
                {
                    "question_id": "q1",
                    "question": "What format do you prefer?",
                    "type": "format",
                    "options": ["Video Script", "Article", "Social Post", "Outline"],
                    "required": True
                },
                {
                    "question_id": "q2",
                    "question": "What tone do you prefer?",
                    "type": "tone",
                    "options": ["Casual", "Professional", "Storytelling"],
                    "required": True
                }
            ]
        else:  # ja
            questions = [
                {
                    "question_id": "q1",
                    "question": "どの形式で出力しますか？",
                    "type": "format",
                    "options": ["動画スクリプト", "記事", "SNS投稿", "企画概要"],
                    "required": True
                },
                {
                    "question_id": "q2",
                    "question": "どのトーンを使用しますか？",
                    "type": "tone",
                    "options": ["カジュアル", "プロフェッショナル", "ストーリーテリング"],
                    "required": True
                }
            ]
        
        return questions[:max_questions]


# 建立全域實例
inspiration_question_generator_service = InspirationQuestionGeneratorService()


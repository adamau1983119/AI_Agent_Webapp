"""
靈感策劃內容生成服務
根據 v5.0 靈感策劃技術設計報告實現

功能：
1. 多格式內容生成（影片講稿/文章/貼文/大綱）
2. 應用用戶偏好（語氣、風格）
3. 包含指定模組（地址、歷史背景等）
"""
from typing import Dict, Any, List, Optional
from app.services.ai.ai_service_factory import AIServiceFactory
from app.services.inspiration_preference_service import inspiration_preference_service
import logging

logger = logging.getLogger(__name__)


class InspirationContentGeneratorService:
    """靈感策劃內容生成服務"""
    
    def __init__(self):
        self.ai_service = None
    
    def _get_ai_service(self):
        """取得 AI 服務實例（延遲載入）"""
        if self.ai_service is None:
            self.ai_service = AIServiceFactory.get_service()
        return self.ai_service
    
    async def generate_content(
        self,
        topic: str,
        user_id: str,
        format_type: str,
        language: str = "zh-TW",
        search_results: Optional[List[Dict[str, Any]]] = None,
        verification_status: Optional[Dict[str, Any]] = None,
        user_answers: Optional[Dict[str, Any]] = None,
        modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成內容
        
        Args:
            topic: 主題
            user_id: 用戶 ID
            format_type: 格式類型（video_script, article, post, outline）
            language: 語言
            search_results: 搜尋結果（可選）
            verification_status: 驗證狀態（可選）
            user_answers: 用戶回答（可選）
            modules: 要包含的模組（可選，如：address, history, signature）
            
        Returns:
            生成的內容，包含：
            - content: 內容文字
            - format: 格式類型
            - modules_included: 包含的模組
            - sources: 使用的來源
        """
        try:
            # 取得用戶偏好
            preferences = await inspiration_preference_service.get_preferences(user_id)
            prefs = preferences.get("preferences", {})
            
            # 建構 Prompt
            prompt = self._build_content_prompt(
                topic=topic,
                format_type=format_type,
                language=language,
                search_results=search_results,
                verification_status=verification_status,
                user_answers=user_answers,
                modules=modules,
                preferences=prefs
            )
            
            # 調用 AI 生成
            ai_service = self._get_ai_service()
            if hasattr(ai_service, '_call_api'):
                content = await ai_service._call_api(prompt)
            else:
                # Fallback
                content = await ai_service.generate_article(
                    topic_title=topic,
                    topic_category="general",
                    keywords=[],
                    length=500
                )
            
            # 提取使用的模組
            modules_included = modules or []
            
            # 提取來源
            sources = []
            if search_results:
                sources = [
                    {
                        "url": r.get("url", ""),
                        "title": r.get("title", ""),
                        "type": r.get("source", "unknown")
                    }
                    for r in search_results[:5]  # 最多 5 個來源
                ]
            
            return {
                "content": content,
                "format": format_type,
                "modules_included": modules_included,
                "sources": sources,
                "verification_status": verification_status
            }
            
        except Exception as e:
            logger.error(f"生成內容失敗: {e}")
            raise
    
    def _build_content_prompt(
        self,
        topic: str,
        format_type: str,
        language: str,
        search_results: Optional[List[Dict[str, Any]]],
        verification_status: Optional[Dict[str, Any]],
        user_answers: Optional[Dict[str, Any]],
        modules: Optional[List[str]],
        preferences: Dict[str, Any]
    ) -> str:
        """建構內容生成 Prompt"""
        
        # 語言標籤
        lang_labels = {
            "zh-TW": "繁體中文",
            "en": "English",
            "ja": "日本語"
        }
        lang_label = lang_labels.get(language, "繁體中文")
        
        # 格式配置
        format_configs = {
            "video_script": {
                "name": "影片講稿",
                "description": "適合拍攝短影片的講稿，包含開場、主體、結尾",
                "length": "300-500 字",
                "structure": ["開場（吸引注意）", "主體（核心內容）", "結尾（行動呼籲）"]
            },
            "article": {
                "name": "文章",
                "description": "適合部落格或長文的文章",
                "length": "800-1200 字",
                "structure": ["引言", "主體段落", "結論"]
            },
            "post": {
                "name": "社交貼文",
                "description": "適合 Instagram、Facebook 等社交媒體的貼文",
                "length": "150-300 字",
                "structure": ["開場", "內容", "Hashtag"]
            },
            "outline": {
                "name": "策劃大綱",
                "description": "內容策劃的大綱結構",
                "length": "200-400 字",
                "structure": ["主題", "要點", "執行建議"]
            }
        }
        
        format_config = format_configs.get(format_type, format_configs["article"])
        
        # 語氣配置
        tone_map = {
            "casual": "輕鬆自然",
            "professional": "專業正式",
            "storytelling": "故事性"
        }
        tone = preferences.get("default_tone", "casual")
        tone_label = tone_map.get(tone, "輕鬆自然")
        
        # 建構 Prompt
        prompt = f"""作為專業內容創作者，請根據以下要求生成{format_config['name']}。

**主題**：{topic}
**格式**：{format_config['name']}
**語言**：{lang_label}
**語氣**：{tone_label}
**目標長度**：{format_config['length']}
**結構要求**：{', '.join(format_config['structure'])}
"""
        
        # 添加搜尋結果
        if search_results:
            prompt += f"\n**參考來源**：\n"
            for i, result in enumerate(search_results[:5], 1):
                prompt += f"{i}. {result.get('title', '')}\n"
                prompt += f"   {result.get('description', '')[:100]}\n"
                prompt += f"   來源：{result.get('url', '')}\n"
        
        # 添加驗證狀態
        if verification_status:
            status = verification_status.get("status", "unknown")
            if status == "verified":
                prompt += "\n**驗證狀態**：✅ 資訊已驗證，可放心使用\n"
            elif status == "partially_verified":
                prompt += "\n**驗證狀態**：⚠️ 資訊部分驗證，請謹慎使用\n"
            else:
                prompt += "\n**驗證狀態**：❌ 資訊未驗證，請謹慎使用\n"
        
        # 添加用戶回答
        if user_answers:
            prompt += f"\n**用戶需求**：\n"
            for key, value in user_answers.items():
                prompt += f"- {key}: {value}\n"
        
        # 添加模組要求
        if modules:
            module_descriptions = {
                "address": "地址資訊",
                "history": "歷史背景",
                "signature": "招牌特色",
                "menu": "菜單項目",
                "hours": "營業時間",
                "price": "價格資訊"
            }
            prompt += f"\n**必須包含的模組**：\n"
            for module in modules:
                desc = module_descriptions.get(module, module)
                prompt += f"- {desc}\n"
        
        # 添加格式特定要求
        if format_type == "video_script":
            prompt += """
**影片講稿要求**：
- 開場要吸引人（3-5 秒）
- 主體要清晰易懂
- 結尾要有行動呼籲
- 適合口語表達
- 可以加入互動元素（如：你知道嗎？）
"""
        elif format_type == "post":
            prompt += """
**社交貼文要求**：
- 開場要吸引眼球
- 內容要簡潔有力
- 結尾要有 Hashtag（3-5 個）
- 適當使用 emoji
- 適合快速閱讀
"""
        elif format_type == "outline":
            prompt += """
**策劃大綱要求**：
- 結構清晰
- 要點明確
- 執行建議具體
- 易於理解
"""
        
        prompt += f"\n請直接輸出{format_config['name']}內容，不要包含標題、說明文字或其他格式標記。輸出語言必須為{lang_label}。"
        
        return prompt


# 建立全域實例
inspiration_content_generator_service = InspirationContentGeneratorService()

